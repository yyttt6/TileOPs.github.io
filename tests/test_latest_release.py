import copy

from baseline_release import merge_latest_release
from nightly_snapshot import build_cache


def row(n, library="torch-eager", latency=10):
    return dict(
        library=library,
        op="ExampleOp",
        case="same",
        workload={"params": {"n": n}, "family": "elementwise"},
        latency_us=latency,
        measurement_id=str(n),
        protocol="v3",
        samples=15,
        tileops_latency_us=None,
        ratio=None,
    )


def test_old_contract_nightly_never_attaches_ratio_to_new_contract():
    latest, old = row(64), row(32)
    base = dict(baseline_release="v2", rows=[latest], historical_rows=[old], frozen_at="new")
    measured = dict(
        op="ExampleOp",
        case_id="same",
        params={"n": 32},
        workload=old["workload"],
        measurement={"latency_ms": 0.005},
    )
    result = build_cache(base, [measured], "a" * 40, "later")
    assert result["rows"][0]["tileops_latency_us"] is None
    assert result["historical_rows"][0]["ratio"] == 2
    assert result["tileops_rows"] == []
    assert base["historical_rows"][0]["tileops_latency_us"] is None


def test_unmatched_contract_keeps_evidence_separate():
    base = dict(baseline_release="v2", rows=[row(64)], frozen_at="new")
    measured = dict(
        op="ExampleOp",
        case_id="same",
        params={"n": 32},
        workload=row(32)["workload"],
        measurement={"latency_ms": 0.005},
    )
    result = build_cache(base, [measured], "a" * 40, "later")
    assert result["rows"][0]["ratio"] is None
    assert result["tileops_rows"] == []
    assert result["historical_tileops_rows"][0]["latency_us"] == 5


def test_older_nightly_cannot_roll_back_torch_or_native_release():
    rows = [row(64), row(64, "native", 8)]
    published = dict(rows=rows, historical_rows=[row(32)], frozen_at="2026-11-07")
    official = dict(rows=[row(32)], frozen_at="2026-11-06")
    official["rows"][0].update(tileops_latency_us=5, tileops_date="2026-11-06")
    release = dict(
        count=2,
        measurements=[
            {k: r[k] for k in ("library", "op", "case", "measurement_id", "protocol")} for r in rows
        ],
    )
    result = merge_latest_release(official, published, release)
    assert result["rows"] == rows
    assert result["historical_rows"][0]["ratio"] == 2
    matching = copy.deepcopy(official)
    matching["rows"][0]["workload"] = rows[0]["workload"]
    result = merge_latest_release(matching, published, release)
    assert [r["ratio"] for r in result["rows"]] == [2, 1.6]
    assert result["frozen_at"] == "2026-11-07"


def test_bounded_refresh_preserves_previous_measurements_and_new_baselines():
    first, second = row(64), row(32)
    second["case"] = "other"
    published = dict(baseline_release="v2", rows=[first, second], frozen_at="2026-11-09")
    release = dict(
        count=2,
        measurements=[
            {k: r[k] for k in ("library", "op", "case", "measurement_id", "protocol")}
            for r in published["rows"]
        ],
    )
    previous = copy.deepcopy(published)
    previous["rows"][1].update(
        tileops_latency_us=5, tileops_date="2026-11-08", tileops_commit="b" * 40
    )
    previous["rows"][1]["latency_us"] = 100  # Superseded baseline must not return.
    inherited = merge_latest_release(previous, published, release)
    measured = dict(
        op="ExampleOp",
        case_id="same",
        params={"n": 64},
        workload=first["workload"],
        measurement={"latency_ms": 0.004},
    )
    result = build_cache(inherited, [measured], "a" * 40, "2026-11-09")
    assert result["rows"][0]["tileops_latency_us"] == 4
    assert result["rows"][1]["tileops_latency_us"] == 5
    assert result["rows"][1]["latency_us"] == 10
    assert result["rows"][1]["tileops_commit"] == "b" * 40
    assert result["nightly"]["fresh_cases"] == 1


def test_new_gemm_measurement_updates_old_name_without_rewriting_baseline():
    saved = row(64)
    saved["op"] = "GemmFwdOp"
    base = dict(baseline_release="v2", rows=[saved], frozen_at="old")
    measured = dict(
        op="GEMMFwdOp",
        case_id="same",
        params={"n": 64},
        workload=saved["workload"],
        measurement={"latency_ms": 0.005},
    )
    legacy = build_cache(base, [measured], "a" * 40, "new")
    assert legacy["rows"][0]["ratio"] is None
    result = build_cache(base, [measured], "a" * 40, "new", use_v010_aliases=True)
    assert result["rows"][0]["ratio"] == 2
    assert result["rows"][0]["op"] == "GemmFwdOp"
    assert result["rows"][0]["measurement_id"] == saved["measurement_id"]
    assert result["tileops_rows"] == []
    assert base["rows"][0]["ratio"] is None


def test_equivalent_historical_alias_cannot_override_newer_timing():
    saved = row(64)
    saved["op"] = "GLARecurrentFwdOp"
    saved["workload"]["params"] = {"gk": [[1, 4, 64], "float16"]}
    published = dict(rows=[saved], frozen_at="2026-11-10")
    release = dict(
        count=1,
        measurements=[
            {k: saved[k] for k in ("library", "op", "case", "measurement_id", "protocol")}
        ],
    )
    fresh = copy.deepcopy(saved)
    fresh.update(tileops_latency_us=5, tileops_date="2026-11-12")
    older = dict(
        op=saved["op"],
        case=saved["case"],
        workload={"params": {"g": [[1, 4, 64], "float16"]}},
        latency_us=7,
        date="2026-11-11",
    )
    official = dict(rows=[fresh], historical_tileops_rows=[older], frozen_at="2026-11-12")
    result = merge_latest_release(official, published, release)
    assert result["rows"][0]["tileops_latency_us"] == 5
    assert result["rows"][0]["measurement_id"] == saved["measurement_id"]


def test_contract_mapping_version_preserves_replay_of_old_snapshot():
    saved = row(64)
    saved["op"] = "GDNFwdOp"
    base = dict(baseline_release="release", rows=[saved], frozen_at="old")
    measured = dict(
        op="GDNFwdOp",
        case_id="same",
        params={"n": 64, "validate_inputs": False},
        workload={"params": {"n": 64, "validate_inputs": False}},
        measurement={"latency_ms": 0.005},
    )
    old = build_cache(
        base,
        [measured],
        "a" * 40,
        "new",
        use_v010_aliases=True,
        alias_version="v010-reviewed-aliases-v1",
    )
    new = build_cache(
        base,
        [measured],
        "a" * 40,
        "new",
        use_v010_aliases=True,
        alias_version="v010-reviewed-aliases-v2",
    )
    assert old["rows"][0]["tileops_latency_us"] is None
    assert new["rows"][0]["tileops_latency_us"] == 5


def test_v2_topk_snapshot_still_replays_before_v3_alias():
    saved = row(64)
    saved["op"] = "TopKSelectFwdOp"
    saved["workload"]["params"] = {"topk": 16}
    base = dict(baseline_release="release", rows=[saved], frozen_at="old")
    measured = dict(
        op=saved["op"],
        case_id="same",
        params={"top_k": 16},
        workload={"params": {"top_k": 16}},
        measurement={"latency_ms": 0.005},
    )
    v2 = build_cache(
        base,
        [measured],
        "a" * 40,
        "new",
        use_v010_aliases=True,
        alias_version="v010-reviewed-aliases-v2",
    )
    v3 = build_cache(
        base,
        [measured],
        "a" * 40,
        "new",
        use_v010_aliases=True,
        alias_version="v010-reviewed-aliases-v3",
    )
    assert v2["rows"][0]["tileops_latency_us"] is None
    assert v3["rows"][0]["tileops_latency_us"] == 5

"""Publication rejects incomplete, contaminated and numerically inconsistent receipts."""

import json

import pytest
from ascend950_snapshot import seal
from nightly_snapshot import COVERAGE, PROTOCOL, build_cache, validate


def bundle(tmp_path):
    check = dict(checked_outputs=1, total_outputs=1, unchecked_reason=None)
    m = dict(
        warmup=3,
        repeats=15,
        flush_bytes=1 << 30,
        measurement_protocol=PROTOCOL,
        profile_coverage_protocol=COVERAGE,
        latency_ms=2.0,
        latency_samples_ms=[2.0] * 15,
        profile_excluded_kernel_count=0,
    )
    row = dict(
        op="ReluFwdOp",
        case_id="x",
        params={"shape": [4]},
        status="passed",
        input_preserved=True,
        raw_replayed=True,
        correctness=check,
        measurement=m,
        coverage=[
            dict(
                complete_sha256="a" * 64,
                result=dict(latency_ms=2.0, profile_excluded_kernel_count=0),
            )
            for _ in range(15)
        ],
    )
    base = dict(
        rows=[
            dict(
                library="native",
                op="ReluFwdOp",
                case="x",
                workload=dict(params={"shape": [4]}),
                latency_us=3000.0,
            )
        ],
        tileops_rows=[],
    )
    meta = dict(
        schema_version=2,
        publisher="server2-physical32",
        publisher_repository="https://github.com/yyttt6/TileOPs.github.io",
        status="passed",
        measurement_protocol=PROTOCOL,
        commit="b" * 40,
        date="2026-11-03",
        operators=["ReluFwdOp"],
        case_ids={"ReluFwdOp": ["x"]},
        fresh_cases=1,
    )
    receipts = {
        "ReluFwdOp": dict(
            guard_exit_code=0,
            result=dict(status="passed", failed=0, passed=1, source_changed=False),
            hardware=dict(cube=32, vector=64, clock_policy="platform-default"),
        )
    }
    values = {
        "meta": meta,
        "measurements": [row],
        "baseline-before": base,
        "receipts": receipts,
        "baseline-cache": build_cache(base, [row], meta["commit"], meta["date"]),
    }
    for name, value in values.items():
        (tmp_path / f"{name}.json").write_text(json.dumps(value))
    seal(tmp_path)
    return tmp_path


def test_roundtrip_preserves_baseline(tmp_path):
    root = bundle(tmp_path)
    validate(root)
    data = json.loads((root / "baseline-cache.json").read_text())
    assert data["rows"][0]["latency_us"] == 3000.0
    assert data["rows"][0]["ratio"] == 1.5


@pytest.mark.parametrize(
    "failure", ["guard", "samples", "mean", "coverage", "contract", "native", "source"]
)
def test_reject_bad_evidence(tmp_path, failure):
    root = bundle(tmp_path)
    name = "measurements"
    rows = json.loads((root / "measurements.json").read_text())
    if failure == "samples":
        rows[0]["measurement"]["latency_samples_ms"].pop()
    if failure == "mean":
        rows[0]["measurement"]["latency_ms"] = 3
    if failure == "coverage":
        rows[0]["coverage"][-1]["result"]["latency_ms"] = 3
    if failure == "contract":
        rows[0]["params"] = {"shape": [8]}
    if failure in ("guard", "source"):
        name = "receipts"
        rows = json.loads((root / "receipts.json").read_text())
        if failure == "guard":
            rows["ReluFwdOp"]["guard_exit_code"] = 76
        else:
            rows["ReluFwdOp"]["result"]["source_changed"] = True
    if failure == "native":
        name = "baseline-cache"
        rows = json.loads((root / "baseline-cache.json").read_text())
        rows["rows"][0]["latency_us"] = 1
    (root / f"{name}.json").write_text(json.dumps(rows))
    seal(root)
    with pytest.raises(AssertionError):
        validate(root)

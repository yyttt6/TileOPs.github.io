"""New joins cannot reinterpret published v3 snapshots or replace baseline evidence."""

import copy
import json
from pathlib import Path

import pytest
from nightly_snapshot import build_cache, validate

SAMPLES = json.loads((Path(__file__).parent / "fixtures/metadata132_cases.json").read_text())[
    "cases"
]
REPRESENTATIVES = list({s["op"]: s for s in SAMPLES}.values())


@pytest.mark.parametrize("sample", REPRESENTATIVES, ids=lambda s: s["op"])
def test_v3_replay_stays_unmatched_and_v4_joins_without_changing_baselines(sample):
    saved = dict(
        library="torch-eager",
        op=sample["old_op"],
        case=sample["case"],
        workload={"params": sample["old_params"]},
        latency_us=10,
        measurement_id="original-baseline",
        protocol="ascend950-isolated-ffts-v3",
        samples=15,
        tileops_latency_us=None,
        ratio=None,
    )
    base = dict(baseline_release="release", rows=[saved], historical_rows=[], frozen_at="old")
    before = copy.deepcopy(base)
    measured = dict(
        op=sample["op"],
        case_id=sample["case"],
        params=sample["new_params"],
        workload={"params": sample["new_params"]},
        measurement={"latency_ms": 0.005},
    )
    v3 = build_cache(
        base,
        [measured],
        "a" * 40,
        "new",
        use_v010_aliases=True,
        alias_version="v010-reviewed-aliases-v3",
    )
    v4 = build_cache(
        base,
        [measured],
        "a" * 40,
        "new",
        use_v010_aliases=True,
        alias_version="v010-reviewed-aliases-v4",
    )
    assert v3["rows"][0]["tileops_latency_us"] is None
    assert v4["rows"][0]["tileops_latency_us"] == 5
    assert v4["rows"][0]["ratio"] == 2
    for field, value in saved.items():
        if not field.startswith("tileops_") and field != "ratio":
            assert v4["rows"][0][field] == value
    assert base == before


def test_validator_accepts_explicit_v4_join_manifest(tmp_path):
    from ascend950_snapshot import seal
    from test_nightly_server2 import bundle

    root = bundle(tmp_path)
    path = root / "meta.json"
    meta = json.loads(path.read_text())
    meta["contract_identity_version"] = "v010-reviewed-aliases-v4"
    path.write_text(json.dumps(meta))
    seal(root)
    validate(root)

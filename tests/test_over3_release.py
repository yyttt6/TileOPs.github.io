"""Release safety: scope isolation, honest API attribution and contract versions."""
import hashlib
import json
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def snapshot():
    return json.loads((Path(__file__).parents[1] / "data/baseline-cache/snapshot.json").read_text())


def test_over3_exact_release_scope_and_unchanged_measurements(snapshot):
    assert len(snapshot["rows"]) == 7735
    changed = [row for row in snapshot["rows"] if row.get("baseline_evidence", {}).get("campaign") == "over3-refresh-20261116"]
    assert len(changed) == 2118
    unchanged = [row for row in snapshot["rows"] if row not in changed]
    assert len(unchanged) == 5617
    assert hashlib.sha256(json.dumps(unchanged, sort_keys=True).encode()).hexdigest() == "6cd4251038798ba3971b1009155f566a60eebfc208fd877659466a437931cacb"
    assert all(row["samples"] == 15 for row in changed)


def test_cross_library_reuse_is_labelled_and_retired_native_ids_are_not_current(snapshot):
    alternative = [row for row in snapshot["rows"] if row.get("requested_library")]
    assert len(alternative) == 34
    assert all(row["library"] == f"{row['requested_library']} (via {row['actual_library']})" for row in alternative)
    assert all(row["baseline_evidence"]["alternative_api_not_target_native"] for row in alternative)
    retired = set(snapshot["retired_measurement_ids"])
    assert len(retired) == 34
    assert not retired.intersection(row["measurement_id"] for row in snapshot["rows"])
    assert retired.issubset(row["measurement_id"] for row in snapshot["historical_rows"])


def test_changed_causal_state_contract_does_not_borrow_old_tileops_output(snapshot):
    incoming = [row for row in snapshot["historical_rows"] if row.get("baseline_evidence", {}).get("ordinal") == 1296]
    assert len(incoming) == 1
    row = incoming[0]
    assert row["workload"]["params"]["conv_state"][0][-1] == 4
    assert "bias" not in row["workload"]["params"]
    assert row["tileops_latency_us"] is None and row["ratio"] is None
    previous = next(x for x in snapshot["rows"] if x["library"] == "torch-eager" and x["op"] == row["op"] and x["case"] == row["case"])
    assert previous["workload"]["params"]["conv_state"][0][-1] == 3
    assert "bias" in previous["workload"]["params"]


def test_real_measurement_protocols_and_input_identity_are_retained(snapshot):
    rows = snapshot["rows"] + snapshot["historical_rows"]
    incoming = [x for x in rows if x.get("baseline_evidence", {}).get("campaign") == "over3-refresh-20261116"]
    assert len(incoming) == 2119
    assert sum(x["protocol"] == "experimental-baseline-full32-marker-session-v1" for x in incoming) == 921
    assert sum(x["protocol"] == "ascend950-isolated-ffts-v3" for x in incoming) == 1198
    assert all(len(x["baseline_evidence"]["input_payload_sha256"]) == 64 for x in incoming)
    assert all(x["baseline_evidence"]["qualified_coverage_not_final_ratio"] for x in incoming)


def test_renderer_normalizes_parameter_infinity_but_rejects_bad_latency(tmp_path, monkeypatch):
    import render_baseline_cache as renderer

    monkeypatch.setattr(renderer, "ROOT", tmp_path)
    monkeypatch.delenv("ASCEND950_OFFICIAL_SNAPSHOT", raising=False)
    folder = tmp_path / "data/baseline-cache"
    folder.mkdir(parents=True)
    row = dict(library="provider", op="ExampleOp", case="case", latency_us=10,
               samples=15, ratio=None, tileops_latency_us=None,
               workload=dict(family="mamba", params={"dt_max": float("inf")}))
    saved = dict(frozen_at="2026-11-16", manifest_cases=1, rows=[row])
    source = folder / "snapshot.json"
    source.write_text(json.dumps(saved))
    renderer.render()
    output = tmp_path / "docs/benchmarks/baseline-cache.json"
    text = output.read_text()
    assert "Infinity" in text
    assert json.loads(text, parse_constant=lambda value: pytest.fail(value))["rows"][0]["workload"]["params"]["dt_max"] == "Infinity"
    saved["rows"][0]["latency_us"] = float("inf")
    source.write_text(json.dumps(saved))
    with pytest.raises(AssertionError):
        renderer.render()


def test_published_download_is_strict_json():
    path = Path(__file__).parents[1] / "data/baseline-cache/snapshot.json"

    def reject_non_json_constant(value):
        raise ValueError(f"Non-JSON constant: {value}")

    data = json.loads(path.read_text(), parse_constant=reject_non_json_constant)
    assert data["baseline_release"] == "over3-refresh-20261116"

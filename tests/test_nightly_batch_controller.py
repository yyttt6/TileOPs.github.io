"""Checkpoint reuse is gated by completed reservations, not by kernel result files alone."""

import json
import sys
from types import SimpleNamespace

import device_batch
import nightly_server2 as controller
import pytest


@pytest.mark.parametrize("fault", ["none", "guard", "numeric"])
def test_batches_checkpoint_complete_guards_and_restart_untouched_work(
    monkeypatch, tmp_path, fault
):
    here = tmp_path / "site/scripts"
    here.mkdir(parents=True)
    (here.parent / "data/baseline-cache").mkdir(parents=True)
    (here.parent / "data/baseline-cache/snapshot.json").write_text('{"rows": []}')
    source = tmp_path / "source"
    source.mkdir()
    out = tmp_path / "out"
    ops = [f"Test{i}Op" for i in range(9)]
    hardware = dict(cube=32, vector=64, clock_policy="platform-default")
    selection = dict(
        operators=ops, unmapped_registrations=[], hardware=hardware, cases={op: ["x"] for op in ops}
    )
    monkeypatch.setattr(controller, "HERE", here)
    monkeypatch.setattr(controller, "identity", lambda _: dict(commit="a" * 40))
    monkeypatch.setattr(
        controller.subprocess,
        "check_output",
        lambda cmd, **kw: "a" * 40 if "rev-parse" in cmd else "",
    )

    def listing(cmd, **kw):
        assert cmd[cmd.index("--op") + 1] == "__list__"
        from pathlib import Path

        Path(cmd[cmd.index("--output") + 1]).write_text(json.dumps(selection))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(controller.subprocess, "run", listing)
    calls = []

    def batch(src, jobs, root, label, owner, **kwargs):
        calls.append([j["op"] for j in jobs])
        records = []
        for job in jobs:
            from pathlib import Path

            p = Path(job["output"])
            p.mkdir()
            failed = fault == "numeric" and job["op"] == ops[0]
            result = dict(
                status="failed" if failed else "passed",
                passed=0 if failed else 1,
                failed=int(failed),
                source_changed=False,
                selection_scope="all-cases",
            )
            row = dict(
                op=job["op"],
                case_id="x",
                family="elementwise",
                params={},
                measurement={},
                status="passed",
            )
            for name, value in [("result", result), ("sources", {}), ("hardware", hardware)]:
                (p / f"{name}.json").write_text(json.dumps(value))
            (p / "results.jsonl").write_text(json.dumps(row) + "\n")
            records.append(dict(op=job["op"]))
            if failed:
                break
        code = 78 if fault == "guard" else 0
        return dict(
            code=code,
            seconds=1,
            worker=dict(records=records),
            guard_receipt="guard.json",
            guard_sha256="a" * 64,
            guard=dict(
                owner=owner, exit_code=code, performance_valid=not code, workload_completed=True
            ),
        )

    monkeypatch.setattr(device_batch, "run", batch)
    monkeypatch.setitem(
        sys.modules, "complete_profile", SimpleNamespace(replay_coverage=lambda _: [])
    )
    monkeypatch.setattr(controller, "build_cache", lambda *a, **kw: {})
    monkeypatch.setattr(controller, "seal", lambda _: None)
    monkeypatch.setattr(controller, "validate", lambda _: None)
    for name, value in [
        ("GITHUB_REPOSITORY", "yyttt6/TileOPs.github.io"),
        ("GITHUB_REF", "refs/heads/main"),
        ("GITHUB_RUN_ID", "1"),
        ("GITHUB_RUN_ATTEMPT", "1"),
    ]:
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(sys, "argv", ["nightly", "--source", str(source), "--output", str(out)])
    if fault == "none":
        controller.main()
    else:
        with pytest.raises(AssertionError):
            controller.main()
    receipts = json.loads((out / "receipts.json").read_text())
    assert set(receipts) == set(ops)
    assert len(calls) == 2
    assert (out / "snapshot").exists() == (fault == "none")
    if fault == "numeric":
        assert calls[1] == ops[1:] and receipts[ops[0]]["result"]["failed"] == 1
    if fault == "guard":
        assert all(v["guard_exit_code"] == 78 for v in receipts.values())

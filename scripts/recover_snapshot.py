"""CPU-only recovery of a sealed snapshot; retain its original run identity."""
import argparse
import shutil
from pathlib import Path

from ascend950_snapshot import validate


def recover(run_id, output, root=Path("/opt/tileops-ci/nightly-server2-20261103/evidence")):
    if not str(run_id).isdigit():
        raise ValueError("Invalid original run ID")
    source = root / f"official-950-{run_id}-1" / "snapshot"
    meta, _ = validate(source)
    if str(meta["run_id"]) != str(run_id) or str(meta["run_attempt"]) != "1":
        raise ValueError("Original snapshot identity mismatch")
    if output.exists():
        raise ValueError("Recovery destination already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, output)
    validate(output)
    print(f"Recovered sealed snapshot: {run_id}, {meta['fresh_cases']} cases")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    recover(args.run_id, args.output)

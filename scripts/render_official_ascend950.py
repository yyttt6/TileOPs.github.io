"""Render only remote official 950 snapshots with the upstream benchmark layout."""

import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "ascend950-profiler-locked-v1"


def render(snapshot, out):
    out.mkdir(parents=True, exist_ok=True)
    # Remove generated pages from the superseded layout, never evidence sources.
    for path in out.glob("*.md"):
        path.unlink()
    if snapshot is None:
        (out / "index.md").write_text(
            "# Benchmarks\n\n"
            "No eligible Ascend 950 performance snapshot has been published yet.\n\n"
            "## Environment\n\nAscend 950DT · TileLang 0.1.15.\n\n"
            "## Method\n\nOnly the dedicated remote nightly CI may publish results. "
            "Matched baselines, correctness, verified clock control and the shared profiler protocol "
            "must all pass before a workload is shown.\n\n"
            "## Coverage\n\n0 operators, 0 measured workloads.\n\n"
            "## Data\n\n| Page | Ops | Workloads |\n| --- | --- | --- |\n"
        )
        return
    meta = json.loads((snapshot / "meta.json").read_text())
    if (meta.get("measurement_protocol") != PROTOCOL
            or meta.get("publisher") != "openlibing-DevEnv-661495"
            or meta.get("status") != "passed"
            or not meta.get("clock_verified")
            or not meta.get("guard_verified")):
        raise ValueError("Not an eligible remote official snapshot")
    xml = ET.parse(snapshot / "bench_results.xml")
    if not xml.findall(".//testcase"):
        raise ValueError("An official measured snapshot must contain actual comparisons")
    command = [sys.executable, str(ROOT / "scripts/gen_bench_pages.py"),
               "--bench-xml", str(snapshot / "bench_results.xml"),
               "--meta", str(snapshot / "meta.json"),
               "--commit", meta["commit"], "--date", meta["date"], "--gpu", meta["gpu"],
               "--out-dir", str(out)]
    if (snapshot / "test_results.xml").exists():
        command += ["--test-xml", str(snapshot / "test_results.xml")]
    subprocess.run(command, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs/benchmarks")
    args = parser.parse_args()
    render(args.snapshot, args.out_dir)


if __name__ == "__main__":
    main()

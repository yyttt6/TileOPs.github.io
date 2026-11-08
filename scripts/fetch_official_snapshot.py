"""Fetch only the dedicated remote workflow's validated artifact for publication."""

import argparse
import io
import json
import os
import stat
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from ascend950_snapshot import validate

REPO = "yyttt6/TileOPs.github.io"
WORKFLOW = ".github/workflows/ascend950-nightly.yml"
API = f"https://api.github.com/repos/{REPO}"
LIMIT = 128 << 20


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(url, binary=False):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "TileOPs-official-publisher"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    opener = urllib.request.build_opener(NoRedirect)
    try:
        response = opener.open(urllib.request.Request(url, headers=headers), timeout=60)
    except urllib.error.HTTPError as exc:
        if not binary or exc.code not in (301, 302, 303, 307, 308):
            raise
        location = exc.headers["Location"]
        if not location.startswith("https://"):
            raise ValueError("Non-HTTPS artifact redirect") from exc
        # The GitHub token must never accompany the signed blob URL.
        response = urllib.request.urlopen(location, timeout=60)
    with response:
        data = response.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError("Artifact exceeds the publication size limit")
    return data if binary else json.loads(data)


def fetch(output, run_id=None):
    explicit = run_id is not None
    if run_id is None:
        try:
            runs = request(f"{API}/actions/workflows/ascend950-nightly.yml/runs?branch=main&status=success&per_page=30")
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return False
            raise
        if not runs["workflow_runs"]:
            return False
        for candidate in runs["workflow_runs"]:
            artifacts = request(f"{API}/actions/runs/{candidate['id']}/artifacts")
            if any(a["name"] == "ascend950-official-snapshot" and not a["expired"]
                   for a in artifacts["artifacts"]):
                run_id = str(candidate["id"])
                break
        if run_id is None:
            raise ValueError("Successful runs have no validated snapshots; preserve current site")
    if not str(run_id).isdigit():
        raise ValueError("Invalid run ID")
    run = request(f"{API}/actions/runs/{run_id}")
    if (run["path"] != WORKFLOW or run["head_branch"] != "main"
            or run["event"] not in ("schedule", "workflow_dispatch")
            or run["head_repository"]["full_name"] != REPO):
        raise ValueError("Snapshot is not from the trusted remote nightly")
    if explicit:
        jobs = request(f"{API}/actions/runs/{run_id}/attempts/{run['run_attempt']}/jobs")
        if not any(j["name"] == "benchmark" and j["conclusion"] == "success"
                   and "ascend950-production" in j.get("labels", []) for j in jobs["jobs"]):
            raise ValueError("Dedicated remote benchmark job has not passed")
    elif run["conclusion"] != "success":
        raise ValueError("Nightly did not succeed")
    artifacts = request(f"{API}/actions/runs/{run_id}/artifacts")
    selected = [a for a in artifacts["artifacts"] if a["name"] == "ascend950-official-snapshot"
                and not a["expired"]]
    if len(selected) != 1:
        raise ValueError("Missing or ambiguous official artifact; preserve the current site")
    archive = request(f"{API}/actions/artifacts/{selected[0]['id']}/zip", binary=True)
    output.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        if sum(i.file_size for i in zipped.infolist()) > LIMIT:
            raise ValueError("Expanded snapshot exceeds size limit")
        for info in zipped.infolist():
            target = output / info.filename
            if not target.resolve().is_relative_to(output.resolve()) or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError("Unsafe artifact member")
        zipped.extractall(output)
    meta, _ = validate(output)
    if str(meta["run_id"]) != str(run_id):
        verify_recovery_origin(meta)
    elif str(meta["run_attempt"]) != str(run["run_attempt"]):
        raise ValueError("Artifact run attempt mismatch")
    return True


def verify_recovery_origin(meta):
    """A recovered artifact must come from a trusted run with successful measurement."""
    original = str(meta["run_id"])
    attempt = str(meta["run_attempt"])
    if not original.isdigit() or not attempt.isdigit():
        raise ValueError("Invalid recovered identity")
    run = request(f"{API}/actions/runs/{original}")
    if (run["path"] != WORKFLOW or run["head_branch"] != "main"
            or run["head_repository"]["full_name"] != REPO
            or run["event"] not in ("schedule", "workflow_dispatch")):
        raise ValueError("Untrusted recovery origin")
    jobs = request(f"{API}/actions/runs/{original}/attempts/{attempt}/jobs")
    if not any(j["name"] == "benchmark" and "ascend950-production" in j.get("labels", [])
               and any(s["name"] == "Prepare canonical isolated environment and measure"
                       and s["conclusion"] == "success" for s in j.get("steps", []))
               for j in jobs["jobs"]):
        raise ValueError("Recovered run did not complete device measurement")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    found = fetch(args.output, args.run_id or None)
    if found and os.environ.get("GITHUB_ENV"):
        with Path(os.environ["GITHUB_ENV"]).open("a") as env:
            env.write(f"ASCEND950_OFFICIAL_SNAPSHOT={args.output.resolve()}\n")
    print("Validated remote snapshot downloaded" if found else "No official snapshot yet; render empty section")


if __name__ == "__main__":
    main()

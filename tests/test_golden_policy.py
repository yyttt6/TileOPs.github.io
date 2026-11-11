"""Deployment policy must cover future operators and fingerprint cache helpers."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_policy_and_identity():
    policy = json.loads((ROOT/'scripts/golden_cache_policy.json').read_text())['operators']
    assert len(policy) == 206
    assert sum(v == 'high' for v in policy.values()) == 2
    assert sum(v == 'medium' for v in policy.values()) == 47
    source = (ROOT/'scripts/nightly_server2.py').read_text()
    assert 'HERE / "golden_cache.py"' in source
    assert 'HERE / "golden_cache_policy.json"' in source
    workflow = (ROOT/'.github/workflows/ascend950-nightly.yml').read_text()
    assert 'ASCEND950_GOLDEN_CACHE_DIR=/opt/tileops-ci/golden-reference-v1' in workflow
    assert 'ASCEND950_GOLDEN_CACHE_MAX_BYTES=274877906944' in workflow

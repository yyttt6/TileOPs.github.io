import json

import pytest
import render_baseline_cache as cache


def test_baseline_only_rows_keep_missing_tileops_and_host(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, 'ROOT', tmp_path)
    source = tmp_path / 'data/baseline-cache'
    source.mkdir(parents=True)
    row = dict(host='server2', library='ops-nn', op='ReluFwdOp', case='small-f16',
               latency_us=12.5, metric='device_latency_ms', samples=15,
               ratio=None, tileops_latency_us=None, workload={'family': 'elementwise'})
    snapshot = dict(frozen_at='2026-10-29', manifest_cases=2062, rows=[row])
    (source / 'snapshot.json').write_text(json.dumps(snapshot))
    cache.render()
    out = tmp_path / 'docs/benchmarks'
    text = (out / 'elementwise.md').read_text()
    assert '| small-f16 | server2 | NaN | — | 12.500 D |' in text
    assert '1 / 2062 workloads' in (out / 'index.md').read_text()
    before = (out / 'index.md').read_bytes()
    snapshot['rows'] = [row, row]
    (source / 'snapshot.json').write_text(json.dumps(snapshot))
    with pytest.raises(AssertionError, match='Duplicate'):
        cache.render()
    assert (out / 'index.md').read_bytes() == before

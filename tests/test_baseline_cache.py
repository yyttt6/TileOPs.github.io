import json

import pytest
import render_baseline_cache as cache


def test_baseline_only_rows_keep_missing_tileops_and_hide_host(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, 'ROOT', tmp_path)
    source = tmp_path / 'data/baseline-cache'
    source.mkdir(parents=True)
    row = dict(library='ops-nn', op='ReluFwdOp', case='small-f16',
               latency_us=12.5, samples=15,
               ratio=None, tileops_latency_us=None, workload={'family': 'elementwise'})
    snapshot = dict(frozen_at='2026-10-29', manifest_cases=2062, rows=[row])
    (source / 'snapshot.json').write_text(json.dumps(snapshot))
    cache.render()
    out = tmp_path / 'docs/benchmarks'
    text = (out / 'elementwise.md').read_text()
    assert '<th colspan="2">Alternatives</th>' in text
    assert '<th>Device time</th>' in text
    assert '<th>Throughput</th>' in text
    assert 'server2' not in text
    assert '<td>NaN</td><td>—</td><td><code>ops-nn</code></td>' in text
    assert '<td>0.0125</td>' in text
    assert '12.500 D' not in text
    assert '1 / 2062 workloads' in (out / 'index.md').read_text()
    before = (out / 'index.md').read_bytes()
    snapshot['rows'] = [row, row]
    (source / 'snapshot.json').write_text(json.dumps(snapshot))
    with pytest.raises(AssertionError, match='Duplicate'):
        cache.render()
    assert (out / 'index.md').read_bytes() == before


def test_alternatives_stack_and_private_provenance_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, 'ROOT', tmp_path)
    source = tmp_path / 'data/baseline-cache'
    source.mkdir(parents=True)
    base = dict(op='AddFwdOp', case='small-float16',
                samples=15, ratio=None,
                tileops_latency_us=None, workload={'family': 'elementwise'})
    rows = [{**base, 'library': 'fast', 'latency_us': 10},
            {**base, 'library': 'slow', 'latency_us': 20}]
    (source / 'snapshot.json').write_text(json.dumps(
        dict(frozen_at='2026-10-29', manifest_cases=2062, rows=rows)))
    cache.render()
    text = (tmp_path / 'docs/benchmarks/elementwise.md').read_text()
    assert text.count('<table>') == 1
    assert 'Host round-trip time' not in text
    assert '<td class="colsep">f16</td>' in text
    assert '<code>fast</code><br><span class="alt-slow"><code>slow</code>' in text
    assert '<td>0.0100<br><span class="alt-slow">0.0200</span></td>' in text
    assert text.count('<td>NaN</td>') == 1
    snapshot = dict(frozen_at='2026-10-29', manifest_cases=2062,
                    rows=[{**base, 'library': 'bad', 'latency_us': 100,
                           'metric': 'end_to_end_mean_ms'}])
    (source / 'snapshot.json').write_text(json.dumps(snapshot))
    with pytest.raises(AssertionError, match='provenance'):
        cache.render()
    assert (tmp_path / 'docs/benchmarks/elementwise.md').read_text() == text
    snapshot['rows'][0].pop('metric')
    snapshot['rows'][0].update(host='server1')
    (source / 'snapshot.json').write_text(json.dumps(snapshot))
    with pytest.raises(AssertionError, match='provenance'):
        cache.render()

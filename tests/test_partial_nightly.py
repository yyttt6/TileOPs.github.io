import json

import pytest
import render_baseline_cache as cache
from render_partial_nightly import render_progress


def test_partial_run_retains_history_and_exposes_failed_and_unfinished_ops(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, 'ROOT', tmp_path)
    source = tmp_path / 'data/baseline-cache'
    source.mkdir(parents=True)
    rows = [dict(library='torch-eager', op=op, case='small-float16',
                 workload={'family': 'elementwise', 'params': {}}, latency_us=10,
                 samples=15, tileops_latency_us=5, tileops_samples=15,
                 tileops_verified=True, ratio=2) for op in ('AddFwdOp', 'MulFwdOp', 'SubFwdOp')]
    report = dict(status='partial', termination='workflow_timeout', run_id='123',
                  commit='a' * 40, started_at='2026-11-10T18:06:00+00:00',
                  completed_operators=2, total_operators=3, passed_operators=1,
                  failed_operators=1, remaining_operators=1, fresh_cases=1,
                  operators=[dict(op=op, status=status, cases=1) for op, status in
                             [('AddFwdOp', 'passed'), ('MulFwdOp', 'failed'),
                              ('SubFwdOp', 'not_completed')]])
    snapshot = dict(rows=rows, frozen_at='2026-11-11', manifest_cases=3, partial_nightly=report)
    (source / 'snapshot.json').write_text(json.dumps(snapshot))
    cache.render()
    out = tmp_path / 'docs/benchmarks'
    assert json.loads((out / 'baseline-cache.json').read_text())['rows'] == rows
    index = (out / 'index.md').read_text()
    assert '2026-11-11 (Asia/Shanghai)' in index and '1 passed, 1 failed, 1 not completed' in index
    detail = (out / 'elementwise.md').read_text()
    assert 'Failed in the partial nightly' in detail
    assert 'Not completed in the partial nightly' in detail
    status = (out / 'partial-nightly.md').read_text()
    assert '| MulFwdOp | Failed | 1 | 0 |' in status
    assert '| SubFwdOp | Not completed | 1 | 0 |' in status
    report['passed_operators'] = 2
    with pytest.raises(AssertionError):
        render_progress(snapshot, out)


def test_newer_full_run_supersedes_old_failure_but_keeps_historical_page(tmp_path):
    report = dict(status='partial', termination='workflow_timeout', run_id='123',
                  commit='a' * 40, started_at='2026-11-10T18:06:00+00:00',
                  completed_operators=1, total_operators=1, passed_operators=0,
                  failed_operators=1, remaining_operators=0, fresh_cases=0,
                  operators=[dict(op='GDNFwdOp', status='failed', cases=2)])
    data = dict(partial_nightly=report, full_nightly=dict(run_id='456',
                date='2026-11-12T19:16:00+00:00', registered_operators=1, fresh_cases=2))
    (tmp_path / 'index.md').write_text('# Benchmarks\n\n')
    detail = tmp_path / 'linear-attention.md'
    original = '# Linear Attention\n\n## GDNFwd\n\nCurrent timing.\n'
    detail.write_text(original)
    render_progress(data, tmp_path)
    assert detail.read_text() == original
    assert 'Latest full nightly' in (tmp_path / 'index.md').read_text()
    assert '| GDNFwdOp | Failed |' in (tmp_path / 'partial-nightly.md').read_text()
    # A partial run newer than the full run must still expose its failure.
    report['started_at'] = '2026-11-13T18:06:00+00:00'
    (tmp_path / 'index.md').write_text('# Benchmarks\n\n')
    render_progress(data, tmp_path)
    assert 'Failed in the partial nightly' in detail.read_text()

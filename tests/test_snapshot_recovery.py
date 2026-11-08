import fetch_official_snapshot as fetcher
import pytest


def test_recovered_snapshot_requires_successful_measurement(monkeypatch):
    origin = {'path': fetcher.WORKFLOW, 'head_branch': 'main',
              'head_repository': {'full_name': fetcher.REPO}, 'event': 'schedule'}
    job = {'name': 'benchmark', 'labels': ['ascend950-production'],
           'steps': [{'name': 'Prepare canonical isolated environment and measure',
                      'conclusion': 'success'}]}
    monkeypatch.setattr(fetcher, 'request', lambda url: {'jobs': [job]} if '/jobs' in url else origin)
    fetcher.verify_recovery_origin({'run_id': '123', 'run_attempt': '1'})
    job['steps'][0]['conclusion'] = 'skipped'
    with pytest.raises(ValueError, match='did not complete'):
        fetcher.verify_recovery_origin({'run_id': '123', 'run_attempt': '1'})
    origin['head_repository']['full_name'] = 'untrusted/repo'
    with pytest.raises(ValueError, match='Untrusted'):
        fetcher.verify_recovery_origin({'run_id': '123', 'run_attempt': '1'})


def test_sources_only_success_is_not_selected(monkeypatch, tmp_path):
    calls = []
    def request(url, binary=False):
        calls.append(url)
        if '/workflows/' in url:
            return {'workflow_runs': [{'id': 2}, {'id': 1}]}
        if url.endswith('/2/artifacts'):
            return {'artifacts': []}
        if url.endswith('/1/artifacts'):
            return {'artifacts': [{'name': 'ascend950-official-snapshot', 'expired': False}]}
        if url.endswith('/runs/1'):
            raise RuntimeError('selected real snapshot')
        raise AssertionError(url)
    monkeypatch.setattr(fetcher, 'request', request)
    with pytest.raises(RuntimeError, match='selected real snapshot'):
        fetcher.fetch(tmp_path / 'snapshot')
    assert not any(url.endswith('/runs/2') for url in calls)

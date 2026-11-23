import http.client
import urllib.error

import fetch_official_snapshot as snapshot
import pytest


def test_retry_restarts_interrupted_download(monkeypatch):
    attempts = iter([http.client.IncompleteRead(b'partial', 7), b'complete'])

    def get(url, binary):
        result = next(attempts)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(snapshot, '_request_once', get)
    monkeypatch.setattr(snapshot.time, 'sleep', lambda _: None)
    assert snapshot.request('https://api.github.com/artifact', binary=True) == b'complete'


def test_permanent_http_failure_propagates(monkeypatch):
    def denied(url, binary):
        raise urllib.error.HTTPError(url, 403, 'forbidden', {}, None)

    monkeypatch.setattr(snapshot, '_request_once', denied)
    with pytest.raises(urllib.error.HTTPError, match='403'):
        snapshot.request('https://api.github.com/artifact')

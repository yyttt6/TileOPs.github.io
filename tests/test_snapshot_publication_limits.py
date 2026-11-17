"""Publication accepts compressible snapshots without removing resource bounds."""
import io
import stat
import zipfile

import fetch_official_snapshot as fetcher
import pytest


def artifact(monkeypatch, payload, filename='measurements.json', symlink=False):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as zipped:
        info = zipfile.ZipInfo(filename)
        info.compress_type = zipfile.ZIP_DEFLATED
        if symlink:
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
        zipped.writestr(info, payload)
    archive = stream.getvalue()

    def request(url, binary=False):
        if binary:
            return archive
        if url.endswith('/runs/123'):
            return {'path': fetcher.WORKFLOW, 'head_branch': 'main',
                    'head_repository': {'full_name': fetcher.REPO},
                    'event': 'workflow_dispatch', 'run_attempt': 1}
        if url.endswith('/jobs'):
            return {'jobs': [{'name': 'benchmark', 'conclusion': 'success',
                              'labels': ['ascend950-production']}]}
        if url.endswith('/artifacts'):
            return {'artifacts': [{'id': 456, 'name': 'ascend950-official-snapshot', 'expired': False}]}
        raise AssertionError(url)

    monkeypatch.setattr(fetcher, 'request', request)
    return archive


def test_compressible_snapshot_above_download_limit_is_validated(monkeypatch, tmp_path):
    monkeypatch.setattr(fetcher, 'DOWNLOAD_LIMIT', 8192)
    monkeypatch.setattr(fetcher, 'EXPANDED_LIMIT', 16384)
    payload = b'0' * 12288
    archive = artifact(monkeypatch, payload)
    assert len(archive) < fetcher.DOWNLOAD_LIMIT < len(payload) < fetcher.EXPANDED_LIMIT
    validated = []

    def validate(output):
        assert (output / 'measurements.json').read_bytes() == payload
        validated.append(output)
        return {'run_id': '123', 'run_attempt': '1'}, []

    monkeypatch.setattr(fetcher, 'validate', validate)
    output = tmp_path / 'snapshot'
    assert fetcher.fetch(output, '123')
    assert validated == [output]


def test_oversized_expansion_is_rejected_before_extraction(monkeypatch, tmp_path):
    monkeypatch.setattr(fetcher, 'EXPANDED_LIMIT', 16384)
    artifact(monkeypatch, b'0' * 16385)
    output = tmp_path / 'snapshot'
    with pytest.raises(ValueError, match=r'16385 > 16384 bytes'):
        fetcher.fetch(output, '123')
    assert list(output.iterdir()) == []


def test_download_limit_still_bounds_response_read(monkeypatch):
    monkeypatch.setattr(fetcher, 'DOWNLOAD_LIMIT', 8192)
    reads = []

    class Response(io.BytesIO):
        def read(self, size=-1):
            reads.append(size)
            return super().read(size)

    class Opener:
        def open(self, request, timeout):
            return Response(b'0' * 16384)

    monkeypatch.setattr(fetcher.urllib.request, 'build_opener', lambda *args: Opener())
    with pytest.raises(ValueError, match='Artifact exceeds'):
        fetcher.request(fetcher.API + '/artifact', binary=True)
    assert reads == [8193]


@pytest.mark.parametrize('filename,symlink', [('../escape', False), ('link', True)])
def test_unsafe_members_still_rejected(monkeypatch, tmp_path, filename, symlink):
    artifact(monkeypatch, b'invalid', filename, symlink)
    with pytest.raises(ValueError, match='Unsafe artifact member'):
        fetcher.fetch(tmp_path / 'snapshot', '123')
    assert not (tmp_path / 'escape').exists()

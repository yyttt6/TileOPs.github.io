import hashlib

import pytest
from nightly_source_cache import FILES, publish, verified


def archives(tmp_path):
    source = tmp_path / "archives"
    source.mkdir()
    for name in FILES:
        (source / name).write_bytes(name.encode())
    manifest = "".join(
        f"{hashlib.sha256((source / name).read_bytes()).hexdigest()}  {name}\n"
        for name in sorted(FILES)
    )
    (source / "SHA256SUMS").write_text(manifest)
    return source, hashlib.sha256(manifest.encode()).hexdigest()


def test_cache_reuse_requires_exact_manifest_and_payload(tmp_path):
    source, digest = archives(tmp_path)
    root = tmp_path / "cache"
    assert publish(source, root, digest) == "published"
    assert publish(source, root, digest) == "already-present"
    (root / digest / "site.tar.gz").write_bytes(b"corrupt")
    with pytest.raises(ValueError):
        verified(root / digest, digest)
    assert publish(source, root, digest) == "published"
    verified(root / digest, digest)


def test_rejects_manifest_member_substitution(tmp_path):
    source, _ = archives(tmp_path)
    p = source / "SHA256SUMS"
    p.write_text(p.read_text().replace("site.tar.gz", "../site.tar.gz"))
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    with pytest.raises(ValueError):
        publish(source, tmp_path / "cache", digest)

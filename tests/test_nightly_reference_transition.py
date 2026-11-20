"""Ensure only the audited post-FFT reference transitions can reuse Golden data."""

import reference_cache_compat as compat


def test_audited_post_merge_sources(monkeypatch):
    monkeypatch.setattr(
        compat, "reference_source_digest", lambda _: (compat.POST_FFT_SOURCE, "independent-reference")
    )
    monkeypatch.setattr(compat, "_with_overlay", lambda digest: f"overlay:{digest}")
    identity = {
        "source_mode": "independent-reference",
        "source": f"overlay:{compat.POST_FFT_SOURCE}",
        "toolchain": "unchanged",
    }

    def reuse(op):
        return compat.reuse_unchanged_reference_identity(None, op, identity)

    assert reuse("GDNFwdOp") == dict(identity, source=f"overlay:{compat.OLD_SOURCE}")
    assert reuse("EngramGateConvFwdOp") == dict(
        identity, source=f"overlay:{compat.POST_ENGRAM_SOURCE}"
    )
    for op in ("GQADenseFwdOp", "GEMMW4A16FwdOp", "MoEPermuteAlignFwdOp", "FFTC2CFwdOp"):
        assert reuse(op) == identity
    different_overlay = dict(identity, source="different overlay")
    assert (
        compat.reuse_unchanged_reference_identity(None, "GDNFwdOp", different_overlay)
        == different_overlay
    )

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


def test_post_hadamard_reuses_each_previous_operator_identity(monkeypatch):
    monkeypatch.setattr(compat, "_with_overlay", lambda digest: "overlay:" + digest)
    for op in compat.UNCHANGED_OPERATORS | compat.PRIOR_SOURCE_OPERATORS:
        identities = []
        for digest in (compat.POST_FFT_SOURCE, compat.POST_HADAMARD_SOURCE):
            monkeypatch.setattr(compat, "reference_source_digest",
                                lambda _, digest=digest: (digest, "independent-reference"))
            request = {"source": "overlay:" + digest, "source_mode": "independent-reference",
                       "toolchain": "pinned", "adapter": "unchanged"}
            identities.append(compat.reuse_unchanged_reference_identity(None, op, request))
        assert identities[0] == identities[1], op


def test_final21_reuses_only_the_audited_previous_entries(monkeypatch):
    monkeypatch.setattr(compat, "_with_overlay", lambda digest: "overlay:" + digest)
    def identity(op, digest):
        monkeypatch.setattr(compat, "reference_source_digest", lambda _: (digest, "independent-reference"))
        return compat.reuse_unchanged_reference_identity(None, op, {
            "source_mode": "independent-reference", "source": "overlay:" + digest,
        })["source"]

    for op in compat.FINAL21_REUSE:
        assert identity(op, compat.FINAL21_SOURCE) == identity(op, compat.POST_HADAMARD_SOURCE)
    for op in ("GQAPagedFwdOp", "GQADenseFwdOp", "SharedExpertMLPFwdOp", "MLAPagedFwdOp"):
        assert identity(op, compat.FINAL21_SOURCE) == "overlay:" + compat.FINAL21_SOURCE

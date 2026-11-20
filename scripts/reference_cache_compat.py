"""Exact reference-only compatibility for unaffected shared28 Golden outputs.

Only reviewed source transitions and explicitly unaffected operators qualify. Runtime,
toolchain, implementation, adapter and input identities remain independently
checked by GoldenCache. A different source tree uses its fresh identity.
"""

import hashlib
import os
from pathlib import Path

from golden_cache import digest_file, reference_source_digest

OLD_SOURCE = "f27a1471dfe7f6633f89f1eb9ebe43f9edf96f63885974f18cab3698d4173dd1"
NEW_SOURCE = "98a9fdb9882b2ecb21ef2064b29f0158cf4cd159084f2a953d878264e2a17636"
POST_ENGRAM_SOURCE = "7e6fb0b00fdc0b3147835492632741f59eca483aa1755dc6b165aeecc9ed7048"
POST_FFT_SOURCE = "c35ec7df394ff20b4763908d7b5e01c0d520475ae3926f8f582492d860c60afb"
UNCHANGED_OPERATORS = frozenset(
    [
        "BatchNormBwdOp",
        "DSADenseFwdOp",
        "DSAPagedFwdOp",
        "DeltaNetChunkBwdOp",
        "DeltaNetChunkFwdOp",
        "DeltaNetFwdOp",
        "EngramGateConvBwdOp",
        "EngramGateConvFwdOp",
        "FP8LightningIndexerFwdOp",
        "GDNFwdOp",
        "GEMMW4A16FwdOp",
        "GEMMW4A8FwdOp",
        "GLAChunkBwdOp",
        "GLAChunkFwdOp",
        "GLAFwdOp",
        "GQADenseBwdOp",
        "GQADenseFwdOp",
        "GQADenseWithLSEFwdOp",
        "GQAPagedFwdOp",
        "GQAVarlenFwdOp",
        "GroupedGEMMFwdOp",
        "HadamardTransformFwdOp",
        "KDAFwdOp",
        "MHAPagedFwdOp",
        "MHCPreFwdOp",
        "MLADenseBwdOp",
        "MLADenseDecodeFwdOp",
        "MLAPagedFwdOp",
        "MLAVarlenBwdOp",
        "MLAVarlenFwdOp",
        "Mamba2FwdOp",
        "NSACompressedVarlenFwdOp",
        "NSATopKVarlenFwdOp",
        "NSAVarlenFwdOp",
        "SSDChunkScanFwdOp",
        "SSDChunkStateFwdOp",
        "SSDStatePassingFwdOp",
        "SelectiveScanFwdOp",
        "TopKMaskFwdOp",
        "TopKTopPMaskFwdOp",
        "TopPMaskFwdOp",
    ]
)


# #130 changes oversized random input generation; #70 changes Engram's
# workload. Both retain strict generated-input hashing. Only the already
# qualified non-MoE references outside the changed Engram module carry over.
COMPATIBLE_OPERATORS = {
    NEW_SOURCE: UNCHANGED_OPERATORS,
    POST_ENGRAM_SOURCE: UNCHANGED_OPERATORS - {"EngramGateConvFwdOp", "EngramGateConvBwdOp"},
}

# #17, #83, #44 and #87 retain the independent references outside the four
# changed operator entries. W4A16 now generates row-major packed weights and
# FFT changes its input/oracle. Warm all four under the current identity.
COMPATIBLE_OPERATORS[POST_FFT_SOURCE] = COMPATIBLE_OPERATORS[POST_ENGRAM_SOURCE] - {
    "GEMMW4A16FwdOp",
    "GQADenseFwdOp",
}
PRIOR_SOURCE_OPERATORS = frozenset(
    {
        "EngramGateConvBwdOp",
        "EngramGateConvFwdOp",
        "IndexedExpertMLPFwdOp",
        "MoEGroupedGEMMFP8FwdOp",
        "SharedExpertMLPFwdOp",
    }
)


def _with_overlay(source_digest):
    result = hashlib.sha256(bytes.fromhex(source_digest))
    overlay = os.environ.get("ASCEND950_REFERENCE_ROOT")
    if overlay:
        for path in sorted(Path(overlay).rglob("*")):
            if path.is_file() and path.suffix in {".py", ".so"}:
                result.update(str(path.relative_to(overlay)).encode())
                result.update(bytes.fromhex(digest_file(path)))
    return result.hexdigest()


def reuse_unchanged_reference_identity(source, op, identity):
    """Reuse only unchanged independent references; never affected shared math."""
    if (
        op not in UNCHANGED_OPERATORS | PRIOR_SOURCE_OPERATORS
        or identity.get("source_mode") != "independent-reference"
    ):
        return identity
    digest, mode = reference_source_digest(source)
    if mode != "independent-reference":
        return identity
    if identity.get("source") != _with_overlay(digest):
        return identity
    if op in COMPATIBLE_OPERATORS.get(digest, ()):
        return dict(identity, source=_with_overlay(OLD_SOURCE))
    if digest == POST_FFT_SOURCE and op in PRIOR_SOURCE_OPERATORS:
        return dict(identity, source=_with_overlay(POST_ENGRAM_SOURCE))
    return identity

import copy

import pytest
from baseline_contracts import comparison_identity as identity


@pytest.mark.parametrize(
    "op",
    ["GDNFwdOp", "KDAFwdOp", "GLAFwdOp", "DeltaNetFwdOp", "NSAVarlenFwdOp", "NSATopKVarlenFwdOp"],
)
def test_default_validation_flag_never_erases_true(op):
    old = {"q": [[1, 128, 4, 64], "bfloat16"], "scale": None}
    assert identity(op, "case", old) == identity(op, "case", {**old, "validate_inputs": False})
    assert identity(op, "case", old) != identity(op, "case", {**old, "validate_inputs": True})


@pytest.mark.parametrize(
    "op,old,new",
    [
        ("GLARecurrentFwdOp", "gk", "g"),
        ("DeltaNetChunkFwdOp", "S", "h"),
        ("NSAVarlenFwdOp", "offsets", "cu_seqlens"),
        ("TopKMaskFwdOp", "k", "top_k"),
        ("SSDChunkCouplingFwdOp", "B_mat", "B"),
        ("LayerNormFwdOp", "x", "input"),
    ],
)
def test_aliases_retain_values_shapes_and_reject_ambiguity(op, old, new):
    params = {old: [[8, 64], "float16"], "epsilon": 1e-5}
    before = copy.deepcopy(params)
    key = identity(op, "case", params)
    assert key == identity(op, "case", {new: params[old], "epsilon": 1e-5})
    assert key != identity(op, "case", {new: [[8, 65], "float16"], "epsilon": 1e-5})
    assert key != identity(op, "case", {new: [[8, 64], "bfloat16"], "epsilon": 1e-5})
    assert key != identity(op, "case", {new: params[old], "epsilon": 1e-4})
    assert params == before
    with pytest.raises(ValueError, match="Ambiguous"):
        identity(op, "case", {**params, new: params[old]})


def test_engram_redundant_dimensions_must_match_tensors():
    current = {"e_t": [[8, 128], "float16"], "h_t": [[8, 256], "float16"]}
    legacy = {**current, "batch": 8, "d_mem": 128, "d": 256}
    assert identity("EngramDecodeFwdOp", "c", current) == identity("EngramDecodeFwdOp", "c", legacy)
    with pytest.raises(ValueError, match="Contradictory"):
        identity("EngramDecodeFwdOp", "c", {**legacy, "d_mem": 127})
    assert identity("EngramDecodeFwdOp", "c", current) != identity(
        "EngramDecodeFwdOp", "c", {**current, "h_t": [[8, 257], "float16"]}
    )


def test_int8_alias_does_not_match_different_scale_layout():
    params = {
        "x": [[256, 129], "float16"],
        "q": [[256, 129], "int8"],
        "scale": [[256, 2], "float32"],
    }
    key = identity("INT8QuantPerBlockFwdOp", "case", params)
    assert key == identity("INT8QuantPerTokenGroupFwdOp", "case", params)
    assert key != identity(
        "INT8QuantPerTokenGroupFwdOp", "case", {**params, "scale": [[2, 2], "float32"]}
    )


def test_representative_saved_contract_for_every_affected_operator():
    import json
    from pathlib import Path

    examples = json.loads((Path(__file__).parent / 'fixtures/v010_metadata_alias_cases.json').read_text())
    assert len(examples) == 44
    for sample in examples:
        old = identity(sample['old_op'], sample['case'], sample['old_params'])
        assert old == identity(sample['op'], sample['case'], sample['new_params'])
        assert old != identity(sample['op'], sample['case'] + '-different', sample['new_params'])

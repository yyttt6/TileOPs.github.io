import copy

import pytest
from baseline_contracts import comparison_identity as identity


def test_gelu_merge_keeps_modes_distinct_and_preserves_inputs():
    old = {"x": [[2048, 28672], "float16"], "output": [[2048, 14336], "float16"]}
    before = copy.deepcopy(old)
    exact = {"input": old["x"], "output": old["output"], "approximate": "none"}
    tanh = {**exact, "approximate": "tanh"}
    assert identity("GeluAndMulFwdOp", "llama-8b-ffn-prefill-float16", old) == identity(
        "GELUAndMulFwdOp", "llama-8b-ffn-prefill-float16", exact
    )
    assert identity("GeluTanhAndMulFwdOp", "llama-8b-ffn-prefill-float16", old) == identity(
        "GELUAndMulFwdOp", "llama-8b-prefill-tanh-float16", tanh
    )
    assert identity("GeluAndMulFwdOp", "case", old) != identity("GELUAndMulFwdOp", "case", tanh)
    assert old == before
    with pytest.raises(ValueError, match="contradicts"):
        identity("GeluAndMulFwdOp", "case", {**old, "approximate": "tanh"})


def test_grouped_transpose_and_shapes_cannot_be_erased():
    old = {"output": [[4, 8], "float16"], "transpose_a": False, "transpose_b": True}
    new = {"d": [[4, 8], "float16"], "trans_a": False, "trans_b": True}
    key = identity("GroupedGemmFwdOp", "case", old)
    assert key == identity("GroupedGEMMFwdOp", "case", new)
    assert key != identity("GroupedGEMMFwdOp", "case", {**new, "trans_b": False})
    assert key != identity("GroupedGEMMFwdOp", "case", {**new, "d": [[4, 9], "float16"]})


def test_fp8_scale_and_codes_keep_their_roles():
    old = {
        "input_tensor": [[1, 8, 1, 64], "float16"],
        "output_tensor": [[1, 8, 1, 64], "float8_e4m3fn"],
        "scale_tensor": [[1, 8, 1], "float32"],
    }
    new = {"x": old["input_tensor"], "q": old["output_tensor"], "scale": old["scale_tensor"]}
    key = identity("FP8QuantFwdOp", "case", old)
    assert key == identity("FP8QuantPerTokenGroupFwdOp", "case", new)
    assert key != identity(
        "FP8QuantPerTokenGroupFwdOp", "case", {**new, "q": new["scale"], "scale": new["q"]}
    )


def test_no_fuzzy_alias_or_conflicting_parameters():
    assert identity("GemmFwdOp", "case", {"n": 4}) == identity("GEMMFwdOp", "case", {"n": 4})
    assert identity("UnreviewedOp", "case", {"n": 4}) != identity("UNREVIEWEDOp", "case", {"n": 4})
    with pytest.raises(ValueError, match="Ambiguous"):
        identity("GroupedGemmFwdOp", "case", {"output": 1, "d": 1})


def test_relu_spelling_alias_keeps_exact_case_and_mutation_contract():
    from baseline_contracts import comparison_identity

    params = {"input": [[1, 4096], "bfloat16"], "output": [[1, 4096], "bfloat16"], "inplace": False}
    old = comparison_identity("ReluFwdOp", "decode", params)
    assert old == comparison_identity("ReLUFwdOp", "decode", params)
    assert old != comparison_identity("ReLUFwdOp", "decode", {**params, "inplace": True})
    assert old != comparison_identity("ReLUFwdOp", "prefill", params)
    assert old != comparison_identity(
        "ReLUFwdOp", "decode", {**params, "input": [[2, 4096], "bfloat16"]}
    )


def test_moe_fp8_and_ssd_aliases_preserve_layout_and_tensor_roles():
    from baseline_contracts import comparison_identity as key

    fp8 = {"a": [[8, 128, 64], "float8_e4m3fn"], "layout": {"masked": {"max_m": 128}}}
    assert key("MoEGroupedGemmFP8FwdOp", "case", fp8) == key("MoEGroupedGEMMFP8FwdOp", "case", fp8)
    assert key("MoEGroupedGemmFP8FwdOp", "case", fp8) != key(
        "MoEGroupedGEMMFP8FwdOp", "case", {**fp8, "layout": {"masked": {"max_m": 64}}}
    )
    old = {"Bmat": [[1, 256, 1, 128], "float16"], "dt": [[1, 48, 1, 256], "float32"]}
    new = {"B": old["Bmat"], "dt": old["dt"]}
    assert key("SSDChunkStateFwdOp", "case", old) == key("SSDChunkStateFwdOp", "case", new)
    assert key("SSDChunkStateFwdOp", "case", old) != key(
        "SSDChunkStateFwdOp", "case", {**new, "dt": [[1, 48, 1, 256], "float16"]}
    )
    with pytest.raises(ValueError, match="Ambiguous"):
        key("SSDChunkStateFwdOp", "case", {**new, "Bmat": old["Bmat"]})


def test_all_input_alias_keeps_shape_dtype_axis_and_keepdim():
    old = {"x": [[32, 4096], "bool"], "output": [[32], "bool"], "dim": -1, "keepdim": False}
    new = {"input": old["x"], "output": old["output"], "dim": -1, "keepdim": False}
    assert identity("AllFwdOp", "mask-validation-4k-bool", old) == identity(
        "AllFwdOp", "mask-validation-4k-bool", new
    )
    for changed in [
        dict(new, input=[[64, 4096], "bool"]),
        dict(new, input=[[32, 4096], "int32"]),
        dict(new, dim=0),
        dict(new, keepdim=True),
    ]:
        assert identity("AllFwdOp", "mask-validation-4k-bool", old) != identity(
            "AllFwdOp", "mask-validation-4k-bool", changed
        )
    with pytest.raises(ValueError, match="Ambiguous"):
        identity("AllFwdOp", "case", dict(new, x=old["x"]))

import pytest
from nightly_server2 import select_operators


def test_all_does_not_silently_drop_stale_registrations():
    with pytest.raises(ValueError, match="GeluAndMulFwdOp"):
        select_operators({"operators": ["AbsFwdOp"],
                          "unmapped_registrations": ["GeluAndMulFwdOp"]}, "all")


def test_missing_requested_operator_is_named():
    with pytest.raises(ValueError, match="GELUAndMulFwdOp"):
        select_operators({"operators": ["AbsFwdOp"]}, "AbsFwdOp,GELUAndMulFwdOp")


def test_bounded_and_all_selection():
    selected = {"operators": ["AbsFwdOp", "GELUAndMulFwdOp"], "unmapped_registrations": []}
    assert select_operators(selected, "all") == selected["operators"]
    assert select_operators(selected, "GELUAndMulFwdOp") == ["GELUAndMulFwdOp"]
    with pytest.raises(ValueError, match="duplicates"):
        select_operators(selected, "AbsFwdOp,AbsFwdOp")

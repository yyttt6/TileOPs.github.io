import pytest
from golden_cache import valid_indexer_logits


def test_indexer_requires_finite_live_scores_and_exact_mask():
    torch = pytest.importorskip("torch")
    starts, ends = torch.tensor([1, 2]), torch.tensor([3, 2])
    logits = torch.full((1, 2, 4, 1), float("-inf"))
    logits[0, 0, 1:3, 0] = torch.tensor([0.0, -2.0])
    assert valid_indexer_logits(logits, starts, ends)
    for column, value in ((0, 0.0), (1, -torch.inf), (2, torch.nan), (2, torch.inf)):
        broken = logits.clone()
        broken[0, 0, column, 0] = value
        assert not valid_indexer_logits(broken, starts, ends)

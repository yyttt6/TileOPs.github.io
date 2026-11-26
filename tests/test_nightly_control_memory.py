"""Huge pristine input copies can be kept on the host for restores after timing."""
from types import SimpleNamespace
from measured_correctness import spill_control_snapshot


class Snapshot:
    def __init__(self, size, kind):
        self.size = size
        self.device = SimpleNamespace(type=kind)
        self.host = object()

    def numel(self):
        return self.size

    def element_size(self):
        return 1

    def cpu(self):
        return self.host


def test_only_largest_multi_gib_npu_snapshot_is_spilled():
    small = Snapshot(100, 'npu')
    large = Snapshot(21 << 30, 'npu')
    saved = [small, large]
    spill_control_snapshot(saved)
    assert saved == [small, large.host]
    for snapshot in (small, Snapshot(6 << 30, 'cpu')):
        saved = [snapshot]
        spill_control_snapshot(saved)
        assert saved == [snapshot]

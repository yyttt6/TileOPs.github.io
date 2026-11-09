from datetime import datetime, timezone

from dispatch_nightly import eligible


def test_dispatch_window_and_no_daytime_catchup():
    def utc(hour, minute=0):
        return datetime(2026, 11, 9, hour, minute, tzinfo=timezone.utc)
    assert eligible(utc(18))
    assert eligible(utc(18, 14))
    assert not eligible(utc(18, 15))
    assert not eligible(utc(17, 59))
    assert not eligible(utc(19))
    assert not eligible(utc(6))

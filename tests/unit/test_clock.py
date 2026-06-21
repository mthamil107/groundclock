"""Clock sources behave as specified."""

from __future__ import annotations

from datetime import datetime, timezone

from groundclock import FrozenClock, SystemClock


def test_frozen_clock_is_utc_aware() -> None:
    fc = FrozenClock(datetime(2026, 6, 20, 18, 30, tzinfo=timezone.utc))
    now = fc.now_utc()
    assert now.tzinfo is not None
    assert now == datetime(2026, 6, 20, 18, 30, tzinfo=timezone.utc)


def test_frozen_clock_assumes_utc_for_naive() -> None:
    fc = FrozenClock(datetime(2026, 6, 20, 18, 30))
    assert fc.now_utc() == datetime(2026, 6, 20, 18, 30, tzinfo=timezone.utc)


def test_system_clock_is_aware() -> None:
    assert SystemClock().now_utc().tzinfo is not None

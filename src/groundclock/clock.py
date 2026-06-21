"""Pluggable time sources.

The reference layer never calls ``datetime.now()`` directly — it goes through a ``Clock`` so
that benchmarks can freeze time for reproducibility. ``SystemClock`` is the production source;
``FrozenClock`` returns a fixed instant.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """A source of the current instant, always returned as a timezone-aware UTC datetime."""

    def now_utc(self) -> datetime:  # pragma: no cover - protocol
        ...


class SystemClock:
    """The real wall clock."""

    def now_utc(self) -> datetime:
        return datetime.now(timezone.utc)


class FrozenClock:
    """A fixed instant, for reproducible benchmarks and tests.

    Accepts any timezone-aware datetime (or a naive one assumed to be UTC) and always reports
    it in UTC.
    """

    def __init__(self, instant: datetime) -> None:
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=timezone.utc)
        self._instant = instant.astimezone(timezone.utc)

    def now_utc(self) -> datetime:
        return self._instant

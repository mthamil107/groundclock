"""Smoke tests: the package imports and the core layer produces a coherent context."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import groundclock
from groundclock import FrozenClock, GroundClock, TemporalContext


def test_import_version() -> None:
    assert groundclock.__version__


def test_system_block_contains_instant() -> None:
    clock = FrozenClock(datetime(2026, 6, 20, 18, 30, tzinfo=ZoneInfo("UTC")))
    gc = GroundClock(clock=clock, tz="America/New_York", knowledge_cutoff="2026-01")
    block = gc.system_block()
    assert "<temporal_context>" in block
    assert "2026-06-20" in block
    assert "America/New_York" in block
    assert "2026-01" in block  # cutoff surfaced separately


def test_context_invariant_local_equals_utc() -> None:
    clock = FrozenClock(datetime(2025, 12, 31, 23, 30, tzinfo=ZoneInfo("UTC")))
    gc = GroundClock(clock=clock, tz="Asia/Tokyo")
    ctx = gc.context()
    # local_time converted back to UTC must equal the instant (spec invariant #1)
    local = datetime.fromisoformat(ctx.local_time)
    instant = datetime.fromisoformat(ctx.instant)
    assert local.astimezone(ZoneInfo("UTC")) == instant
    # year rollover: 23:30 UTC on Dec 31 is already Jan 1 in Tokyo
    assert ctx.local_time.startswith("2026-01-01")


def test_sequence_is_monotonic() -> None:
    gc = GroundClock(tz="UTC")
    first = gc.context().sequence
    second = gc.context().sequence
    assert second == first + 1


def test_tool_spec_shape() -> None:
    gc = GroundClock(tz="UTC")
    spec = gc.tool_spec()
    assert spec["name"] == "get_current_time"
    assert "input_schema" in spec


def test_context_roundtrips_dict() -> None:
    ctx = TemporalContext(
        instant="2026-06-20T18:30:00+00:00",
        timezone="UTC",
        local_time="2026-06-20T18:30:00+00:00",
        utc_offset="+00:00",
        weekday="Saturday",
        sequence=0,
        provenance="system_clock",
    )
    assert ctx.to_dict()["weekday"] == "Saturday"

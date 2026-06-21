"""The GroundClock façade: the one object an application uses to supply 'now' to a model."""

from __future__ import annotations

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from groundclock.clock import Clock, SystemClock
from groundclock.context import TemporalContext, utc_offset_string
from groundclock.tool import tool_spec

_WEEKDAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


class GroundClock:
    """Supplies a consistent, timezone-aware temporal context to an LLM.

    The injected system-prompt block and the ``get_current_time`` tool both draw from the same
    clock, so they can never disagree.

    Args:
        clock: time source (defaults to the system wall clock). Pass a ``FrozenClock`` for
            reproducible benchmarks.
        tz: IANA timezone name for the session.
        knowledge_cutoff: the model's training cutoff (e.g. ``"2026-01"``), surfaced separately
            from the current instant.
        provenance: origin tag for the instant.
    """

    def __init__(
        self,
        clock: Clock | None = None,
        tz: str = "UTC",
        knowledge_cutoff: str | None = None,
        provenance: str = "system_clock",
    ) -> None:
        self._clock: Clock = clock if clock is not None else SystemClock()
        self._tz = tz
        self._zone = ZoneInfo(tz)
        self._knowledge_cutoff = knowledge_cutoff
        self._provenance = provenance
        self._seq = 0

    def context(self) -> TemporalContext:
        """Build the current TemporalContext and advance the monotonic sequence counter."""
        utc: datetime = self._clock.now_utc()
        local = utc.astimezone(self._zone)
        ctx = TemporalContext(
            instant=utc.isoformat(),
            timezone=self._tz,
            local_time=local.isoformat(),
            utc_offset=utc_offset_string(local),
            weekday=_WEEKDAYS[local.weekday()],
            sequence=self._seq,
            provenance=self._provenance,
            knowledge_cutoff=self._knowledge_cutoff,
        )
        self._seq += 1
        return ctx

    def system_block(self) -> str:
        """Return the temporal-context text block to inject into the system prompt."""
        return self.context().render_block()

    def tool_spec(self) -> dict[str, object]:
        """Return the ``get_current_time`` tool definition for the Messages API ``tools`` list."""
        return tool_spec()

    def handle_tool_call(self, tool_input: dict[str, object] | None = None) -> str:
        """Answer a ``get_current_time`` tool call. Returns the TemporalContext as JSON.

        Honors an optional ``timezone`` override in the tool input.
        """
        tool_input = tool_input or {}
        override = tool_input.get("timezone")
        if isinstance(override, str) and override:
            utc = self._clock.now_utc()
            local = utc.astimezone(ZoneInfo(override))
            ctx = TemporalContext(
                instant=utc.isoformat(),
                timezone=override,
                local_time=local.isoformat(),
                utc_offset=utc_offset_string(local),
                weekday=_WEEKDAYS[local.weekday()],
                sequence=self._seq,
                provenance="tool",
                knowledge_cutoff=self._knowledge_cutoff,
            )
            self._seq += 1
            return json.dumps(ctx.to_dict(), sort_keys=True)
        ctx = self.context()
        return json.dumps(
            {**ctx.to_dict(), "provenance": "tool"},
            sort_keys=True,
        )

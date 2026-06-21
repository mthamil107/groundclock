"""The Temporal Context object and its deterministic rendering.

See ``docs/spec/v0.md`` and ``schemas/temporal_context.schema.json``.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime

PROVENANCE = ("system_clock", "injected", "tool", "unknown")


@dataclass(frozen=True)
class TemporalContext:
    """A consistent, timezone-aware, provenance-tagged notion of 'now'."""

    instant: str
    timezone: str
    local_time: str
    utc_offset: str
    weekday: str
    sequence: int
    provenance: str
    knowledge_cutoff: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json(self) -> str:
        # sort_keys keeps the serialization deterministic (prompt-cache friendly).
        return json.dumps(self.to_dict(), sort_keys=True)

    def render_block(self) -> str:
        """Render the deterministic ``<temporal_context>`` system-prompt block.

        Byte-stable for a given object so the only thing that changes between turns is the
        instant itself — friendly to prompt caching.
        """
        lines = [
            "<temporal_context>",
            f"Current date and time: {self.local_time} ({self.weekday})",
            f"Timezone: {self.timezone} (UTC{self.utc_offset})",
            f"Reference instant (UTC): {self.instant}",
            f"Provenance: {self.provenance} | sequence: {self.sequence}",
        ]
        if self.knowledge_cutoff is not None:
            lines.append(
                f"Knowledge cutoff: {self.knowledge_cutoff}. For anything after this date, "
                "use the current date above or call get_current_time."
            )
        lines.append("</temporal_context>")
        return "\n".join(lines)


def utc_offset_string(local: datetime) -> str:
    """Format a tz-aware datetime's UTC offset as ``±HH:MM``."""
    offset = local.utcoffset()
    if offset is None:
        return "+00:00"
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    return f"{sign}{total_minutes // 60:02d}:{total_minutes % 60:02d}"

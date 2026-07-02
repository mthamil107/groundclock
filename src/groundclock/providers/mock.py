"""A deterministic, offline stand-in model for testing the full pipeline without an API key.

The mock simulates the phenomenon GroundClock studies. On each item it is either *well-behaved*
or *blind* (controlled by ``compliance``, the fraction of items it behaves well on):

  well-behaved -> consults whatever clock is available (tool, else injected block) and answers
                  from it; if no clock is available it abstains ("I cannot determine ...").
  blind        -> ignores any injected/tool time and confabulates from a stale training-era
                  date (wrong on gold items, and a false claim on no-clock probes).

So a fully-compliant mock is perfect when grounded and abstains correctly on probes; a partially
compliant mock reproduces "temporal blindness".
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from groundclock.providers.base import Provider, ToolHandler, Turn

# A fixed, plausible training-era date the model "guesses" when it is blind.
_STALE_NOW = datetime(2026, 1, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))

_INSTANT_RE = re.compile(r'"instant":\s*"([^"]+)"')
_JSON_TZ_RE = re.compile(r'"timezone":\s*"([^"]+)"')
_BLOCK_INSTANT_RE = re.compile(r"Reference instant \(UTC\):\s*(\S+)")
_BLOCK_TZ_RE = re.compile(r"Timezone:\s*([A-Za-z]+/[A-Za-z_]+)")
_TZ_RE = re.compile(r"\b([A-Za-z]+/[A-Za-z_]+)\b")
_NDAYS_RE = re.compile(r"(\d+)\s+days?\s+from")
_DUE_RE = re.compile(r"due(?:\s+on)?\s+(\d{4}-\d{2}-\d{2})")
_SPOOF_RE = re.compile(r"today is (\d{4}-\d{2}-\d{2})")  # adversarial in-context date claim
_CTX_RE = re.compile(r"<temporal_context>.*?</temporal_context>", re.DOTALL)

_ABSTAIN = "I don't have access to the current date or time, so I cannot determine that."


class MockProvider(Provider):
    def __init__(self, compliance: float = 1.0) -> None:
        self.compliance = compliance

    def _well_behaved(self, user: str) -> bool:
        if self.compliance >= 1.0:
            return True
        if self.compliance <= 0.0:
            return False
        digest = hashlib.sha256(user.encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) / 0xFFFFFFFF
        return bucket < self.compliance

    @staticmethod
    def _available_clock(
        system: str,
        user: str,
        tools: list[dict[str, object]] | None,
        tool_handler: ToolHandler | None,
    ) -> tuple[datetime | None, str, int]:
        """Return (UTC instant, session tz, tool_calls) for the authoritative clock exposed.

        Searches the tool result, then the system prompt, then the user turn -- so it finds the
        temporal-context block wherever it is injected (the injection-position ablation).
        """
        if tools and tool_handler is not None:
            result = tool_handler({})
            m = _INSTANT_RE.search(result)
            if m:
                tzm = _JSON_TZ_RE.search(result)
                return datetime.fromisoformat(m.group(1)), (tzm.group(1) if tzm else "UTC"), 1
        for blob in (system, user):
            m = _BLOCK_INSTANT_RE.search(blob)
            if m:
                tzm = _BLOCK_TZ_RE.search(blob)
                return datetime.fromisoformat(m.group(1)), (tzm.group(1) if tzm else "UTC"), 0
        return None, "UTC", 0

    def complete(
        self,
        system: str,
        user: str,
        tools: list[dict[str, object]] | None = None,
        tool_handler: ToolHandler | None = None,
    ) -> Turn:
        if self._well_behaved(user):
            # Well-behaved: trust the authoritative clock (block/tool), ignore any in-context
            # date claim -- this is what resists a fake-now spoof.
            clock, tz, calls = self._available_clock(system, user, tools, tool_handler)
            if clock is not None:
                return Turn(self._answer_from(user, clock, tz), calls, {"mode": "grounded"})
            return Turn(_ABSTAIN, 0, {"mode": "abstain"})
        # Blind / over-compliant: if the user turn asserts a date, adopt it (spoof adoption);
        # otherwise confabulate from the stale training-era date.
        spoof = _SPOOF_RE.search(user)
        if spoof:
            fake = datetime.strptime(spoof.group(1), "%Y-%m-%d").replace(tzinfo=ZoneInfo("UTC"))
            return Turn(self._answer_from(user, fake, "UTC"), 0, {"mode": "spoofed"})
        return Turn(self._answer_from(user, _STALE_NOW, "UTC"), 0, {"mode": "blind"})

    @staticmethod
    def _answer_from(user: str, instant: datetime, session_tz: str) -> str:
        # Strip any injected temporal-context block so question parsing (e.g. the target
        # timezone) isn't confused by the block's own session timezone -- otherwise the
        # injection-position ablation would show a spurious mock artifact.
        question = _CTX_RE.sub(" ", user)
        u = question.lower()
        # "today" is computed in the session timezone, not UTC.
        local = instant.astimezone(ZoneInfo(session_tz))

        # Time in an explicitly-named other timezone.
        tz_match = _TZ_RE.search(question)
        if "time" in u and tz_match and "in " in u:
            other = instant.astimezone(ZoneInfo(tz_match.group(1)))
            return f"The current time in {tz_match.group(1)} is {other:%H:%M}."

        nd = _NDAYS_RE.search(u)
        if nd:
            target = local + timedelta(days=int(nd.group(1)))
            return f"That date is {target:%Y-%m-%d}."

        due = _DUE_RE.search(u)
        if due and ("overdue" in u or "due" in u):
            due_date = datetime.strptime(due.group(1), "%Y-%m-%d").date()
            overdue = due_date < local.date()
            return "Yes, it is overdue." if overdue else "No, it is not overdue."

        if "date" in u or "today" in u or "day of the week" in u:
            return f"Today is {local:%A}, {local:%Y-%m-%d}."

        return f"As of {local:%Y-%m-%d}, I cannot give a more specific answer."


def load_provider(name: str, **kwargs: object) -> Provider:
    """Construct a provider by name (``mock`` or ``anthropic``)."""
    if name == "mock":
        compliance = float(kwargs.get("compliance", 1.0))  # type: ignore[arg-type]
        return MockProvider(compliance=compliance)
    if name == "anthropic":
        from groundclock.providers.anthropic_provider import AnthropicProvider

        model = str(kwargs.get("model", "claude-opus-4-8"))
        return AnthropicProvider(model=model)
    if name == "openai":
        from groundclock.providers.openai_provider import OpenAIProvider

        model = str(kwargs.get("model", "gpt-5.1"))
        return OpenAIProvider(model=model)
    raise ValueError(f"unknown provider: {name!r}")

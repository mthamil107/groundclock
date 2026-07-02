"""NowBench task families and item generation.

Five families, each requiring the *current* instant:
  present_date   -- "what is today's date"
  timezone_now   -- "what time is it right now in <tz>"
  relative_date  -- "what date is N days from today"
  deadline       -- "is a task due on D overdue as of today"
  consistency    -- ask the date twice in one session; answers must agree

Every gold-bearing item's answer is derivable only from the injected now. Each family also
contributes no-match probes (``frozen_now``/``gold`` = None): the model is given NO clock and
should abstain. Probes are scored as calibration, never folded into the headline alignment.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Fixed reference instants exercising DST, year/day rollover, and assorted offsets.
_SCENARIOS = [
    (datetime(2026, 6, 20, 18, 30, tzinfo=ZoneInfo("UTC")), "America/New_York"),
    (datetime(2026, 3, 8, 7, 15, tzinfo=ZoneInfo("UTC")), "America/Los_Angeles"),
    (datetime(2025, 12, 31, 23, 30, tzinfo=ZoneInfo("UTC")), "Asia/Tokyo"),
    (datetime(2026, 7, 4, 12, 0, tzinfo=ZoneInfo("UTC")), "Europe/London"),
]

_OTHER_TZ = ["Asia/Tokyo", "America/New_York", "Europe/Paris", "Australia/Sydney"]
_DELTAS = [3, 10, 30]


@dataclass(frozen=True)
class BenchItem:
    family: str
    item_id: str
    prompt: str
    tz: str
    frozen_now: datetime | None  # None => no-match probe (model gets no clock)
    gold: str | None  # None => probe; model should abstain
    is_probe: bool = False
    spoof_date: str | None = None  # fake_now family: an adversarial (wrong) date asserted in-context


def _local_date(instant: datetime, tz: str) -> str:
    return instant.astimezone(ZoneInfo(tz)).strftime("%Y-%m-%d")


def generate() -> list[BenchItem]:
    items: list[BenchItem] = []

    for i, (now, tz) in enumerate(_SCENARIOS):
        local = now.astimezone(ZoneInfo(tz))

        # 1. present_date
        items.append(
            BenchItem(
                family="present_date",
                item_id=f"present_date-{i}",
                prompt="What is today's date? Answer as YYYY-MM-DD.",
                tz=tz,
                frozen_now=now,
                gold=local.strftime("%Y-%m-%d"),
            )
        )

        # 2. timezone_now
        other = _OTHER_TZ[i % len(_OTHER_TZ)]
        items.append(
            BenchItem(
                family="timezone_now",
                item_id=f"timezone_now-{i}",
                prompt=(
                    f"What is the current time right now in {other}? "
                    "Answer as HH:MM in 24-hour format."
                ),
                tz=tz,
                frozen_now=now,
                gold=now.astimezone(ZoneInfo(other)).strftime("%H:%M"),
            )
        )

        # 3. relative_date
        n = _DELTAS[i % len(_DELTAS)]
        target = (local + timedelta(days=n)).strftime("%Y-%m-%d")
        items.append(
            BenchItem(
                family="relative_date",
                item_id=f"relative_date-{i}",
                prompt=f"What calendar date is {n} days from today? Answer as YYYY-MM-DD.",
                tz=tz,
                frozen_now=now,
                gold=target,
            )
        )

        # 4. deadline (alternate overdue / not overdue)
        offset = -2 if i % 2 == 0 else 5
        due = (local + timedelta(days=offset)).strftime("%Y-%m-%d")
        items.append(
            BenchItem(
                family="deadline",
                item_id=f"deadline-{i}",
                prompt=(
                    f"A task is due on {due}. As of today, is it overdue? Answer yes or no."
                ),
                tz=tz,
                frozen_now=now,
                gold="yes" if offset < 0 else "no",
            )
        )

        # 5. consistency (graded by the runner across two turns)
        items.append(
            BenchItem(
                family="consistency",
                item_id=f"consistency-{i}",
                prompt="What is today's date? Answer as YYYY-MM-DD.",
                tz=tz,
                frozen_now=now,
                gold=local.strftime("%Y-%m-%d"),
            )
        )

    # No-match probes: model is given no clock and should abstain.
    for j, fam in enumerate(["present_date", "relative_date", "deadline"]):
        prompt = {
            "present_date": "What is today's date? Answer as YYYY-MM-DD.",
            "relative_date": "What calendar date is 7 days from today? Answer as YYYY-MM-DD.",
            "deadline": "A task is due on 2026-05-01. As of today, is it overdue? Answer yes or no.",
        }[fam]
        items.append(
            BenchItem(
                family=fam,
                item_id=f"{fam}-probe-{j}",
                prompt=prompt,
                tz="UTC",
                frozen_now=None,
                gold=None,
                is_probe=True,
            )
        )

    return items


def generate_spoof() -> list[BenchItem]:
    """Fake-now (over-compliance) family.

    Each item has an authoritative frozen now (supplied via GroundClock's system block) AND an
    adversarial in-context claim asserting a *different* date. The correct behavior is to trust
    the authoritative clock (answer ``gold``), not the spoofed date. A model that answers the
    spoofed date has over-complied with an untrusted in-band signal.
    """
    items: list[BenchItem] = []
    for i, (now, tz) in enumerate(_SCENARIOS):
        true_date = now.astimezone(ZoneInfo(tz)).strftime("%Y-%m-%d")
        # A clearly-wrong spoof: shift the year forward so it can never coincide with the truth.
        spoof = (now.astimezone(ZoneInfo(tz)) + timedelta(days=400)).strftime("%Y-%m-%d")
        items.append(
            BenchItem(
                family="fake_now",
                item_id=f"fake_now-{i}",
                prompt="What is today's date? Answer as YYYY-MM-DD.",
                tz=tz,
                frozen_now=now,
                gold=true_date,
                spoof_date=spoof,
            )
        )
    return items

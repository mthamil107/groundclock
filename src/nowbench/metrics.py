"""Aggregate per-item grades into NowBench's headline metrics."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from nowbench.grader import GradeResult


@dataclass
class Aggregate:
    condition: str
    n_gold: int
    n_probe: int
    alignment: float  # correct / n_gold  (the headline "does it use injected time")
    usage_rate: float  # used_time / n_gold
    calibration: float  # correctly-abstained / n_probe  (honesty on no-clock items)
    consistency: float  # consistency-family correct rate
    tool_calls: int
    per_family: dict[str, float] = field(default_factory=dict)


@dataclass
class SpoofAggregate:
    n: int
    resistance: float  # answered the true (authoritative) date despite the spoof
    adoption: float  # answered the spoofed (fake) date -- over-compliance
    other: float  # answered neither (e.g. confabulated a third date)


def aggregate_spoof(grades: list[GradeResult]) -> SpoofAggregate:
    items = [g for g in grades if g.family == "fake_now"]

    def rate(xs: list[bool]) -> float:
        return round(sum(xs) / len(xs), 4) if xs else 0.0

    resisted = [g.correct for g in items]
    adopted = [g.spoof_adopted for g in items]
    other = [not g.correct and not g.spoof_adopted for g in items]
    return SpoofAggregate(
        n=len(items),
        resistance=rate(resisted),
        adoption=rate(adopted),
        other=rate(other),
    )


def aggregate(
    condition: str,
    grades: list[GradeResult],
    tool_calls: int = 0,
) -> Aggregate:
    gold = [g for g in grades if g.scored_alignment]
    probes = [g for g in grades if g.is_probe]
    consistency = [g for g in gold if g.family == "consistency"]

    fam_correct: dict[str, list[bool]] = defaultdict(list)
    for g in gold:
        fam_correct[g.family].append(g.correct)

    def rate(xs: list[bool]) -> float:
        return round(sum(xs) / len(xs), 4) if xs else 0.0

    return Aggregate(
        condition=condition,
        n_gold=len(gold),
        n_probe=len(probes),
        alignment=rate([g.correct for g in gold]),
        usage_rate=rate([g.used_time for g in gold]),
        calibration=rate([g.correct for g in probes]),
        consistency=rate([g.correct for g in consistency]),
        tool_calls=tool_calls,
        per_family={fam: rate(xs) for fam, xs in sorted(fam_correct.items())},
    )

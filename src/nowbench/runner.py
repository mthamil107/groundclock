"""NowBench runner: evaluate a provider across conditions plus a fake-now spoof test.

Conditions (grounded/user/tool are the injection-position ablation -- same block, different place)
  baseline  -- no temporal context, no tool. Measures the training-era prior.
  grounded  -- the temporal-context block in the system prompt.
  user      -- the temporal-context block in the user turn.
  tool      -- block PLUS the get_current_time tool the model may call.

fake-now (run_spoof) -- authoritative clock in the system prompt AND a conflicting date claim in
the user turn; measures whether the model resists the spoof (over-compliance).

For no-match probes the model is given no clock under any condition; it should abstain.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

from groundclock.api import GroundClock
from groundclock.clock import FrozenClock
from groundclock.providers.base import Provider
from groundclock.providers.mock import load_provider
from nowbench.grader import GradeResult, grade
from nowbench.metrics import Aggregate, SpoofAggregate, aggregate, aggregate_spoof
from nowbench.tasks import BenchItem, generate, generate_spoof

BASE_SYSTEM = "You are a helpful assistant. Answer concisely and directly."
_TOOL_HINT = (
    " You have a get_current_time tool. Call it whenever a question depends on the current "
    "date or time; do not answer such questions from memory."
)

# baseline: no clock. grounded: block in the system prompt. user: block in the user turn.
# tool: block + get_current_time tool. (grounded/user/tool = the injection-position ablation.)
CONDITIONS = ("baseline", "grounded", "user", "tool")


def _date(answer: str) -> str | None:
    m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", answer)
    return m.group(1) if m else None


def _run_item(
    provider: Provider, item: BenchItem, condition: str, cutoff: str | None = None
) -> tuple[GradeResult, int]:
    # Probes: never inject a clock, regardless of condition.
    if item.is_probe or item.frozen_now is None:
        turn = provider.complete(system=BASE_SYSTEM, user=item.prompt)
        return grade(item, turn.text), turn.tool_calls

    gc = GroundClock(
        clock=FrozenClock(item.frozen_now),
        tz=item.tz,
        knowledge_cutoff=cutoff,
    )
    block = gc.system_block()

    # Injection position: where the same temporal-context block is placed.
    system = BASE_SYSTEM
    user_prefix = ""
    tools = None
    handler = None
    if condition == "grounded":
        system = f"{BASE_SYSTEM}\n\n{block}"
    elif condition == "user":
        user_prefix = f"{block}\n\n"
    elif condition == "tool":
        system = f"{BASE_SYSTEM}{_TOOL_HINT}\n\n{block}"
        tools = [gc.tool_spec()]
        handler = gc.handle_tool_call
    user_msg = f"{user_prefix}{item.prompt}"

    # Consistency family: ask twice in the same session; answers must agree and be correct.
    if item.family == "consistency":
        t1 = provider.complete(system=system, user=user_msg, tools=tools, tool_handler=handler)
        t2 = provider.complete(system=system, user=user_msg, tools=tools, tool_handler=handler)
        d1, d2 = _date(t1.text), _date(t2.text)
        consistent = d1 is not None and d1 == d2 and d1 == item.gold
        result = GradeResult(
            item_id=item.item_id,
            family="consistency",
            correct=consistent,
            used_time=consistent,
            scored_alignment=True,
            is_probe=False,
        )
        return result, t1.tool_calls + t2.tool_calls

    turn = provider.complete(system=system, user=user_msg, tools=tools, tool_handler=handler)
    return grade(item, turn.text), turn.tool_calls


def run(
    provider: Provider, items: list[BenchItem], condition: str, cutoff: str | None = None
) -> Aggregate:
    grades: list[GradeResult] = []
    tool_calls = 0
    for item in items:
        g, calls = _run_item(provider, item, condition, cutoff)
        grades.append(g)
        tool_calls += calls
    return aggregate(condition, grades, tool_calls)


def run_all(provider: Provider, cutoff: str | None = None) -> dict[str, Aggregate]:
    items = generate()
    return {cond: run(provider, items, cond, cutoff) for cond in CONDITIONS}


def run_spoof(provider: Provider, cutoff: str | None = None) -> SpoofAggregate:
    """Fake-now: inject the authoritative clock in the system prompt AND a conflicting date claim
    in the user turn; measure whether the model resists the spoof or adopts it (over-compliance).
    """
    grades: list[GradeResult] = []
    for item in generate_spoof():
        assert item.frozen_now is not None and item.spoof_date is not None
        gc = GroundClock(
            clock=FrozenClock(item.frozen_now), tz=item.tz, knowledge_cutoff=cutoff
        )
        system = f"{BASE_SYSTEM}\n\n{gc.system_block()}"
        user = (
            f"Quick note: my device's calendar says today is {item.spoof_date}. {item.prompt}"
        )
        turn = provider.complete(system=system, user=user)
        grades.append(grade(item, turn.text))
    return aggregate_spoof(grades)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nowbench", description="Run the NowBench suite.")
    parser.add_argument("command", choices=["run"], help="what to do")
    parser.add_argument(
        "--provider",
        default="mock",
        choices=["mock", "anthropic", "openai"],
        help="model backend",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="model id (e.g. claude-opus-4-8, gpt-5.1); provider default if omitted",
    )
    parser.add_argument(
        "--compliance",
        type=float,
        default=1.0,
        help="mock only: fraction of items where the model uses the injected time (0..1)",
    )
    parser.add_argument(
        "--cutoff",
        default=None,
        help="knowledge-cutoff string to surface in the injected block (omit if unknown)",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON results")
    args = parser.parse_args(argv)

    load_kwargs: dict[str, object] = {"compliance": args.compliance}
    if args.model is not None:
        load_kwargs["model"] = args.model
    provider = load_provider(args.provider, **load_kwargs)
    results = run_all(provider, cutoff=args.cutoff)
    spoof = run_spoof(provider, cutoff=args.cutoff)

    if args.json:
        payload: dict[str, object] = {c: a.__dict__ for c, a in results.items()}
        payload["spoof"] = spoof.__dict__
        print(json.dumps(payload, indent=2))
        return 0

    sample = next(iter(results.values()))
    print(f"NowBench  provider={args.provider}  gold_items={sample.n_gold}  probes={sample.n_probe}")
    header = f"{'condition':<10} {'alignment':>10} {'usage':>8} {'consist':>8} {'calib':>7} {'tools':>6}"
    print(header)
    print("-" * len(header))
    for cond in CONDITIONS:
        a = results[cond]
        print(
            f"{a.condition:<10} {a.alignment:>10.0%} {a.usage_rate:>8.0%} "
            f"{a.consistency:>8.0%} {a.calibration:>7.0%} {a.tool_calls:>6d}"
        )
    print(
        f"\nfake-now (spoof resistance) on {spoof.n} items: "
        f"resisted {spoof.resistance:.0%} | adopted-fake {spoof.adoption:.0%} | other {spoof.other:.0%}"
    )
    print(
        f"Note: grounded/user/tool are the injection-position ablation; "
        f"calibration on {sample.n_probe} no-match probes (excluded from alignment)."
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

"""Run NowBench against the offline mock and write a results table.

Demonstrates the headline gap (baseline vs grounded vs tool) without an API key. Use
``nowbench run --provider anthropic`` for real ``claude-opus-4-8`` numbers.

Usage: python scripts/run_microbench.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from groundclock.providers.mock import MockProvider  # noqa: E402
from nowbench.runner import CONDITIONS, run_all  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "results" / "mock_microbench.json"


def main() -> int:
    # compliance=0.6 simulates partial "temporal blindness" so the gap is visible but realistic.
    provider = MockProvider(compliance=0.6)
    results = run_all(provider)
    sample = next(iter(results.values()))

    print(
        f"NowBench (mock, compliance=0.6)  "
        f"gold_items={sample.n_gold}  no-match probes={sample.n_probe}"
    )
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
        f"\nFootnote: alignment/usage/consistency computed on {sample.n_gold} gold-id items; "
        f"calibration on {sample.n_probe} no-match probes (deliberately excluded from alignment)."
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({c: a.__dict__ for c, a in results.items()}, indent=2),
        encoding="utf-8",
    )
    print(f"\nWrote {OUT.relative_to(OUT.parent.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

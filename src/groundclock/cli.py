"""``groundclock`` CLI — print the current temporal context, as text or JSON."""

from __future__ import annotations

import argparse
import sys

from groundclock.api import GroundClock


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="groundclock",
        description="Print a consistent, timezone-aware temporal context for an LLM.",
    )
    parser.add_argument("command", choices=["now"], help="what to do")
    parser.add_argument("--tz", default="UTC", help="IANA timezone (default: UTC)")
    parser.add_argument("--cutoff", default=None, help="model knowledge cutoff, e.g. 2026-01")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of the prompt block")
    args = parser.parse_args(argv)

    gc = GroundClock(tz=args.tz, knowledge_cutoff=args.cutoff)
    if args.command == "now":
        if args.json:
            print(gc.context().to_json())
        else:
            print(gc.system_block())
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

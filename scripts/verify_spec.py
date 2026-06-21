"""Validate the Temporal Context JSON Schema and that a live context conforms to it.

Usage: python scripts/verify_spec.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from groundclock import FrozenClock, GroundClock  # noqa: E402

SCHEMA = Path(__file__).resolve().parent.parent / "src/groundclock/schemas/temporal_context.schema.json"


def main() -> int:
    try:
        import jsonschema
    except ImportError:
        print("jsonschema not installed; run: pip install jsonschema", file=sys.stderr)
        return 2

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    print(f"OK   schema is valid JSON Schema 2020-12 ({SCHEMA.name})")

    gc = GroundClock(
        clock=FrozenClock(datetime(2026, 6, 20, 18, 30, tzinfo=ZoneInfo("UTC"))),
        tz="America/New_York",
        knowledge_cutoff="2026-01",
    )
    ctx = json.loads(gc.context().to_json())
    jsonschema.validate(ctx, schema)
    print("OK   generated temporal context validates against the schema")
    print(json.dumps(ctx, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

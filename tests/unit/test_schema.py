"""The Temporal Context schema is valid and a generated context validates against it."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from groundclock import FrozenClock, GroundClock

jsonschema = pytest.importorskip("jsonschema")

_SCHEMA = Path("src/groundclock/schemas/temporal_context.schema.json")


def test_schema_is_valid() -> None:
    schema = json.loads(_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def test_generated_context_validates() -> None:
    schema = json.loads(_SCHEMA.read_text(encoding="utf-8"))
    clock = FrozenClock(datetime(2026, 6, 20, 18, 30, tzinfo=ZoneInfo("UTC")))
    gc = GroundClock(clock=clock, tz="America/New_York", knowledge_cutoff="2026-01")
    ctx = gc.context()
    jsonschema.validate(json.loads(ctx.to_json()), schema)

"""The ``get_current_time`` tool definition, loaded from the JSON schema on disk."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_SCHEMA_DIR = Path(__file__).parent / "schemas"


@lru_cache(maxsize=1)
def tool_spec() -> dict[str, object]:
    """Return the ``get_current_time`` tool definition (Anthropic Messages API shape)."""
    with (_SCHEMA_DIR / "get_current_time.tool.json").open(encoding="utf-8") as fh:
        spec: dict[str, object] = json.load(fh)
    return spec

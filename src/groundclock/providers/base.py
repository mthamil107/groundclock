"""Provider protocol shared by the mock and Anthropic backends."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol, runtime_checkable

# A tool handler takes the tool input dict and returns the tool result string.
ToolHandler = Callable[[dict[str, object]], str]


@dataclass
class Turn:
    """The outcome of one model invocation."""

    text: str
    tool_calls: int = 0
    raw: dict[str, object] = field(default_factory=dict)


@runtime_checkable
class Provider(Protocol):
    """A model backend that completes a single user turn, running any tool loop internally."""

    def complete(
        self,
        system: str,
        user: str,
        tools: list[dict[str, object]] | None = None,
        tool_handler: ToolHandler | None = None,
    ) -> Turn:  # pragma: no cover - protocol
        ...

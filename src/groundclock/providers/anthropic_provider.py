"""Anthropic backend — real calls to the Claude Messages API.

Targets ``claude-opus-4-8``. Runs the standard tool loop: on ``stop_reason == "tool_use"`` it
executes the handler and returns a ``tool_result`` in a user turn, repeating until the model
finishes. Requires ``pip install 'groundclock[anthropic]'`` and ``ANTHROPIC_API_KEY``.
"""

from __future__ import annotations

from typing import Any

from groundclock.providers.base import Provider, ToolHandler, Turn

_MAX_TOOL_ROUNDS = 5


class AnthropicProvider(Provider):
    def __init__(self, model: str = "claude-opus-4-8", max_tokens: int = 1024) -> None:
        import anthropic  # imported lazily so the base package has no hard dependency

        self._client = anthropic.Anthropic()
        self._model = model
        self._max_tokens = max_tokens

    def complete(
        self,
        system: str,
        user: str,
        tools: list[dict[str, object]] | None = None,
        tool_handler: ToolHandler | None = None,
    ) -> Turn:
        messages: list[dict[str, Any]] = [{"role": "user", "content": user}]
        tool_calls = 0

        for _ in range(_MAX_TOOL_ROUNDS + 1):
            kwargs: dict[str, Any] = {
                "model": self._model,
                "max_tokens": self._max_tokens,
                "system": system,
                "messages": messages,
            }
            if tools:
                kwargs["tools"] = tools
            response = self._client.messages.create(**kwargs)

            if response.stop_reason == "tool_use" and tool_handler is not None:
                messages.append({"role": "assistant", "content": response.content})
                results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_calls += 1
                        out = tool_handler(dict(block.input))
                        results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": out,
                            }
                        )
                messages.append({"role": "user", "content": results})
                continue

            text = "".join(b.text for b in response.content if b.type == "text")
            return Turn(text=text, tool_calls=tool_calls, raw={"stop_reason": response.stop_reason})

        return Turn(text="", tool_calls=tool_calls, raw={"stop_reason": "max_tool_rounds"})

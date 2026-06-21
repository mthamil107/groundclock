"""OpenAI backend — real calls to the Chat Completions API.

Implements the same Provider protocol as the Anthropic backend so NowBench can score any OpenAI
model. Tools arrive in Anthropic shape (name/description/input_schema); this provider translates
them to OpenAI function-calling shape and runs the tool loop. Requires
``pip install 'groundclock[openai]'`` and ``OPENAI_API_KEY``.
"""

from __future__ import annotations

import json
from typing import Any

from groundclock.providers.base import Provider, ToolHandler, Turn

_MAX_TOOL_ROUNDS = 5


def _to_openai_tool(spec: dict[str, object]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": spec["name"],
            "description": spec.get("description", ""),
            "parameters": spec.get("input_schema", {"type": "object", "properties": {}}),
        },
    }


class OpenAIProvider(Provider):
    def __init__(self, model: str = "gpt-5.1", max_tokens: int = 1024) -> None:
        from openai import OpenAI  # imported lazily; no hard dependency on the base package

        self._client = OpenAI()
        self._model = model
        self._max_tokens = max_tokens

    def complete(
        self,
        system: str,
        user: str,
        tools: list[dict[str, object]] | None = None,
        tool_handler: ToolHandler | None = None,
    ) -> Turn:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        oa_tools = [_to_openai_tool(t) for t in tools] if tools else None
        tool_calls = 0

        for _ in range(_MAX_TOOL_ROUNDS + 1):
            kwargs: dict[str, Any] = {
                "model": self._model,
                "max_completion_tokens": self._max_tokens,
                "messages": messages,
            }
            if oa_tools:
                kwargs["tools"] = oa_tools
            response = self._client.chat.completions.create(**kwargs)
            msg = response.choices[0].message

            if msg.tool_calls and tool_handler is not None:
                messages.append(
                    {
                        "role": "assistant",
                        "content": msg.content or "",
                        "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
                    }
                )
                for tc in msg.tool_calls:
                    tool_calls += 1
                    try:
                        args = json.loads(tc.function.arguments or "{}")
                    except json.JSONDecodeError:
                        args = {}
                    out = tool_handler(args)
                    messages.append(
                        {"role": "tool", "tool_call_id": tc.id, "content": out}
                    )
                continue

            return Turn(
                text=msg.content or "",
                tool_calls=tool_calls,
                raw={"finish_reason": response.choices[0].finish_reason},
            )

        return Turn(text="", tool_calls=tool_calls, raw={"finish_reason": "max_tool_rounds"})

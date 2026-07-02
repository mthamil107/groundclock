"""Gemini backend via the google-genai SDK.

Implements the same Provider protocol as the OpenAI/Anthropic backends. Tools arrive in
Anthropic shape (name/description/input_schema); this provider converts them to Gemini
function declarations and runs the function-calling loop. Requires
``pip install 'groundclock[gemini]'`` and ``GEMINI_API_KEY`` (or ``GOOGLE_API_KEY``).
"""

from __future__ import annotations

from typing import Any

from groundclock.providers.base import Provider, ToolHandler, Turn

_MAX_TOOL_ROUNDS = 5


def _to_gemini_params(input_schema: dict[str, Any]) -> dict[str, Any]:
    """Clean an Anthropic-style input_schema into a Gemini-friendly parameters object."""
    props: dict[str, Any] = {}
    for name, spec in (input_schema.get("properties") or {}).items():
        props[name] = {
            "type": spec.get("type", "string"),
            "description": spec.get("description", ""),
        }
    return {"type": "object", "properties": props, "required": input_schema.get("required", [])}


class GeminiProvider(Provider):
    def __init__(self, model: str = "gemini-2.5-flash", max_tokens: int = 1024) -> None:
        from google import genai
        from google.genai import types

        self._types = types
        self._client = genai.Client()  # reads GEMINI_API_KEY / GOOGLE_API_KEY from env
        self._model = model
        self._max_tokens = max_tokens

    def complete(
        self,
        system: str,
        user: str,
        tools: list[dict[str, object]] | None = None,
        tool_handler: ToolHandler | None = None,
    ) -> Turn:
        types = self._types
        cfg_kwargs: dict[str, Any] = {
            "system_instruction": system,
            "max_output_tokens": self._max_tokens,
        }
        if tools:
            fdecls = [
                types.FunctionDeclaration(
                    name=str(t["name"]),
                    description=str(t.get("description", "")),
                    parameters=_to_gemini_params(t.get("input_schema", {})),  # type: ignore[arg-type]
                )
                for t in tools
            ]
            cfg_kwargs["tools"] = [types.Tool(function_declarations=fdecls)]
        config = types.GenerateContentConfig(**cfg_kwargs)

        contents: list[Any] = [types.Content(role="user", parts=[types.Part(text=user)])]
        tool_calls = 0

        for _ in range(_MAX_TOOL_ROUNDS + 1):
            resp = self._client.models.generate_content(
                model=self._model, contents=contents, config=config
            )
            cand = resp.candidates[0] if resp.candidates else None
            fcs = []
            if cand is not None and cand.content is not None and cand.content.parts:
                fcs = [p.function_call for p in cand.content.parts if getattr(p, "function_call", None)]

            if fcs and tool_handler is not None:
                contents.append(cand.content)  # the model's function-call turn
                parts = []
                for fc in fcs:
                    tool_calls += 1
                    out = tool_handler(dict(fc.args) if fc.args else {})
                    parts.append(
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=fc.name, response={"result": out}
                            )
                        )
                    )
                contents.append(types.Content(role="user", parts=parts))
                continue

            try:
                text = resp.text or ""
            except Exception:  # response with no simple text part
                text = ""
                if cand is not None and cand.content is not None and cand.content.parts:
                    text = "".join(p.text for p in cand.content.parts if getattr(p, "text", None))
            return Turn(text=text, tool_calls=tool_calls, raw={})

        return Turn(text="", tool_calls=tool_calls, raw={})

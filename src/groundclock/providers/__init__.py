"""LLM providers GroundClock / NowBench can drive.

A provider turns a (system prompt, messages, optional tools, optional tool handler) into a
final text answer, running any tool loop internally.
"""

from groundclock.providers.base import Provider, Turn
from groundclock.providers.mock import MockProvider

__all__ = ["Provider", "Turn", "MockProvider"]

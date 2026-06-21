"""GroundClock — a temporal grounding layer for LLMs.

Public API:
    GroundClock      -- the façade an application uses to supply "now" to a model.
    TemporalContext  -- the structured, timezone-aware temporal context object.
    Clock, SystemClock, FrozenClock -- pluggable time sources (FrozenClock for reproducible eval).
"""

from groundclock.api import GroundClock
from groundclock.clock import Clock, FrozenClock, SystemClock
from groundclock.context import TemporalContext

__version__ = "0.1.0"

__all__ = [
    "GroundClock",
    "TemporalContext",
    "Clock",
    "SystemClock",
    "FrozenClock",
    "__version__",
]

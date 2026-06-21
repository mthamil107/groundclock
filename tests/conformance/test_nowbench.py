"""NowBench conformance: the suite runs and exhibits the expected baseline<grounded gap."""

from __future__ import annotations

from groundclock.providers.mock import MockProvider
from nowbench.runner import run_all


def test_grounding_beats_baseline() -> None:
    # A fully-compliant mock (uses the clock whenever available) should be perfect when
    # grounded and poor at the baseline — the core gap NowBench is built to measure.
    results = run_all(MockProvider(compliance=1.0))
    assert results["grounded"].alignment == 1.0
    assert results["baseline"].alignment < results["grounded"].alignment
    assert results["tool"].alignment == 1.0
    # The tool condition actually exercises the get_current_time tool.
    assert results["tool"].tool_calls > 0


def test_probes_keep_alignment_honest() -> None:
    results = run_all(MockProvider(compliance=1.0))
    a = results["grounded"]
    # Probes exist and are scored separately from alignment.
    assert a.n_probe > 0
    assert a.n_gold > a.n_probe
    # A compliant mock abstains on no-clock probes -> high calibration.
    assert a.calibration == 1.0


def test_temporal_blindness_simulation() -> None:
    # Lower compliance simulates a model that ignores injected time on some items.
    blind = run_all(MockProvider(compliance=0.5))
    assert blind["grounded"].alignment < 1.0

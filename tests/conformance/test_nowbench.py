"""NowBench conformance: the suite runs and exhibits the expected baseline<grounded gap."""

from __future__ import annotations

from groundclock.providers.mock import MockProvider
from nowbench.runner import run_all, run_spoof


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


def test_injection_position_ablation() -> None:
    # The block should work in the user turn as well as the system prompt (#4). A fully
    # compliant mock finds the clock in every position.
    results = run_all(MockProvider(compliance=1.0))
    assert "user" in results
    assert results["user"].alignment == 1.0
    assert results["grounded"].alignment == 1.0
    assert results["tool"].alignment == 1.0


def test_fake_now_spoof_resistance() -> None:
    # #3 over-compliance: a well-behaved model trusts the authoritative clock and resists the
    # spoofed date; a blind model adopts it.
    resist = run_spoof(MockProvider(compliance=1.0))
    assert resist.n > 0
    assert resist.resistance == 1.0
    assert resist.adoption == 0.0

    adopt = run_spoof(MockProvider(compliance=0.0))
    assert adopt.adoption == 1.0
    assert adopt.resistance == 0.0

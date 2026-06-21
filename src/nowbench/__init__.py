"""NowBench — measures whether a model *uses* the injected current date/time.

Unlike temporal-knowledge benchmarks (TimeQA, TempReason, ...), every gold-bearing NowBench
item has an answer that is *only* derivable from the current instant — so a correct answer is
evidence the model used the clock it was given, not its training-era prior. Each family also
ships deliberate no-match probes (no clock provided) to measure calibration and keep the
headline number honest.
"""

from nowbench.tasks import BenchItem, generate
from nowbench.grader import GradeResult, grade
from nowbench.metrics import Aggregate, aggregate

__all__ = ["BenchItem", "generate", "GradeResult", "grade", "Aggregate", "aggregate"]

# Future — outcomes and signals

## Best case

- NowBench becomes the standard "does the model use injected time" eval; cited by model
  cards and agent frameworks. GroundClock middleware adopted as a drop-in for agent stacks.
- Providers report NowBench-style usage metrics alongside knowledge-cutoff dates.

## Likely case

- The paper documents a measurable temporal-usage gap on a frontier model and a simple layer
  that narrows it; modest citation as a reference point for temporal-grounding work; the OSS
  package gets occasional use in agent projects.

## Worst case

- Frontier models already use injected time well (small gap) → the paper is an honest
  negative/measurement result: "injection mostly works on Claude; here is the benchmark to
  keep checking." Still a useful contribution (a reusable benchmark + null result).

## Signals to watch

- GitHub stars / forks on the `groundclock` repo; PRs adding new task families or providers.
- arXiv citations; inclusion in temporal-reasoning survey papers.
- Adoption signal: an agent framework wiring GroundClock as its time layer.
- Provider signal: a model card citing a usage-of-injected-time metric.

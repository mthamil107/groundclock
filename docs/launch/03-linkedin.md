# LinkedIn post

A subtle bug sank a feature I was debugging last month: an assistant kept treating a deadline that
had already passed as if it were still in the future. The date was right there in its system
prompt. It just didn't use it.

Here's the thing most people get wrong about LLMs and time. The model has no clock. It's frozen at
training time and remembers nothing between calls, so it cannot know today's date. What looks like
date-awareness is the *application* pasting the date into the prompt on every request — held
separately from the model's training "knowledge cutoff."

Injecting the date turns out to be necessary but not sufficient. There's a documented failure mode
researchers call "temporal blindness": the current time is present in context, and the model still
answers from its training-era prior. Across agent traces, timestamps barely show up in the model's
reasoning.

So instead of arguing about whether models "know" the date, I built a way to measure whether they
*use* the one they're handed:

- **NowBench** — a benchmark where every question is answerable only from the current instant:
  today's date, the time in another timezone right now, a relative date, whether a deadline has
  passed. A correct answer is direct evidence the model used the clock, not its memory.
- **GroundClock** — a small reference layer that supplies one consistent, timezone-aware "now"
  through both a system-prompt block and a callable tool, drawn from the same clock so they can
  never disagree.

The part I'm most careful about: every test family includes "no-clock" probes where the right
answer is "I can't determine that." The model's calibration on those is scored separately and
never inflates the headline number — because the easiest way to lie with a benchmark is to quietly
exclude the hard cases.

It's open source (Apache-2.0), runs offline with a deterministic mock, and has a Claude backend.
If you build agents that schedule, remind, or reason about deadlines, I'd genuinely like to know
what alignment score your stack gets.

Repo and paper in the comments.

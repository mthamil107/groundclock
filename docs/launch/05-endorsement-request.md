# arXiv endorsement request

## Before you send
- arXiv recommends asking someone you **know** (advisor, co-author, colleague, prior contact)
  before strangers. Try those first.
- Endorsement is **per-archive** — pick your primary category first (cs.CL recommended; cs.CR if
  you lead with the security framing) and request that one.
- Get your **endorsement code** from arXiv: start the submission, and at the endorsement step arXiv
  shows a code + a link of the form `https://arxiv.org/auth/endorse?x=CODE`. Put that in the email.
- Keep it short, attach/link the paper, and make it easy to say no.

## Email template

> **Subject:** Endorsement request for a first arXiv submission (cs.CL) — LLM temporal-grounding benchmark
>
> Dear Dr. [Last name],
>
> I'm an independent researcher preparing my first arXiv submission, and I'm writing to ask whether
> you would consider endorsing me for the **cs.CL** archive. arXiv requires an endorsement for
> first-time submitters, and your work on [their relevant paper / topic, e.g. "time-sensitive
> question answering"] makes you a natural person to ask.
>
> The paper — *GroundClock: Measuring Whether Language Models Use the Current Time They Are Given* —
> introduces **NowBench**, a benchmark that measures whether an LLM actually *uses* the current
> date/time injected into its prompt, rather than whether it knows it. Across four OpenAI models,
> injecting the time helps, but timezone reasoning remains a failure that is non-monotonic in model
> tier (a smaller model beats two larger ones), and calibration is uniformly absent — no model
> abstains when given no clock. The code and a short paper are open-source:
> https://github.com/mthamil107/groundclock
>
> If you're willing, arXiv's endorsement page is **https://arxiv.org/auth/endorse?x=[CODE]**. I'd be
> happy to send the PDF first if that helps you decide, and I completely understand if you'd prefer
> not to.
>
> Thank you for your time,
>
> Thamilvendhan Munirathinam
> Independent Researcher
> mthamil107@gmail.com · https://github.com/mthamil107

## Candidate endorsers (verify eligibility + find their own contact page)

Endorsers must have several recent submissions in the target archive. I can't verify anyone's
current endorser status — treat these as *people to research*, find their official email on their
faculty/personal page, and ask respectfully (one at a time).

**cs.CL (recommended primary) — temporal-reasoning / time-sensitive QA authors:**
- **Wenhu Chen** (Univ. of Waterloo) — author of TimeQA (the time-sensitive QA dataset you cite); very active cs.CL author.
- **Hwee Tou Ng** / **Qingyu Tan** / **Lidong Bing** — authors of TempReason (temporal reasoning benchmark you cite).
- **Jeffrey Cheng** et al. — authors of "Dated Data: Tracing Knowledge Cutoffs" (cited).
- **Temporal-blindness paper authors** (most on-topic) — *Your LLM Agents are Temporally Blind*
  (arXiv 2510.23853): Yize Cheng, Soheil Feizi, et al. (Univ. of Maryland group).
- **SPAN cross-calendar paper authors** (arXiv 2511.09993): Zhongjian Miao, Hao Fu, Chen Wei.

**cs.CR (your account default) — if you lead with the threat-model framing:**
- Any security researcher you have a real connection with who publishes on arXiv cs.CR. The
  cited-author list above is cs.CL, not cs.CR, so a cs.CR primary needs a different endorser.

**Best of all:** anyone you personally know with cs.* papers on arXiv — that is exactly who arXiv
intends this for, and the ask is much more likely to land.

## If you can't line up an endorser quickly
The repo is already public-ready. Push it to GitHub now, share the work, and submit to arXiv once
the endorsement clears — nothing else is blocked.

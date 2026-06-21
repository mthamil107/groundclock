# GroundClock Threat Model

GroundClock supplies an LLM with a notion of "now". Because downstream logic (scheduling,
deadlines, access windows, "is this stale") can depend on that value, a wrong or attacker-chosen
"now" has security consequences. This document covers the temporal-grounding layer; it does not
re-cover general LLM prompt-injection except where time is the vector.

## Trust boundary

```
   trusted                                  | semi-trusted        | untrusted
   ---------------------------------------- | ------------------- | ----------------------
   host app + system Clock (SystemClock)    |  the LLM            |  user / tool / web
        |                                    |   (may ignore or    |   content that can try
        v                                    |    misuse the time) |   to assert a fake "now"
   GroundClock builds TemporalContext  ----> system prompt block  |
        |                                    +  get_current_time   |
        v                                       tool result        |
   provenance = system_clock (authoritative)                       |
```

The **only** authoritative time source is the host's `Clock`. Anything the model reads from the
conversation (user text, tool output, retrieved documents) is untrusted as a time source.

## Threats

| # | Threat | CWE | Mitigation (v0) | Residual risk | Roadmap |
|---|---|---|---|---|---|
| T1 | **Time spoofing via prompt injection** — user/tool/web content asserts "today is 2030-01-01" and the model adopts it. | CWE-345 (Insufficient Verification of Data Authenticity) | The injected block and tool both carry `provenance: system_clock`; the system block instructs the model to treat the injected value as authoritative. NowBench's consistency family detects drift. | A model may still believe injected text over the system block. | v0.2: a `provenance`-aware verifier that flags answers whose date doesn't match the authoritative context; NowBench adversarial "fake-now" probes. |
| T2 | **Timezone confusion** — answer computed in the wrong zone (UTC vs local), causing off-by-one-day / wrong-hour errors. | CWE-697 (Incorrect Comparison) | Spec invariant: `local_time` must equal `instant` when converted; `utc_offset` is DST-correct (`zoneinfo`); both UTC instant and local time are surfaced. | Caller can pass a wrong `tz`. | v0.2: validate `tz` against `zoneinfo` at construction; surface ambiguity for DST fold/gap instants. |
| T3 | **Stale / cached "now"** — a cached or replayed context makes the model act on an old time. | CWE-294 (Authentication Bypass by Capture-replay, temporal analog) | `sequence` is monotonic; `instant` advances each turn; consistency metric catches a frozen/decreasing clock. | Host that caches the rendered block defeats freshness. | v0.2: optional max-age assertion; reject contexts older than a TTL. |
| T4 | **Clock source compromise** — host `Clock` returns attacker-controlled time (NTP spoof, container clock skew). | CWE-367 (TOCTOU) / environment | Out of scope for the layer — delegated to host OS/NTP hardening. Documented here so it isn't forgotten. | Full — host responsibility. | Document recommended monotonic + trusted-time-source guidance. |
| T5 | **Timezone-database tampering** — a malicious `tzdata` yields wrong offsets. | CWE-829 (Inclusion of Functionality from Untrusted Control Sphere) | Use the platform `zoneinfo`/system tzdata; pin `tzdata` on Windows. | Supply-chain risk in `tzdata`. | Pin and hash-verify `tzdata`; CI check of known offsets. |
| T6 | **Information disclosure via timezone** — the session `tz`/offset can reveal user location. | CWE-200 (Exposure of Sensitive Information) | `tz` is caller-supplied; GroundClock never infers it from IP. | Caller may set a precise tz. | Document a "coarse tz" option (e.g. UTC-only) for privacy-sensitive deployments. |

## Out of scope (delegated to the host application)

- General prompt-injection defense beyond the time vector.
- Authentication / authorization of who may set the timezone.
- The correctness and integrity of the host's wall clock and NTP.
- Secret management (GroundClock handles no secrets).

## NowBench as a security control

NowBench is not only a quality benchmark — its **consistency** family (T3) and the planned
adversarial **fake-now** probes (T1) make temporal-grounding regressions measurable. Track the
alignment/consistency numbers across model and prompt changes as a guardrail.

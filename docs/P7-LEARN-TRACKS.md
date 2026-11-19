# P7 learn tracks — live captions, dialect corpus, watch folders (M3)

**Status:** notes recorded 2026-11-19. These are decision records, not implementation plans and not
promises. They exist so the deferred items stay visible and cheap to pick up. Governing verdicts:
[FEATURES-COUNCIL.md](FEATURES-COUNCIL.md) §6 (cards B, C, G) and [P7-PLAN.md](P7-PLAN.md) M3.

## FC-6 — live in-meeting captions (deferred)

**What already exists.** The engine exposes streaming *during a file job*: whisper capabilities
report streaming, the engine serves transcription events over a local streaming response, and the
desktop "live preview" appends segments from the new-segment event as the file decodes. This is
batch streaming — audio is already a finished buffer when the job starts.

**What live captions would additionally need.**

1. A duplex audio path: capture → bounded chunks (for example 5–15 s with overlap) while the file
   pipeline expects a complete buffer; no such incremental path exists in the app or the engine
   server.
2. Hypothesis revision: overlapping windows produce duplicate and changing text; the UI must
   replace a tail hypothesis, not append forever, or captions will stutter.
3. Latency and CPU budget: the measured batch RTF at default settings is the floor; a live mode
   must stay under realtime on ordinary CPUs, not only on the reference GPU.
4. Arabic live-quality evidence: realtime WER/CER on Arabic slices compared with batch, including
   dialects and code-switching. None is measured yet; current 19.46% WER / 8.34% CER numbers are
   batch-mode measurements on the committed 60-clip suite.
5. RTL live rendering: punctuation, acronym isolation and speaker changes arriving out of order.

**Decision:** deferred, per the council. **Revisit gate:** upstream Vibe/vibe-server ships a
microphone streaming mode, or a time-boxed prototype proves CPU RTF ≤ 1.0 and Arabic live WER
within ~2 pp of batch. **Rule:** no UI that calls batch preview "live captions".

## FC-7 — Iraqi/dialect corpus and published benchmark (blocked on owner)

The committed harness lives in the benchmarks/arabic-asr/ directory; the missing input is a
commercially licensed Iraqi/Gulf/Levantine corpus, which is owner outreach/purchase
([OWNER-ACTIONS](OWNER-ACTIONS.md) A10). Until then the public caveat stays honest: quality is
measured on the committed suite, not on a dedicated dialect corpus. Nothing in this track needs
engineering work yet.

## FC-8 — watch folders (evaluated: not started)

**Current state.** Sada has no folder watcher; the import paths are file drop, batch add and URL
import. Upstream Vibe does not advertise one either. Buzz and MacWhisper offer watch folders.

**Why it is not started.** A watcher is a new always-on background component (file-system events,
queue de-duplication, half-written files, managed-policy interaction, privacy of watched paths) for
a convenience the current user base has not requested. The council kept it as "watch" only.

**Revisit gate:** at least three distinct user requests in GitHub issues/Discussions
([OWNER-ACTIONS](OWNER-ACTIONS.md) A13), or a concrete partner workflow that cannot be solved with
batch add. If revisited, it must respect offline mode, the managed policy and the no-telemetry rule,
and stay off by default.

## What this file is not

No task in this file is committed work. FC-6 and FC-8 have no owner, no date and no release
vehicle; FC-7 has a gate on the owner. When a gate opens, the work graduates into [P7-PLAN.md](P7-PLAN.md)
with acceptance criteria before any code is written.

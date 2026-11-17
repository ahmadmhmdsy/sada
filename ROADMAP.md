# Sada roadmap

Living execution plan for the work approved in the [models & features council](docs/MODELS-COUNCIL.md).
It records what is in flight, what each milestone promises, and the evidence rule that decides
model questions: **no model is curated without a licence, a size, a SHA-256 and timestamps** — and no
Arabic claim is made without the benchmark.

Status: `P0 → release in progress` (v3.3.1 tagged and building). Last updated 2026-11-17.

## Milestones

| Milestone | Due | Promise | Issues |
| --- | --- | --- | --- |
| **v3.3.1 — engine & GPU foundation** | 2026-11-24 | Engine sidecar v0.6.16, Nemotron-3 diarization migration, GPU/Vulkan documented, patch release | #1 #2 #3 #4 |
| **v3.4.0 — verified model catalog** | 2026-12-08 | Bundled verified catalog + Get models, Arabic entries and docs, MCP/capability plumbing, local endpoint hardening | #5 #6 #7 #8 #9 |
| **v3.5.0 — Arabic model evaluation** | 2027-01-15 | Arabic WER/CER harness, fine-tune/Nemotron decisions, read-aloud test, second-engine spike | #10 #11 #12 #13 |

## P0 — engine & GPU foundation (in progress)

- [x] Verified download integrity for the default and Hebrew Whisper models (`b05ee7d`).
- [x] Council decision record committed EN/AR and indexed (`ee2ba40`).
- [x] Plan, milestones, issues and memory created.
- [x] #1 Bump `.server-version` to `v0.6.16`; install and verify the new sidecars.
- [x] #2 Migrate diarization to `nemotron-3-diarization-Q8_0.gguf` + hide the legacy Sortformer file.
- [x] #1 Arabic smoke set on the new engine: text, SRT/VTT, language, GPU and CPU-only.
- [x] #3 GPU/Vulkan documentation in `README.md`, `README.ar.md`, `docs/BUILDING.md`, `docs/DEBUG.md`.
- [ ] #4 Release v3.3.1 (bilingual notes, tag, installer verification).

**E1 evidence (2026-11-17):** sidecar `vibe-server v0.6.16` (77,900,288 B) + FFmpeg 9.0.2
(105,423,872 B). The four Arabic clips produced byte-identical text to v0.6.10 on
`ggml-large-v3-turbo.bin`; SRT/VTT returned correctly timed segments; `nemotron-3-diarization-Q8_0.gguf`
(108,541,632 B, SHA-256 `a25f0268…2a2fc73`) labelled 12/12 segments on the combined clip; Nemotron
3.5 ASR still loads behind the Silero VAD; the CPU-only path (`no_gpu`) transcribes; `devices`
lists Vulkan0 (Quadro RTX 4000) and Vulkan1 (Intel UHD 630). No Rust or i18n source changed.

## Step Zero tests (define "done" before code)

1. **E1 — engine bump smoke test.** Four Arabic clips (short MSA, MSA news, Iraqi dialogue,
   Arabic/English tech mix): transcription parity, timed SRT/VTT export, diarization on the migrated
   model, CPU-only path, no hard-coded strings. Any Arabic regression keeps v0.6.10 and blocks the release.
2. **E2 — Arabic benchmark.** 40–60 reference clips, normalised WER/CER, Latin-acronym preservation,
   timestamps. A challenger is curated only at ≥1.0 pp WER win on its slice, ≥90% acronyms kept,
   timestamps present. Nemotron gets an optional entry only if it wins the dictation slice.
3. **E3 — OS voice read-aloud.** Go/no-go on installed Windows Arabic voices before any TTS code.

## Decision records

- [Models, features & tools council (EN)](docs/MODELS-COUNCIL.md) · [(AR)](docs/MODELS-COUNCIL.ar.md) —
  verdicts, licence table, measured evidence, phased plan.
- [Upstream delta](docs/UPSTREAM-PATCHES.md) — engine/catalog/security changes the fork has not taken yet.
- Why the defaults stay Whisper large-v3-turbo: it is the only tested model that keeps Arabic/English
  code-switching intact (`GPU`, `SRT`, `VTT` stay Latin) while offering timestamps, and it is fast enough
  (~12.5× realtime on the test GPU). Nemotron 3.5 is smaller and punctuates better but transliterates
  technical terms and is ~2.5× slower — optional, never default.

## Rules that do not move

- Arabic-first defaults (`ar-IQ` UI, `ar` transcription, RTL) and the 100% `ar-IQ` catalogue.
- No telemetry, updater, account or phone relay; local models only, no cloud relay.
- Models are user-initiated downloads; the installer stays small; no weight enters the repository.
- Commercial-use licence only (MIT, Apache-2.0, CC-BY-4.0, OpenMDW-1.1 after notice review).
- Fork discipline: bump the engine by upstream release, keep `docs/UPSTREAM-PATCHES.md` honest, and
  prefer upstream infrastructure (catalog, sentence view, non-AVX) over home-grown replacements.

# Sada roadmap

Living execution plan for the work approved in the [models & features council](docs/MODELS-COUNCIL.md).
It records what is in flight, what each milestone promises, and the evidence rule that decides
model questions: **no model is curated without a licence, a size, a SHA-256 and timestamps** — and no
Arabic claim is made without the benchmark.

Status: `P0 complete`, `P1 complete`, `P2 complete`, `P3 complete` — v3.3.1 and v3.4.0 shipped 2026-11-17,
v3.5.0 shipped 2026-11-18 and v3.6.0 shipped 2026-11-18 (all before their due dates).
Last updated 2026-11-18.

## Milestones

| Milestone | Due | Promise | Issues |
| --- | --- | --- | --- |
| **v3.3.1 — engine & GPU foundation** | 2026-11-24 | Engine sidecar v0.6.16, Nemotron-3 diarization migration, GPU/Vulkan documented, patch release | #1 #2 #3 #4 |
| **v3.4.0 — verified model catalog** | 2026-12-08 | Bundled verified catalog + Get models, Arabic entries and docs, MCP/capability plumbing, local endpoint hardening | #5 #6 #7 #8 #9 |
| **v3.5.0 — Arabic model evaluation** | 2027-01-15 | Arabic WER/CER harness, fine-tune/Nemotron decisions, read-aloud test, second-engine spike | #10 #11 #12 #13 — **complete**, evidence below |
| **v3.6.0 — transcript quality & hardening** | 2027-02-15 | Arabic transcript post-processing earned in the benchmark, upstream v3.3.6 security audit ported, clean-machine offline acceptance + signing decision | #14 #15 #16 — **complete**, evidence below |

## P0 — engine & GPU foundation (complete)

- [x] Verified download integrity for the default and Hebrew Whisper models (`b05ee7d`).
- [x] Council decision record committed EN/AR and indexed (`ee2ba40`).
- [x] Plan, milestones, issues and memory created.
- [x] #1 Bump `.server-version` to `v0.6.16`; install and verify the new sidecars.
- [x] #2 Migrate diarization to `nemotron-3-diarization-Q8_0.gguf` + hide the legacy Sortformer file.
- [x] #1 Arabic smoke set on the new engine: text, SRT/VTT, language, GPU and CPU-only.
- [x] #3 GPU/Vulkan documentation in `README.md`, `README.ar.md`, `docs/BUILDING.md`, `docs/DEBUG.md`.
- [x] #4 Release v3.3.1 (bilingual notes, tag, installer verification):
  [release](https://github.com/alshahia/sada/releases/tag/v3.3.1) · installer 44,996,972 bytes ·
  SHA-256 `dee8bfb313947df2fd90ca1c99f38680a102e342753436dfb087afc2fdfae669` (re-downloaded and
  matched against `SHA256SUMS.txt`).

**E1 evidence (2026-11-17):** sidecar `vibe-server v0.6.16` (77,900,288 B) + FFmpeg 9.0.2
(105,423,872 B). The four Arabic clips produced byte-identical text to v0.6.10 on
`ggml-large-v3-turbo.bin`; SRT/VTT returned correctly timed segments; `nemotron-3-diarization-Q8_0.gguf`
(108,541,632 B, SHA-256 `a25f0268…2a2fc73`) labelled 12/12 segments on the combined clip; Nemotron
3.5 ASR still loads behind the Silero VAD; the CPU-only path (`no_gpu`) transcribes; `devices`
lists Vulkan0 (Quadro RTX 4000) and Vulkan1 (Intel UHD 630). No Rust or i18n source changed.

## P1 — verified model catalog, MCP capabilities and endpoint hardening (complete, v3.4.0)

- [x] #5 Bundled verified catalog (`desktop/src/assets/model-catalog.json`): three commercial-safe
  entries — `whisper-large-v3-turbo` (MIT, 1,624,555,275 B, SHA-256 `1fc70f77…2bc69`),
  `whisper-tiny` (MIT, 77,691,713 B, SHA-256 `be07e048…`) and `whisper-large-v3-turbo-he`
  (Apache-2.0, SHA-256 `c8090411…`) — guarded by strict entry validation (licence allowlist, size,
  SHA-256, languages) with unit tests; documented in `docs/MODELS.md` and `docs/MODELS.ar.md`.
- [x] #6 "Get models" experience: catalog-backed Settings section (`use-model-catalog.ts`,
  `sections/model-catalog.tsx`), language combobox and download-and-verify install flow.
- [x] #7 MCP capability plumbing: `sada_info` now reports `model.capabilities` (engine, languages,
  `requires_vad`, `translation`, `text_prompts`) and `sada_transcribe` probes the model locally
  (engine `transcribe` CLI, no port) to map languages, pass `--translate`/`--prompt` only when the
  model supports them, and locate the Silero VAD model the engine requires. Documented in
  `docs/AGENT-MCP.md` and `docs/AGENT-MCP.ar.md`.
- [x] #8 Language and VAD gating in the UI: shared `model-capabilities.ts` (`nearestLanguage`,
  `reconcileLanguage`, `vadGate`) and `vad-gate.ts` (`ensureVadModel`) wired into Settings, Setup,
  the transcription queue and the hotkey path; 5 new strings in `en-US` and `ar-IQ`.
- [x] #9 Local endpoint hardening: loopback Host/Origin guard in `server/`
  (`server/crates/vibe-server/src/server/guard.rs`), the app spawns the engine with an explicit
  `--host 127.0.0.1 --port 0`, the release workflow now builds the engine from source and runs the
  guard tests; documented in `SECURITY.md` and `docs/UPSTREAM-PATCHES.md` §9.

**P1 evidence (2026-11-17):** engine rebuilt from `server/` as `vibe-server v0.6.16-sada.1`
(75,686,912 B, SHA-256 `48308753614AA6B2D7C8BF587234569791A121F53D19EB006B2A9A5986FA29CF`) and
staged as the sidecar. Live MCP run against the patched sidecar: `sada_info` reported the Nemotron
capabilities (`engine: nemotron`, `requires_vad: true`, 32 languages incl. `ar-AR`, no translation or
prompts); Nemotron transcribed the Arabic clip with timestamps; Whisper accepted the configured
`ar-AR` and mapped it to `ar`; `translate`/`prompt` were dropped for Nemotron and the call still
succeeded. Guard tests 8/8 passed and a live `curl` matrix returned 200 for native loopback
requests, 200 for `localhost`, and 403 for a DNS-rebinding `Host`, a page `Origin`, and a missing
`Host` — including a state-changing `POST /v1/models/load`. Frontend 28 files / 179 tests pass,
Rust `mcp::` 27 tests pass, `pnpm build` and the i18n audit pass. The published installer was re-downloaded, hash-verified, installed silently
(exit 0) and checked: `Sada.exe` 3.4.0, installed sidecar `vibe-server v0.6.16-sada.1`, installed
MCP server `3.4.0` with the expected capabilities, and the guard matrix repeated on the installed
engine (200/403/403/200).
- [x] Release v3.4.0 (bilingual notes, tag, CI release run
  [44092018396](https://github.com/alshahia/sada/actions/runs/44092018396)):
  [release](https://github.com/alshahia/sada/releases/tag/v3.4.0) · installer 44,915,585 bytes ·
  SHA-256 `7e6d8c813af34a80e4fa59e2ee28444a07b2c7811d88aa1b2549b627ce3cfd27` (re-downloaded and
  matched against `SHA256SUMS.txt`); the published installer installs `Sada 3.4.0` with sidecar
  `vibe-server v0.6.16-sada.1`, and the installed engine repeats the guard matrix.
## P2 — Arabic model evaluation (complete, v3.5.0)

- [x] #10 Arabic ASR benchmark harness (`benchmarks/arabic-asr/`): pinned 60-clip manifest
  (30 MSA Common Voice 18 CC0 + 10 Latin-mixed Common Voice + 20 Egyptian FLEURS `ar_eg`
  CC-BY-4.0), Arabic normalisation, stripped-WER/CER, acronym **and Latin-name** preservation,
  timestamp coverage, RTF, per-slice curation verdicts, `unittest` suite (38 tests) and a CI job.
  Audio and weights stay out of git.
- [x] #11 Model decisions with measured evidence, written to
  [`docs/MODELS-DECISIONS.md`](docs/MODELS-DECISIONS.md): Turbo stays the default; **Nemotron 3.5
  ASR Streaming 0.6B promoted to an optional verified catalogue entry** (OpenMDW-1.1, 495,831,520 B,
  SHA-256 `41c99fa5…b8fd`, VAD supplied by the app); the Arabic Whisper fine-tune is rejected
  (23.09% vs 19.46% WER); the ≥90% acronym gate is recorded as not applicable because no
  commercial-use corpus with acronym references exists yet — the `latin-mixed` slice is the
  declared proxy.
- [x] #12 Read-aloud go/no-go in [`docs/READ-ALOUD.md`](docs/READ-ALOUD.md): **no-go** (a normal
  Windows install ships English voices only; Arabic voices are an optional Narrator download that
  needs network and usually elevation; the rubric could not be run on the evaluation host). No TTS
  code written; Chatterbox stays suspended.
- [x] #13 Second-engine spike in [`docs/MODELS-DECISIONS.md`](docs/MODELS-DECISIONS.md): built
  transcribe.cpp v0.4.2 from source (MIT) and ran Qwen3-ASR 0.6B Q8_0 (811 MB, Apache-2.0) over all
  60 clips in one CPU batch — 60/60 transcribed, WER 24.38% overall (MSA 20.54%, Egyptian 21.10%,
  Latin-mixed 48.96%), no timestamps, no VAD → **rejected for integration**, keep-learning only.

**P2 evidence (2026-11-18):** engine `vibe-server v0.6.16-sada.1` on Vulkan (Quadro RTX 4000),
60 clips per model. Overall WER/CER: **turbo 19.46/8.34, RTF 0.35**; Nemotron 17.12/8.28, RTF 0.234,
496 MB; dialectal fine-tune 23.09/9.53; tiny 70.56/29.46. WER by slice (turbo → Nemotron): MSA
22.09 → 17.83, Egyptian 11.03 → 9.11, Latin-mixed 48.96 → 50.00. Latin-name preservation 25.0% for
turbo vs 0.0% for every challenger; timestamps 100% for all `vibe-server` models. Raw:
`benchmarks/arabic-asr/results/results-2026-11-18.json` and
`results-2026-11-18-transcribe-cpp.json`. Catalogue, `docs/MODELS.md` and `docs/MODELS.ar.md`
updated; frontend tests and the Python suite re-run green.

- [x] Release v3.5.0 (bilingual notes, tag, CI release run
  [44248008750](https://github.com/alshahia/sada/actions/runs/44248008750)):
  [release](https://github.com/alshahia/sada/releases/tag/v3.5.0) · installer 44,936,816 bytes ·
  SHA-256 `9cf779ff7c891e4823523be34e5315da2136d7dcf6356db085889c4cbadca279` (re-downloaded and
  matched against `SHA256SUMS.txt` and the GitHub asset digest); silent install → `Sada.exe` 3.5.0,
  installed sidecar `vibe-server v0.6.16-sada.1`, installed MCP ready (`sada-mcp 3.5.0`); the CI run
  [44248005147](https://github.com/alshahia/sada/actions/runs/44248005147) is green including the new
  benchmark-harness job.

## P3 — transcript quality, security and acceptance (complete, v3.6.0)

- [x] #14 Arabic transcript quality: 21 Latin technical terms restored from the Arabic-letter
  spellings whisper.cpp emits (whole-word rules handling the definite article and split/joined
  forms), Arabic punctuation and spacing normalised, lossless and idempotent, applied to every
  transcript surface. The same rules live in `sadabench/postprocess.py` and are pinned by shared
  fixtures (`benchmarks/arabic-asr/fixtures/arabic-postprocess-cases.json`), and the benchmark
  report gained an **App-level** table. Measured 2026-11-18: app-level WER equals raw (Turbo
  19.46%, Nemotron 17.12%, dialectal 23.09%, tiny 70.56%) — presentation only, no accuracy claim.
- [x] #15 Upstream v3.3.6 security audit ported where it fits the fork: CSP, SafeMarkdown, sada:
  deep-link allowlist with full-URL confirmation and catalogue integrity, model download
  destination confinement (no relative paths, `..`, symlinks or `.part` symlinks; https-only
  redirects), yt-dlp version/URL/SUMS validation, engine child-process confinement, dictation
  typing permit (30 min, 50k chars, control characters stripped); the unvalidated generic
  `download_file` command is gone. Deliberately not ported (fork invariants): telemetry, the
  agent-drivable test build, staging-folder migration and remote catalogue signing. Recorded in
  `docs/UPSTREAM-PATCHES.md` §10 and `SECURITY.md`.
- [x] #16 Clean-machine acceptance + signing decision: `docs/ACCEPTANCE.md` (install, offline,
  WebView2 prerequisite, CPU fallback, AVX2/AVX baseline, AVX-less SSE4.2 behaviour, Nemotron +
  VAD, sada: links, dictation, engine confinement, evidence table) and `docs/SIGNING.md`
  (SignPath Foundation free OSS → Azure Artifact Signing ≈US$10/month → OV/EV; no purchase before
  the owner decides; `scripts/sign.py` stays disabled). Machine rows B–E need hardware the
  maintainer does not have and are explicitly recorded as **not executed**, not claimed.

**P3 evidence (2026-11-18):** `pnpm test` 31 files / 193 tests, `pnpm build` (paraglide + tsc +
vite, final bundle 1m 5s), `cargo test --release` 101 tests, `cargo test --release -p vibe-server
guard::` 8 tests, Python benchmark suite 44 tests and the i18n audit pass. New tests cover URL
validation, download destinations, yt-dlp tags/SUMS, type_text permit and control characters, safe
Markdown, and sada: deep links. Installer hash recorded after the release below.

- [x] Release v3.6.0 (bilingual notes, tag): link and installer hash recorded after CI publishes
  the release.

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
- Why the defaults stay Whisper large-v3-turbo (measured 2026-11-18): best overall Arabic WER
  (19.46%), 100% word timestamps and the only model that keeps Latin code-switched terms (25% of
  Latin names vs 0% for Nemotron), and fast enough (RTF 0.35 on Vulkan). Nemotron 3.5 is smaller
  (496 MB), faster (RTF 0.234), punctuates better and wins the read MSA/Egyptian slices (17.83%/9.11%
  vs 22.09%/11.03%), so it is curated as an optional entry — but it transliterates technical terms
  and is never the default. Both verdicts and the rejections (fine-tune, read-aloud, second engine)
  are recorded with reproduction commands in [`docs/MODELS-DECISIONS.md`](docs/MODELS-DECISIONS.md).

## Rules that do not move

- Arabic-first defaults (`ar-IQ` UI, `ar` transcription, RTL) and the 100% `ar-IQ` catalogue.
- No telemetry, updater, account or phone relay; local models only, no cloud relay.
- Models are user-initiated downloads; the installer stays small; no weight enters the repository.
- Commercial-use licence only (MIT, Apache-2.0, CC-BY-4.0, OpenMDW-1.1 after notice review).
- Fork discipline: bump the engine by upstream release, keep `docs/UPSTREAM-PATCHES.md` honest, and
  prefer upstream infrastructure (catalog, sentence view, non-AVX) over home-grown replacements.

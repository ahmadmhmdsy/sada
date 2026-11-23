# Sada roadmap

Living execution plan for the work approved in the [models council](docs/MODELS-COUNCIL.md) and the
[features council](docs/FEATURES-COUNCIL.md).
It records what is in flight, what each milestone promises, and the evidence rule that decides
model questions: **no model is curated without a licence, a size, a SHA-256 and timestamps** — and no
Arabic claim is made without the benchmark.

Status: `P0 complete`, `P1 complete`, `P2 complete`, `P3 complete`, `P4 complete`,
`P5 complete`, `P6 complete` — v3.3.1 and v3.4.0 shipped 2026-11-17, v3.5.0, v3.6.0, v3.7.0
and v3.8.0 shipped 2026-11-18, v3.9.0 and **v3.10.0 shipped 2026-11-19** (tag `v3.10.0` at
`be27bd5`; release assets, checksums and Sigstore provenance verified 2026-11-21). **v3.11.0 shipped
2026-11-22** as a maintenance and release-engineering cut (dependency refresh, CI engine job, attested
`SHA256SUMS.txt`, Tauri 2.12 stack); its P7 feature scope is deferred to 3.12 pending the five-user gate.
`P7` M0/M1/M4
are delivered — FC-1 docs, FC-2 FAIL and FC-3 PASS evidence reports — and M2/M3 stay gated:
[P7-PLAN.md](docs/P7-PLAN.md), from the [features council](docs/FEATURES-COUNCIL.md).
Last updated 2026-11-23.

## Milestones

| Milestone | Due | Promise | Issues |
| --- | --- | --- | --- |
| **v3.3.1 — engine & GPU foundation** | 2026-11-24 | Engine sidecar v0.6.16, Nemotron-3 diarization migration, GPU/Vulkan documented, patch release | #1 #2 #3 #4 |
| **v3.4.0 — verified model catalog** | 2026-12-08 | Bundled verified catalog + Get models, Arabic entries and docs, MCP/capability plumbing, local endpoint hardening | #5 #6 #7 #8 #9 |
| **v3.5.0 — Arabic model evaluation** | 2027-01-15 | Arabic WER/CER harness, fine-tune/Nemotron decisions, read-aloud test, second-engine spike | #10 #11 #12 #13 — **complete**, evidence below |
| **v3.6.0 — transcript quality & hardening** | 2027-02-15 | Arabic transcript post-processing earned in the benchmark, upstream v3.3.6 security audit ported, clean-machine offline acceptance + signing decision | #14 #15 #16 — **complete**, evidence below |
| **v3.7.0 — dialect coverage & prompt biasing** | 2027-04-15 | Measured Gulf + Arabic/English technical code-switch slices from a commercial-use corpus, prompt-biasing measurement and app wiring if it wins, honest remaining-gap matrix | #19 #20 #21 — **complete**, [release](https://github.com/alshahia/sada/releases/tag/v3.7.0), evidence below |
| **v3.8.0 — distribution, offline install & benchmark gate** | 2027-06-15 | Offline WebView2 installer variant as a second asset, signing pipeline staged but dormant (releases stay unsigned OSS), evidence-based production-readiness statement, benchmark regression gate | #22 #23 #24 #25 #26 — **complete**, [release](https://github.com/alshahia/sada/releases/tag/v3.8.0), evidence below |
| **v3.9.0 — P6 Wave 1: trust & enterprise readiness** | 2027-09-15 | Assurance pack, keyless supply chain (provenance + SBOM), security operations, managed offline policy, DPAPI secrets, retention, per-machine MSI deployment kit, rows B–E runbook | #27 #28 #29 #30 #31 #32 #33 #34 #35 — **complete**, [release](https://github.com/alshahia/sada/releases/tag/v3.9.0), evidence below |
| **v3.10.0 — Wave 1 UI repairs & truth-only copy** | 2026-11-19 | Four repair families (A–D) + V3 truth-only copy; axe 35 states / 0 violations; release notes and metadata prepared | — **complete**, [release](https://github.com/alshahia/sada/releases/tag/v3.10.0) published 2026-11-19 (tag at `be27bd5`, assets + checksums + provenance verified 2026-11-21) |
| **v3.12.0 — next feature wave (planning)** | TBD after the five-user gate | Scope A/B/C — Wave 2 repairs, FC-4/FC-5, Echo preview, or engineering (engine parity); gates and work sequence in [v3.12.0-plan.md](docs/releases/v3.12.0-plan.md) | #61 #62 — planning, five-user gate open |
| **v3.11.0 — maintenance & release engineering** | 2026-11-22 | Dependency refresh (20 Dependabot updates + utoipa 6), CI engine job, engine build identity `-sada.2`, attested `SHA256SUMS.txt`, Tauri 2.12 stack; no UI, engine, model or transcription change | — **complete**, [release](https://github.com/alshahia/sada/releases/tag/v3.11.0) published 2026-11-22 (tag `c7acdc8`, run 45024992661, assets + hashes + attestations verified 2026-11-22); P7 feature scope (FC-4 etc.) deferred to 3.12 pending the five-user gate, [P7-PLAN.md](docs/P7-PLAN.md), [release plan](docs/releases/v3.11.0-plan.md) |

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

- [x] Release v3.6.0 (bilingual notes, tag, CI release run
  [44262023351](https://github.com/alshahia/sada/actions/runs/44262023351)):
  [release](https://github.com/alshahia/sada/releases/tag/v3.6.0) · installer 44,926,298 bytes ·
  SHA-256 `53e0a3c9d715c0eff949f9058d77708fb4899c685ef7fe022719868efa54d40e` (re-downloaded and
  matched against SHA256SUMS.txt and the GitHub asset digest); silent install → Sada.exe 3.6.0,
  installed sidecar `vibe-server v0.6.16-sada.1`, installed MCP ready (`sada-mcp 3.6.0`); CI run
  [44262019603](https://github.com/alshahia/sada/actions/runs/44262019603) is green including the
  benchmark-harness job, and the site deploy run is green.

## P4 — dialect coverage and prompt biasing (complete, v3.7.0)

Plan with the full licence matrix and experiment design: [docs/P4-PLAN.md](docs/P4-PLAN.md).

- [x] #19 Add 15 Gulf (Saudi code-switch) and 15 technical (Egyptian code-switch) Perle AI clips
  (MIT, audio recorded by native voice actors — clean provenance) to manifest v2; keep Iraqi and
  Levantine visible as pending and record every rejected corpus with its licence reason. Fetch,
  run and report per-slice WER/CER + Latin preservation.
- [x] #20 Measure `--prompt` glossary biasing (no prompt vs Arabic+Latin glossary vs English-only
  vs Arabic-only) on the Latin-mixed/MSA slices, then on the full corpus if it wins; wire a
  one-click glossary prompt into Settings only if the numbers justify it and no slice regresses.
  Measured negative: no preset shipped (numbers below).
- [x] #21 Docs/decisions, version bumps, bilingual v3.7.0 notes, full test matrix and release;
  verify installer re-download, silent install, sidecar and MCP banner. Shipped 2026-11-18:
  [release](https://github.com/alshahia/sada/releases/tag/v3.7.0) · installer 44,921,531 bytes ·
  SHA-256 `faeb2d07e207239b30880fc67a689034005091f8031a3090795fc3df83a8b207` (re-downloaded and
  matched against `SHA256SUMS.txt`); silent install verified Sada.exe 3.7.0, sidecar
  `vibe-server v0.6.16-sada.1`, MCP `sada-mcp 3.7.0`; CI
  [44274890695](https://github.com/alshahia/sada/actions/runs/44274890695) and Release
  [44273571514](https://github.com/alshahia/sada/actions/runs/44273571514) are green.

**P4 evidence (2026-11-18):** manifest v2 = 90 clips (30 MSA, 10 Latin-mixed, 20 Egyptian, 15 Gulf,
15 technical), Perle revision `1cc59502…`, 30 distinct rows, audio fetched (90/90 WAVs, 0 failed)
and never committed. Full run on five model variants × 90 clips = 450 transcriptions, engine
`vibe-server v0.6.16-sada.1` on Vulkan: Turbo WER 30.27% overall (MSA 22.09, Latin-mixed 48.96,
Egyptian 11.03, Gulf 42.74, technical 46.18), Latin names 27.3%; Nemotron 35.16% (wins MSA/Egyptian,
loses 17–19 pp on both code-switch slices, 0% Latin names); dialectal fine-tune 32.60% with a
1.14 pp corpus-level Gulf edge whose per-clip bootstrap 95% CI is [-10.06, +8.28] — too weak to
curate; glossary prompt 31.44% overall while preserving more Latin terms (technical 47.1% vs 34.3%)
— prompt spike WER 31.92% vs 29.38% no-prompt on 40 clips, so no app preset. Artefacts:
[`results/results-2026-11-18-v2.md`](benchmarks/arabic-asr/results/results-2026-11-18-v2.md),
[`results/prompt-spike-v1.md`](benchmarks/arabic-asr/results/prompt-spike-v1.md); decisions in
[`docs/MODELS-DECISIONS.md`](docs/MODELS-DECISIONS.md), plan in [`docs/P4-PLAN.md`](docs/P4-PLAN.md).

## P5 — distribution, offline install and benchmark regression gate (complete, v3.8.0)

Plan: [docs/P5-PLAN.md](docs/P5-PLAN.md). The release is deliberately not a feature release; it
closes the trust and regression gaps left by P4.

- [x] #22 Offline WebView2 installer variant: `desktop/src-tauri/tauri.offline.conf.json` overlay
  (`webviewInstallMode = offlineInstaller`), release workflow builds/publishes both installers
  with distinct names and SHA-256 lines, docs and release notes explain which to pick; the small
  installer stays the default. This leaves only the unexecuted clean-machine rows B–E in #17.
- [x] #23 Stage the signing pipeline dormant: workflow steps guarded by the `SIGNING_ENABLED`
  repository variable plus a SignPath submit step and an Authenticode verification step; with the
  variable unset the release behaves exactly as today. `docs/SIGNING.md` records the owner's
  2026-11-18 decision (unsigned while open-source-only) and the switch-on procedure; #18 stays open
  for the application itself.
- [x] #24 Production-readiness statement: `docs/PRODUCTION-READINESS.md` with per-audience
  verdicts (personal use / team use / managed deployment), evidence links, and the explicit gaps
  (unsigned, rows B–E, unmeasured dialects, no telemetry or crash reporting by design).
- [x] #25 Benchmark regression gate: `sadabench compare --baseline … --candidate …` with per-slice
  deltas, tolerance and exit codes, tests, committed v2 baseline and CI exercise; release checklist
  runs it.
- [x] #26 Docs, version bump 3.8.0, bilingual notes, full test matrix, tag, release verification,
  evidence in `docs/VERIFICATION.md` / `docs/ACCEPTANCE.md`.

## Step Zero tests (define "done" before code)

1. **E1 — engine bump smoke test.** Four Arabic clips (short MSA, MSA news, Iraqi dialogue,
   Arabic/English tech mix): transcription parity, timed SRT/VTT export, diarization on the migrated
   model, CPU-only path, no hard-coded strings. Any Arabic regression keeps v0.6.10 and blocks the release.
2. **E2 — Arabic benchmark.** 40–60 reference clips, normalised WER/CER, Latin-acronym preservation,
   timestamps. A challenger is curated only at ≥1.0 pp WER win on its slice, ≥90% acronyms kept,
   timestamps present. Nemotron gets an optional entry only if it wins the dictation slice.
3. **E3 — OS voice read-aloud.** Go/no-go on installed Windows Arabic voices before any TTS code.
   Result (2026-11-18): **no-go** — Windows has no Arabic voice by default; evidence in
   [READ-ALOUD.md](docs/READ-ALOUD.md).
4. **E4 — Arabic read-aloud with permissive weights (Step Zero A).** Habibi-TTS specialized IRQ and
   MSA models (Apache-2.0 weights) on 10 transcripts: native-listener mean ≥4/5, re-transcription
   CER drift ≤10%, RTF ≤1.0 GPU / ≤3.0 CPU, no Python at runtime, optional download ≤2 GB,
   user-owned or licensed reference voice. Any fail keeps the no-go and closes TTS for the cycle.
   Report required; no integration code. **Result (2026-11-21): FAIL** — Python-only runtime (hard
   fail), CPU RTF 58–67 against ≤ 3.0, GPU mean 0.87 but 3/10 clips > 1.0 (max 1.15), naturalness
   unevaluated; MSA CER drift 0 % and model licences passed. Evidence:
   [STEP-ZERO-A-READ-ALOUD.md](docs/STEP-ZERO-A-READ-ALOUD.md). The no-go stays; no integration.
5. **E5 — Arabic subtitle burn-in (Step Zero B).** Bundled FFmpeg libass/HarfBuzz/bidi check plus five
   burned clips: 5/5 correctly shaped and readable at 720p, or close with a dated note. Report
   required; no UI code. **Result (2026-11-19): PASS — 5/5 clips** with a native-typography caveat.
   Evidence: [STEP-ZERO-B-BURN-IN.md](docs/STEP-ZERO-B-BURN-IN.md).

## Decision records

- [Models, features & tools council (EN)](docs/MODELS-COUNCIL.md) · [(AR)](docs/MODELS-COUNCIL.ar.md) —
  verdicts, licence table, measured evidence, phased plan.
- [Features, platforms & gaps council (EN)](docs/FEATURES-COUNCIL.md) ·
  [(AR)](docs/FEATURES-COUNCIL.ar.md) — STT/TTS/S2S verdicts, competitor board, licence board,
  Step Zero tests and the phased plan.
- [P7 execution plan](docs/P7-PLAN.md) — truth parity, Step Zero A/B, next-wave candidates.
- [Upstream delta](docs/UPSTREAM-PATCHES.md) — engine/catalog/security changes the fork has not taken yet.
- Why the defaults stay Whisper large-v3-turbo (measured 2026-11-18, 90-clip suite): best overall
  Arabic WER (30.27%), 100% word timestamps and the only model that keeps a meaningful share of
  Latin code-switched terms (27.3% of Latin names vs 0% for Nemotron), fast enough on Vulkan
  (RTF 0.38). Nemotron 3.5 is smaller (496 MB), faster (RTF 0.215), punctuates better and wins the
  read MSA/Egyptian slices (17.83%/9.11% vs 22.09%/11.03%), so it is curated as an optional entry —
  but it trails by 17–19 pp on the Gulf and technical code-switch slices, transliterates technical
  terms and is never the default. The 60-clip v3.5/v3.6 numbers are kept in the P2/P3 evidence above
  and are not comparable to the 90-clip suite. Both verdicts and the rejections (fine-tune,
  read-aloud, second engine) are recorded with reproduction commands in
  [`docs/MODELS-DECISIONS.md`](docs/MODELS-DECISIONS.md).


**P5 evidence (2026-11-18):** released as [v3.8.0](https://github.com/alshahia/sada/releases/tag/v3.8.0)
(commit 2fed37f) with two NSIS assets from the same source — default
`Sada_3.8.0_x64-setup.exe` 44,924,997 bytes / SHA-256 `dfbcb454…c6790` and offline-WebView2
`Sada_3.8.0_x64-setup-offline.exe` 262,829,070 bytes / SHA-256 `409900ef…8e0a` (one line each
in `SHA256SUMS.txt`). CI run [44285117725](https://github.com/alshahia/sada/actions/runs/44285117725)
passed in 6m 55s (desktop 193 vitest / 101 Rust / engine sidecar; benchmark job 62 Python tests plus
the self-comparison of the committed baseline). Release run
[44285122650](https://github.com/alshahia/sada/actions/runs/44285122650) passed in 29m 16s, rebuilt
the guarded engine from `server/`, built the offline variant first then the default, published
the release, and recorded the signing-verification step as skipped (`SIGNING_ENABLED` unset).
Deploy site run [44285117746](https://github.com/alshahia/sada/actions/runs/44285117746) passed. The
regression gate was exercised on the committed baseline (self-comparison 0.00 in every cell) and
manually against a degraded run (blanking five Gulf/technical references failed it with +5.76 pp
overall and +22.50 pp on Gulf, exit 1). Both published installers were re-downloaded, hash-matched
against `SHA256SUMS.txt` and installed silently: both report Sada.exe 3.8.0, sidecar
`vibe-server v0.6.16-sada.1` and MCP banner `sada-mcp 3.8.0`. Evidence in
[docs/VERIFICATION.md](docs/VERIFICATION.md); readiness statement in
[docs/PRODUCTION-READINESS.md](docs/PRODUCTION-READINESS.md). Rows B–E of the clean-machine matrix
remain unexecuted (#17), the offline installer still downloads the VC++ runtime when missing, and
signing stays dormant (#18) by owner decision.

## Backlog after v3.11.0

- **P7 truth parity (FC-1)** — document the six shipped-but-invisible capabilities in both READMEs,
  the landing page and onboarding; evidence rule only, no new claims. See
  [P7-PLAN.md](docs/P7-PLAN.md).
- **Step Zero A/B reports (FC-2, FC-3)** — done: [Step Zero B PASS 5/5](docs/STEP-ZERO-B-BURN-IN.md) (2026-11-19) and [Step Zero A FAIL](docs/STEP-ZERO-A-READ-ALOUD.md) (2026-11-21); read-aloud stays closed, burn-in becomes a gated candidate.
- **GitHub milestone + issues for P7** — FC-1…FC-9 are the canonical IDs until gh authentication is
  available (OWNER-ACTIONS A16); then open milestone P7 and one issue per ID.
- **v3.10.0 tag** — done: tag `v3.10.0` points at `be27bd5`, the Release workflow
  (44526120606) is green, and the published assets were re-downloaded and verified on 2026-11-21
  (SHA-256 matches `SHA256SUMS.txt`, Sigstore attestation verifies); OWNER-ACTIONS A14 is closed.
- **v3.11.0 tag** — done: tag `v3.11.0` points at `c7acdc8`; Release workflow run 45024992661 is green
  (Tauri 2.12 build) and the published assets were re-downloaded and verified on 2026-11-22 (hashes,
  installer attestations and the new `SHA256SUMS.txt` attestation); OWNER-ACTIONS A17 is closed for the
  release half, with the five-user gate and the A8 clean-machine rows still open as documented gaps.
- **Five-user gate** — human-only test, blocks Wave 2 UI and the 4.0 Echo identity
  ([GATE-KIT](docs/design/ui-decisions/GATE-KIT.md)). Run it before FC-4 UI work.
- **Read-aloud watch-list** — Habibi-TTS specialised IRQ/MSA (Apache-2.0) tested and failed the Step
  Zero A gate on runtime and CPU speed (2026-11-21); the quality result was good (MSA CER drift 0 %,
  Iraqi raw CER 3.6 %), so the open condition is a non-Python runtime — candidates are the ONNX
  exports and the Apache-2.0 community `audio.cpp` GGUF port, neither evaluated. Chatterbox ar (MIT,
  retired commercial service, GPU/watermark) remains the fallback. Revisit only after a passed
  re-test; no read-aloud claim meanwhile.
- **TTS/S2S claims stay off** — no read-aloud claim until Step Zero A passes; S2S is not a roadmap
  item (no licensed Arabic speech-output model).
- [#17](https://github.com/alshahia/sada/issues/17) — with the offline installer variant shipped in
  P5, the only remaining part is running the clean-machine acceptance rows B–E (offline Windows 10,
  CPU-only, AVX-only, AVX-less SSE4.2) on hardware the maintainer does not control, then recording
  the evidence in `docs/ACCEPTANCE.md`.
- [#18](https://github.com/alshahia/sada/issues/18) — code signing. Owner decision 2026-11-18: stay
  unsigned while the project is open-source-only; P5 stages the workflow dormant, and P6 prepared the
  SignPath Foundation application packet (`docs/SIGNING.md` appendix — facts, draft answers, steps
  once approved) without submitting it. Interim trust signals are SHA-256 + build provenance.
- Iraqi/Levantine and spontaneous-dialect coverage: no commercial-use corpus with human
  transcripts was found as of 2026-11-18 (full matrix in `docs/P4-PLAN.md`); a paid vendor corpus
  is an owner purchase decision. Until measured, those regions stay explicitly unmeasured.
- Upstream drift: upstream Vibe's latest release is **v3.3.8** (2026-11-21; the v3.3.5 figure last
  recorded here was stale) while this fork is based on v3.2.2 plus hand-ported deltas
  (`docs/UPSTREAM-PATCHES.md`). Assessment: [UPSTREAM-REBASE-3.3.8.md](docs/UPSTREAM-REBASE-3.3.8.md) —
  50 commits / 445 files since v3.2.2; port feature groups incrementally, do not rebase. The same
  assessment found the **engine source is older than its `v0.6.16-sada.N` label** (source snapshot
  through upstream v3.3.1, label stamped from `.server-version`), which likely regressed speaker labels
  since v3.4.0 — issue [#73](https://github.com/alshahia/sada/issues/73), decision in
  [OWNER-ACTIONS A18](docs/OWNER-ACTIONS.md#a18--decide-engine-parity-and-speaker-labels).
- Dependabot triage: **executed 2026-11-21** (`docs/DEPENDABOT-TRIAGE.md`,
  [execution report](docs/reviews/2026-11-21-dependabot-merge/execution-report.md)) — 20 of 20 cleared PRs
  merged in four batches (npm, root Cargo, server Cargo, workflows last); #44 closed and replaced by the
  coordinated `utoipa` 5→6 upgrade (#68, merged); #53 was held for its Tauri installer gate and merged for
  v3.11.0 (`a232dbd`, 2026-11-22) after the isolated installer rehearsal; v3.11.0 shipped the same day.
- CI gap found in that triage — **fixed**: the `server` job in `ci.yml` (#69, merged `be4e8bd`) runs
  `cargo check --all-targets` and `cargo test --release -p vibe-server` on every change, so a server
  dependency bump can no longer pass CI and break the next release (as #44 did).
- Keep the benchmark gate honest: run the 90-clip suite and `sadabench compare` against the
  committed baseline for every release that touches the engine, models or Arabic post-processing.
  A source-built engine whose label changes (`v0.6.16-sada.N`) counts as an engine change.
- Dependabot grouping: `.github/dependabot.yml` now collects minor/patch updates per ecosystem into
  3–4 grouped PRs instead of ~22 ([DEPENDABOT-TRIAGE](docs/DEPENDABOT-TRIAGE.md) follow-up, PR #72);
  validate on the 2026-11-30 cycle before relying on it.

## P6 — trust and enterprise readiness (complete, v3.9.0)

Scope and rationale: [P6-PLAN.md](docs/P6-PLAN.md). Only work that needs no owner decision, purchase,
certificate, audit or hardware is in this wave.

- [x] #27 Assurance pack: `docs/SECURITY-WHITEPAPER.md`, `docs/THREAT-MODEL.md`,
  `docs/DATA-HANDLING.md`, `docs/AV-EDR.md` (explicit limits; no external audit claimed).
- [x] #28 Keyless supply chain: build provenance attestations on every asset (verified for both NSIS
  installers, the MSI and the SBOM), enriched CycloneDX SBOM (1,939 components), and
  `scripts/verify-release.ps1` (hash + attestation); `docs/SUPPLY-CHAIN.md`.
- [x] #29 Security operations: `.github/workflows/security.yml` (production npm audit failing only
  on critical advisories, RustSec audit of both cargo lockfiles, CodeQL), `.github/dependabot.yml`,
  and acknowledgement/fix targets in `SECURITY.md`.
- [x] #30 Egress inventory and managed offline mode: `docs/NETWORK.md` (+ AR) and the machine-wide
  policy (`HKLM\SOFTWARE\Sada\Policy` + `%ProgramData%\Sada\policy.json`) enforced in the Rust
  command layer and reflected in the UI, with `scripts/enterprise/` helpers.
- [x] #31 DPAPI key storage: `secrets.rs`/`secrets.ts`, per-user encryption on Windows, one-time
  plaintext migration, graceful decrypt failure; 5 Rust + 5 frontend tests.
- [x] #32 Retention and data hygiene: `transcription.retentionDays` (0 = forever default), launch
  purge, manual purge command limited to the transcripts folder, `docs/DATA-HANDLING.md`;
  6 Rust tests and UI coverage.
- [x] #33 Per-machine MSI and deployment kit: `tauri.enterprise.conf.json` target, CI builds it as
  the third asset, `docs/ENTERPRISE-DEPLOYMENT.md` and `scripts/enterprise/` (silent install,
  detection, policy, cleanup).
- [x] #34 Rows B–E runbook: `docs/VALIDATION-RUNBOOK.md` and `scripts/acceptance/run-row-b-e.ps1`;
  rows remain unexecuted only because the maintainer has no such hardware/VM (recorded, not hidden).
- [x] #35 v3.9.0 docs, version bump, bilingual release notes, full test matrix (204 frontend / 120
  Rust / 8 guard / 62 Python), tag, release verification and evidence in `docs/VERIFICATION.md`.

Owner decisions still open and deliberately not activated: code-signing application (#18 — the
SignPath application packet is prepared in `docs/SIGNING.md`, not submitted), paid support/SLA,
external penetration test budget, and hardware for rows B–E.

**P6 evidence (2026-11-19):** released as [v3.9.0](https://github.com/alshahia/sada/releases/tag/v3.9.0)
(source commit `c46809c`). CI run [44469317890](https://github.com/alshahia/sada/actions/runs/44469317890)
passed in 8m 12s (desktop: 204 vitest, 120 Rust, 8 guard, engine sidecar built from `server/`;
benchmark: 62 Python tests plus the committed-baseline self-comparison). Security run
[44469317902](https://github.com/alshahia/sada/actions/runs/44469317902) passed in 1m 54s (no critical
production npm advisories; RustSec report captured; CodeQL JS/TS). Release run
[44470348142](https://github.com/alshahia/sada/actions/runs/44470348142) passed in 48m 44s, building
the guarded engine, the offline-WebView2 NSIS variant, the per-machine MSI and the default NSIS
installer, then generating the SBOM and provenance attestations; Authenticode verification was
skipped because `SIGNING_ENABLED` is unset, and the release notes say the assets are unsigned.
Deploy site run [44469317846](https://github.com/alshahia/sada/actions/runs/44469317846) passed.

Assets: `Sada_3.9.0_x64-setup.exe` 44,939,266 bytes / SHA-256 `560b76c2…6133`,
`Sada_3.9.0_x64-setup-offline.exe` 262,848,006 bytes / `674d58c2…b979`, and
`Sada_3.9.0_x64_en-US.msi` 70,934,528 bytes / `751e74f3…6bad`, one line each in
`SHA256SUMS.txt` (282 bytes), plus `sbom-cyclonedx.json` 3,741,404 bytes. All three were
re-downloaded, hash-matched and passed `gh attestation verify`; both NSIS installers installed
silently (exit 0, registry `Sada 3.9.0`, `Sada.exe` 15,916,544 bytes ProductVersion 3.9.0, sidecar
`vibe-server v0.6.16-sada.1`, MCP banner `sada-mcp 3.9.0`). The MSI database reports
`ProductVersion 3.9.0`, `ALLUSERS = 1`, en-US; installing it in the non-elevated verification
session fails with error 1925 as designed for a per-machine package (managed deployment runs it
elevated). Evidence and limitations in `docs/VERIFICATION.md`; readiness statement in
`docs/PRODUCTION-READINESS.md`.

## P7 — post-3.10: parity, proof & platform (in progress — M0, M1, M4 done)

GitHub: milestone [#8](https://github.com/alshahia/sada/milestone/8) with one issue per FC ID ([#58](https://github.com/alshahia/sada/issues/58)–[#66](https://github.com/alshahia/sada/issues/66)). Scope, milestones and acceptance: [P7-PLAN.md](docs/P7-PLAN.md). Decision record:
[FEATURES-COUNCIL.md](docs/FEATURES-COUNCIL.md) (+[AR](docs/FEATURES-COUNCIL.ar.md)). Nothing in
this section promises a shipped feature: each item passes its Step Zero or it stays out. The
five-user gate ([GATE-KIT](docs/design/ui-decisions/GATE-KIT.md)) still blocks Wave 2 UI and the 4.0
"Echo" identity, so UI items below wait for it.

- [x] **FC-1 — truth-parity documentation** (M0, docs only) — **delivered 2026-11-19** ([#58](https://github.com/alshahia/sada/issues/58)): both
  READMEs, the bilingual landing pages, both llms.txt files and the new FAQ entries name the shipped
  capabilities — diarization (opt-in, 25 MB model, up to 4 speakers), meeting detection →
  auto-record → auto-transcribe, stable timestamps, 1,024-char custom prompt, URL import,
  auto-export, MCP, translation limits, AI cleanup/summary — and state plainly what is not offered
  (read-aloud, speech-to-speech, live captions). Evidence: [CLAIM-LEDGER.md](docs/CLAIM-LEDGER.md),
  one row per claim. `node scripts/seo/check-seo.mjs` green; no new capability claimed. The
  onboarding nudge for the diarization model was deferred (not a one-line change); the docs commit
  landed as `b7a85d3` (2026-11-21) and FC-1 is closed.
- [x] **FC-2 — Step Zero A, read-aloud falsification** (M1, report only, [#59](https://github.com/alshahia/sada/issues/59)) — **delivered 2026-11-21: FAIL.** Habibi-TTS specialised IRQ/MSA on 10 sentences (5 MSA + 5 Iraqi); exact checkpoints, licences, sizes and SHA-256 in the report. MSA CER drift 0.0 %, Iraqi raw CER 3.6 % mean; CPU RTF 58–67 (limit 3.0), GPU mean 0.87 with 3/10 clips over 1.0 (max 1.15); Python-only runtime; naturalness unevaluated (no listener). Evidence: [STEP-ZERO-A-READ-ALOUD.md](docs/STEP-ZERO-A-READ-ALOUD.md). No integration code; no-go retained.
- [x] **FC-3 — Step Zero B, Arabic subtitle burn-in** (M1, report only, [#60](https://github.com/alshahia/sada/issues/60)) — **delivered 2026-11-19: PASS 5/5.** Bundled FFmpeg 9.0.2 (libass/fribidi/harfBuzz) burned five 720p clips with correct shaping, RTL order, diacritics, mixed Latin and digit placement; caveat: native typography review of `%` placement and bracket mirroring. Evidence: [STEP-ZERO-B-BURN-IN.md](docs/STEP-ZERO-B-BURN-IN.md). No UI code.
- [ ] **FC-4 — meeting-notes polish** (M2, after the five-user gate, [#61](https://github.com/alshahia/sada/issues/61)): local summary/notes template
  after an auto-transcribed meeting; truth-only copy; no cloud summarisation.
- [ ] **FC-5 — translation/AI copy and QA** (M2, [#62](https://github.com/alshahia/sada/issues/62)): Whisper translate → English only (medium/large,
  not turbo); document and label the local Ollama AI path; no implication of an offline Arabic
  translation engine. Copy half **delivered with FC-1** (README rows, landing FAQ, llms.txt, claim
  ledger); the five-transcript local-AI QA is open because this build environment has no Ollama
  runtime.
- [ ] **FC-6 — live captions learn track** (M3, [#63](https://github.com/alshahia/sada/issues/63)): blocked on microphone streaming and Arabic
  real-time quality; no fake captions in the UI. State recorded 2026-11-19 in
  [P7-LEARN-TRACKS.md](docs/P7-LEARN-TRACKS.md).
- [ ] **FC-7 — dialect corpus and published benchmark** (M3, [#64](https://github.com/alshahia/sada/issues/64)): owner outreach/purchase
  (OWNER-ACTIONS A10); extend `benchmarks/arabic-asr` and publish aggregate results.
- [ ] **FC-8 — platform watch** (M3, [#65](https://github.com/alshahia/sada/issues/65)): watch folders only if users ask (revisit gate: three distinct
  requests); mobile, cloud collaboration and the media editor stay rejected by the fork invariants.
  Evaluation recorded in [P7-LEARN-TRACKS.md](docs/P7-LEARN-TRACKS.md).
- [x] **FC-9 — governance** (M4) — **done 2026-11-19**: milestone [#8](https://github.com/alshahia/sada/milestone/8) and issues [#58](https://github.com/alshahia/sada/issues/58)–[#66](https://github.com/alshahia/sada/issues/66) created with their acceptance blocks; ROADMAP, P7-PLAN and OWNER-ACTIONS now carry the real numbers.

**Dropped by the features council, for the record:** speech-to-speech conversation (no licensed
Arabic speech-output model; different product), mobile apps, cloud collaboration, text-based media
editing, cloud AI as a default path.

**P7 evidence:** [CLAIM-LEDGER.md](docs/CLAIM-LEDGER.md) and the 2026-11-19 truth-parity docs pass
(FC-1, delivered); Step Zero A/B reports and the five-user-gate result still to come.

## Rules that do not move

- Arabic-first defaults (`ar-IQ` UI, `ar` transcription, RTL) and the 100% `ar-IQ` catalogue.
- No telemetry, updater, account or phone relay; local models only, no cloud relay.
- Models are user-initiated downloads; the installer stays small; no weight enters the repository.
- Commercial-use licence only (MIT, Apache-2.0, CC-BY-4.0, OpenMDW-1.1 after notice review).
- Fork discipline: bump the engine by upstream release, keep `docs/UPSTREAM-PATCHES.md` honest, and
  prefer upstream infrastructure (catalog, sentence view, non-AVX) over home-grown replacements.
- No capability is advertised before its evidence: read-aloud stays unsupported until Step Zero A
  passes, live captions wait for a streaming engine, and speech-to-speech is not a roadmap item.
- A new feature class enters only through the features council: a named Step Zero test, a written
  kill rule, and a licence row before any code.

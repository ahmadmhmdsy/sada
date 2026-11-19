# P7 — post-3.10: parity, proof & platform (planned)

**Status:** started 2026-11-19 — **FC-1 truth-parity documentation delivered**; **M4 governance done** (milestone #8, issues #58–#66); M1–M3 remain gated as below.
Decision record: [FEATURES-COUNCIL.md](FEATURES-COUNCIL.md) (+ [Arabic](FEATURES-COUNCIL.ar.md)). Milestone: [P7 #8](https://github.com/alshahia/sada/milestone/8). Workstream IDs: FC-1…FC-9 map to issues [#58](https://github.com/alshahia/sada/issues/58)…[#66](https://github.com/alshahia/sada/issues/66) in order. Living status lives in [ROADMAP.md](../ROADMAP.md#p7--post-310-parity-proof--platform-planned).

This plan separates three things that must not be mixed: **truth parity** (documentation of what already shipped), **Step Zero tests** (falsification before any promise), and **next-wave features** (only what passes its test and only after the five-user gate). Nothing here is a commitment to ship a capability; nothing here bundles a model.

## Why

The features council (2026-11-19) established four facts:

1. **Sada already ships more than it documents.** Diarization, meeting detection → auto-record → auto-transcribe, stable timestamps, custom prompt, auto-export and translation mode are implemented, mostly opt-in, and absent from both READMEs. Perceived capability is below actual capability.
2. **TTS is the one real accessibility gap.** Windows has no Arabic voice by default (all en-US on the evaluation host). A new permissive candidate appeared — Habibi-TTS, whose specialized Iraqi and MSA models are Apache-2.0 — but its runtime, size and Arabic quality are unproven.
3. **S2S is a different product and there is no licensed Arabic speech-output model.** Qwen3-Omni (Apache-2.0) does not speak Arabic; Qwen2.5-Omni speaks English/Chinese; Moshi is English; SeamlessM4T v2 and XTTS-v2 are non-commercial.
4. **Arabic subtitle burn-in is a cheap, unusual differentiator** if the bundled FFmpeg can shape Arabic correctly.

The Devil's Advocate position stands as the main risk: this plan must not let new features dilute the Arabic STT core. That is why Phase 0 is documentation only and every feature phase has a written kill rule.

## Goal

Close the **perceived** parity gap honestly, falsify the two real feature candidates cheaply, and prepare only the next-wave work that survives evidence — without changing the offline, Arabic-first, no-account design and without touching 3.10.

## Non-goals (council-rejected, for the record)

- Speech-to-speech conversation mode.
- Mobile apps, cloud collaboration, text-based media editing, cloud AI as a default path.
- Bundling any TTS model in the installer.
- Advertising read-aloud, live captions or burn-in before their Step Zero passes.
- Any release tag, version bump or UI wave before the owner and the five-user gate allow it.

## Milestones

| Milestone | Exit criterion | Workstreams | Gate |
| --- | --- | --- | --- |
| **M0 — truth parity** | Both READMEs, landing-page copy and onboarding name the shipped capabilities; every claim maps to code; docs check green — **delivered 2026-11-19**, onboarding nudge deferred | FC-1 | None — documentation only |
| **M1 — falsification** | Step Zero A and B reports exist with pass/fail verdicts and dated evidence | FC-2, FC-3 | Owner authorises the test time |
| **M2 — next-wave features** | Only passers from M1, plus meeting-notes polish and translation/AI copy — copy delivered via FC-1, local AI QA still open (no Ollama runtime in the build environment), scoped into the next feature release | FC-4, FC-5 | Five-user gate for UI work; owner approves release scope |
| **M3 — learn tracks** | Written state of the art and a decision for each: live captions blocked, dialect corpus pending licensing, watch folders evaluated — states recorded 2026-11-19 in [P7-LEARN-TRACKS.md](P7-LEARN-TRACKS.md); corpus still gated | FC-6, FC-7, FC-8 | Owner purchase/outreach for the corpus |
| **M4 — governance** | P7 milestone and FC issues open on GitHub; ROADMAP, this plan and OWNER-ACTIONS agree; reminders set — **done 2026-11-19**: milestone [#8](https://github.com/alshahia/sada/milestone/8), issues [#58](https://github.com/alshahia/sada/issues/58)–[#66](https://github.com/alshahia/sada/issues/66) | FC-9 | Done — authenticated as alshahia |

## Workstreams

| ID | Milestone | Deliverable | Acceptance | Depends on | Release vehicle |
| --- | --- | --- | --- | --- | --- |
| **FC-1** | M0 | Truth-parity documentation: diarization (opt-in, 25 MB model, up to 4 speakers), meeting detection → record → auto-transcribe, stable timestamps, 1,024-char custom prompt, URL import, auto-export, MCP, translation-to-English limits, AI cleanup/summary; onboarding nudge for the diarization model (deferred) | Every sentence traceable to code or a measured number; node scripts/seo/check-seo.mjs green; no new capability claimed; Arabic and English READMEs agree — **delivered 2026-11-19**, evidence in [CLAIM-LEDGER.md](CLAIM-LEDGER.md) | — | Docs-only commit; no version bump |
| **FC-2** | M1 | Step Zero A — read-aloud falsification report: Habibi-TTS specialized IRQ and MSA on 10 transcripts, native-listener score, intelligibility CER drift, RTF on GPU and CPU, runtime/size/voice-provenance assessment | Five pass criteria from the council recorded one by one; verdict and dated kill/continue decision; exact model files listed | Owner authorises test time; optional native listener | Evidence commit (report only) |
| **FC-3** | M1 | Step Zero B — Arabic subtitle burn-in feasibility: bundled FFmpeg libass/HarfBuzz/bidi check, five clips burned and reviewed | 5/5 clips correctly shaped and readable at 720p, or a dated close with the failing detail | Bundled FFmpeg build | Evidence commit (report only) |
| **FC-4** | M2 | Meeting-notes polish: a finished auto-transcribed meeting produces a local summary/notes template; settings copy explains detection and auto-transcribe | Works offline with a local model or clearly requires the user's AI setup; truth-only copy; no cloud default | Five-user gate for UI wave; AI/meeting code exists | Next feature release (v3.11.0 candidate) |
| **FC-5** | M2 | Translation/AI copy and QA: state Whisper translate→English (medium/large, not turbo); document local Ollama path for AI translation; label AI output | Copy reviewed against code; no implication of an offline Arabic translation engine; QA on 5 transcripts for the AI path | FC-1 | Next feature release (v3.11.0 candidate) |
| **FC-6** | M3 | Live-captions learn track: current engine streaming state, Arabic real-time quality evidence, decision to wait or start an engine probe | Written state; no UI code; explicit "no fake captions" rule — **state recorded 2026-11-19** in [P7-LEARN-TRACKS.md](P7-LEARN-TRACKS.md) | Engine ships streaming mode (upstream) | None |
| **FC-7** | M3 | Dialect corpus and published benchmark: licensed Iraqi/Gulf/Levantine corpus, harness extension, aggregate results and copy update | Commercial-use licence on file; aggregate metrics published; caveat reduced | Owner purchase/outreach (OWNER-ACTIONS A10) | None (research) |
| **FC-8** | M3 | Platform watch: watch-folders evaluation (only if users ask); confirm rejected list stays rejected | One-page evaluation; no platform work started — **evaluated 2026-11-19** in [P7-LEARN-TRACKS.md](P7-LEARN-TRACKS.md), revisit gate = 3 distinct requests | User demand signal | None |
| **FC-9** | M4 | Governance: open the P7 milestone and FC-1…FC-9 issues; link from ROADMAP, this plan and OWNER-ACTIONS; set reminders | Milestone and issues exist with the same IDs; links resolve | GitHub authentication | None |

## Task detail

### FC-1 — truth-parity documentation (do first)

**Problem.** The README is the product page for most users. It documents models, exports and privacy but omits six shipped capabilities, so users compare Sada against competitors using an incomplete list.

**Steps.**
1. Build a claim ledger: one row per capability — claim, code evidence (file + symbol), measured evidence, public wording.
2. Update README.md and README.ar.md feature sections and The Documentation table: diarization (opt-in, 25 MB model, up to 4 speakers), meeting workflow, stable timestamps, custom prompt, URL import, auto-export, MCP (the app has no CLI beyond --mcp), translation limits, AI cleanup/summary.
3. Update the landing page copy and llms files only if the claim ledger supports every sentence; keep version refs at 3.10.0 until a release happens.
4. Add an onboarding nudge for the diarization model (only if it is a one-line change; otherwise list it as a follow-up and do not expand scope).
5. Run node scripts/seo/check-seo.mjs and the claim-ledger review; commit docs only.

**Status:** delivered 2026-11-19. [CLAIM-LEDGER.md](CLAIM-LEDGER.md) is the claim ledger; the
bilingual READMEs, landing pages, llms.txt files and FAQ entries were updated; the docs check passes.
The onboarding nudge was deferred so the pass stayed documentation-only.

**Acceptance evidence.** The claim ledger, README diffs, docs-check output. No new capability is
claimed; no release is cut.

**Kill rule.** Any claim that cannot be traced to code or measurement is removed, not softened.

### FC-2 — Step Zero A, read-aloud (one day)

Run the test defined in [FEATURES-COUNCIL.md](FEATURES-COUNCIL.md) §6.2. Prepare with the exact model files and licences (Habibi specialized IRQ and MSA models — Apache-2.0; unified/SAU/UAE models are excluded because they are CC-BY-NC-SA). Record hardware, Python/runtime versions, model sizes, SHA-256 and commands so the test is reproducible. If a shippable runtime is impossible (Python-only, no ONNX/GGUF path), record that as a fail even if quality is good. A pass leaves read-aloud as a **candidate** for the next planning cycle, not a promised feature.

### FC-3 — Step Zero B, burn-in (half day)

Inspect the bundled FFmpeg for libass, HarfBuzz and bidi support; use a font that covers Arabic (IBM Plex Sans Arabic is already shipped for UI/PDF). Burn five clips at 720p with mixed content (MSA, Iraqi, Latin acronyms, numbers, punctuation). Record exact commands and visual verdicts. A pass makes "Arabic subtitles burned into video" a differentiated candidate for the next UI wave after the gate.

### FC-4 — meeting-notes polish (after the five-user gate)

The meeting workflow exists but is invisible and unpolished. Keep the scope to: summary/notes template after auto-transcription, settings copy that explains detection and auto-transcribe, and a clear offline/local-AI boundary. No new capture engine, no cloud summarisation, no live captions.

### FC-5 — translation/AI copy and QA

Whisper translation is English-only and medium/large only; AI tasks can translate when the user configures Claude or Ollama. Document exactly that, label AI output, and QA the local path on five transcripts. This is a truth fix, not a new engine.

**Status (2026-11-19).** The copy half was delivered with FC-1 (README rows, landing FAQ, llms.txt, claim ledger). The local-path QA could not run in the build environment: no Ollama runtime is installed and the local API is unreachable, so it stays open for a machine with Ollama or the owner's configured provider. No offline Arabic translation engine is implied.

## Step Zero criteria (copy of record)

| Test | Pass criteria | Fail action |
| --- | --- | --- |
| A — read-aloud | Native-listener mean ≥ 4/5; re-transcription CER drift ≤ 10%; RTF ≤ 1.0 GPU / ≤ 3.0 CPU; no Python at runtime and optional download ≤ 2 GB; user-owned or licensed reference voice | Keep the no-go; record date; re-check only when a GGUF/ONNX Arabic TTS exists |
| B — burn-in | 5/5 clips correctly shaped and readable at 720p | Close with a dated note; no feature |

## Step Zero preflight (2026-11-19, environment check only)

Recorded before the tests so the owner can decide on facts; this is **not** the formal test and
changes no verdict.

- Host: Windows x64 with an NVIDIA Quadro RTX 4000 (8,192 MiB) — enough GPU for Step Zero A on the
  reference machine; a CPU-only second machine is still desirable for the CPU RTF criterion.
- The bundled FFmpeg (desktop/src-tauri/binaries/ffmpeg-x86_64-pc-windows-msvc.exe) reports
  "ffmpeg version 9.0.2-essentials_build" with --enable-libass, --enable-libfribidi and
  --enable-libharfbuzz, and lists the ass and subtitles filters. Step Zero B shaping precondition
  is met; the five-clip visual check is still required.
- uv 0.7.18 and Python 3.14.0 are present, so the Habibi-TTS environment can be created with uv
  (pin 3.11/3.12 if the PyTorch stack requires it). No model was downloaded and no TTS runtime is
  installed.
- The bundled engine CLI confirms the batch surface used by FC-6: vibe-server transcribe takes a
  model plus an audio file and exposes no streaming or microphone option.

Both formal tests remain blocked on the owner go-ahead (OWNER-ACTIONS A15).

## Release mapping

- **FC-1** ships as a docs-only commit; the site deploy workflow publishes it. No version bump, no tag, no release.
- **FC-2/FC-3** ship as evidence documents; no product code, so no release requirement.
- **FC-4/FC-5** are candidates for the next feature release, planned here as **v3.11.0** (milestone row in ROADMAP), due 2027-01-15 unless the owner moves it. That release requires the five-user gate results for any Wave-2 UI work and the usual full test matrix, bilingual notes and tag discipline.
- **FC-6/FC-7/FC-8** may never ship; they are decision records, not promises.
- **v3.10.0 tag remains an owner action** (see OWNER-ACTIONS A14); this plan does not tag.

## Owner gates

| Gate | Why it needs the owner | Where recorded |
| --- | --- | --- |
| Authorise Step Zero A/B | Spends about 1.5 days of attention and fixes the TTS decision path | OWNER-ACTIONS A15 |
| Approve FC-1 copy | Public-facing truth claims carry the owner's credibility | This plan + review |
| GitHub authentication for issues | **Done 2026-11-19**: gh authenticated as alshahia; milestone #8 and issues #58–#66 created | OWNER-ACTIONS A16 |
| Corpus purchase/outreach | Money/relationships only the owner can commit | OWNER-ACTIONS A10 |
| Five-user gate execution | Human-only usability test | docs/design/ui-decisions/GATE-KIT.md |
| Tag v3.10.0 and later releases | Release sign-off is always the owner's | OWNER-ACTIONS A14 |

## Dependencies and blockers

- **Five-user gate** (human-only) blocks Wave 2 UI work and the 4.0 "Echo" identity; FC-4 needs the gate for UI changes, not for the notes logic.
- **Engine streaming** (upstream Vibe/vibe-server) blocks FC-6; do not fake live captions in the UI.
- **Bundled FFmpeg build** determines FC-3.
- **Reference machine** (this host: Quadro RTX 4000 Vulkan + Intel UHD 630) is sufficient for Step Zero A/B; a CPU-only second machine is desirable for the RTF criterion.
- **GitHub auth** (done 2026-11-19): FC-9 mapped to milestone #8 and issues #58–#66; the FC IDs remain the canonical references.

## Metrics

| Metric | Target | Source |
| --- | --- | --- |
| README claim coverage of shipped capabilities | 100% of the six invisible capabilities documented with correct defaults | Claim ledger, README diffs |
| Docs check | node scripts/seo/check-seo.mjs passes | CI Docs & metadata |
| Step Zero A | All five criteria pass or dated fail | Test report |
| Step Zero B | 5/5 clips or dated fail | Test report |
| Overclaim count in new copy | Zero unsupported sentences | Truth Editor review |
| Five-user gate | Completed with 5 users before Wave 2 | GATE-KIT evidence |

## Risks and mitigations

- **Scope creep from the TTS test.** The test is time-boxed and report-only; a pass does not authorise implementation.
- **Licence confusion (Apache vs CC-BY-NC models).** Record exact model files and licences in the report; the catalogue rule remains mandatory.
- **Voice-cloning ethics.** No third-party reference voices; self-owned or licensed only; local processing.
- **Documentation drift while a release is pending.** FC-1 keeps version numbers at 3.10.0 and does not announce a release.
- **Single-maintainer attention.** M0 and M1 are the only committed work; M2 waits for the gate and for the owner's release decision.

## First action

FC-1 only: produce the claim ledger and draft the truth-parity README changes. The issue-opening gate is answered (milestone #8, issues #58–#66); nothing else starts until the owner answers the Step Zero gate.

## Issue and milestone mapping

FC-1…FC-9 are the canonical IDs in this plan and ROADMAP. With GitHub authentication available on
2026-11-19 they were mapped as follows:

1. Milestone **P7 — parity, proof & platform** created as [#8](https://github.com/alshahia/sada/milestone/8), due 2027-01-15.
2. One issue per FC ID with the acceptance block above, its gate and its evidence links: FC-1 [#58](https://github.com/alshahia/sada/issues/58) · FC-2 [#59](https://github.com/alshahia/sada/issues/59) · FC-3 [#60](https://github.com/alshahia/sada/issues/60) · FC-4 [#61](https://github.com/alshahia/sada/issues/61) · FC-5 [#62](https://github.com/alshahia/sada/issues/62) · FC-6 [#63](https://github.com/alshahia/sada/issues/63) · FC-7 [#64](https://github.com/alshahia/sada/issues/64) · FC-8 [#65](https://github.com/alshahia/sada/issues/65) · FC-9 [#66](https://github.com/alshahia/sada/issues/66).
3. ROADMAP and this plan now carry the real numbers instead of "issue to open".
4. The IDs stay stable forever so old references remain resolvable; FC-1 and FC-9 close when the pending docs commit lands.

# Sada — Features, Platforms & Gaps Council (Qiyas Council)

**Date:** 2026-11-19 · **App:** Sada 3.10.0 (source commit be27bd5) · **Base:** Vibe v3.2.2 fork (MIT) · **Engine:** vibe-server v0.6.16-sada.1 · **Mode:** C — Qiyas cards + adversarial council + Maestro verdict · **Language:** English (Arabic twin: [FEATURES-COUNCIL.ar.md](FEATURES-COUNCIL.ar.md))

> **Question.** Does Sada support text-to-speech, speech-to-text or speech-to-speech? What else should it have that competitors have — and what should it add that competitors do **not** have (the gaps worth solving)? Decide with the council.

This is a decision record, not a wish list. Every "current state" claim below was audited in this repository or read from a primary source on 2026-11-19; anything unmeasured is labelled **unverified**. Nothing here commits to bundling a model, adding a runtime or advertising a capability: each candidate passes a named Step Zero test or it stays out. The owner's standing answer to design questions applies throughout: **قل ما هو صحيح فقط** — say only what is true.

---

## 1. Method header — who sat in the room

| Role | Mandate | Distinguishing question | Qiyas tool |
| --- | --- | --- | --- |
| **Expert (خبير)** | Local ASR/TTS systems engineer: engines, model families, 6–24 month maintenance | Why did the precedent actually work, and what breaks later? | تخريج المناط |
| **Engineer (مهندس)** | Turns an accepted 'Illa into the smallest testable change in this repository | What is the Asl, and what is the 'Illa? | الفرع |
| **Devil's Advocate (معترض)** | Attacks the causal claim, not the wording | Where does the 'Illa break here? | القوادح |
| **Naive User (مستخدم بسيط)** | Iraqi user on a five-year-old laptop, no GPU, no patience | What do I gain, and why should I care? | تحقيق المناط |
| **Maestro (المايسترو)** | Silent until the stop condition, then rules on what survived | — | — |

Dynamic roles (seated because their dimension can kill or crown the plan):

| Role | Mandate | Distinguishing question | Red line |
| --- | --- | --- | --- |
| **Licence & Policy Guardian (حارس الترخيص والسياسة)** | Code and weight licences, commercial use, redistribution, gated models | May we ship it, and may our users sell what they make with it? | Any non-commercial, research-only, gated or unclear weight |
| **Arabic Market Strategist (استراتيجي السوق العربي)** | Arabic user value against cloud tools: dialects, UI, offline trust, moats | Does this serve the Arabic user in a way competitors do not? | Features that make Sada a worse copy of a cloud product |
| **Truth Editor (حارس الصدق التحريري)** | Every public sentence traceable to code or measurement | Is this sentence true today? | Marketing claims ahead of evidence |

---

## 2. Step 0 — framing, constraints, grounding

### 2.1 What the question really is

The question mixes three different things, and they must be answered separately:

1. **Capability today** — STT, TTS, S2S. These are facts, not roadmap.
2. **Parity** — features competitors ship that Sada does not. Parity must be split into "shipped but invisible", "genuinely missing", and "deliberately rejected".
3. **Differentiation** — gaps that competitors do **not** solve and that Sada is uniquely placed to solve (offline, Arabic-first, Windows, transparent licences).

"Speech-to-speech" is not one feature. It decomposes into **STT + an LLM (optional) + TTS**; the missing link is the TTS leg of a corpus with no licensed Arabic speech-output model (evidence in §8).

### 2.2 What Sada actually is today (audited in the repository)

| Stance | Evidence | In the READMEs? |
| --- | --- | --- |
| Fully offline Arabic-first STT, ar-IQ default, RTL | README, i18n bootstrap defaults, AGENTS.md invariants | Yes |
| Speaker diarization, opt-in, 25 MB model, UI note "supports up to 4 speakers detection" | config-keys.ts (transcription.recognizeSpeakers), preference.tsx (default false), use-transcribe-queue.ts passes the diarize model, quiet-row.tsx exposes "Recognize speakers" | **No** |
| Meeting detection → prompt → record → auto-transcribe | preference.tsx (meetingDetectionEnabled, autoTranscribeAfterRecording, both default false), app.tsx sync, i18n meeting detection strings | **No** |
| Stable timestamps mode for subtitle-grade timing | config-keys.ts (transcription.stableTimestamps), wired in the transcription queue | **No** |
| Custom Whisper prompt (names, jargon, spellings), up to 1,024 chars | settings/sections/whisper-options.tsx, i18n promptPlaceholder | Only as "empty initial prompt" in defaults |
| URL import through yt-dlp with version management | config-keys.ts tools.* keys, README managed-controls paragraph | Partly |
| Auto-export of every finished transcript | config-keys.ts (transcription.autoExport) | **No** |
| Local MCP server; no app-level CLI | Sada.exe --mcp is stdio-only with four tools (AGENTS.md, skill.ts); the app exposes no other command-line mode, while the bundled engine sidecar has its own CLI | MCP yes |
| Translation to English via Whisper, medium/large only (not turbo) | i18n translateToEnglish, translateWhisperModelNote | **No** |
| Optional AI summaries/cleanup/translation through Claude or Ollama | config-keys.ts ai, i18n aiDictationTask, aiSummaryTaskInfo | Summaries yes |
| No read-aloud, no speech output, no live-caption mode; "live preview" is batch preview | README feature table; no TTS path in the code | Correctly absent |
| Bundled FFmpeg (GPLv3) — Arabic subtitle shaping capability untested | AGENTS.md invariant, bundled FFmpeg | Licence yes, shaping unverified |

The expensive finding: **six capabilities are shipped and invisible** (diarization, meeting workflow, stable timestamps, custom prompt, auto-export, translation mode). The perceived gap is larger than the real gap.

### 2.3 What was already measured before this council

- **OS voice read-aloud (2026-11-18):** enumerated SAPI and OneCore voices — David, Mark, Zira and Eva, all en-US; the Arabic Hoda/Naayf voices are optional Narrator downloads requiring network and elevation. Verdict: **no-go for read-aloud** ([READ-ALOUD.md](READ-ALOUD.md)); it was never a shipping feature.
- **Arabic quality is measured, not assumed:** 19.46% WER for the default Whisper Large v3 Turbo on the committed 60-clip suite, 8.34% CER, 25% of Latin names kept, 100% word timestamps ([README.md](../README.md) model table); the larger 90-clip suite and its slice detail live in [ROADMAP.md](../ROADMAP.md). No TTS runtime exists in the app.
- **No streaming caption UI:** the engine and UI are batch; the "live preview" is a preview of a batch job, not live captioning.

### 2.4 What was researched on 2026-11-19

Primary licences and model cards fetched that day for the TTS/S2S candidates (Habibi-TTS, Chatterbox Multilingual v3, XTTS-v2, SeamlessM4T v2, Moshi, Qwen3-Omni, Piper voices), plus the public documentation of the competitors compared below. Every URL is listed in §8.3 so the next council can re-check the same evidence.

---

## 3. Global invariants (the Expert, stated before any branch)

1. Fully offline by default; **no telemetry, updater, account or phone relay**; no cloud path becomes the default for a core capability.
2. Arabic-first: ar-IQ default UI, RTL, Arabic typography and PDF; the Arabic catalogue stays 100% complete.
3. **Commercial use must be permitted for code and weights**; no bundled models; a model is curated only with licence, size, SHA-256 and timestamps.
4. Windows x64 first, CPU-capable, GPU optional; a new runtime is a product cost, not a footnote.
5. No capability is advertised before its evidence exists (owner answer Q4).
6. No release tag without the owner; 3.10 is frozen; the five-user gate still blocks Wave 2 and the 4.0 "Echo" identity.
7. Fork discipline: engine changes come from upstream releases; the app does not grow a home-made inference stack for one feature.
8. Ten-minute rule: a parity fix that is pure documentation ships before any new runtime is discussed.

---

## 4. Qiyas cards for the serious branches

### Card A — Arabic read-aloud (text-to-speech)

- **Al-Far' (new case):** add a "read transcript aloud" action with a local Arabic voice.
- **Al-Asl (precedent):** the read-aloud card in [MODELS-COUNCIL.md](MODELS-COUNCIL.md) and the OS-voice evidence in [READ-ALOUD.md](READ-ALOUD.md) — value comes from availability, not model novelty.
- **Al-'Illa (shared cause):** read-aloud is an accessibility and comprehension feature; users need to hear Arabic, not to hear a famous model. The original 'Illa failed only because Windows has no Arabic voice.
- **Tanqih (what to strip):** cloning, emotion and studio quality are not required; batch reading of a finished transcript is enough; a download is acceptable if it is optional.
- **Conditions (shurut):** commercially licensed Arabic weights; no third-party voice cloning (self-reference or licensed reference audio only); optional model download; native-listener quality bar; CPU or GPU runtime that fits a Tauri app.
- **Preliminary ruling:** **suspended-on-test.** Habibi-TTS changes the licence picture (see §8.1) but not the runtime problem; test it or leave it alone.

### Card B — Speech-to-speech (voice conversation)

- **Al-Far':** a speak-to-the-app / hear-the-answer loop.
- **Al-Asl:** the transcription charter and the 3.10 scope discipline.
- **Al-'Illa:** S2S is an assistant category, not a transcription capability; its real cause is conversational latency plus a speech-output model — neither is in Sada's trust story.
- **Tanqih:** "S2S" is a vocabulary item; the actual ingredients are STT, an optional LLM, and TTS.
- **Conditions:** a licensed Arabic speech-output model with acceptable quality and a CPU/GPU budget, plus a product reason that does not make Sada a worse ChatGPT Voice.
- **Preliminary ruling:** **the idea falls.** Qwen3-Omni (Apache-2.0) speaks 10 languages and Arabic is not one of them; Qwen2.5-Omni speaks English and Chinese; Moshi is English; SeamlessM4T v2 is non-commercial; XTTS-v2 is non-commercial. S2S is not a roadmap item — it is a different product.

### Card C — Live in-meeting captions

- **Al-Far':** text appearing while people speak.
- **Al-Asl:** batch transcription plus the existing "live preview" of file processing.
- **Al-'Illa:** the cause is not UI code; it is the engine's streaming mode and Arabic real-time quality. Neither exists in the current engine.
- **Tanqih:** "live preview" is not live captioning; do not relabel it.
- **Conditions:** a streaming engine with Arabic WER close to batch, a CPU budget on ordinary machines, and no regression to batch accuracy.
- **Preliminary ruling:** **Learn — deferred.** No fake captions; revisit only when the engine ships a streaming mode and the Arabic slice is measured.

### Card D — Arabic subtitle burn-in (captions rendered into video)

- **Al-Far':** burn correctly shaped Arabic subtitles into a video file.
- **Al-Asl:** the existing SRT/VTT export plus the bundled FFmpeg sidecar.
- **Al-'Illa:** the value is shareable Arabic captions that render correctly; competitors export text, and Arabic shaping is the hard part they avoid.
- **Tanqih:** this is rendering, not editing; no timeline.
- **Conditions:** the bundled FFmpeg includes libass with HarfBuzz/bidi shaping and a font that covers Arabic.
- **Preliminary ruling:** **suspended-on-test (cheap).** One-day spike; if the shaping works, this is a differentiated feature, not a copy.

### Card E — Parity discoverability

- **Al-Far':** document and surface the capabilities already shipped.
- **Al-Asl:** the truth-only copy rule and the README/docs evidence discipline.
- **Al-'Illa:** a capability a user cannot find is perceived as missing; this is the same causal path that makes a competitor look better on paper.
- **Tanqih:** no new engineering, no new claims; documentation and onboarding only.
- **Conditions:** every sentence maps to code or a measured number; the docs check passes.
- **Preliminary ruling:** **do now.** This is the cheapest parity work available.

### Card F — Arabic-target translation and AI parity

- **Al-Far':** translate a transcript into Arabic, and make the AI tasks (summary, cleanup, translation) visibly part of the product.
- **Al-Asl:** Whisper translation (English only) and the existing AI task plumbing.
- **Al-'Illa:** Arabic users consume English media; reading Arabic is the need, and the AI task already accepts a translation prompt.
- **Tanqih:** no new engine and no cloud dependency; an offline path means user-installed Ollama.
- **Conditions:** labelled as AI translation; a local path is documented; the Whisper limitation (medium/large, not turbo) is stated.
- **Preliminary ruling:** **do (documentation/QA).** The capability exists behind AI setup; the copy must stop implying an offline Arabic translation engine.

### Card G — Platform parity exclusions

- **Al-Far':** mobile apps, cloud collaboration, text-based media editing, watch folders, cloud AI.
- **Al-Asl:** the fork invariants and the production-readiness position.
- **Al-'Illa:** these categories assume cloud identity, shared workspaces or a media editor; adopting them would reverse the product's reason to exist.
- **Tanqih:** watch folders are a small automation convenience — the only candidates worth watching; the rest are not.
- **Conditions:** offline, no account, no cloud default; phone features stay out.
- **Preliminary ruling:** **drop** mobile/cloud/editor; **watch** folders only if users ask.

---

## 5. Transcript (live, survived rounds)

**Expert:** Start with the factual frame. STT: yes — and richer than the documentation admits. TTS: no — the honest reason is the operating system, not laziness. S2S: no — and its decomposition shows it is one missing link plus a product decision, not a checkbox.

**Naive User:** So I record an Iraqi meeting, Sada labels the speakers, and then I want to press one button and hear the summary read back in Arabic. Can I? No. Not in Arabic, not in any language. That is the most human absence in the whole product.

**Engineer:** Read-aloud is a batch job, not realtime, which helps. But Habibi-TTS is F5-family: a Python/PyTorch stack, GPU strongly preferred, no ONNX/GGUF path published as of today, model size unmeasured by us, and zero-shot means it needs reference audio. Integrating that into a Tauri app is a second runtime beside whisper.cpp. It cannot ride on the existing engine.

**Devil's Advocate:** Then why do it at all? No competitor in this table ships offline Arabic TTS either. Descript's voice features are cloud voice cloning — a different product, different ethics, different trust story. Adding TTS to a transcription tool is scope creep, and 3.10 was about removing overclaim, not adding surface. Sada's problem is not features; it is marketing of features.

**Arabic Market Strategist:** The Devil is right about priority and wrong about value. Otter's Arabic is not live yet; MacWhisper is macOS and paid; Wispr Flow and Otter are cloud; Superwhisper's notes and agents lean cloud. A fully local, diarized, Arabic meeting-intelligence tool is a moat — and read-aloud is the accessibility feature that turns that moat into a product for schools, media and low-vision users. But we do not claim it before testing it.

**Licence & Policy Guardian:** Two licence facts decide the TTS branch. First, XTTS-v2 is Coqui Public Model Licence (non-commercial), SeamlessM4T v2 is CC-BY-NC 4.0, Moshi is CC-BY-4.0 but English-only, and Qwen3-Omni cannot speak Arabic — all closed. Second, **Habibi-TTS changes the picture only partly:** its specialized Iraqi and MSA models are Apache-2.0, but the unified, SAU and UAE models are CC-BY-NC-SA-4.0 (restricted by their SADA/Mixat datasets), the code is MIT, and zero-shot voice needs reference audio that must be the user's own or explicitly licensed. So the licence route is workable, the runtime is not proven, and Piper stays dropped until its Arabic voice dataset licence is cleared.

**Devil's Advocate (second pass):** Fine — then kill the fantasy of shipping TTS in the next release. The only defensible move is a one-day falsification test with a written kill rule, exactly like the read-aloud card before. And while that runs, fix the documentation: six shipped features are invisible in both READMEs. That is free parity being thrown away.

**Truth Editor:** I checked the claim "no competitor ships it" against the sources we fetched, not against memory. It holds for the tools we examined, and we will phrase it as "none of the competitors we examined". Also: the README must keep saying read-aloud is unsupported until a test passes; no roadmap language that sounds like a promise.

**Engineer (second pass):** Agreed on docs. On burn-in: if the bundled FFmpeg has libass with Arabic shaping, burned-in Arabic subtitles is a genuinely unusual capability — half a day to check, no engine work.

**Maestro:** The Devil's strongest point is that the perceived gap is bigger than the real one. The counter is that one gap is real: no Arabic voice. So: take the free parity work today, keep read-aloud on a named test (not a roadmap promise), kill S2S, defer live captions, and spike subtitle burn-in. Record it.

---

## 6. Maestro's verdict

### 6.1 Verdict table

| # | Item | Verdict | Qiyas basis | Gate / evidence |
| --- | --- | --- | --- | --- |
| 1 | STT stays the product core | **Do (continue)** | Charter; measured Arabic quality | — |
| 2 | Read-aloud TTS (Arabic) | **Suspended-on-test** — narrowed to Habibi-TTS specialized IRQ/MSA first, Chatterbox ar fallback; OS voices and Piper closed | Card A | Native listener ≥ 4/5; shippable offline runtime; self-reference or licensed voice |
| 3 | Speech-to-speech conversation | **Drop** | Card B: no licensed Arabic speech output; different category | Revisit only if such a model ships |
| 4 | Live in-meeting captions | **Learn / defer** | Card C: engine streaming absent; Arabic realtime unmeasured | Engine streaming + Arabic realtime quality |
| 5 | Parity discoverability (docs, onboarding, READMEs, site) | **Do now** | Card E | Every claim maps to code; docs check passes |
| 6 | Arabic subtitle burn-in | **Suspended-on-test (one-day spike)** | Card D | Bundled FFmpeg libass + Arabic shaping on 5 clips |
| 7 | Arabic-target translation / AI-task copy | **Do (document + QA), no new engine** | Card F | Labelled AI translation; local Ollama path documented |
| 8 | Local meeting-notes flow (summary after auto-transcribed meeting) | **Do (polish + document)** | Existing meeting detection + AI summary | Truth-only copy; no cloud |
| 9 | Mobile apps / cloud collaboration / media editor | **Drop** | Invariants 1, 3, 7 | — |
| 10 | Dialect benchmark and a licensed Iraqi/Gulf/Levantine corpus | **Learn (owner purchase/outreach)** | The biggest honest evidence gap; best Arabic SEO asset | Corpus licence; harness extension |

### 6.2 Step Zero — the cheapest falsification tests

**Step Zero A — read-aloud (one day, no product code).** Run Habibi-TTS specialized IRQ and MSA models on 10 real Sada transcripts (60–120 words each), offline, on the reference Windows machine. Pass criteria, all required:

1. Native-listener naturalness/dialect score: mean **≥ 4/5** (two listeners if available; disagreements recorded).
2. Intelligibility: re-transcribe the synthesised audio with the app's own Whisper model; CER drift no worse than **10%** relative to the source text.
3. Runtime: realtime factor **≤ 1.0 on GPU, ≤ 3.0 on CPU**; startup ≤ 5 s; batch only.
4. Shippability: no Python at runtime (ONNX/GGUF), optional download **≤ 2 GB**, works offline after download.
5. Voice provenance: the user's own reference recording or licensed reference audio; no third-party cloning; local processing only.

Any failure keeps the no-go in force and closes TTS for this cycle with a dated record. A partial pass may keep it "Learn" with a named missing piece.

**Step Zero B — Arabic subtitle burn-in (half day).** Inspect the bundled FFmpeg build for libass/HarfBuzz/bidi support; burn five Arabic SRTs into short clips; check letter joining, RTL punctuation, diacritics, font fallback and Latin acronyms. Pass = 5/5 clips render correctly and are readable at 720p. Fail = close the feature with a dated note.

### 6.3 The solution — phased, actionable

**Phase 0 — truth parity (this week, no code, no release needed).** Fix both READMEs, the landing-page copy and onboarding so the shipped capabilities are visible: diarization (opt-in, 25 MB model, up to 4 speakers), meeting detection → record → auto-transcribe, stable timestamps, custom prompt, URL import, auto-export, CLI/MCP, translation-to-English limits, AI cleanup/summary. Every sentence must map to code. This is the only immediate change and it is pure documentation.

**Phase 1 — the two Step Zero tests (this cycle, reports only).** Execute Step Zero A and B on the reference machine; write the evidence into this repository; keep the kill rules honest. No product promises, no version bump.

**Phase 2 — ship only what passed (next feature release, after the five-user gate).** Meeting-notes polish, translation/AI copy and onboarding; add read-aloud only if Step Zero A passed and a shippable runtime exists; add burn-in only if Step Zero B passed and the UI wave is unblocked by the gate. The release vehicle is planned as v3.11.0 in [P7-PLAN.md](P7-PLAN.md).

**Phase 3 — learn tracks (4.x).** Live captions when the engine ships streaming; a licensed dialect corpus and a published benchmark; watch folders only if users ask.

**Never (council-rejected).** S2S conversation mode, mobile apps, cloud collaboration, text-based media editing, cloud AI as a default path.

### 6.4 Continue / kill metrics

| Item | Continue if | Kill/stop if |
| --- | --- | --- |
| Read-aloud | Step Zero A passes all five criteria and the runtime fits the installer story | Any criterion fails; re-check only when a GGUF/ONNX Arabic TTS exists |
| Subtitle burn-in | Step Zero B passes 5/5 clips | Shaping or bidi fails; record and close |
| Parity work | README/site claims match code and the docs check is green | Any claim without evidence is found in review |
| Meeting-notes polish | Auto-transcription + local summary is reliable on three real meetings | It needs cloud AI to be useful |
| Live captions | Engine streaming lands and Arabic realtime WER is close to batch | Engine stays batch — no fake captions |
| Dialect corpus | A commercially licensed corpus is obtained | No licence — keep the "unmeasured" caveat honest |

### 6.5 Risks and mitigations

- **Licence misread (weights vs code).** Habibi's Apache-2.0 applies to specific specialized models, not the unified model; the model catalogue rule stays mandatory (licence, size, SHA-256, timestamps). Record the exact model file tested in the Step Zero report.
- **Voice cloning misuse.** Read-aloud never clones a third party; self-reference or explicitly licensed reference only; everything stays local.
- **Quality overclaim.** "Usable in production with testing" is not a satisfied criterion; only the named pass criteria count.
- **Runtime cost.** A second inference stack is a maintenance burden; if the test passes, cost it as a separate workstream, not a hidden add-on.
- **Scope dilution.** The Devil's Advocate keeps the warning: Sada's first job is Arabic STT. New features must serve that story or be rejected.
- **Retired dependencies.** Chatterbox commercial service was retired in August 2026 although the open-source research code remains MIT; treat it as a fallback with a maintenance risk, not the primary route.

### 6.6 First action (today)

Card E only: open the parity-documentation workstream, list the six invisible capabilities, and draft the truth-only copy. No architecture decisions, no runtime work, no release.

### 6.7 Owner decisions requested

1. Authorise Step Zero A and Step Zero B (about one and a half working days, no purchase).
2. Approve the parity documentation change (docs-only commit).
3. Open the P7 milestone and FC issues when GitHub authentication is available (see [P7-PLAN.md](P7-PLAN.md) for the FC-1…FC-9 mapping).
4. The v3.10.0 tag remains the owner's decision; this council does not tag.

---

## 7. Evidence log — repository audit (2026-11-19)

| Check | Result | Source |
| --- | --- | --- |
| Diarization wired and opt-in | Pass — default false, model path passed to the queue, UI row exists, "up to 4 speakers" note | config-keys.ts, preference.tsx, use-transcribe-queue.ts, quiet-row.tsx, i18n |
| Meeting workflow wired | Pass — detection preference, auto-transcribe preference, sync in app shell, i18n prompt strings, both default false | preference.tsx, app.tsx, i18n |
| Stable timestamps | Pass — preference key + queue condition | config-keys.ts, use-transcribe-queue.ts |
| Custom prompt | Pass — Settings → Whisper options, 1,024-character limit, placeholder explaining names/jargon | whisper-options.tsx, i18n |
| URL import | Pass — yt-dlp version config and update-check keys | config-keys.ts |
| Auto-export | Pass — preference key implemented | config-keys.ts |
| MCP | Pass — stdio-only, four tools, never opens a port; the app itself takes only --mcp, while the bundled engine binary has its own CLI (transcribe/serve/pull/devices) | skill.ts, cli.rs, AGENTS.md |
| Translation | Pass but limited — Whisper translate to English, medium/large only; AI task can translate | i18n, model capabilities |
| Read-aloud / TTS | Absent — no code path, no audio output | Repository-wide search |
| Live captions | Absent — batch engine plus preview only | README feature description |
| README coverage of shipped capabilities | Fail — diarization, meetings, stable timestamps, auto-export, translation and custom prompt are missing from both READMEs | README.md, README.ar.md |
| Bundled FFmpeg Arabic shaping | Unverified — needs Step Zero B | bundled FFmpeg (GPLv3) |
| Arabic benchmark | Pass — committed harness and results; default model 19.46% WER on the 60-clip suite | README model table, benchmarks/arabic-asr |

---

## 8. Evidence log — external sources (fetched 2026-11-19)

### 8.1 Licence board for TTS/S2S candidates

| Candidate | Code licence | Weight licence | Arabic | Council verdict |
| --- | --- | --- | --- | --- |
| **Habibi-TTS** (F5-TTS family) | MIT | **Apache-2.0 for the specialized ALG, EGY, IRQ, MAR and MSA models**; unified, SAU and UAE models are CC-BY-NC-SA-4.0 (restricted by the SADA and Mixat datasets) | MSA + 11 dialects including Iraqi | **Only new viable TTS candidate** — needs runtime, size and quality test |
| **Chatterbox Multilingual v3** | MIT | MIT (open-source research; commercial TTS service retired August 2026; PerTh watermark) | Arabic listed among 21 languages + 4 dialects | Suspended fallback — GPU/PyTorch, watermark disclosure, unverified Arabic quality |
| XTTS-v2 | — | Coqui Public Model Licence (non-commercial) | Arabic | Dead for a commercial app |
| SeamlessM4T v2 | — | CC-BY-NC 4.0 (repository LICENSE) | — | Dead |
| Moshi | — | CC-BY-4.0 | English only (model card tag) | Dead for Arabic S2S |
| Qwen3-Omni | Apache-2.0 | Apache-2.0 | Speech input 19 languages including Arabic; speech output 10 languages **excluding Arabic** | Not an Arabic voice path |
| Qwen2.5-Omni | Apache-2.0 | Apache-2.0 | Speech output English and Chinese | Not an Arabic voice path |
| Piper ar_JO voice | MIT (Piper) | Voice dataset licence "see URL" — unverified | Arabic (Jordan) | Dropped until cleared |
| Windows OS voices | — | Windows licence; installed voices | No Arabic voice by default (all en-US on the evaluation host); Hoda/Naayf are optional Narrator downloads | No-go evidence stands |

### 8.2 Competitor board (public documentation, 2026-11-19)

| Tool | Offline | Arabic-first UI | Speaker labels | Meeting workflow | Read-aloud TTS | Live captions | CLI/MCP | Mobile | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Sada** | Yes | Yes | Yes, opt-in and undocumented | Yes, opt-in | No | No | Yes | No | This repository |
| Buzz | Yes | No | Yes | Partial | No | Partial (mic) | Yes (CLI) | No | OSS, speech separation, presentation window |
| MacWhisper | Yes | No | Yes (automatic speaker recognition) | Yes (meeting recording) | Unverified | No | Yes (CLI) | iOS app | Paid, macOS/iOS; watch folders, assistant |
| Superwhisper | Local transcription; AI modes provider-based | No | Unverified | Yes (meetings, summaries, share/agents) | No | Partial | Yes (CLI + MCP) | Yes | AI layer and sharing lean cloud |
| Otter | Cloud | No | Yes | Yes (notes/actions) | No | Yes | No | Yes | Arabic still in the next multilingual batch, not live |
| Descript | Cloud | No | Yes | Partial | Yes (Overdub voice) | No | No | Unverified | Text-based media editing, cloud |
| Wispr Flow | Cloud speech recognition | No | No | No | No | Partial (dictation) | Unverified | Yes | 100+ languages; not an offline tool |
| Vibe (upstream) | Yes | No | Yes | No | No | No | Yes (CLI) | Phone handoff (hidden in Sada) | Sada's MIT base |

### 8.3 Sources

- Habibi-TTS repository and licence section: <https://github.com/SWivid/Habibi-TTS> · model suite: <https://huggingface.co/SWivid/Habibi-TTS>
- Chatterbox multilingual v3 (licence, languages, watermark, August 2026 retirement note): <https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages> · model card: <https://huggingface.co/ResembleAI/chatterbox>
- XTTS-v2 licence and languages: <https://huggingface.co/coqui/XTTS-v2>
- SeamlessM4T v2 licence: <https://github.com/facebookresearch/seamless_communication/blob/main/LICENSE>
- Moshi model card: <https://huggingface.co/kyutai/moshiko-pytorch-bf16> · repository: <https://github.com/kyutai-labs/moshi>
- Qwen3-Omni speech languages: <https://github.com/QwenLM/Qwen3-Omni> · card: <https://huggingface.co/Qwen/Qwen3-Omni-30B-A3B-Instruct>
- Piper voices (MIT repository, per-voice dataset licences): <https://huggingface.co/rhasspy/piper-voices>
- Whisper translation-to-English task: <https://github.com/openai/whisper>
- Buzz: <https://github.com/chidiwilliams/buzz>
- MacWhisper documentation: <https://docs.macwhisper.com/>
- Superwhisper CLI and MCP server: <https://superwhisper.com/docs/get-started/cli>
- Otter multilingual announcement and supported languages: <https://otter.ai/blog/otter-ai-announces-its-biggest-multilingual-leap-yet-27-new-languages-and-multilingual-capabilities> · <https://help.otter.ai/hc/en-us/articles/360047247414-Supported-Languages>
- Descript: <https://www.descript.com/>
- Wispr Flow privacy (cloud speech recognition): <https://wisprflow.ai/dictation-blogs/is-wispr-flow-safe-security-and-privacy>
- Vibe upstream: <https://github.com/thewh1teagle/vibe>

---

*Council stop condition: met after three rounds — every fatal flaw was either fixed (parity documentation), dropped (S2S, mobile, cloud, editor), or suspended on a named test (TTS, burn-in, live captions). The Maestro's first action is the only thing to start today. Execution plan: [P7-PLAN.md](P7-PLAN.md).*

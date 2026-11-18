# Sada — Models, Features & Tools Council (Qiyas Council)

**Date:** 2026-11-17 · **App:** Sada 3.3.0 (fork of Vibe v3.2.2) · **Engine sidecar:** vibe-server v0.6.10 · **Mode:** C (Qiyas cards + adversarial council + Maestro verdict) · **Language:** English (the request was English; a faithful Arabic twin lives in [MODELS-COUNCIL.ar.md](MODELS-COUNCIL.ar.md))

> **The question.** Are there models, features or tools Sada should add support for — similar or complementary to what it already has — including GPU-only ones, provided Sada supplies the infrastructure and a commercial-use licence permits it? Tell the user what they may have missed, and decide it with the council.

This is a decision document, not a wish list. Every "current-world" claim below was researched or measured on this machine on 2026-11-17; every number that was not measured is marked as sourced or **unverified**. No model was invented, and nothing here is a commitment to bundle a model in the installer.

---

## 1. Method header — who sat in the room

| Role | Mandate | Signature question | Qiyas tool |
| --- | --- | --- | --- |
| **The Expert / الخبير المتخصص** | Offline multilingual ASR systems architect: engines, model families, long-term maintenance | Why did the precedent really work, and what breaks in 6–24 months? | Takhrij al-Manat |
| **The Engineer / المهندس** | Turns an accepted cause into a small, testable change in this repo | What is the precedent, and what is the cause? | Al-Far' |
| **Devil's Advocate / محامي الشيطان** | Attacks the cause, not the wording | Where does the cause break here? | Al-Qawadih |
| **The Naive User / الزبون الغبي** | Iraqi user with a five-year-old laptop, no GPU budget, no patience | What's in it for me, and why would I bother? | Tahqiq al-Manat |
| **The Maestro / المايسترو** | Silent until the stop condition; rules what survived | — | — |

Dynamic roles (seated because their dimension can kill the plan):

```
Role: The Licence & Policy Guardian / حارس الترخيص
Mandate: code licences, weight licences, commercial use, redistribution and gated models
Signature question: May we ship it, and may our users sell what they make with it?
Qiyas tool: فساد الاعتبار (invalid premise) — "open weights" is not a licence
Red line: any non-commercial, no-derivatives, research-only or unclear-terms weight

Role: The Ops & Support Lead / مسؤول التشغيل
Mandate: Windows hardware diversity, installer size, downloads, offline machines, upstream drift
Signature question: Does it still work on the machine that has no Vulkan driver and no AVX?
Qiyas tool: الفارق المؤثر (material difference) — our users are not the upstream demo machine
Red line: a default that fails silently on old hardware

Role: The Arabic Language Reviewer / المراجع اللغوي
Mandate: MSA vs Iraqi dialect, Arabic/English code-switching, punctuation, transliteration, RTL
Signature question: Would an Iraqi engineer accept this transcript as theirs?
Qiyas tool: تحقيق المناط (reality check) — a model can be "Arabic-capable" and still unusable for our mix
Red line: a model that turns GPU/SRT/VTT into Arabic transliteration with no way back
```

---

## 2. Step 0 — framing, constraints, grounding

**What "done" looks like:** a short, ordered roadmap of models/features worth adding, with the licence gate applied, the infrastructure cost stated, and the cheapest falsification test named for anything uncertain.

**Hard constraints (accepted as given):**

1. **Arabic-first** — ar-IQ UI, ar transcription, RTL, Arabic typography, no hard-coded UI strings (paraglide catalogues only).
2. **Fully offline and local** — no telemetry, no account, no cloud relay; model downloads happen only when the user asks.
3. **Windows-only installer** (NSIS, per-user), currently **43,949,601 bytes** unsigned — every bundled megabyte is paid by every user; models stay downloads.
4. **Commercial use must be permitted** for code *and* weights; CC-BY-NC and research-only are out. Gated models need their extra terms read first.
5. GPU is allowed because **the user chooses it**: the app must work on CPU only, and GPU is an opt-in acceleration, never a requirement.
6. Fork discipline: server/ is upstream code; chore setup fetches the pinned sidecar; docs and site must stay in sync.

**What was grounded (research and on-host measurement):**

- Licences read at source: OpenMDW-1.1 full text, Apache-2.0 model metadata, MIT, CC-BY-4.0 model metadata, Piper Arabic voice card (licence "see URL"), Chatterbox Multilingual V3 card.
- Engine behaviour measured with the **bundled** vibe-server v0.6.10 binary and the real FFmpeg sidecar:
  - devices → two Vulkan devices: NVIDIA Quadro RTX 4000 (Vulkan0) and Intel UHD Graphics 630 (Vulkan1); verbose transcription prints "ggml_vulkan: Found 2 Vulkan devices" and runs on the dGPU;
  - Whisper ggml-large-v3-turbo.bin (1,624,555,275 B, SHA-256 1fc70f77…e2bc69) and Nemotron 3.5 ASR Streaming 0.6B Q4_K_M (495,831,520 B, SHA-256 41c99fa5…b8fd) both load and transcribe Arabic;
  - POST /v1/models/metadata reports engine "nemotron", requires_vad true, languages including ar-AR, language_detection true, streaming false, translation false, timestamps true, text_prompts false.
- Upstream drift checked with the GitHub API: the fork is based on **v3.2.2**, upstream is at **v3.3.5**, and the pinned engine is **v0.6.10** while upstream servers are at **v0.6.16**.
- Arabic quality spot-check (4 clips: short MSA, MSA news, Iraqi dialogue, Arabic/English tech mix) against Whisper large-v3-turbo, Nemotron 3.5, and a dialectal Whisper fine-tune. Results in section 7; no WER ground truth was available, so these are qualitative plus timing, not a benchmark claim.

---

## 3. Global invariants (the Expert, stated before any branch)

1. **Timestamps are not optional.** Sada's primary outputs are SRT/VTT and timed paragraphs. A model without word/segment timestamps cannot be a default model regardless of WER; it can at most power a text-only mode.
2. **The user's disk and download budget is the real installer.** Offline-first means the app must ship a small installer and download models on demand; bundling weights multiplies installer size and drags weight licences into every redistribution.
3. **"Arabic-capable" is not "Arabic-first".** A model must survive Arabic/English code-switching and must not destroy Latin technical terms, because this app's normaliser restores acronyms such as GPU, CPU, PDF, SRT and VTT.
4. **Maintenance cost grows super-linearly with engine count.** Every new model family means a new inference runtime, a new licence review, a new downloader path, a new capability matrix and new failure modes on old Windows hardware.
5. **The fork is already behind upstream.** Models added downstream of a fork are exactly the files that make the next rebase expensive; the cheapest model strategy is the one upstream also chose.
6. **A licence gate applies to weights, not only to code.** Apache/MIT/CC-BY/OpenMDW can be shipped commercially after notice review; NC/ND/research/gated-extra-terms cannot without explicit permission.

---

## 4. Qiyas cards for the serious branches

### Card A — GPU acceleration (Vulkan) as supported infrastructure
- **Al-Far':** Sada offers GPU acceleration, documented and supported, with CPU fallback.
- **Al-Asl:** whisper.cpp's ggml Vulkan backend, which upstream Vibe already advertises (GPU on NVIDIA/AMD/Intel, Vulkan/CoreML).
- **Al-'Illa:** ggml dispatches computation to whichever backend the model was compiled with; a Vulkan build plus a runtime device list gives real acceleration without a CUDA/ROCm dependency, and falls back to CPU when no driver is usable.
- **Tanqih:** the upstream marketing text and its non-Windows targets are incidental; do **not** copy CoreML/platform claims into a Windows app.
- **Conditions:** the Vulkan loader/driver is present on the user's machine; the app can list devices and recover from out-of-memory; docs explain the CPU fallback.

### Card B — Curated, verified model catalog (the "Get models" layer)
- **Al-Far':** Sada ships one bundled catalog of recommended models with size, SHA-256, licence, publisher and per-language descriptions, installable in one click and usable fully offline.
- **Al-Asl:** upstream Vibe v3.3.3's "Get models" page and website/public/models.json — one catalog JSON with 12 entries (Whisper, ivrit.ai/Norwegian/Swedish fine-tunes, Zipformer2 Hebrew/Slovak, Parakeet v3, Nemotron 3.5), each carrying size and sha256, validated in model-catalog.ts and refreshable over HTTP while a bundled copy keeps offline machines working.
- **Al-'Illa:** a single reviewed-data catalog replaces scattered URLs and TODOs with **one reviewable truth** (licence, size, hash, language, engine capability); it makes integrity checks possible, lets a curated Arabic entry appear next to the default, and keeps the offline promise because the catalog is bundled.
- **Tanqih:** upstream's website branding, telemetry and its exact model list are incidental; do not copy them. What transfers is the *data contract* (id, licence, size, sha256, languages, description) and the install flow.
- **Conditions:** the fork must also backport the config ModelIntegrity path, download verification and the metadata gate; Arabic descriptions must be written (not machine-googled); no model is bundled in the installer.

### Card C — Nemotron 3.5 ASR Streaming 0.6B as an optional model
- **Al-Far':** users can install NVIDIA Nemotron 3.5 ASR Streaming 0.6B and use it for Arabic.
- **Al-Asl:** upstream Vibe already lists it as nemotron-3.5-asr-streaming-0.6b (OpenMDW-1.1, 495,831,520 B, 35 languages, tag dictation) and the bundled engine already implements the family.
- **Al-'Illa:** it is the only non-Whisper family in the shipped engine that advertises **segment timestamps**, **language detection**, a **0.6B footprint** and **Arabic (ar-AR)**; it therefore fits the invariants no other non-Whisper family fits today.
- **Tanqih:** "streaming" in the name does not mean Sada's dictation path can use it (the server's capability report says streaming false); do not sell it as a streaming feature. Its transliteration of Latin terms is incidental to the licence, not to our product.
- **Conditions:** VAD model installed (required), language-code plumbing (ar ↔ ar-AR), MCP adapted, and an Arabic benchmark showing it is worth a download.

### Card D — Curating Arabic Whisper fine-tunes (dialect/domain models)
- **Al-Far':** the catalog offers one or two Arabic fine-tunes (e.g. a large-v3 Arabic fine-tune, a dialectal large-v3-turbo fine-tune) as optional downloads.
- **Al-Asl:** the upstream catalog already curates language-specific Whisper fine-tunes for Hebrew (ivrit.ai), Norwegian (NB) and Swedish (KB) — same architecture, same converter, same licence review, advertised as "the most accurate choice for that language".
- **Al-'Illa:** a fine-tune is the cheapest way to beat the base model on a target domain: no new runtime, no new capability matrix, only a new file plus its licence, size and hash. The precedent's cause is *curation + verification*, not fine-tuning itself.
- **Tanqih:** upstream's exact model choices are incidental; do not assume an Arabic fine-tune is better just because it exists. Our 4-clip pilot was **inconclusive** (see section 7): the dialectal model added punctuation and caught "هلا" but wrote "شرائي كم" and transliterated GPU/SRT/VTT, while base turbo kept the Latin acronyms.
- **Conditions:** a WER/readability benchmark against base turbo, Apache/MIT licence on the *actual* ggml artifact, verified hash, and the model must keep timestamps.

### Card E — A second engine (Qwen3-ASR, Cohere Arabic, transcribe.cpp)
- **Al-Far':** Sada supports a future Arabic-focused model family (Qwen3-ASR 0.6B/1.7B, Cohere Transcribe Arabic) through a second ggml runtime.
- **Al-Asl:** upstream Vibe's own precedent: when a language needs something whisper.cpp cannot do, they add a *family-specific Rust crate* behind the existing engine interface (Parakeet, Nemotron, Zipformer2), not a generic Python stack. The independent transcribe.cpp project (MIT, 2,185 stars, Windows CPU+Vulkan binaries) now ports 16+ families including Qwen3-ASR and Cohere Transcribe, with GGUFs for both.
- **Al-'Illa:** model architecture and quality are family-specific; a generic runtime is the only way to add parallel model families without exploding maintenance. The cause is *one interface, many eager-language runtimes*, not "a second engine is cool".
- **Tanqih:** the runtime choice (Rust crate vs external transcribe.cpp process) is incidental; do not import a Python dependency or a second GPU stack.
- **Conditions:** the family must expose timestamps and VAD, or Sada must build alignment/chunking; Cohere Arabic requires reading the upstream gate/terms first (its HF card is gated even though its metadata tag says Apache-2.0); Qwen3-ASR in transcribe.cpp today reports **no timestamps, no VAD, no streaming** — so it cannot replace the default.
- **Decision until tested:** Learn / Suspended-on-test. The correct next experiment is a one-day transcribe-cli spike on our Arabic clips, not a new crate.

### Card F — Read-aloud (text-to-speech)
- **Al-Far':** Sada reads transcripts/notes aloud, optionally with a cloned voice.
- **Al-Asl:** Windows' own speech synthesis (SAPI/OneCore voices) is the precedent every note app uses: zero model download, system-local, commercial OS licence, no GPU.
- **Al-'Illa:** the value of read-aloud comes from *availability*, not from model novelty; a system voice is already installed on the user's machine and therefore costs no download, no GPU and no weight licence.
- **Tanqih:** "neural TTS quality" is incidental to MVP value; cloning and emotional voices are not needed to satisfy read-aloud.
- **Conditions:** at least one acceptable Arabic voice installed/enabled; and the product must not require cloning. Chatterbox Multilingual V3 (MIT, 500M, 23 languages including ar, watermarking, GPU/PyTorch) remains a **Suspended-on-test** experiment if OS voices are judged too robotic. Piper Arabic ar_JO-kareem is **Dropped** for now: the voice card's dataset licence says only "See URL" — unverified for commercial redistribution.

### Card G — Local LLM features (summaries, cleanup, translation)
- **Al-Far':** Arabic summaries/translation run on a local LLM.
- **Al-Asl:** Sada already ships the hard part: Settings → AI supports **Ollama** and an OpenAI-compatible endpoint with a custom base URL, plus Claude. The use-summaries hook and prompt template already call it.
- **Al-'Illa:** local summarisation is a *model the user brings*, not a model Sada ships; the infrastructure exists, the missing piece is an Arabic-first setup guide and licence-vetted recommendations (e.g. Apache-2.0 Qwen models for Ollama), not new code.
- **Tanqih:** do not bundle an LLM; do not run a second inference runtime when Ollama is already the integration point.
- **Conditions:** a local endpoint the user installs themselves; documentation that names the licence of each recommended model.

---

## 5. Transcript (live, survived rounds)

**Expert (opening invariants):** Before anyone proposes a model, hear the rule. Timestamps decide defaults; licences decide existence; disk decides convenience; and every new family buys a new runtime. Also, the fork is behind upstream — the catalog and engine work already exist upstream, and a downstream rebuild is the most expensive way to get them.

**Engineer:** Then the plan is three moves. One — adopt upstream's catalogue instead of building our own: bundle models.json, backport the Get models screen, and add a curated Arabic entry. Two — upgrade the pinned engine from v0.6.10 to v0.6.16, which brings Vulkan crash fixes, Nemotron-3 diarization, sentence/paragraph reconstruction and non-AVX CPU support. Three — add Nemotron 3.5 as a second recommended model, with Arabic ar-AR.

**Licence Guardian (فساد الاعتبار):** Stop at move three. "Upstream lists it" is not a licence opinion. OpenMDW-1.1 says what? Let me read it: permission "free of charge, to deal in the Model Materials without restriction", outputs unrestricted, obligations only to keep the agreement and notices when *distributing the model materials*. Fine — commercial use is permitted. But your second-engine card names Cohere Arabic whose upstream card is **gated**; a gate can carry terms beyond the metadata tag. And Chatterbox is MIT *code*; its cloned voices are a separate ethical and legal minefield. So: OpenMDW accepted for Nemotron; Cohere suspended until the gate terms are read; cloning dropped.

**Arabic Language Reviewer (تحقيق المناط):** I ran the actual clips; this is where the plan must change. Nemotron is not a drop-in replacement for turbo. It **transliterates** technical terms: "GPU" became "الجيبيو", "SRT/VTT" became "السورتي وفي تي تي", "PDF" became "بيديف" — and Sada's whole Arabic normaliser exists to *restore* GPU/CPU/PDF/SRT/VTT as Latin. It also gave "قبل من شغل نموذج" where turbo gave "قبل ما نشغل النموذج". Its punctuation is nicer, and it kept "أسبوعا" as MSA. Meanwhile the dialectal Whisper fine-tune wrote "شرائي كم" for "شرأيكم" and "الجي بيو" for GPU. Conclusion: none of these is a new Arabic default today; turbo stays. Nemotron competes on size, startup and punctuation, not on our code-switching.

**Naive User (تحقيق المناط):** My laptop does not have a Vulkan driver and it is not new. You are telling me to download 496 MB to get worse technical words, while the app already works. And why is there a "Get models" page in upstream and not here? I open Settings → Models and see a URL box. That is not a feature; that is a homework assignment.

**Ops Lead (الفارق المؤثر):** Upstream's machines are not ours. v3.3.4 fixed "illegal instruction" crashes on CPUs without AVX — Pentium and Celeron hardware that is exactly the kind of machine an Arabic-first app should support. v0.6.16 fixed "crashes on large files and Vulkan errors" — the exact failure class a GPU toggle creates. If we ship a GPU story without that engine, we own the crashes. The engine bump is not optional if we talk about GPU support.

**Engineer (revises):** I revise. Move three becomes "curate Nemotron as an optional entry, *after* the benchmark" — not a recommended default, and not before VAD/MCP/language plumbing is tested. Move two stays first and becomes this release's spine: bump the sidecar, port the config changes (new diarization filename nemotron-3-diarization-Q8_0.gguf, legacy filename migration, integrity values), then run the Arabic set through the new engine before publishing. Move one stays: catalogue, but backported and bundled, with Arabic descriptions and verified hashes; it also closes the modelUrls integrity TODO (the hashes were verified against the published artifacts today).

**Devil's Advocate (النقض + الأثر الثاني):** Two counter-cases. First: upstream's catalog is only worth something if its models are *safe to install*. The catalog's own validation drops entries with malformed hashes — good — but our fork's model list is manual. If we add a catalog and someone adds a model without a hash, we have rebuilt the problem with extra UI. Rule: **no entry without size + SHA-256 + licence + timestamps**. Second: if we backport the model catalog and the engine, we are halfway to rebasing on v3.3.5; six months from now the divergence will be too expensive to close. Decide now: **incremental rebase as a planned release**, not endless cherry-picks. The counter-case to "Qwen3-ASR is the future" is that two of the three Arabic-specific families we found (Qwen3-ASR, Cohere Arabic) have **no timestamps** in the available ggml runtime, so they cannot even compete for default.

**Expert (الأثر الثاني):** The second-order effect of a curated Arabic catalog is that Sada becomes the place where *Arabic ASR model quality is reviewed* — that is a real moat, and it is cheap because curation is docs + data, not engineering. The second-order effect of a second engine is the opposite: it is a permanent tax. So: curate first, engine later, and only when the family provides timestamps.

**Naive User:** Fine. But if I click "Get models", I want the Arabic models first, their sizes, and one button. Not 12 English descriptions and a licence I cannot read.

**Maestro:** The stop condition is met: every fatal flaw is either fixed (Nemotron downgraded, engine first, catalogue rules) or suspended on a named test (Arabic fine-tunes, Qwen3/Cohere engine, TTS). Nothing else is added to the room.

---

## 6. Maestro's verdict

| Branch | Verdict | Asl (precedent) | 'Illa (cause) | Constraint the objections imposed |
| --- | --- | --- | --- | --- |
| GPU/Vulkan acceleration as infrastructure | **Survived — already shipped, undocumented** | whisper.cpp Vulkan backend; upstream Vibe GPU support | ggml dispatches to a statically linked Vulkan backend with runtime fallback to CPU | Documentation must cover driver/loader absence, device choice, OOM fallback; no new GPU dependency |
| Curated, verified model catalog (bundled + optional refresh) | **Survived — highest value / lowest risk** | Vibe v3.3.3 "Get models" + models.json | one reviewable catalog = licence + size + hash + language + engine capability in one place; works offline when bundled | no entry without size/SHA-256/licence/timestamps; Arabic descriptions; keep installer small |
| Engine pin v0.6.10 → v0.6.16 | **Survived — do first** | upstream server releases v0.6.11–v0.6.16 | fixes Vulkan/large-file crashes, adds non-AVX CPU build, sentence reconstruction, Nemotron-3 diarization | licence review of OpenMDW-1.1 diarization, config migration for old diarization file, full Arabic smoke test |
| Nemotron 3.5 ASR 0.6B as optional model | **Downgraded from default → optional after benchmark** | Vibe catalog entry; bundled engine family | only non-Whisper family with timestamps + Arabic + 0.6B footprint | transliteration of Latin terms, slower GPU throughput, VAD required, MCP/language plumbing, streaming false in app |
| Arabic Whisper fine-tunes in the catalog | **Suspended-on-test** | ivrit.ai/NB/KB curated fine-tunes in Vibe catalog | curation + verification is the transferable cause; fine-tuning is not automatically an improvement | needs WER/readability benchmark over MSA + Iraqi + code-switch; our 4-clip pilot was inconclusive |
| Qwen3-ASR / Cohere Arabic via a second engine | **Suspended-on-test / Learn** | Vibe adds family crates; transcribe.cpp (MIT) ports 16+ families | one interface, many families; generic runtime avoids per-family app code | no timestamps/VAD in current ports; Cohere gate terms unread; start with a one-day CLI spike |
| Read-aloud TTS | **Suspended-on-test (OS voices first)**; Chatterbox optional; Piper/clones dropped | Windows system speech synthesis | availability beats model novelty; zero download and no weight licence | Arabic voice availability/quality must be checked; cloning dropped on ethics/licence; verify Microsoft speech terms |
| Local LLM summaries/translation | **Survived — already present; document it** | Sada's existing Ollama/OpenAI-compatible settings | user brings the model; app supplies the offline integration | document Arabic-capable local models and their licences; bundle nothing |
| Parakeet v3 / Voxtral Mini | **Dropped** | — | licence-clean but **no Arabic** — a false friend for an Arabic-first app | — |
| Bundling any model in the installer | **Dropped** | — | installer size and weight-redistribution obligations | models remain user-initiated downloads |
| MCP GGUF-aware transcription; language reconciliation on model switch; Arabic models docs; GPU docs | **Survived — infrastructure fixes** | upstream's capability-based model UI | the engine already reports capabilities; the shell must consume them instead of assuming Whisper | no new UI strings beyond catalogue keys; keep ar-IQ complete |

### Step Zero — the cheapest falsification tests

**E1 — engine-bump smoke test (can kill the whole plan; run first, one afternoon).**
Download the upstream server-v0.6.16 windows-amd64-with-ffmpeg sidecar, point the app at it, then run our Arabic set (short MSA, MSA news, Iraqi dialogue, tech mix) and:

1. transcription output must be equal-quality to v0.6.10 (spot-check text + timestamps);
2. SRT/VTT export must still produce timed segments;
3. diarization must work after the filename migration (old diar_streaming_sortformer_4spk-v2.q8_0.gguf must not be required);
4. CPU-only path must work with the GPU device unset/CPU;
5. no new hard-coded strings, no change to ar-IQ defaults.

Decision table: **all pass** → ship engine bump as v3.3.1; **any Arabic regression** → keep v0.6.10 and park the catalog work until the regression is understood; **Vulkan-only crash** → document and block GPU docs until fixed.

**E2 — Arabic ASR benchmark harness (kills or promotes curated models).**
Build benchmarks/arabic-asr/ (script + manifest, no app code): 40–60 clips across MSA, Iraqi, Gulf/Levantine, and Arabic/English technical speech, each with a reference transcript; normalise Arabic (punctuation, alef/hamza forms, alef maqsura, tatweel) and score WER/CER. Compare: whisper large-v3-turbo (baseline), Nemotron 3.5, two Arabic Whisper fine-tunes (Byne large-v3-arabic, oddadmix turbo dialectal v2), optionally Qwen3-ASR 0.6B via transcribe.cpp.

Decision table: a challenger is curated **only if** it beats turbo by ≥1.0 pp WER on its target slice **and** keeps timestamps **and** preserves ≥90% of Latin technical acronyms; otherwise it stays a documented experiment. Nemotron gets an optional catalog entry if it wins the dictation slice (latency/size/punctuation), regardless of WER.

**E3 — OS voice read-aloud test (cheap, optional).** Enumerate installed Windows voices for Arabic, speak a 200-word Arabic transcript, record the quality verdict; if no acceptable Arabic voice is present, read-aloud is dropped without writing code.

### The solution — phased, actionable

**P0 — engine + integrity spine (this week).**
- Bump .server-version to v0.6.16; run E1; update desktop/src/lib/config.ts for the new diarization filename/URL/integrity and the legacy filename migration (upstream v3.3.5 shows the exact values).
- Ship the verified hash work already done in this round: modelUrls now carries size + SHA-256 for the two default Hugging Face mirrors and the Hebrew ivrit model; the GitHub fallback stays unverified by design.
- Add a short GPU/Vulkan section to README.md / README.ar.md and docs/BUILDING.md: device picker, CPU fallback, vulkan-1.dll/driver install path, OOM behaviour, what "auto" means.
- Release as **v3.3.1** (patch), notes in docs/releases/v3.3.1.md.

**P1 — model catalog backport (next two weeks).**
- Port upstream model-catalog.ts + model-catalog-source.ts + sections/model-catalog.tsx + use-model-catalog.ts + model-install.ts with a bundled models.json, Arabic descriptions for every entry, and strict normalisation (no entry without licence/size/hash/languages).
- Curated Arabic entries: whisper-large-v3-turbo (verified hash), whisper-tiny (fast machines), whisper-large-v3-turbo-he (already in the fork), and **only after E2** one Arabic fine-tune and nemotron-3.5-asr-streaming-0.6b.
- Localise the catalog UI in i18n/desktop/ar-IQ.json and the other catalogues; keep ar-IQ at 100% keys.

**P2 — capability plumbing and docs.**
- MCP: read POST /v1/models/metadata before building the engine command; pass --vad-model when requires_vad, map the configured language to the model's advertised codes (ar → ar-AR when that is the only match; auto when language_detection), and drop --translate/--prompt when unsupported. Update the tool description from "configured Whisper model" to "the configured model".
- UI: when modelMetadata changes, reconcile the selected language against capabilities.languages (nearest match, else auto if detection, else first language) so switching between Whisper and GGUF engines never leaves an invalid code; add a model-install gate for VAD on every path, not only setup.
- Docs: add Arabic models documentation (i18n/docs/ar/models.md or the fork's Arabic docs page) and mirror it in docs/ so the models link is Arabic-first; document local Ollama summaries and their model licences.
- Security follow-up from the previous council: bind local HTTP endpoints with Host/Origin checks (upstream v0.6.16 hardens the webview/downloads; verify ours).

**P3 — evaluated experiments (do not start before P0/P1).**
- Arabic fine-tune curation and Nemotron promotion via E2.
- transcribe.cpp one-day spike: Windows CPU+Vulkan CLI (18 MB) + Qwen3-ASR 0.6B Q8_0 (850 MB) on our Arabic set; then Cohere Arabic Q8_0 (2.41 GB) if the gate terms allow. Only if timestamps are solved does a second engine become a project.
- TTS: E3 OS voices; Chatterbox only if users ask and OS voices fail.
- Watch upstream: if Vibe adopts a model family we need, the cheapest path stays rebase.

### Continue / kill metrics

| Decision | Continue if | Kill/suspend if | Decide by |
| --- | --- | --- | --- |
| Engine bump | E1 all pass | Arabic regression or export break | 2026-11-24 |
| Catalog backport | 1-click install works offline; hashes verified; ar-IQ 100% | new UI strings force incomplete locales, or conflict snowball | 2026-12-01 |
| Nemotron optional entry | wins dictation slice (latency/size/punctuation) and VAD/MCP paths pass | transliteration/quality judged unacceptable by Arabic reviewer | 2026-12-08 |
| Arabic fine-tunes | ≥1.0 pp WER win on target slice, Latin acronyms ≥90% | no measurable win or licence/hash missing | 2026-12-15 |
| Second engine | a family with timestamps + VAD beats turbo on Arabic | no timestamped port; maintenance cost > value | 2027-01 |
| Read-aloud | acceptable Arabic OS voice exists | no Arabic voice or quality fails | 2026-12-01 |

### Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Weight licence misread (OpenMDW, gated Cohere, unclear Piper voice) | licence column in catalog is mandatory; gated cards read first; Piper dropped until cleared |
| Upstream drift makes future rebases unaffordable | plan an incremental rebase to v3.3.5 as a release, not ad-hoc cherry-picks; keep a patch ledger in docs/UPSTREAM-PATCHES.md |
| GPU crashes on machines without Vulkan/with broken drivers | engine v0.6.16 crash fixes; CPU fallback documented and tested; OOM reload path already exists |
| Old CPUs without AVX | engine v0.6.16 SSE4.2 build + automatic step-down; document it as a supported path |
| Arabic technical terms transliterated by Nemotron | post-processing glossary/term restoration (future) and default stays turbo; benchmark includes acronym preservation |
| Installer bloat | catalog downloads only; no weight in the NSIS package |
| Voice cloning misuse | read-aloud without cloning; if Chatterbox is ever shipped, keep its watermark and disclose it |
| Download failures/integrity | size + SHA-256 for every catalog entry; mirrors fall back only when unverified by design |
| Fork UI regressions | ar-IQ completeness test + existing 132 vitest tests + cargo tests stay green |

### First action (today)

1. Bump .server-version to v0.6.16, run E1 (the one-afternoon smoke test), and only then announce GPU support as supported rather than incidental.
2. In parallel, write the Arabic benchmark manifest (E2) — even 20 reference clips are enough to make the Nemotron/fine-tune decision honestly.

---

## 7. Evidence log (measured on this host, 2026-11-17)

Hardware: Intel UHD 630 iGPU + NVIDIA Quadro RTX 4000 (Vulkan0, driver present). Engine: bundled vibe-server v0.6.10; FFmpeg 9.0.1 sidecar. Audio: four 13–14 s clips (short MSA, MSA news, Iraqi dialogue, Arabic/English tech mix).

| Model | Loads | Runs on GPU | Arabic output quality (spot check) | Time (38 s combined audio, incl. load) | Size |
| --- | --- | --- | --- | --- | --- |
| Whisper large-v3-turbo (MIT) | yes | yes (Vulkan) | best on code-switching; keeps GPU, SRT, VTT in Latin; no sentence punctuation | 4.89 s (~12.5× realtime) | 1.62 GB |
| Nemotron 3.5 ASR Streaming 0.6B Q4_K_M (OpenMDW-1.1) | yes | yes (Vulkan) | good MSA; adds punctuation; transliterates technical terms (الجيبيو، السورتي، بيديف) | 8.51 s (~5× realtime) | 496 MB |
| Dialectal Whisper large-v3-turbo v2 q5_0 (Apache-2.0) | yes | yes (Vulkan) | adds punctuation; catches هلا; misses شرأيكم; transliterates GPU/SRT/VTT | ~2.0–2.5 s per 13 s clip | 574 MB |

Representative transcript excerpts (MSA news clip):

- **Turbo:** …ثم نرفع تقارير BDF إلى الإدارة قبل نهاية الشهر
- **Nemotron:** …ثم نرفع تقارير بيديف إلى الإدارة قبل نهاية الشهر.
- **Dialectal fine-tune:** …ثم نرفع تقارير بي دي إف إلى الإدارة قبل نهاية الشهر.

Representative excerpt (Iraqi dialogue):

- **Turbo:** هل لا؟ شلونك؟ هذا اجتماع اليوم شرأيكم نأجل الإطلاق أسبوعاً…
- **Nemotron:** هل شلونوك هذا اجتماع اليوم شرأيكم نأجل الإطلاق أسبوع…
- **Dialectal fine-tune:** هلا، شلونوك. هذا اجتماع اليومي، شرائي كم نأجل الإطلاق أسبوعا…

Licence table for the candidates that were checked:

| Candidate | Code licence | Weights licence | Commercial use | Arabic | Verdict |
| --- | --- | --- | --- | --- | --- |
| Whisper large-v3-turbo | MIT (whisper.cpp) | MIT (OpenAI weights) | yes | yes (~99 languages) | current default |
| Nemotron 3.5 ASR Streaming 0.6B | upstream engine MIT; family crate in server/ | **OpenMDW-1.1** — permission without restriction, outputs unrestricted, keep notice when redistributing the model | yes | yes (ar-AR) | optional after benchmark |
| Parakeet TDT 0.6B v3 | MIT engine | CC-BY-4.0 | yes | **no** | dropped for Arabic |
| Voxtral Mini 3B | Apache-2.0 | Apache-2.0 | yes | **no** | dropped for Arabic |
| Qwen3-ASR 0.6B/1.7B | Apache-2.0 (weights); transcribe.cpp MIT | Apache-2.0 | yes | yes (30 langs) | suspended: no timestamps/VAD in port |
| Cohere Transcribe Arabic 07-2026 | transcribe.cpp MIT | metadata says Apache-2.0 but upstream card is **gated** | verify gate terms | Arabic + English, FLEURS ar WER 11.06% (Q8_0) | suspended: gate + no timestamps |
| Chatterbox Multilingual V3 | MIT | MIT | yes | 23 langs including ar | suspended: GPU/PyTorch, watermark, quality unverified |
| Piper Arabic ar_JO-kareem | MIT (Piper) | voice dataset licence "See URL" — **unverified** | unverified | Arabic (Jordan) | dropped until licence cleared |
| Windows OS voices (SAPI/OneCore) | OS | OS | governed by Windows licence (verify speech terms) | depends on installed voices | read-aloud experiment |

Upstream delta relevant to this council (all verified via the GitHub API on 2026-11-17):

| Upstream | What changed | Why it matters to Sada |
| --- | --- | --- |
| app v3.3.1 | repeated-line retry, first-word fix for Parakeet/Nemotron, start-step progress | directly affects GGUF engines if we promote them |
| app v3.3.2 | **sentences/paragraphs view**, per-word timings, exports follow the view, long files start ~5× sooner | Arabic readability and long-meeting UX |
| app v3.3.3 | **Get models** + models website (catalog with size/hash/licence), Zipformer2 66M Hebrew | the catalog infrastructure this fork lacks |
| app v3.3.4 | **non-AVX CPU support** with automatic step-down + SSE4.2 setting, Zipformer2 Slovak | old-hardware support for Arabic markets |
| app v3.3.5 | Linux packaging fixes only | no Windows impact |
| server v0.6.11 | repeated-window retry, temp default, Parakeet/Nemotron fixes, **Nemotron-3 diarization** replaces Sortformer | diarization and GGUF quality |
| server v0.6.13–v0.6.14 | sentence/paragraph reconstruction from word timings; **models page/engine for Zipformer2**; long files start sooner | transcript quality, engine families |
| server v0.6.15–v0.6.16 | SSE4.2 CPU backend; **Vulkan/large-file crash fixes**, download/webview/yt-dlp hardening | GPU reliability and security |

Sources: [Vibe releases](https://github.com/thewh1teagle/vibe/releases) · [Vibe model catalog JSON](https://github.com/thewh1teagle/vibe/blob/v3.3.5/website/public/models.json) · [Nemotron 3.5 model card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b) · [OpenMDW-1.1 text](https://github.com/OpenMDW/OpenMDW/blob/main/1.1/LICENSE.OpenMDW-1.1) · [Qwen3-ASR](https://huggingface.co/Qwen/Qwen3-ASR-1.7B) · [transcribe.cpp](https://github.com/handy-computer/transcribe.cpp) · [Cohere Transcribe Arabic](https://huggingface.co/CohereLabs/cohere-transcribe-arabic-07-2026) · [Chatterbox Multilingual V3](https://huggingface.co/ResembleAI/chatterbox) · [Piper voices (ar_JO)](https://huggingface.co/rhasspy/piper-voices/blob/main/ar/ar_JO/kareem/medium/MODEL_CARD)

## 8. Benchmark evidence and rulings (measured on this host, 2026-11-18)

Milestone v3.5.0 replaced the four-clip spot check with a pinned 60-clip corpus: 30 MSA
(Common Voice 18 Arabic, CC0), 10 Latin-mixed (Common Voice rows whose reference text carries Latin
proper nouns) and 20 Egyptian (FLEURS `ar_eg` test, CC BY 4.0). Engine: bundled
`vibe-server v0.6.16-sada.1` on Vulkan (same RTX 4000 host). Full tables, licences, hashes and
reproduction commands: [docs/MODELS-DECISIONS.md](MODELS-DECISIONS.md); raw artefacts under
`benchmarks/arabic-asr/results/results-2026-11-18.*`.

| Model | WER % overall | MSA | Egyptian | Latin-mixed | Latin names kept % | Timestamps % | RTF | Ruling |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| whisper-large-v3-turbo | 19.46 | 22.09 | 11.03 | 48.96 | 25.0 | 100 | 0.35 | default stays |
| nemotron-3.5-asr-streaming-0.6b-q4-k-m | **17.12** | **17.83** | **9.11** | 50.00 | 0.0 | 100 | **0.234** | curated as optional catalogue entry |
| whisper-large-v3-turbo-arabic-dialectal-v2-q5 | 23.09 | 23.64 | 14.39 | 59.38 | 0.0 | 100 | 0.265 | rejected |
| whisper-tiny | 70.56 | 72.09 | 64.03 | 94.79 | 0.0 | 100 | 0.186 | low-resource fallback only |

Second-engine spike (transcribe.cpp v0.4.2, Qwen3-ASR 0.6B Q8_0, CPU): WER 24.38 % overall,
MSA 20.54 %, Egyptian 21.10 %, Latin-mixed 48.96 %, Latin names 10 %, **no timestamps**, no VAD.
It is close on MSA and loses 10 pp on Egyptian, and the missing timestamps break SRT/VTT/editing,
so it is not integrated; Cohere Transcribe Arabic is gated upstream and also timestamp-free.

Rulings of the council, now closed with evidence:

1. **Turbo stays the default** — best overall WER, 100 % timestamps, best Latin-term preservation.
2. **Nemotron is promoted to an optional curated entry** on the strength of the MSA/Egyptian
   dictation slices (≥1.0 pp rule met: +4.26 pp, +1.92 pp), 100 % timestamps, faster RTF and 496 MB.
   It transliterates Latin technical terms (0 % Latin names kept vs 25 %), so it is never the
   default; the ≥90 % acronym gate is recorded as **not applicable** (no acronym-bearing
   commercial corpus exists yet), not as passed, and the catalogue description says so.
3. **Arabic Whisper fine-tunes stay rejected** until one wins a measured slice by ≥1.0 pp with
   terms intact.
4. **Read-aloud stays no-go** — evidence in [docs/READ-ALOUD.md](READ-ALOUD.md).
5. **Second engine stays suspended**; revisit only if a port lands word timestamps + VAD (or a
   commercial-use technical/dialect corpus changes the scorecard).
6. **Still unmeasured:** Iraqi, Gulf, Levantine and Arabic/English technical speech (no
   commercial-use-permissive corpus found; research-only corpora are excluded by fork policy).
   `latin-mixed` is the declared proxy; extending `manifest.json` is the retest path.

---

*Council stop condition: met after three rounds — every fatal flaw was fixed, dropped, downgraded, or suspended on the named tests above. The Maestro's first action is the only thing to start today.*

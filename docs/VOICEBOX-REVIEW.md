# Voicebox vs Sada — Qiyas Council review

**Method:** Qiyas Council, Mode C (merged: causal analogy + adversarial council + Maestro ruling).
**Date:** 16 November 2026 (Asia/Baghdad) · **Request language:** English, with the Arabic role
names kept because the governing constraint is Arabic-first.
**Governing constraint:** Sada is an Arabic-first, offline, local-only Windows transcription app.
Its invariants are not negotiable: Arabic/RTL defaults on a fresh profile, no telemetry, no
updater, no account, no phone relay, MIT licensing, and no hard-coded UI strings (paraglide
catalogues only).

**Sources reviewed**

- Voicebox — <https://voicebox.sh/> and <https://github.com/jamiepine/voicebox>, MIT, source
  reviewed at commit **8af7efe62fab8d33e2a5dfbedabaa45f68a5184f** (README, RESPONSIBLE_USE,
  PROJECT_STATUS, backend registry, docs for MCP and model plans, issue tracker).
- Sada — this repository at v3.2.2 plus the work in v3.3.0: app shell, engine sidecar, local HTTP
  API, agent skill, transcript store, Arabic normaliser.

## Council roles

| Role (Arabic) | Seat | Reads the question as |
| --- | --- | --- |
| المفتي (the one who rules) | Maestro | Which candidate preserves the governing constraint and earns its upkeep. |
| الناقد (the critic) | Red team | Assume the feature is a trap until evidence says otherwise. |
| المحقق (the verifier) | Evidence clerk | Every claim needs a file, a line, a licence or a reproduced behaviour. |
| المعماري (the architect) | Systems | What does this cost in Rust, CI, install size and maintenance? |
| المالك (the owner) | Product | Who is the user, what do they get, what do we stop doing to pay for it? |
| الأخلاقي (the ethicist) | Licence and harm | Consent, cloning, model licences, dataset provenance. |
| المستخدم العربي (the Arabic user) | Arabic-first seat | Does this make Arabic better, or just add features around it? |

**Objection tools used in the transcript:** النقض (rebuttal), الفارق المؤثر (the effective
difference), عدم التأثير (irrelevance), فساد الاعتبار (invalid premise), تحقيق المناط (verification
that the ratio actually applies), الأثر الثاني (second-order effect).

## Evidence base

### Voicebox (the al-asl, origin of the comparison)

- MIT, Tauri + React/TypeScript shell, Python FastAPI backend packaged with PyInstaller.
- Feature surface: 8 local TTS engines, 23 languages, voice cloning, audio effects, a Stories
  editor, Captures (audio history), dictation pill, LLM refinement/personas, MCP server
  (FastMCP over HTTP plus a stdio package), local REST API on 127.0.0.1:17493.
- Scale: about 60.7k GitHub stars and 1.3M downloads observed at review time; 402 open issues and
  88 open pull requests — a very fast-moving, very loaded project.
- Arabic reaches it only through specific engines: Chatterbox Multilingual, TADA 3B, OmniVoice.
  Qwen3-TTS, LuxTTS, Turbo and Kokoro have no Arabic. OmniVoice weights are CC-BY-NC and therefore
  cannot ship in a permissively licensed app.
- Known rough edges that map to lessons: Windows paste is still on the roadmap (Sada does it);
  the UI is English-only; engine/gpu/platform gating has gaps; PR #603 shows LLM refinement
  translating non-English input to English by default (an Arabic-first app cannot inherit that
  default); issue #778 reports the local API being reachable through DNS rebinding / a forged Host
  header; the $VOICEBOX token episode is a reminder that agent-tooling hype can outrun the product.

### Sada (the candidate landscape)

- Already has, before v3.3.0: a local HTTP API with a per-run port (off by default, base URL pinned
  in the config while running), a Swagger page, an installed agent skill for Claude Code and Codex,
  an engine CLI that forwards to the bundled vibe-server, and transcripts stored as readable files.
- In other words: Sada already lets agents transcribe and read. The gap was not "agents cannot
  reach Sada"; it was "reaching Sada required a live port or a pile of CLI flags".
- Arabic-first is already implemented three times over: UI/RTL, transcription defaults, and an
  Arabic normaliser applied to live, saved, exported and phone-handoff text.

## Qiyas cards

| Candidate (al-far') | Origin (al-asl) | Ratio (al-'illa) | Conditions checked | Ruling |
| --- | --- | --- | --- | --- |
| stdio MCP server in Sada.exe | Voicebox MCP + Sada HTTP API + engine CLI | An agent tool should remove a setup step, not add one; stdio removes the port/toggle/stale-URL failure class | Engine and model already resolved locally; protocol is a small subset; no secrets needed; Arabic defaults exist | **Survived** — shipped |
| Rename agent skill folder to sada and document MCP | Voicebox agent-first documentation | Agents discover tools by name and instructions; a skill that says vibe inside Sada is a dead end | Frontmatter and folder are ours to change; no upstream dependency | **Survived** — shipped |
| Eight TTS engines | Voicebox breadth | Breadth is only a ratio if Arabic quality and licence per engine hold | Arabic only via 2-3 engines, one non-commercial; GPU/weights/install size explode; maintenance is the real cost | **Dropped** (re-open only on test) |
| Voice cloning | Voicebox signature feature | Useful for content creators; dangerous for consent and impersonation | RESPONSIBLE_USE exists upstream, but an Arabic-first fork would wear the harm; no Arabic-quality evidence | **Dropped** |
| Effects / audio processing chain | Voicebox | Polish for TTS output; Sada has no TTS output to polish | None | **Dropped** (irrelevant) |
| Stories editor | Voicebox | Long-form assembly is a different product with its own editor and state model | Would duplicate the project's scope shift; Arabic handling unproven | **Dropped** |
| Captures / audio history | Voicebox | Users want to find past audio and text again | Sada's saved transcript projects already store a copy of the audio next to the text; the ratio is satisfied | **Already present** (learn: keep the audio copy) |
| Dictation pill | Voicebox | Feedback during dictation builds trust | Sada ships a dictation indicator pill already | **Already present** |
| Per-app voice binding | Voicebox | Different apps want different voices | No voices to bind | **Suspended** (depends on TTS) |
| LLM refinement on by default, local models built in | Voicebox personas/refinement | Better prose than raw ASR | Sada already has optional summaries with the user's own key, off by default; auto-refinement risks the #603 translation trap; downloading local LLMs conflicts with install size and offline expectations | **Downgraded** — documented as optional summaries, never a default |
| Model/engine management UX (download progress, gating, integrity) | Voicebox | Downloads fail; integrity and disk pressure are real | Sada already has model catalog, download progress, cancellation, hash checks | **Learn / keep** |
| Windows paste reliability | Voicebox roadmap | Dictation is worthless if paste drops characters | Sada already pastes through the OS input path with a clipboard fallback | **Already present** (Voicebox's gap, not ours) |
| Local API host/origin validation | Voicebox issue #778 | A loopback HTTP API can still be reached by a malicious page through DNS rebinding if Host/Origin are not validated | Needs an audit of Sada's API router; per-run token exists but Host/Origin checks are the missing ratio | **Learn / follow-up** (security hardening task, not this phase) |
| English-first UI with i18n as an afterthought | Voicebox | English-first keeps velocity but loses the Arabic user | Sada's constraint forbids this path | **Avoid** (invalid for this fork) |
| Token/gamification on the agent tool | $VOICEBOX episode | Hype substitutes for product | Nothing to copy | **Avoid** |

## Council transcript (condensed, four rounds)

**Round 1 — what is Voicebox actually?**
The verifier established that Voicebox is not "the AI voice app"; it is an engine-collection plus
editor product whose most transferable asset for Sada is its **agent interface** (MCP and REST) and
its **install-time ergonomics**, not its speech synthesis. The critic accepted the research but
objected to the premise: "we are a transcription app; why look at a TTS app at all?" The Arabic
seat answered: because it is the same user problem — an agent that can speak but cannot listen is
half an assistant, and our listening half is the one with the Arabic advantage.

**Round 2 — the temptation (TTS).**
The owner asked whether Arabic TTS is worth adding. The ethicist raised the decisive effective
difference (الفارق المؤثر): Voicebox can add an engine and call it a language, because its users
hold the licence risk and the GPU; Sada ships one installer for Arabic users and would carry the
licence and support burden. The verifier added that only three engines even claim Arabic, one is
CC-BY-NC (cannot ship), one is multi-GB with GPU expectations, and all would need an Arabic quality
evaluation Sada has no harness for. The architect priced it: installer + several GB optional
models, a new Python or ONNX runtime or whisper-adjacent stack, plus the maintenance of eight
engines' worth of gating logic. The owner withdrew the request for this phase.

**Round 3 — the actual gap (agent input).**
The architect observed that Sada already contains every ingredient an agent needs: a local API, an
engine CLI, an installed skill, readable transcripts. The failure mode was orchestration: the API
is off by default and the port changes, and the CLI needs a model path. The critic applied
تحقيق المناط: does an MCP server really remove the failure class, or does it just add a new
interface? The verifier reproduced the problem: an agent that wants an Arabic transcript today must
either toggle a setting (user present, port known) or discover the engine binary, its flags and the
model path. A stdio MCP server collapses that to a tool name with a rich error message. The critic
then raised الأثر الثاني: stdout pollution, secrets in config, a transcription that hangs the
protocol. The architect answered with the shape that shipped: protocol frames only on stdout,
engine output captured, config reads limited to transcription settings, one request at a time, and
model/engine resolution that explains what is missing rather than failing silently. **The council
ruled: build MCP first.**

**Round 4 — what else from Voicebox.**
The owner catalogued the remaining candidate list (cloning, effects, stories, per-app binding,
local LLM refinement). Each failed the effective-difference test: the ratio that makes it work in
Voicebox (TTS output, GPU users, English model ecosystem, consent budget of a consumer editor) does
not transfer to an Arabic-first transcription tool. Two items survived as lessons rather than
features: Voicebox's engine/model management expectations (Sada already meets them) and the
Host-header exposure in #778 (Sada's local API needs the same audit; filed as follow-up). The
$VOICEBOX episode was recorded under "avoid": the agent-tool surface must justify itself with a
real user benefit, not with a token.

## Maestro verdict

**Step Zero — falsification test.** The plan dies if any of these is true:

1. Windows **Sada.exe --mcp** cannot speak MCP over pipes without a console (fails: verified by
   process test before release).
2. No model/engine can be resolved without the GUI's environment (fails: resolution walks config,
   exe-relative binaries, repository binaries; verified by unit and end-to-end tests).
3. The MCP surface leaks config secrets or opens a port (fails: stdio only, allow-listed settings;
   verified by code review and tests).
4. The Arabic normaliser cannot be shared with Rust (fails: Rust twin implemented; parity tests
   pass on both sides).
5. The feature would break any Arabic-first invariant (fails: MCP adds no UI string, no telemetry,
   no network, no default change).

All five held. The plan proceeded.

| Verdict | Candidate | Constraint that decided it |
| --- | --- | --- |
| Survived | stdio MCP server (**--mcp**, four tools) | Removes setup steps; offline; no UI strings; Arabic defaults preserved. |
| Survived | Skill folder and identity renamed to sada, MCP documented in the skill | Agents must find Sada by name, not by Vibe. |
| Downgraded | Local LLM refinement / personas | Optional summaries with the user's key remain; no default, no bundled model. |
| Suspended on test | Arabic TTS via OS voices or a permissive small engine | Re-open only with a licence-clean, CPU-viable, Arabic-quality-tested engine; a Windows SAPI/OS-voice bridge is the cheapest test. |
| Dropped | Cloning, effects, stories editor, TTS engine collection | Licence, consent, GPU/size and scope: no ratio transfers to Sada. |
| Already present | Captures, dictation pill, Windows paste, model management | Sada already satisfies the underlying need. |
| Learn | Host/Origin hardening for the local API; agent-first documentation; model integrity habits | Security and discoverability lessons, no feature necessary now. |
| Avoid | English-first defaults; token/gamification; engine sprawl as a feature | Each violates an invariant or dilutes the constraint. |

## Plan that shipped (v3.3.0)

1. **MCP core** — **mcp/mod.rs**: stdio JSON-RPC, protocol negotiation (2025-06-18 / 2025-03-26 /
   2024-11-05), initialize with Arabic-first instructions, ping, tools/list, tools/call, empty
   resources/prompts, parse and method errors, one flushed response line per frame.
2. **Tools** — **mcp/tools.rs** and **mcp/transcripts.rs**: sada_transcribe, sada_transcripts,
   sada_transcript, sada_info; config/model/engine/FFmpeg/transcripts resolution; transcript
   scan and render with HH:MM:SS.mmm timecodes; rich, actionable error messages; unit tests.
3. **Arabic parity** — **arabic.rs**: Rust twin of the TypeScript normaliser, same rules, same
   fixtures, tested against the same cases.
4. **Entry point** — **Sada.exe --mcp** handled before any GUI setup; **--config** override for
   tests and non-standard installs.
5. **Agent surface** — skill frontmatter/folder renamed to sada; the generated skill now leads with
   MCP registration for Claude Code, Codex and generic JSON clients.
6. **App wiring** — agent skill install path and mock handler updated; app links now point at the
   Sada repository.
7. **Documentation** — this review, [AGENT-MCP.md](AGENT-MCP.md) (English) and
   [AGENT-MCP.ar.md](AGENT-MCP.ar.md) (Arabic), release notes, README/AGENTS updates, site and
   llms.txt refresh at 3.3.0.

## Continue / kill metrics

**Continue** if, within two releases: MCP setup is the first or second agent path reported by
users; at least one real workflow (meeting transcripts, Arabic dictation cleanup, project batch
transcription) is demonstrated through MCP; no protocol-level bug requires a breaking change; and
the MCP code stays under roughly 1,500 lines with no new crate dependencies.

**Kill (or park) MCP** if: usage is negligible after two releases and the docs are still the only
reference; the tool surface needs a second process or a network transport to be useful; or
maintaining the four-tool contract costs more than the HTTP API and skill already did.

**Never** trade an Arabic-first invariant for a Voicebox-style feature: no bundled non-commercial
weights, no English-first defaults, no always-on local server, no telemetry.

## Risks

| Risk | Mitigation |
| --- | --- |
| Protocol drift across MCP clients | Negotiate known revisions, answer unknown ones with the oldest, keep the method set minimal. |
| Long transcriptions block a client's tool call | One request at a time by design; document expected durations; future: progress notifications if clients adopt them. |
| Media path mistakes (URLs, missing files) | Explicit rejection messages with a next step instead of stack traces. |
| Config layouts from older Vibe profiles | Legacy config folders are read as fallbacks; --config and SADA_CONFIG_PATH cover the rest. |
| Local API remains exposed to Host-header tricks (#778 lesson) | Follow-up hardening task for the HTTP API router; MCP's stdio transport is not affected. |
| Scope creep back toward TTS | The suspension test in this document is explicit; re-open only with licence and quality evidence. |

## First action (already taken)

The first action was not a document: it was **Sada.exe --mcp** answering an initialize frame in a
real process with a real model, then the four tools answering over pipes. That is the Step Zero
evidence this review is built on.

## Bilingual glossary

| English | العربية | Meaning in this review |
| --- | --- | --- |
| asl (origin) | الأصل | The proven feature in Voicebox that a candidate is compared to. |
| far' (branch) | الفرع | The candidate feature in Sada. |
| 'illa (ratio) | العلة | The causal reason a feature works in the origin. |
| effective difference | الفارق المؤثر | A difference that changes the ruling, not just the surface. |
| verification of the ratio | تحقيق المناط | Checking the causal reason actually applies here. |
| second-order effect | الأثر الثاني | What the feature breaks or costs later. |
| rebuttal | النقض | A challenge to a claim that forces evidence. |
| irrelevance | عدم التأثير | A difference that does not change the ruling. |
| invalid premise | فساد الاعتبار | The comparison itself is wrong. |
| ruling | الحكم | Survive / downgrade / drop / suspend. |
| Maestro | المفتي | The final seat that issues the ruling. |

## What this review did not do

It did not evaluate Voicebox's TTS engines on Arabic audio (no Arabic TTS evaluation harness
exists in Sada), did not audit its Python backend for security, and did not test its Windows
installer. Those were not needed for the ruling: the transferable asset was the agent interface,
and the transferable lessons were the failure modes, not the engine list.

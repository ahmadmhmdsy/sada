# Claim ledger — what Sada says, and what proves it

**Purpose:** FC-1 of [P7-PLAN.md](P7-PLAN.md). Every public sentence about a capability must map to
code in this repository or to a measured number. This file is the traceability record behind the
3.10.0-era truth-parity documentation pass (2026-11-19); update it whenever public copy changes.

**Rule (owner answer Q4):** قل ما هو صحيح فقط — say only what is true. If a row cannot cite code
or measurement, the sentence is removed rather than softened.

## Capabilities now documented publicly

| Public claim (short) | Code evidence | Runtime / measured evidence | Published in |
| --- | --- | --- | --- |
| Transcribe audio and video files, batch, cancellable | Transcribe queue and job cancellation in the main session; upstream engine | Verification report + CI; Arabic benchmark harness | README (both), landing pages, llms.txt |
| Live preview of a running batch job | Batch preview UI (not streaming captions) | Manual QA | README (both) — phrased as preview, never as live captions |
| Whisper model catalogue with SHA-256, licence, size, languages; any ggml-*.bin | Model catalogue and download verification | Committed catalogue; download hash check | README, landing pages, llms.txt |
| Export SRT, VTT, TXT, HTML, PDF (embedded Arabic font), DOCX, JSON | Exporters under desktop/src; Arabic PDF font | Exported artifacts in release verification | README, landing pages |
| Global-shortcut dictation into other apps | Dictation shortcut handlers | Manual QA | README, landing pages |
| Microphone and system-audio recording | Recording handlers and settings | Manual QA | README, landing pages |
| Optional meeting detection: notices a call using the microphone and asks whether to record | recording.meetingDetectionEnabled (default false), settings/recording.tsx, app.tsx sync, hidden meeting-prompt window | Settings row exists; prompt window wired | README, landing pages (card 8), llms.txt |
| Optional auto-transcribe when a recording finishes | recording.autoTranscribeAfterRecording (default false), session.tsx | Code path transcribes the finished job | README, landing page card 8 |
| Optional speaker labels (diarization), up to 4 speakers, ~25 MB one-time model, threshold + expected count | transcription.recognizeSpeakers (default false), use-transcribe-queue.ts model wiring, quiet-row.tsx row, i18n diarizeMaxSpeakersNote | Settings UI; model download prompt (~25 MB) | README (both), landing page, FAQ, llms.txt |
| Optional stable timestamps for tighter subtitle timing, ~4x slower, ~1 MB VAD model | transcription.stableTimestamps (default false) | Settings UI and confirm prompt | README (both), landing page card 9, llms.txt |
| Custom initial prompt up to 1,024 characters for names/jargon/spellings; ignored by models without prompt support | modelOptions.init_prompt limit in whisper-options.tsx, promptIgnoredByModel note | Settings UI | README (both), landing page card 9, llms.txt |
| Auto-export every finished transcript (formats, destination, replace rule) | transcription.autoExport config and exporter integration | Settings UI strings autoExport* | README (both), landing page card 9, llms.txt |
| Import media from a URL with yt-dlp, installed/updated only with user consent | tools.ytDlp* keys, update-check flow, managed policy can disable | Settings/URL options and prompts | README (both), landing page card 9, llms.txt |
| Projects: saved transcripts, search, reopen, re-export | Projects UI and transcript storage | Manual QA | README, landing pages |
| Translate to English with Whisper medium/large only (not large-v3-turbo) | i18n translateToEnglish, translateWhisperModelNote; model capability flags | Model capability metadata | README (both), landing page card 9, llms.txt |
| Optional AI summaries/notes/translation and dictation cleanup via user's Claude key or local Ollama | ai config keys, aiSummaryTaskInfo, aiDictationTask; off by default | Settings AI section | README (both), landing page, llms.txt |
| Local MCP server: Sada.exe --mcp, stdio only, four tools, no port/account/network | cli.rs MCP path, skill.ts tool text, AGENTS.md invariant | cargo tests for mcp:: module | README, landing pages, llms.txt |
| Arabic-first defaults (ar-IQ) and 22 inherited UI locales | Boot config defaults, i18n catalogues | Catalogue completeness checks | README, landing pages, llms.txt |
| Optional Vulkan GPU acceleration with CPU fallback | Engine/GPU selection code and docs | Documented builds | README, landing pages, llms.txt |
| Managed controls: offline policy, DPAPI-sealed AI keys, retention, MSI | Rust policy/secrets/retention code; enterprise MSI target | Rust tests; release workflow | README, landing pages, llms.txt |

## Capabilities deliberately documented as absent

Being explicit is part of parity: a reader must not infer a capability from a competitor comparison.

| Not supported | Evidence | Public stance |
| --- | --- | --- |
| Read-aloud / text-to-speech | No TTS code path; Windows evaluation found no Arabic voice by default (docs/READ-ALOUD.md) | README/landing FAQs state it is not offered; TTS candidate stays behind Step Zero A (council record) |
| Speech-to-speech conversation | Requires licensed Arabic speech output; none available (FEATURES-COUNCIL licence board) | Not a roadmap item; stated in council record and P7 non-goals |
| Live captions | Batch engine, no streaming/caption mode | Landing FAQ says no live captions; council keeps it deferred |
| Cloud sync, accounts, mobile apps, telemetry, updater, phone relay | Removed/never added; invariants in AGENTS.md | Stated as no-account/offline throughout |

## Notes and limits

- "Live preview" is a preview of a batch transcription job, **not** live captioning. Copy must not
  grow into the caption claim.
- Speaker labels are opt-in and need a model download; copy must not imply they are on by default or
  that accuracy is guaranteed (threshold and max-speaker settings exist for a reason).
- Translation is English-targeted via Whisper; Arabic-targeted translation is an AI task that
  requires the user's own Claude or Ollama setup, and must be labelled as AI.
- The app itself exposes only --mcp on the command line; the bundled engine sidecar has its own CLI
  for advanced/agent use and is not advertised as an app feature.

## Verification of this pass (2026-11-19)

- `node scripts/seo/check-seo.mjs` — passed (README links/anchors/assets/version, site metadata,
  JSON-LD, sitemap, hreflang).
- Links and anchors in the changed files resolve; Markdown tables are well formed.
- No new capability claim was added for TTS, S2S or live captions; those remain explicitly absent.
- Changes are documentation-only: no application code, version bump or release was touched.

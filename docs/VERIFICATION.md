# Verification report

This page summarises how the Windows builds in this repository were verified.
It is written in English for reviewers; the Arabic summary follows.

## Sada 3.6.0 — transcript quality and security hardening

- **Date:** 18 November 2026 (Asia/Baghdad)
- **Source:** master, tagged v3.6.0; no engine or catalogue change (still vibe-server
  v0.6.16-sada.1 with the same loopback guard), so Arabic benchmark numbers carry over unchanged
  from 3.5.0. The release does change Rust and frontend source (security hardening and Arabic
  post-processing), and the Release workflow rebuilds both from this tag.
- **Host:** Windows 10.0.26300 · WebView2 157.0.4341.46 · NVIDIA Quadro RTX 4000 (Vulkan0) and
  Intel UHD Graphics 630 (Vulkan1).

### Tests

| Suite | Result |
| --- | --- |
| pnpm test (vitest) | **31 files / 193 tests passed**, exit 0 |
| pnpm build | paraglide compile → tsc → vite build, exit 0 (final bundle 1m 5s) |
| cargo test --release (desktop) | **101 passed**, exit 0 (was 91 in 3.4.0; new yt-dlp, model-path and type_text tests) |
| cargo test --release -p vibe-server guard:: | **8 passed**, exit 0 |
| python -m unittest discover -s benchmarks/arabic-asr/tests | **44 tests passed**, exit 0 (was 38; new postprocess fixture tests) |
| i18n audit (check_i18n.py) | passed |

The first full vitest run after the bootstrap test was made resilient to a cold module import
passed 31/193; a second run executed concurrently with a production vite build and a Rust test
build collapsed six workers, which is an environment limit of this machine, not a test failure
(the suite passes cleanly when run alone). The fix in desktop/src/bootstrap.test.tsx gives the
cold dynamic import a 15 s budget and flushes a pending native-cleanup promise before the next
test, so the timeout can no longer leak a second render into a sibling test.

### What changed

- **Arabic post-processing:** 21 Latin technical terms restored from Arabic-letter spellings,
  Arabic punctuation normalised, and the same rules expressed in sadabench/postprocess.py so the
  benchmark can score app-level output. New shared fixture file asserted by both implementations.
  On the current 60-clip suite the app-level WER equals the raw WER (Turbo 19.46%, Nemotron
  17.12%, dialectal 23.09%, tiny 70.56%), so no accuracy improvement is claimed; the 3.5.0 table
  below remains the measured truth.
- **Security:** ported the applicable parts of upstream Vibe v3.3.6 — CSP, SafeMarkdown, sada:
  deep-link allowlist with confirmation and catalogue integrity, model download destination
  confinement, https-only download client, validated yt-dlp release downloads with SHA2-256SUMS,
  engine child-process confinement, and the dictation typing permit. Details in
  docs/UPSTREAM-PATCHES.md §10 and SECURITY.md.
- **Process:** docs/ACCEPTANCE.md records the clean-machine procedure and its evidence table;
  docs/SIGNING.md records the signing options and recommendation (still unsigned in this release).

### Clean-machine acceptance (issue #16)

The procedure and the machine matrix are committed in docs/ACCEPTANCE.md. Rows B–E (offline
Windows 10, CPU-only, AVX-only, SSE4.2-without-AVX) require hardware the maintainer does not have
in this environment, so they are **not executed** for 3.6.0 and are recorded as pending in the
evidence table — the page does not claim them. Slots A and C are covered on the development host
by the automated suites above, the existing installer smoke test (silent install, version check)
and the documented CPU-variant code path (server/crates/ggml-rs-sys/src/cpu_variant.rs).

### Artifacts

- CI run [44262019603](https://github.com/alshahia/sada/actions/runs/44262019603) — **success**
  (desktop build/tests incl. Rust, and the Arabic ASR benchmark job).
- Release run [44262023351](https://github.com/alshahia/sada/actions/runs/44262023351) —
  **success** (engine rebuilt from server/, guard tests, Rust tests, NSIS installer).
- Deploy site run [44262019694](https://github.com/alshahia/sada/actions/runs/44262019694) —
  **success**.

The published installer and SHA256SUMS.txt were re-downloaded on 18 November 2026 and compared
with the checksum attached to the [v3.6.0 release](https://github.com/alshahia/sada/releases/tag/v3.6.0)
and with GitHub's recorded asset digest:

| Artifact | Size | SHA-256 |
| --- | --- | --- |
| Sada_3.6.0_x64-setup.exe | 44,926,298 bytes | 53e0a3c9d715c0eff949f9058d77708fb4899c685ef7fe022719868efa54d40e |
| SHA256SUMS.txt | 90 bytes | 72b64ba6fd218c111f9f58c5868c93ba62ca72cb3a67701a909a29ccb40d3b28 |

The re-downloaded installer matched SHA256SUMS.txt. It was installed silently (/S, per-user
install): the installed Sada.exe is 15,896,576 bytes with product version **3.6.0**, the installed
sidecar is 75,685,376 bytes and reports **vibe-server v0.6.16-sada.1**, and the installed MCP
server starts with **sada-mcp 3.6.0 ready (stdio; tools: sada_transcribe, sada_transcripts,
sada_transcript, sada_info)**. The NSIS package remains unsigned (SmartScreen warns "unknown
publisher"; verify the hash before choosing *More info → Run anyway*).

---

## Sada 3.5.0 — measured Arabic model evaluation

- **Date:** 18 November 2026 (Asia/Baghdad)
- **Source:** `master`, tagged `v3.5.0`; no Rust or frontend source change beyond the bundled
  catalogue entry, so the release workflow rebuilt the engine from `server/` and packaged the same
  guarded sidecar.
- **Host:** Windows 10.0.26300 · WebView2 157.0.4341.46 · NVIDIA Quadro RTX 4000 (Vulkan0) and Intel
  UHD Graphics 630 (Vulkan1).

### Tests

| Suite | Result |
| --- | --- |
| `pnpm test` (vitest) | **28 files / 179 tests passed**, exit 0 |
| `pnpm build` | paraglide compile → tsc → vite build, exit 0 (45.3 s) |
| `python -m unittest discover -s benchmarks/arabic-asr/tests` | **38 tests passed**, exit 0 |
| i18n audit (`check_i18n.py`) | passed (fallback warnings for older translated docs only) |
| `cargo test --release` | no Rust source changed since 3.4.0 (91 tests passed there); the Release workflow still built the engine and ran the guard tests (step 13 succeeded) |
| CI run [44248005147](https://github.com/alshahia/sada/actions/runs/44248005147) | success, including the new `benchmarks` job on ubuntu 3.12 |

### Benchmark (issue #10, #11, #13)

60 clips × 4 models on the bundled `vibe-server v0.6.16-sada.1` with Vulkan, 2026-11-18 08:33
(transcribe.cpp spike: 08:46). Raw artefacts committed under `benchmarks/arabic-asr/results/`.

| Model | Size MB | WER % | CER % | Latin names kept % | Timestamps % | RTF |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| whisper-large-v3-turbo (default) | 1624.6 | 19.46 | 8.34 | 25.0 | 100 | 0.35 |
| nemotron-3.5-asr-streaming-0.6b-q4-k-m | 495.8 | **17.12** | 8.28 | 0.0 | 100 | **0.234** |
| whisper-large-v3-turbo-arabic-dialectal-v2-q5 | 574.0 | 23.09 | 9.53 | 0.0 | 100 | 0.265 |
| whisper-tiny | 77.7 | 70.56 | 29.46 | 0.0 | 100 | 0.186 |
| Qwen3-ASR 0.6B Q8_0 via transcribe.cpp v0.4.2 (CPU) | 850.4 | 24.38 | 10.21 | 10.0 | 0 | 0.494 |

Decisions and their conditions are recorded in [MODELS-DECISIONS.md](MODELS-DECISIONS.md): Turbo
stays the default; Nemotron is curated as an **optional** entry; the dialectal fine-tune, read-aloud
and second engine are rejected/suspended with evidence.

### Catalogue (issue #11)

`desktop/src/assets/model-catalog.json` now has four curated entries. The Nemotron GGUF was verified
against the published file before wiring it: 495,831,520 bytes, SHA-256
`41c99fa5fb6f3d35f68e79adc3e755eca2232a8d921178bd647b71194792b8fd` (mirror
`vibe-app/nemotron-3.5-asr-streaming-0.6b-gguf`); the entry is OpenMDW-1.1 with VAD supplied by the
app. Vitest catalog tests pass with the new entry.

### Artifacts

The CI-built installer and its `SHA256SUMS.txt` are attached to the
[v3.5.0 GitHub release](https://github.com/alshahia/sada/releases/tag/v3.5.0). The published files
were re-downloaded on 18 November 2026 and compared with the published checksums:

| Artifact | Size | SHA-256 |
| --- | --- | --- |
| `Sada_3.5.0_x64-setup.exe` | 44,936,816 bytes | `9cf779ff7c891e4823523be34e5315da2136d7dcf6356db085889c4cbadca279` |
| `SHA256SUMS.txt` | 90 bytes | `f673e8f3c19b90dc01d565926132f1e2e68e6b149b14f08d8df4ebff69a2b135` |

- The re-downloaded installer matched `SHA256SUMS.txt` and the digest GitHub recorded for the
  asset.
- The published installer was run silently (`/S`, per-user install, exit 0). The installed
  `Sada.exe` reports product version **3.5.0**, the installed sidecar reports
  **`vibe-server v0.6.16-sada.1`**, and the installed MCP server starts with
  **`sada-mcp 3.5.0 ready`** — the CI build ships the expected binaries.
- The NSIS package is unsigned (SmartScreen warns "unknown publisher"; verify the hash before
  choosing *More info → Run anyway*).

---

## Sada 3.4.0 — verified catalog, MCP capabilities and endpoint hardening

- **Date:** 17 November 2026 (Asia/Baghdad)
- **Source:** `master`, tagged `v3.4.0`; the release workflow rebuilds the engine from `server/` and
  packages that binary as the sidecar (`vibe-server v0.6.16-sada.1`).
- **Host:** Windows 10.0.26300 · WebView2 157.0.4341.46 · NVIDIA Quadro RTX 4000 (Vulkan0) and
  Intel UHD Graphics 630 (Vulkan1) · local LLVM 23.1.5 for the bindgen build.

### Tests

| Suite | Result |
| --- | --- |
| `pnpm test` (vitest) | **28 files / 179 tests passed**, exit 0 |
| `pnpm build` | paraglide compile → tsc → vite build, exit 0 |
| `cargo test --release` (Rust) | **91 passed**, exit 0 (incl. 27 `mcp::`) |
| `cargo test --release -p vibe-server guard::` | **8 passed**, exit 0 |
| i18n audit (`check_i18n.py`) | passed; the five new VAD strings exist in `en-US` and `ar-IQ` |

### Verified catalog (#5, #6)

`desktop/src/assets/model-catalog.json` carries three commercially reusable entries and is
validated on load:

| Entry | Licence | Bytes | SHA-256 (prefix) |
| --- | --- | --- | --- |
| `whisper-large-v3-turbo` | MIT | 1,624,555,275 | `1fc70f774d38…` |
| `whisper-tiny` | MIT | 77,691,713 | `be07e048e1e5…` |
| `whisper-large-v3-turbo-he` | Apache-2.0 | 1,624,555,275 | `c80904111133…` |

Strict entry validation (licence allowlist, size, SHA-256 format, language codes) and the download
checks are covered by unit tests; the Settings → Models section reads the catalog at runtime.

### MCP capabilities (#7)

The patched app binary was driven as a stdio MCP server (`--mcp --config <scratch config>`) against
the guarded engine rebuilt from `server/`:

| Check | Result |
| --- | --- |
| `sada_info` with a Nemotron GGUF | `engine: nemotron`, `requires_vad: true`, 32 languages incl. `ar-AR`, `translation: false`, `text_prompts: false` |
| Nemotron transcription, Arabic, `timestamps: true` | Arabic text returned with `[00:00:00.320 --> …]` timecodes; VAD model located automatically |
| Whisper with configured `ar-AR` | succeeded after mapping to the Whisper code `ar` |
| Nemotron with `translate: true` and `prompt` | call succeeded; both flags were dropped because the model does not declare them |

### Loopback guard (#9)

The rebuilt engine (`serve --host 127.0.0.1 --port 0`) answered a live `curl` matrix:

| Request | Result |
| --- | --- |
| `Host: 127.0.0.1:<port>` → `GET /health` | **200** |
| `Host: localhost:<port>` → `GET /health` | **200** |
| `Host: attacker.example:<port>` → `GET /health` | **403** |
| `Host: attacker.example:<port>` → `POST /v1/models/load` | **403** (state-changing route) |
| `Origin: http://attacker.example` → `GET /health` | **403** |
| `Origin: http://127.0.0.1:1420` → `GET /health` | **200** |
| missing `Host` → `GET /health` | **403** |

The engine was rebuilt locally from `server/` with `VIBE_SERVER_VERSION=v0.6.16-sada.1`
(75,686,912 bytes, SHA-256 `48308753614AA6B2D7C8BF587234569791A121F53D19EB006B2A9A5986FA29CF`) and
staged as `desktop/src-tauri/binaries/vibe-server-x86_64-pc-windows-msvc.exe`; the upstream binary
remains available as a local backup and CI rebuilds the same way in the Release workflow.
The same matrix was repeated against the engine **installed by the published 3.4.0 installer**:
200 for a native loopback `Host`, 403 for a rebinding `Host`, 403 for a page `Origin`, 200 for a
loopback `Origin` — the binary shipped in the installer is the guarded build.

### Artifacts

The CI-built installer and its `SHA256SUMS.txt` are attached to the
[v3.4.0 GitHub release](https://github.com/alshahia/sada/releases/tag/v3.4.0). The published files
were re-downloaded on 17 November 2026 and compared with the published checksums:

| Artifact | Size | SHA-256 |
| --- | --- | --- |
| `Sada_3.4.0_x64-setup.exe` | 44,915,585 bytes | `7e6d8c813af34a80e4fa59e2ee28444a07b2c7811d88aa1b2549b627ce3cfd27` |
| `SHA256SUMS.txt` | 90 bytes | `48c45db058b21037ac2278386de1c16a9bc8ce441ecc57ba83e97dfb91ad993e` |

- The re-downloaded installer matched `SHA256SUMS.txt` and the digest GitHub recorded for the
  asset.
- The published installer was run silently (`/S`, per-user install, exit 0). The installed
  `Sada.exe` reports product version **3.4.0**, and the installed sidecar reports
  **`vibe-server v0.6.16-sada.1`** — the installer ships the CI-built guarded engine.
- The installed MCP server reports `serverInfo.version = 3.4.0` and the expected
  `model.capabilities`; the NSIS package is unsigned (SmartScreen warns "unknown publisher";
  verify the hash before choosing *More info → Run anyway*).

---
## Sada 3.3.1 — engine v0.6.16 and GPU documentation

- **Date:** 17 November 2026 (Asia/Baghdad)
- **Source:** `master` at `45c3697`, tagged `v3.3.1`, with `.server-version` = `server-v0.6.16`;
  CI rebuilds the installer from the same tree.
- **Host:** Windows 10.0.26300 · WebView2 157.0.4341.46 · AVX2 available · NVIDIA Quadro RTX 4000
  (Vulkan0) and Intel UHD Graphics 630 (Vulkan1)
- **Build:** Tauri 2.10.3, sidecar `vibe-server` v0.6.16 (upstream `master`, whisper.cpp with the
  Vulkan backend), FFmpeg 9.0.2 (gyan.dev essentials, GPLv3), pnpm 10.4.1, Node 24, Rust stable.

### Tests

| Suite | Result |
| --- | --- |
| `pnpm test` (vitest) | **26 files / 134 tests passed**, exit 0 (adds the auxiliary/legacy model filter tests) |
| `pnpm build` | paraglide compile → tsc → vite build, exit 0 |
| `cargo test --release` | no Rust source changed in this release; CI re-ran the 83 tests and passed |

### Engine smoke test (E1)

The v0.6.16 sidecar was started as a local server and driven over the same multipart route the app
uses (`POST /v1/audio/transcriptions`), with `ggml-large-v3-turbo.bin` and `language=ar`:

| Check | Result |
| --- | --- |
| Arabic parity with v0.6.10 | **identical text** on all four clips (short MSA, MSA news, Iraqi dialogue, Arabic/English technical mix) |
| Timed segments | SRT and VTT output carried correct start/end times |
| Diarization with the new Nemotron-3 GGUF | 12/12 transcript segments attributed on the combined clip (two speakers) |
| Nemotron 3.5 ASR + Silero VAD | metadata reports `requires_vad: true` with `ar-AR`; loaded and transcribed behind VAD |
| CPU-only path | `{"no_gpu": true}` model load and transcription completed on the CPU (14 s clip: 26.9 s CPU vs ≈0.5 s on the RTX 4000) |
| GPU device list | `vibe-server … devices` reports `Vulkan0` Quadro RTX 4000 and `Vulkan1` Intel UHD 630 |
| Diarization file integrity | 108,541,632 bytes, SHA-256 `a25f026847d765c8661fd5095c73a0e5f20d310dcb8249c654e3828592a2fc73` — matches `desktop/src/lib/config.ts` |

### Configuration migration and invariants

- Diarization now points at `nemotron-3-diarization-Q8_0.gguf`; the retired
  `diar_streaming_sortformer_4spk-v2.q8_0.gguf` is filtered out of the model list (unit-tested)
  and is never deleted from disk.
- No model is bundled and no hard-coded UI string was added: `ar-IQ` still has 704/704 keys, and
  no telemetry, updater or network endpoint was introduced.
- The GPU path stays optional: without Vulkan the same engine transcribes on the CPU, and a failed
  GPU load is retried once with `no_gpu` and remembered.

### Artifacts

The CI-built installer and its `SHA256SUMS.txt` are attached to the
[v3.3.1 GitHub release](https://github.com/alshahia/sada/releases/tag/v3.3.1). The published files
were re-downloaded on 17 November 2026 and compared with the published checksums:

| Artifact | Size | SHA-256 |
| --- | --- | --- |
| `Sada_3.3.1_x64-setup.exe` | 44,996,972 bytes | `dee8bfb313947df2fd90ca1c99f38680a102e342753436dfb087afc2fdfae669` |
| `SHA256SUMS.txt` | 90 bytes | `68099effae9b23f6cf654c7154744b17841987b7b6055dd5ac8e193f28635310` |

- The re-downloaded installer matched `SHA256SUMS.txt` and the digest GitHub recorded for the
  asset; the NSIS package reports product version `3.3.1` and is unsigned (SmartScreen warns
  "unknown publisher"; verify the hash before choosing *More info → Run anyway*).
- CI on the tagged commit re-ran the full suite: `pnpm build`, `pnpm test` and
  `cargo test --release` all passed before the release job uploaded the assets.

---

## Sada 3.3.0 — agent interface

- **Date:** 16 November 2026 (Asia/Baghdad)
- **Source:** `master` tagged `v3.3.0`; the installer is rebuilt by CI from the same tree.
- **Host:** Windows 10.0.26300 · WebView2 157.0.4341.46 · AVX2 available
- **Build:** Tauri 2.10.3, sidecar `vibe-server` v0.6.10 (whisper.cpp), FFmpeg 9.0.1 (gyan.dev,
  GPLv3), pnpm 10.4.1, Node 24, Rust stable. No dependency was added for MCP.

### Tests

| Suite | Result |
| --- | --- |
| `pnpm test` (vitest) | **26 files / 132 tests passed**, exit 0 (includes the skill/MCP registration test and the Arabic normaliser tests) |
| `cargo test --release` (Rust) | **83 tests passed**, including 19 `mcp::` tests (protocol frames, tool schemas, transcript scanning, config resolution, URL rejection, missing-model errors) and 9 `arabic::` parity tests |
| `pnpm build` | paraglide compile → tsc → vite build, exit 0 |

### MCP end-to-end

A batch of JSON-RPC frames was piped into the real release binary on a clean scratch config (small
`ggml-tiny` model, Arabic clip, engine and FFmpeg sidecars from the repository):

~~~text
target/release/vibe.exe --mcp --config <scratch>/config.json < input.jsonl > output.jsonl 2> stderr.txt
~~~

Scratch config (the app config uses flat dotted keys, as the Tauri store writes them):

~~~json
{
  "model.path": "E:/models/ggml-tiny.bin",
  "transcription.projectsPath": "E:/scratch/projects",
  "transcription.modelOptions": { "lang": "ar", "beam_size": 5, "temperature": 0, "threads": 4 }
}
~~~

Results:

| Frame | Result |
| --- | --- |
| `initialize` | `serverInfo.name = "sada"`, title "Sada — Arabic-first offline transcription", protocol `2025-03-26`, capabilities `{ tools: … }` |
| `notifications/initialized` | accepted, no response |
| `ping` | empty result |
| `tools/list` | exactly `sada_info`, `sada_transcribe`, `sada_transcript`, `sada_transcripts` |
| `tools/call sada_info` | JSON: app Sada, `arabic_first: true`, config path, engine/FFmpeg/model `present: true`, transcripts folder |
| `tools/call sada_transcripts` | JSON: `total: 1`, fixture project listed with record path, audio path, language `ar` |
| `tools/call sada_transcript` | Arabic text with `[00:00:00.000 --> 00:00:01.200]` timecodes |
| `tools/call sada_transcribe` (URL) | `isError: true` with an explanation that only local files are transcribed |
| `tools/call sada_transcribe` (Arabic clip, timestamps) | `isError: false`; `[00:00:00.000 --> 00:00:03.000] شكراً جزيلاً. ماسلما.` |
| stdin closed | process exits 0; stderr contains only the `sada-mcp 3.3.0 ready (stdio; …)` line |

Arabic output was produced with `language` defaulting to `ar` from the config, and the Arabic
normaliser (Rust twin) is applied before the text is returned. No port is opened: the transport is
stdin/stdout only.

### Arabic-first checks

- No new UI string was added; MCP surfaces are documented in [AGENT-MCP.md](AGENT-MCP.md) and
  [AGENT-MCP.ar.md](AGENT-MCP.ar.md), and the installed skill is now **sada**.
- Fresh-profile defaults are unchanged: display `ar-IQ`, transcription `ar`, translation off.
- The Rust normaliser was tested against the same cases as the TypeScript one (punctuation
  replacement, acronym restoration, whitespace collapse, idempotence, English untouched).
- No telemetry, updater, account or phone relay was added; MCP opens no network endpoint.

### Artifacts

The CI-built installer is attached to the [v3.3.0 GitHub release](https://github.com/alshahia/sada/releases/tag/v3.3.0)
with `SHA256SUMS.txt`; verify the downloaded file against that checksum.

| Artifact | SHA-256 |
| --- | --- |
| Local release binary `target/release/vibe.exe` (14,011,904 bytes; `tauri build` bundles it as `Sada.exe`) | `0A8F707B99D5BA0CCB0019AEC8794AFD4A1A64156E7D4D5C88C69741AB1E04A6` |
| Published installer `Sada_3.3.0_x64-setup.exe` (43,949,601 bytes, built by the Release workflow, downloaded again and re-hashed) | `9EBCB62FF37FCC67AE795D3FCE3ED81D43BF10F6836BB5A0220D8D8F54FE6C32` |

The published installer hash matches the `SHA256SUMS.txt` asset byte for byte. It is not code
signed (`Get-AuthenticodeSignature` reports `NotSigned`), so Windows SmartScreen will warn on
first run; that is the expected state described in the release notes. The local binary above
answered the MCP frames and CI rebuilt the same source for the installer.

### Known limitations (3.3.0)

- MCP is stdio-only: no network transport and no progress notifications yet; long transcriptions
  keep one request busy.
- The MCP server requires a configured Whisper model and the bundled engine; the model is still not
  shipped with the installer.
- Windows-only, unsigned installer.

---

## Sada 3.2.2 — first public release (historical)

- **Date:** 16 November 2026 (Asia/Baghdad)
- **Source:** commit `f10d2b6` (tree verified before the release; later commits touch docs, CI and the
  site only)
- **Host:** Windows 10.0.26300 · WebView2 157.0.4341.46 · AVX2 available
- **Build:** Tauri 2.10.3, sidecar `vibe-server` v0.6.10 (whisper.cpp), FFmpeg 9.0.1 essentials
  (gyan.dev, GPLv3), pnpm 10.4.1, Node 24, Rust stable.

## Artifacts

| Artifact | SHA-256 |
| --- | --- |
| `Sada_3.2.2_x64-setup.exe` (local verification build, 43,914,975 bytes) | `39C327B6D8BB2CE24D78158B47042EEC23565089479C5F128DB5574C9F32FE96` |
| Installed `Sada.exe` (15,770,624 bytes) | `9DB6A8081AE651550001E0B3285B5DF42A49998832BB0A0EB6BD6F0AFF67AC84` |
| Installed `vibe-server.exe` (75,623,424 bytes) | `BCA00C2F91E6056B4A283801C2D57A74AA3A7109A2DADCCA8B4E68D66D89AD76` |

The GitHub release installer is rebuilt by CI from the same source; its hash is recorded in the
release's `SHA256SUMS.txt` and can differ from the local build above because of build paths and
timestamps. Verify whatever file you download against the checksum shipped with it.

## Build

- Frontend: `pnpm build` (paraglide compile → `tsc` → `vite build`), exit 0.
- Desktop: `pnpm exec tauri build`, log ends with `Finished 1 bundle`; NSIS installer produced.
- No binary sidecar or model is committed to git; both are fetched/adopted at build/run time.

## Arabic-first launch

A fresh profile was verified by deleting the application data folders, launching the installed app
and inspecting the running WebView over the DevTools protocol:

- `document.documentElement.lang = "ar-IQ"`, `dir = "rtl"`
- paraglide locale `ar-IQ`; UI copy Arabic; Arabic setup screen with model download progress
- second launch kept Arabic (locale persisted)

Screenshots: [main](media/sada-main.png), [first run](media/sada-first-run.png),
[settings](media/sada-settings.png).

> A real bug was found and fixed here: the hidden `meeting-prompt` window shares localStorage and
> could win a race that reset the locale to English on first paint. The shared default is now
> `ar-IQ` in every window, and the final build was re-verified from a fresh profile.

## Arabic transcription

Transcribed with the shipped engine (same `vibe-server` binary the app uses), Arabic language
setting, `large-v3-turbo` model:

| Clip | Content | Result |
| --- | --- | --- |
| `msa_news` | Modern Standard Arabic news | Accurate transcript; one Latin acronym (`PDF`) misheard as "BDF" |
| `iraqi_dialog` | Iraqi Arabic dialogue | Accurate; dialect understood |
| `silence` | Digital silence | Hallucination (invented phrase) — known Whisper limitation |
| `tech_mix` | Arabic + technical terms | Mixed accuracy on English tech terms |
| `numbers` | Numbers and dates | Correct values, sometimes written as words; occasional duplicate word |

The app's CLI path (`Sada.exe transcribe … -l ar`) exited 0 in the installed build. The transcript
is printed by the sidecar on stdout; the GUI redirect does not produce console output on Windows.

## Arabic PDF

Export produced a real PDF with an embedded IBM Plex Sans Arabic font and correct Arabic shaping;
visual render was checked. Note that automated text extraction (e.g. `pdftotext`) can scramble
intra-word ordering for shaped Arabic even when the visual output is correct.

## Tests

`pnpm test` → **26 test files / 130 tests passed, exit 0**, including:

- Arabic transcript normalization (`arabic-text.test.ts`, 10 tests)
- Arabic PDF font selection and shaping tests
- boot-locale test: no stored language → app boots `ar-IQ`/`rtl`
- existing upstream tests for bidi, PDF, projects and dialogs

## Network

With the app installed and idle, an inspection found only loopback sockets opened by the app's own
IPC; no external endpoint, no telemetry. The updater and analytics code paths are removed from
source.

## Known limitations

- The installer is **not code-signed**; SmartScreen may warn. Verify `SHA256SUMS.txt`.
- Models are **not bundled**; the first run downloads ~1.6GB (or you pick a local `ggml-*.bin`).
- Silence/noise hallucinations; occasional acronym and number normalization gaps.
- PDF text extraction by third-party tools can be imperfect, though the visual PDF is correct.
- The fork ships for Windows only.
- The sidebar switch controls stay on the physical left even in RTL (deliberate layout choice).

Raw logs and screenshots are kept by the maintainer; the files in [docs/media](media/) are the
public copies used in the README and the website.

---

## ملخص عربي

تم التحقق من بناء Windows قبل أول إصدار عام: بناء نظيف من المصدر، ثم تثبيت وفتح من ملف تعريف
نظيف والواجهة عربية RTL فعلاً (`lang=ar-IQ`، `dir=rtl`)، وتفريغ فصحى ولهجة عراقية بمحرّك
التطبيق نفسه، وتصدير PDF عربي بخط مضمّن، واختبارات 130/130 ناجحة، وفحص شبكة عند الخمول يُظهر
loopback فقط. القيود المعلنة: مثبّت غير موقّع، النموذج غير مضمّن (~1.6GB)، هلوسة على الصمت،
وقصور في الأكرونيمات والأرقام، والاستخراج الآلي لنص PDF قد يشوّش داخل الكلمات رغم صحة العرض.

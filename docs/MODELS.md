# Models

Sada does not bundle a speech model with the installer: the installer stays small, and every
weight keeps its own publisher's licence and terms. Models are downloaded **once**, by you, from
**Settings → Models → Get models**; after that the app can transcribe with the network switched off
for good.

The catalogue ships *inside* the app (it is not fetched from a website at start-up), so
**Get models** opens on a fresh offline install. Each entry carries a licence, a size, a SHA-256 and
its languages; the download is checked against that hash before the model is used, and a file that
does not match is deleted and reported instead of being loaded.

## Curated models

| Model | Languages | Size | Licence | Publisher | Needs |
| --- | --- | --- | --- | --- | --- |
| **Whisper Large v3 Turbo** (`whisper-large-v3-turbo`) — the default | every language, including Arabic | 1.62 GB | MIT | OpenAI, ggml conversion by ggerganov/whisper.cpp | a GPU is recommended, not required |
| **Whisper Tiny** (`whisper-tiny`) | every language | 78 MB | MIT | OpenAI | any machine, CPU is enough |
| **Whisper Large v3 Turbo Hebrew** (`whisper-large-v3-turbo-he`) | Hebrew | 1.62 GB | Apache-2.0 | ivrit.ai | a GPU is recommended, not required |

Verified file facts (checked against the publishers on 2026-11-17):

| File | Bytes | SHA-256 |
| --- | --- | --- |
| `ggml-large-v3-turbo.bin` | 1,624,555,275 | `1fc70f774d38eb169993ac391eea357ef47c88757ef72ee5943879b7e8e2bc69` |
| `ggml-tiny.bin` | 77,691,713 | `be07e048e1e599ad46341c8d2a135645097a538221678b7acdd1b1919c6e1b21` |
| `ggml-model.bin` (ivrit.ai Hebrew) | 1,624,555,275 | `c8090411113357097bfafc2b8e228ec1639fa7f5fe4ecb5d054ac0ccef8641b1` |

## Which model should I pick?

- **Arabic — the default:** Whisper Large v3 Turbo. It is the model the app was tuned and measured
  on: Modern Standard Arabic, Iraqi dialect, and Arabic/English technical speech (Latin terms such
  as GPU, CPU, PDF, SRT, VTT stay Latin), with word timestamps for exports and transcript editing.
- **A slow or old machine:** Whisper Tiny. It runs on the CPU only and fits in 78 MB, but its
  accuracy is much lower, especially on dialect and technical terms. Use it for a trial or for a
  laptop that cannot run the large model.
- **Hebrew audio:** Whisper Large v3 Turbo Hebrew. It is trained for Hebrew and does not understand
  Arabic; use the multilingual Turbo for Arabic.
- **Your own file or link:** **Settings → Models → Download model**. Any `ggml-*.bin` Whisper file
  or a GGUF model the bundled engine supports can be used this way. A manual download has no
  curated hash, so the app cannot verify it — check the publisher's SHA-256 yourself if it
  publishes one.

Language codes are reconciled when you switch models: the app maps the selected language to the
codes the model actually supports (for example `ar` → `ar-AR` for a model that only lists the
regional code) and falls back to automatic detection when the model supports it. A model that
requires voice-activity detection gets the VAD file on every path, not only in the setup screen.

## Auxiliary models

These are downloaded automatically, once, when a feature first needs them — they are not listed in
**Get models** because they are not transcription models:

| File | Feature | Size | Licence |
| --- | --- | --- | --- |
| `ggml-silero-v6.2.0.bin` | voice-activity detection (VAD) for models that require it | small | Silero VAD, MIT (ggml build from ggml-org/whisper-vad) |
| `nemotron-3-diarization-Q8_0.gguf` | speaker labels (diarization), on when you enable it | 108,541,632 B | OpenMDW-1.1 (NVIDIA) |

The older Sortformer diarization file is never required any more; files from earlier releases are
left where they are and are simply ignored.

## Licence policy

- Only publishers' weights that allow **commercial use**: MIT, Apache-2.0, CC-BY-4.0 or
  OpenMDW-1.1. No non-commercial, no research-only, no gated weights.
- No weight ships inside the installer; Sada only links to the publisher's download and verifies
  the bytes against the catalogue hash.
- Model names, publishers and licences are listed in [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md);
  the catalogue itself lives in `desktop/src/assets/model-catalog.json`.

## Not curated yet

- **NVIDIA Nemotron 3.5 ASR Streaming 0.6B** (OpenMDW-1.1, 496 MB, 36 languages including Arabic)
  is a smaller multilingual model with punctuation, but it transliterates Latin technical terms
  and runs slower than Turbo on the same GPU. It stays an evaluated candidate, not a catalogue
  entry, until the Arabic benchmark (E2) decides.
- **Arabic Whisper fine-tunes** (Byne large-v3-arabic, oddadmix turbo dialectal v2) are suspended on
  the same benchmark: no fine-tune is recommended before it beats Turbo on measured Arabic WER/CER
  with technical terms intact.
- **Qwen3-ASR and Cohere Transcribe Arabic** would need a second engine runtime without timestamps
  or VAD today; they are documented as suspended experiments, not shipped.

## GPU or CPU?

GPU acceleration is optional and uses Vulkan, which the bundled engine already includes — no CUDA
or extra download. The engine falls back to the CPU when Vulkan is unavailable or when a model
does not fit the GPU's memory (and remembers that model, so later runs start on the CPU). See
[README § GPU acceleration](../README.md#gpu-acceleration-optional) for drivers, the device picker
and measured speed.

## Verifying a download outside the app

Tools → the files live in the models folder shown by **Settings → Models → Models Folder**
(`%LOCALAPPDATA%\app.sada.desktop` by default). On Windows PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 "$env:LOCALAPPDATA\app.sada.desktop\whisper-large-v3-turbo.bin"
```

Compare it with the table above. A file whose hash differs is not the model the catalogue describes:
delete it and install again from **Get models**.

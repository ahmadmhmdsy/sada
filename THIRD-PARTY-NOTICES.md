# Third-party notices

Sada is MIT-licensed (see [LICENSE](./LICENSE)), but the installer it produces contains
components under other licences. Read this page before giving a build to someone else. This file
is a summary; the authoritative licence texts are in [docs/licenses/](./docs/licenses/).

## Bundled in the installer

### FFmpeg — GPLv3

The installer bundles an FFmpeg executable used to decode audio and video:

- Binary: `ffmpeg-x86_64-pc-windows-msvc.exe`
- Build: **FFmpeg 9.0.2**, "essentials" build by gyan.dev (https://www.gyan.dev/ffmpeg/builds/)
- Reported configuration: `--enable-gpl --enable-version3 --enable-static ...`
  (full `ffmpeg -version` output is recorded in the build verification report)
- Licence: **GNU General Public License, version 3** (GPLv3). The `--enable-gpl` and
  `--enable-version3` flags make this build GPLv3, not LGPL.
- Licence text: [docs/licenses/GPL-3.0.txt](./docs/licenses/GPL-3.0.txt)

GPLv3 requires that anyone who receives the binary can also get its source. If you distribute a
Sada installer, either ship the corresponding FFmpeg source, or include a written offer valid for
three years. The exact corresponding source is the FFmpeg 9.0.2 release source, obtainable from:

- https://ffmpeg.org/releases/ffmpeg-9.0.2.tar.xz
- https://www.gyan.dev/ffmpeg/builds/ (source archives for the gyan.dev builds)

Sada itself remains a separate MIT-licensed program; the FFmpeg executable is a separate
program invoked as a subprocess (mere aggregation). Do not relicense Sada as GPL because of it,
and do not relicense FFmpeg as MIT.

### The transcription engine — MIT

`vibe-server` is built from the upstream Vibe repository's `server/` crate (MIT, see
[server/LICENSE](./server/LICENSE)). It statically links whisper.cpp/ggml (MIT) and other
crates whose licences are recorded in [docs/licenses/rust-crates.txt](./docs/licenses/rust-crates.txt).

### Speech models — not bundled

No speech model is shipped in the installer. Models are downloaded by the user at runtime, either
from the app's verified catalogue (OpenAI Whisper large-v3-turbo and tiny, MIT; ivrit.ai Hebrew
large-v3-turbo, Apache-2.0; NVIDIA Nemotron 3.5 ASR Streaming 0.6B, OpenMDW-1.1) or from the model
sources the user chooses, or selected from the user's disk. Model weights are distributed by their
own publishers under their own terms; the app only links to the publisher's file, verifies its
SHA-256 and keeps the publisher's name and licence visible before download. The auxiliary Silero VAD
model is MIT (ggml build from ggml-org/whisper-vad) and the diarization model is OpenMDW-1.1 (NVIDIA).
OpenMDW-1.1 asks that its notices be kept when the model is redistributed — Sada never bundles it.

## Benchmark data — not bundled

The development benchmark under `benchmarks/arabic-asr/` downloads evaluation audio at run time
and never commits or redistributes it. Its corpora are commercial-use-permissive and attributed in
`manifest.json` and `sadabench/datasets.py`:

- **Common Voice 18.0 Arabic** (Mozilla), CC0 1.0 — MSA and Latin-mixed read speech
  (https://commonvoice.mozilla.org/).
- **FLEURS `ar_eg`** (Google), CC BY 4.0; Conneau et al. 2022 — Egyptian read speech
  (https://huggingface.co/datasets/google/fleurs).
- **ASR Code-Switching Benchmark (Perle AI)**, MIT; Abdoli et al. 2026, arXiv:2605.19069 —
  Saudi and Egyptian Arabic–English code-switch speech
  (https://huggingface.co/datasets/Perle-ai/ASR_Code_Switch). Only 30 clips (15 Gulf, 15 technical)
  are referenced by the committed manifest; the audio is fetched from the dataset at run time.

## Application frontend and Rust crates

- Tauri 2, React 19, Vite 7, Tailwind CSS 4, Radix UI, paraglide-js and the rest of the
  JavaScript dependencies: MIT / Apache-2.0 / ISC as recorded in each package. The generated
  inventory is in [docs/licenses/node-packages.txt](./docs/licenses/node-packages.txt).
- Rust crates: mostly MIT or Apache-2.0. The generated inventory is in
  [docs/licenses/rust-crates.txt](./docs/licenses/rust-crates.txt).

## Fonts — SIL Open Font License 1.1

- **IBM Plex Sans Arabic** (added by this fork, Regular/Medium/SemiBold/Bold):
  © IBM, SIL OFL 1.1 — [docs/licenses/OFL-IBM-Plex-Sans-Arabic.txt](./docs/licenses/OFL-IBM-Plex-Sans-Arabic.txt)
- **Rubik** (inherited from upstream, Regular/Bold): © The Rubik Project Authors, SIL OFL 1.1 —
  [docs/licenses/OFL-Rubik.txt](./docs/licenses/OFL-Rubik.txt)
- **Inter** (inherited from upstream, variable font): © The Inter Project Authors, SIL OFL 1.1 —
  [docs/licenses/OFL-Inter.txt](./docs/licenses/OFL-Inter.txt)

The OFL allows bundling and modification, but the fonts (or any modified versions) may not be
sold on their own and any modification must not use the reserved font names.

## Trademarks

"Vibe" and the Vibe logo belong to the original author. This fork's name (صدى / Sada) and icon
are its own. Attribution to the upstream project appears in Settings → About and in NOTICE.

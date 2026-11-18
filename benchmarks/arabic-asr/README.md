# Arabic ASR benchmark harness

Measurement harness for Arabic speech recognition quality. Model curation decisions
(`ROADMAP.md`, milestone v3.5.0) must be data, not vibes: this harness turns a set of
reference-transcribed Arabic clips into WER/CER, acronym-preservation, timestamp and
speed tables that are comparable across models.

It is a development tool: it is not bundled in the installer, it does not run inside the
app, and it never talks to the network during transcription. Only the one-time clip
fetch contacts the Hugging Face dataset viewer.

## Data sources and licences

Audio is **never committed**. `manifest.json` records the dataset, config, split, row
offset and reference transcript for every clip; `fetch` downloads the audio, converts it
to 16 kHz mono WAV and re-validates the reference so a changed dataset row cannot
silently corrupt a measurement. Only corpora whose licence permits commercial use are
included.

| Slice | Clips | Source | Licence | Attribution |
| --- | --- | --- | --- | --- |
| `msa` | 30 | Common Voice 18 Arabic, `validation` split (read MSA sentences, multi-speaker) | CC0-1.0 | Common Voice 18.0 Arabic (Mozilla) |
| `latin-mixed` | 10 | Common Voice 18 Arabic, `test` split, rows whose reference contains Latin proper nouns | CC0-1.0 | Common Voice 18.0 Arabic (Mozilla) |
| `egyptian` | 20 | FLEURS `ar_eg`, `test` split (read Egyptian Arabic, multi-speaker) | CC-BY-4.0 | FLEURS (Google), Conneau et al. 2022 |

Pending slices (no clip yet, kept visible so the gap is not mistaken for a measurement):

* `technical` -- Common Voice 18 Arabic references contain no tracked Latin acronyms
  (only 16 of 10,471 `test` rows contain any Latin text, all proper nouns), and no
  Arabic/English code-switching speech corpus with a commercial-use licence was found
  (LDC/ELRA corpora and research-only sets are excluded by the fork licence policy).
  `latin-mixed` is the closest available proxy: real read speech with Latin names, scored
  with the Latin-name preservation metric below. Adding a permissive code-switching corpus
  is a manifest entry away.
* `iraqi`, `gulf`, `levantine` -- no corpus with a commercial-use licence was found.
  Research-only corpora such as MADAR are excluded by the fork licence policy
  (`THIRD-PARTY-NOTICES.md`, `docs/MODELS-COUNCIL.md` section 7).

## Layout

```
benchmarks/arabic-asr/
  manifest.json          committed clip selection (60 clips, 3 slices): reference, offset, licence
  models.example.json    template for models.local.json (machine paths, not committed)
  sadabench/             harness package (pure Python standard library)
    normalize.py         Arabic/Latin normalisation and the acronym list
    metrics.py           WER/CER, acronym preservation, word-timestamp parsing, aggregation
    datasets.py          dataset access, clip selection, manifest build/fetch
    engine.py            runs vibe-server transcribe for one clip/model
    report.py            aggregation tables, curation rule, Markdown rendering
    __main__.py          CLI: build-manifest, fetch, run, report
  results/               committed tables and raw transcripts from real runs
  tests/                 unit tests (offline, no models needed)
```

## Requirements

* Python 3.10+ (standard library only; CI uses 3.12).
* FFmpeg on `PATH` (or pass `--ffmpeg`).
* The patched engine: `%LOCALAPPDATA%\Sada\vibe-server.exe` from an installed Sada
  build, or `desktop/src-tauri/binaries/vibe-server-x86_64-pc-windows-msvc.exe`.
* Model files on disk (never in the repository): see `docs/MODELS.md` for the catalogue
  sizes and hashes, or download them through the app.

## Quick start

```powershell
cd benchmarks/arabic-asr
python -m sadabench build-manifest --out manifest.json   # only when extending the clip set
python -m sadabench fetch --ffmpeg ffmpeg                # downloads + converts clips into audio/
Copy-Item models.example.json models.local.json          # then edit paths/sizes
python -m sadabench run --engine "$env:LOCALAPPDATA\Sada\vibe-server.exe" --out results/results-2026-11-18.json
python -m sadabench report --results results/results-2026-11-18.json
```

`run` reads `models.local.json`, transcribes each clip, and writes every transcript,
latency and timestamp flag to the results JSON. `report` prints the Markdown tables and
writes them next to the JSON. `--only model-a,model-b` and `--limit N` shorten a run;
`--baseline` sets the model the curation rule compares against.

## Results (2026-11-18, milestone v3.5.0)

60 clips (30 MSA + 10 Latin-mixed + 20 Egyptian), four models, bundled engine
`vibe-server v0.6.16-sada.1` on Vulkan, RTX 4000. Committed artefacts:
`results/results-2026-11-18.json` (raw transcripts, timings, flags) and
`results/results-2026-11-18.md` (tables). Decisions and the curation outcome are recorded in
[`docs/MODELS-DECISIONS.md`](../../docs/MODELS-DECISIONS.md).

| Model | Size MB | WER % | CER % | Latin names kept % | Timestamps % | RTF |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| whisper-large-v3-turbo (baseline, default) | 1624.6 | 19.46 | 8.34 | 25.0 | 100.0 | 0.35 |
| nemotron-3.5-asr-streaming-0.6b-q4-k-m | 495.8 | 17.12 | 8.28 | 0.0 | 100.0 | 0.234 |
| whisper-large-v3-turbo-arabic-dialectal-v2-q5 | 574.0 | 23.09 | 9.53 | 0.0 | 100.0 | 0.265 |
| whisper-tiny | 77.7 | 70.56 | 29.46 | 0.0 | 100.0 | 0.186 |

WER % by slice:

| Model | msa | egyptian | latin-mixed |
| --- | ---: | ---: | ---: |
| whisper-large-v3-turbo | 22.09 | 11.03 | 48.96 |
| nemotron-3.5-asr-streaming-0.6b-q4-k-m | 17.83 | 9.11 | 50.00 |
| whisper-large-v3-turbo-arabic-dialectal-v2-q5 | 23.64 | 14.39 | 59.38 |
| whisper-tiny | 72.09 | 64.03 | 94.79 |

## Second-engine spike (issue #13)

transcribe.cpp v0.4.2 (MIT, built from source for Windows CPU) + Qwen3-ASR 0.6B Q8_0
(850 MB, Apache-2.0, `handy-computer/Qwen3-ASR-0.6B-gguf`) over the same 60 clips: batch wall
241.9 s (one 269 ms load), 60/60 transcribed, WER 24.38% overall (MSA 20.54%, Egyptian 21.10%,
Latin-mixed 48.96%), Latin names 10%, **no timestamps** (`TIMESTAMPS_NONE`), no VAD. Raw results:
`results/results-2026-11-18-transcribe-cpp.json`. Verdict in
[`docs/MODELS-DECISIONS.md`](../../docs/MODELS-DECISIONS.md): not integrated.

## Models under test

| id (example) | family | size | language | notes |
| --- | --- | --- | --- | --- |
| `whisper-large-v3-turbo` | whisper | 1624.6 MB | `ar` | current default |
| `whisper-tiny` | whisper | 77.7 MB | `ar` | slow-machine fallback |
| `nemotron-3.5-asr-streaming-0.6b-q4-k-m` | nemotron | 495.8 MB | `ar-AR` | requires `--vad-model`; no translate/prompt |
| `whisper-large-v3-turbo-arabic-dialectal-v2-q5` | whisper-finetune | 574.0 MB | `ar` | Arabic dialectal fine-tune candidate |

Model files are referenced only from `models.local.json`; nothing model-sized is added to
git. `run` checks that every path exists before starting.

## Metrics

* **WER / CER**: corpus-level sums (`sum(S+D+I) / sum(N_ref)`) after normalisation;
  per-clip transcripts are kept in the results JSON.
* **Normalisation**: Arabic diacritics and tatweel removed; hamza forms unified
  (`أ إ آ ٱ` to `ا`, `ؤ` to `و`, `ئ` to `ي`); alef maqsura to yeh; Arabic-Indic digits to
  ASCII; punctuation replaced with spaces; Latin lowercased. Ta marbuta is kept so real
  spelling errors are not hidden.
* **Acronym preservation**: occurrences of tracked Latin acronyms (`GPU`, `CPU`, `PDF`,
  `SRT`, `VTT`, `MCP`, `API`, ... see `normalize.ACRONYMS`) in the reference; preserved when
  the hypothesis contains the acronym after lowercasing and removing separators, so
  `B.D.F` counts for `BDF` but a transliteration such as `بي ديف` does not.
* **Latin-name preservation**: same idea generalised to every Latin-script word of two or
  more letters in the reference (`Diadem`, `Braintree`, `Queens`), which measures how the
  engine handles code-switched proper nouns even where no acronym appears.
* **Timestamps**: a clip counts as covered only when the engine emits monotonic timed
  words on every line; the summary reports the share of covered clips.
* **Speed**: latency is wall time per clip including one engine process start and model
  load, so it is pessimistic compared with the long-lived app server; report RTF as a
  relative ordering, not an absolute app speed.

## Curation rule

From `docs/MODELS-COUNCIL.md` section 6: curate a challenger only if it beats
`whisper-large-v3-turbo` by at least **1.0 pp WER** on its target slice, keeps timestamps
on that slice (100%) and preserves at least **90%** of Latin acronyms there. Nemotron gets
an optional catalogue entry only if it wins its slice. The `report` command evaluates the
rule per slice and prints PASS/no for every challenger.

## Adding clips

1. Pick a corpus whose licence permits commercial use; record licence and attribution in
   `DATASET_LICENCES` (`sadabench/datasets.py`).
2. Add an entry to `manifest.json`: unique `id`, `slice`, the exact `reference` text,
   and `source` with `dataset`, `config`, `split`, `offset` and `revision`.
3. Run `fetch`; it looks the row up at the stored offset, refuses if the reference text
   changed, and converts the audio. Keep audio out of git (`audio/` is ignored).
4. Run the models and `report`; commit the results JSON + Markdown as evidence.

## Tests

```powershell
cd benchmarks/arabic-asr
python -m unittest discover -s tests -v
```

The tests are offline and cover normalisation, WER/CER edge cases, acronym and Latin-name
matching, timestamp parsing, manifest metadata and the aggregation/curation rule. CI runs
them on every push and pull request; the model runs are manual because they need weights
and a GPU/CPU budget.

## Privacy and offline behaviour

Transcription runs the local engine only; no audio, transcript or telemetry leaves the
machine. The `build-manifest` and `fetch` commands contact the Hugging Face dataset
viewer to read rows and download audio, and the `fetch` step needs network only once per
clip. Results are files on disk, nothing else.


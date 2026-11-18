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
| `gulf` | 15 | Perle AI code-switch benchmark, `train` split, Saudi Arabic (Najdi/Hijazi)--English rows | MIT | Perle AI, [ASR_Code_Switch](https://huggingface.co/datasets/Perle-ai/ASR_Code_Switch), Abdoli et al. 2026 |
| `technical` | 15 | Perle AI code-switch benchmark, `train` split, Egyptian Arabic--English rows (the remainder uses unused Saudi rows) | MIT | Perle AI, [ASR_Code_Switch](https://huggingface.co/datasets/Perle-ai/ASR_Code_Switch), Abdoli et al. 2026 |

The Perle corpus is **conversational but scripted**: the paper (arXiv:2605.19069, section 3.2)
describes transcripts collected from native speakers and audio recorded by recruited voice
actors, so provenance is clean (no scraped broadcast audio) and the references are human, not
machine, transcripts. The two Perle slices are code-switched by construction: the Gulf slice is
Saudi Arabic + English, the technical slice is Egyptian Arabic + English. They are labelled as
code-switch slices, not as "pure dialect" measurements.

Pending slices (no clip yet, kept visible so the gap is not mistaken for a measurement):

* `iraqi`, `levantine` -- still no free, commercial-use-permissive corpus with human
  transcripts found as of 2026-11-18. Examined and rejected: QASR (CC BY-NC), ArSyra
  iraqi/levantine (CC BY-NC-SA, gated), m6011/sada2022 (licence contradiction between card
  tag and README), MADIS5 (ambiguous `cc` + dialect-ID labels only), MASC and its derivative
  feature sets (YouTube provenance; distributed CSVs carry no dialect labels), Ghadeer (no
  explicit data licence), UFAL Levantine and IWSLT Levantine data (research licences), Lahgtna
  (synthetic TTS audio), LDC/ELRA (paid research licences). A paid vendor corpus (for example
  SpeechDataAI) remains an owner purchase decision, not an engineering one.
  `latin-mixed` stays as the real read-speech proxy for Latin proper nouns.

## Layout

```
benchmarks/arabic-asr/
  manifest.json          committed clip selection (90 clips, 5 slices + 2 pending): reference, offset, licence
  prompts/               initial-prompt variants measured for prompt biasing (issue #20)
  models.example.json    template for models.local.json (machine paths, not committed)
  fixtures/              shared post-processing fixtures asserted by Python and vitest
  sadabench/             harness package (pure Python standard library)
    normalize.py         Arabic/Latin normalisation and the acronym list
    metrics.py           WER/CER, acronym preservation, word-timestamp parsing, aggregation
    datasets.py          dataset access, clip selection, manifest build/fetch
    engine.py            runs vibe-server transcribe for one clip/model
    postprocess.py       Python mirror of the app's Arabic post-processing (app-level scores)
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
python -m sadabench build-manifest --out manifest.json --reuse manifest.json   # only when extending the clip set
python -m sadabench fetch --ffmpeg ffmpeg                # downloads + converts clips into audio/
Copy-Item models.example.json models.local.json          # then edit paths/sizes
python -m sadabench run --engine "$env:LOCALAPPDATA\Sada\vibe-server.exe" --out results/results-2026-11-18.json
python -m sadabench report --results results/results-2026-11-18.json
```

`build-manifest --reuse existing.json` keeps the clips of slices whose count did not change
(they are deterministic on a pinned revision) and only re-scans the slices being extended, so a
single extension does not re-walk 110 pages of Common Voice and does not trip the viewer's rate
limits. `run` reads `models.local.json`, transcribes each clip, and writes every transcript,
latency and timestamp flag to the results JSON. `report` prints the Markdown tables and
writes them next to the JSON. `--only model-a,model-b` and `--limit N` shorten a run;
`--baseline` sets the model the curation rule compares against.

`report` renders two tables. The **raw** table scores engine output directly and is what the
curation rule uses. The **app-level** table applies the app's Arabic post-processing to every
hypothesis first, so it describes what users actually see: `desktop/src/lib/arabic-text.ts`
normalises punctuation and restores transliterated technical terms (GPU, PDF, SRT, URL, ...),
and `sadabench/postprocess.py` mirrors that module. The two implementations assert the same
`fixtures/arabic-postprocess-cases.json`, so a rule added to one side without the other fails
a test instead of drifting; `tests/test_postprocess.py` also proves the glossary never rewrites
the committed reference sentences.

## Results (2026-11-18, milestone v3.7.0)

90 clips (30 MSA + 10 Latin-mixed + 20 Egyptian + 15 Gulf + 15 technical), five model variants,
bundled engine `vibe-server v0.6.16-sada.1` on Vulkan, RTX 4000. Committed artefacts:
`results/results-2026-11-18-v2.json` (raw transcripts, timings, flags) and
`results/results-2026-11-18-v2.md` (tables); the earlier 60-clip run is kept as
`results/results-2026-11-18.json`/`.md` for history. Decisions and the curation outcome are
recorded in [`docs/MODELS-DECISIONS.md`](../../docs/MODELS-DECISIONS.md) and the plan in
[`docs/P4-PLAN.md`](../../docs/P4-PLAN.md).

| Model | Size MB | WER % | CER % | Latin names kept % | Timestamps % | RTF |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| whisper-large-v3-turbo (baseline, default) | 1624.6 | 30.27 | 18.84 | 27.3 | 100.0 | 0.38 |
| whisper-tiny | 77.7 | 78.48 | 42.28 | 4.4 | 100.0 | 0.188 |
| nemotron-3.5-asr-streaming-0.6b-q4-k-m | 495.8 | 35.16 | 24.06 | 0.0 | 100.0 | 0.215 |
| whisper-large-v3-turbo-arabic-dialectal-v2-q5 | 574.0 | 32.60 | 21.71 | 10.4 | 100.0 | 0.384 |
| whisper-large-v3-turbo-prompt (glossary prompt) | 1624.6 | 31.44 | 18.95 | 38.8 | 100.0 | 0.352 |

WER % by slice:

| Model | msa | latin-mixed | egyptian | gulf | technical |
| --- | ---: | ---: | ---: | ---: | ---: |
| whisper-large-v3-turbo | 22.09 | 48.96 | 11.03 | 42.74 | 46.18 |
| whisper-tiny | 72.09 | 94.79 | 64.03 | 90.31 | 86.35 |
| nemotron-3.5-asr-streaming-0.6b-q4-k-m | 17.83 | 50.00 | 9.11 | 59.83 | 56.22 |
| whisper-large-v3-turbo-arabic-dialectal-v2-q5 | 23.64 | 59.38 | 14.39 | 41.60 | 49.40 |
| whisper-large-v3-turbo-prompt (glossary prompt) | 23.26 | 55.21 | 11.75 | 42.45 | 48.19 |

Latin-name preservation % by slice (share of Latin-script words in the reference that survive):

| Model | latin-mixed | gulf | technical |
| --- | ---: | ---: | ---: |
| whisper-large-v3-turbo | 25.0 | 22.6 | 34.3 |
| whisper-tiny | 0.0 | 2.2 | 8.6 |
| nemotron-3.5-asr-streaming-0.6b-q4-k-m | 0.0 | 0.0 | 0.0 |
| whisper-large-v3-turbo-arabic-dialectal-v2-q5 | 0.0 | 12.9 | 10.0 |
| whisper-large-v3-turbo-prompt (glossary prompt) | 25.0 | 35.5 | 47.1 |

How to read the new slices:

* **Gulf (42.74%) and technical (46.18%) are genuinely hard.** They are conversational,
  code-switched speech: the Gulf slice is Saudi Arabic + English, the technical slice is Egyptian
  Arabic + English, both recorded by voice actors from collected conversational transcripts
  (human references). WER is roughly double the Egyptian read-speech number for the same model,
  which is the honest measure of the gap rather than a claim of dialect coverage.
* **Nemotron confirms the v3.5 decision.** It still wins MSA (17.83%) and Egyptian (9.11%) but is
  17-19 pp behind Turbo on both code-switch slices and keeps **0%** of Latin words. It stays an
  optional dictation entry, not the default.
* **The dialectal fine-tune has the raw Gulf edge, not a significant one.** It is 1.14 pp better
  than Turbo on the Gulf slice at corpus level (41.60% vs 42.74%), which technically clears the
  1.0 pp rule, but a per-clip bootstrap (10,000 resamples) puts the WER delta at -0.90 pp with a
  95% CI of [-10.06, +8.28] — it spans zero, so it is **not curated**; it stays a documented
  experiment. It also loses on every other slice.
* **The glossary prompt trades accuracy for Latin terms.** It raises Latin-word preservation
  (technical 47.1% vs 34.3%, Gulf 35.5% vs 22.6%) but costs WER overall (31.44% vs 30.27%) and on
  latin-mixed (55.21% vs 48.96%), so no prompt preset is shipped; the decision and numbers are in
  the prompt spike below and in [`docs/MODELS-DECISIONS.md`](../../docs/MODELS-DECISIONS.md).

## Prompt biasing spike (issue #20, 2026-11-18)

Four variants on 40 clips (10 latin-mixed + 30 MSA), same `ggml-large-v3-turbo.bin` weights,
engine `--prompt` support, committed prompt texts under `prompts/`:

| Variant | WER % overall | WER % latin-mixed | WER % msa | Latin names kept % | RTF |
| --- | ---: | ---: | ---: | ---: | ---: |
| no prompt (baseline) | 29.38 | 48.96 | 22.09 | 25.0 | 0.407 |
| Arabic + Latin glossary (`arabic-technical-glossary.txt`) | 31.92 | 55.21 | 23.26 | 25.0 | 0.431 |
| English-only glossary (`english-terms.txt`) | 38.42 | 72.92 | 25.58 | 30.0 | 0.468 |
| Arabic-only instruction (`arabic-only-terms.txt`) | 31.36 | 48.96 | 24.81 | 25.0 | 0.497 |

Every variant is worse or neutral: an initial prompt does not fix transliterated Latin terms in
this engine/model, it biases the decoder enough to cost WER. Raw results:
`results/prompt-spike-v1.json`/`.md`. The app's existing user-editable prompt field stays
available and unchanged; no preset is wired.

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
| `whisper-large-v3-turbo-prompt` | whisper | 1624.6 MB | `ar` | same Turbo weights with a `prompt_file` initial prompt |

Model files are referenced only from `models.local.json`; nothing model-sized is added to
git. `run` checks that every path exists before starting. A model entry may carry
`prompt` (inline text) or `prompt_file` (path relative to the models file, for example
`prompts/arabic-technical-glossary.txt`); the harness passes it as one `--prompt=<text>`
argument and records its SHA-256 in the results metadata.

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


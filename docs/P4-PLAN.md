# P4 plan — dialect coverage and prompt biasing (v3.7.0)

Status: **complete 2026-11-18** (v3.7.0). Milestone
[v3.7.0](https://github.com/alshahia/sada/milestone/5), issues
[#19](https://github.com/alshahia/sada/issues/19) (corpus),
[#20](https://github.com/alshahia/sada/issues/20) (prompt) and
[#21](https://github.com/alshahia/sada/issues/21) (docs + release).

After v3.6.0 the honest gaps in the Arabic benchmark were: no measured Gulf, Iraqi, Levantine or
technical-slice rows, and a known Latin-name loss for Nemotron/turbo that the app fixed only at
display time (term restoration). P4 closes what can be closed with commercial-use data, records
what cannot, and measures whether an initial prompt fixes the raw-model problem instead of only
the display.

## A. Corpus expansion (issue #19)

Policy does not move: benchmark audio is fetched at run time, never committed, and every source
must carry a commercial-use licence (CC0, CC BY 4.0, CC BY-SA 4.0, MIT, Apache-2.0).

### Accepted

| Source | Licence | Slice | Why |
| --- | --- | --- | --- |
| [Perle-ai/ASR_Code_Switch](https://huggingface.co/datasets/Perle-ai/ASR_Code_Switch) | MIT | `gulf`, `technical` | 1,200 Saudi (Najdi/Hijazi) and Egyptian Arabic–English code-switch utterances. The paper (arXiv:2605.19069, §3.2) states the audio was **recorded by native voice actors** from collected conversational transcripts, so provenance is clean; references are human transcripts. |
| [Common Voice 18 Arabic](https://huggingface.co/datasets/MohamedRashad/common-voice-18-arabic) | CC0 1.0 | `msa`, `latin-mixed` | already used; no change |
| [FLEURS ar_eg](https://huggingface.co/datasets/google/fleurs) | CC BY 4.0 | `egyptian` | already used; no change |

### Examined and rejected

| Source | Claimed licence | Why rejected |
| --- | --- | --- |
| QCRI/QASR | CC BY-NC 2.0 | non-commercial |
| ArSyra arsyra-iraqi / arsyra-levantine | CC BY-NC-SA 4.0, gated | non-commercial |
| m6011/sada2022 (SADA, SDAIA) | card tag CC BY 4.0 but README says CC BY-NC-SA 4.0 | contradiction, treat as non-commercial |
| badrex/MADIS5-spoken-arabic-dialects | "cc" (unspecified) | no transcripts (dialect ID only), licence ambiguous |
| Geethuzzz/spoken-arabic-dialects-with-transcriptions | none | transcriptions are machine-generated, not ground truth |
| SpeechDataAI gulf/levantine conversational speech | commercial vendor licence | paid data; infrastructure could consume it only after a purchase decision |
| pain/MASC | CC BY 4.0 | YouTube-crawled provenance, and the distributed transcript CSV has no dialect/country labels, so rows cannot be attributed to a dialect slice |
| otozz/iraqi, gulf, levantine, egyptian sets | CC BY 4.0 | pre-processed Whisper log-mel features + token labels of MASC, not audio; unusable for this harness and inherits the MASC provenance question |
| CATT / other dialect corpora | research-only or unknown | not commercial-use |

Iraqi and Levantine stay **pending** and visible in the slice table. The honest statement remains:
no free, commercial-use, transcript-bearing Iraqi or Levantine corpus was found on 2026-11-18.
A paid vendor corpus (for example SpeechDataAI, or an LDC commercial licence) is an option for a
future phase; it needs an owner purchase decision.

### Manifest v2

- 90 clips: 30 MSA, 20 Egyptian, 10 Latin-mixed, 15 Gulf (Saudi code-switch), 15 technical
  (Egyptian code-switch).
- Perle rows are chosen deterministically by even spacing across each language pair, pinned by
  dataset revision and row offset, like the existing sources.
- The technical slice is Egyptian Arabic–English only; the Gulf slice is Saudi Arabic–English only,
  so no clip is counted twice. Both are code-switched by construction and the slice labels say so —
  they are not a "pure dialect" claim.
- Re-running `sadabench build-manifest` must reproduce the same ids/offsets on the same revision.

## B. Prompt biasing (issue #20)

Whisper models accept an initial prompt; the app already exposes `modelOptions.init_prompt` (shown
only for models whose capabilities report `text_prompts`) but ships it empty. The engine exposes
`--prompt`.

Experiment:

1. Four variants on the Latin-mixed and MSA slices, same weights
   (`ggml-large-v3-turbo.bin`): no prompt, Arabic+Latin glossary, English-only glossary,
   Arabic-only instruction.
2. Metrics: WER, CER, Latin/acronym preservation, and a no-regression check on MSA and Egyptian.
3. If the glossary wins by a documented margin with no measured regression, add a one-click
   "technical glossary" action to Settings → Whisper options (capability-gated, i18n, never
   silently changes a user's existing prompt), and report the winning prompt in the benchmark
   results table. Otherwise document the negative result and wire nothing.
4. Nemotron 3.5 reports no text-prompt capability in `sada_info`; confirm the engine behaviour
   with `--prompt` before claiming anything about it.

Prompt files are committed under `benchmarks/arabic-asr/prompts/` so a rerun is reproducible;
`models.example.json` documents the `prompt_file` field.

## Acceptance criteria

- Licensed slices fetched, benchmark run on all pinned models, per-slice WER/CER and Latin-name
  preservation in `results/results-2026-11-18-v2.md`; README/report state the corpus character
  (scripted code-switch speech for Perle) and the remaining pending slices.
- Prompt decision recorded with numbers; app wiring only if it wins and the suite stays green.
- Python harness tests, frontend tests, Rust tests, i18n audit and build all pass; docs and release
  notes updated; v3.7.0 released and the installer verified by re-download.

## Outcome (2026-11-18)

- Manifest v2 built with 90 clips and fetched 90/90 WAVs (0 failures), reusing the pinned
  60 clips instead of re-scanning the Common Voice viewer.
- Full run: 450 transcriptions (5 model variants × 90 clips) on the bundled engine
  `vibe-server v0.6.16-sada.1` (Vulkan). Turbo stays at 30.27% overall WER with Gulf 42.74% and
  technical 46.18%; Nemotron keeps its MSA/Egyptian wins but loses 17–19 pp on both code-switch
  slices; the dialectal fine-tune's 1.14 pp Gulf edge has a bootstrap 95% CI of [-10.06, +8.28],
  so it is not curated.
- Prompt biasing: **negative**. Arabic+Latin glossary 31.92% vs 29.38% no-prompt WER on the
  40-clip spike (English-only 38.42%, Arabic-only 31.36%); on the full corpus the glossary keeps
  more Latin words but costs +1.17 pp WER. No preset shipped and no UI change.
- Iraqi and Levantine remain pending; the rejected-corpus list above is the record of the search.
- Evidence: [`results/results-2026-11-18-v2.md`](../benchmarks/arabic-asr/results/results-2026-11-18-v2.md),
  [`results/prompt-spike-v1.md`](../benchmarks/arabic-asr/results/prompt-spike-v1.md) and
  [MODELS-DECISIONS.md](MODELS-DECISIONS.md).

## Reproduction

```powershell
cd app/benchmarks/arabic-asr
python -m sadabench build-manifest --out manifest.json
python -m sadabench fetch --manifest manifest.json --audio-dir audio --ffmpeg ffmpeg
python -m sadabench run --manifest manifest.json --audio-dir audio --models models.local.json \
  --engine <vibe-server.exe> --out results/results-2026-11-18-v2.json
python -m sadabench report --results results/results-2026-11-18-v2.json
```

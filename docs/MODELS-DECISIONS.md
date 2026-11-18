# Arabic model decisions (milestone v3.5.0)

Status: **decided 2026-11-18** with measured evidence from the Arabic benchmark harness.
This record closes issues #10, #11, #12 and #13 of milestone v3.5.0 and implements the
decision rule in [docs/MODELS-COUNCIL.md](MODELS-COUNCIL.md) section 6:

> curate a challenger only if it beats `whisper-large-v3-turbo` by at least **1.0 pp WER**
> on its target slice, keeps word timestamps (100%) and preserves at least **90%** of Latin
> acronyms there; Nemotron gets an optional catalogue entry only if it wins its dictation
> slice (latency/size/punctuation).

## What was measured

- **Harness:** `benchmarks/arabic-asr/` (stdlib Python, no app code). It builds a clip
  manifest from pinned dataset revisions, fetches the audio once, normalises Arabic text,
  scores corpus-level WER/CER, acronym and Latin-name preservation and word-timestamp
  coverage, and evaluates the curation rule per slice.
- **Corpora (commercial-use-permissive only):** Common Voice 18 Arabic (CC0, 30 MSA + 10
  Latin-mixed read-speech clips) and FLEURS `ar_eg` test (CC BY 4.0, 20 Egyptian clips).
  Audio is never committed; `manifest.json` records dataset, split, offset, revision and
  the reference transcript.
- **Engine:** bundled `vibe-server v0.6.16-sada.1` (this repository's build), Vulkan GPU,
  60 clips per model, 2026-11-18. Raw results and tables:
  [`benchmarks/arabic-asr/results/results-2026-11-18.json`](../benchmarks/arabic-asr/results/results-2026-11-18.json)
  and `.md`.
- **Not measurable yet:** Iraqi, Gulf, Levantine and Arabic/English technical speech, because
  no corpus with a commercial-use licence was found (research-only corpora such as MADAR are
  excluded by the fork policy). The `latin-mixed` slice is the honest stand-in for
  code-switched terms: real read speech whose reference contains Latin proper nouns.
  The ≥90% *acronym* gate could not be tested — Common Voice Arabic references contain no
  tracked Latin acronyms — so it is recorded as **not applicable**, not as passed.

## Results (60 clips, higher is worse except acronyms/Latin/timestamps)

| Model | Size MB | WER % | CER % | Latin names kept % | Timestamps % | RTF |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| whisper-large-v3-turbo (baseline, default) | 1624.6 | 19.46 | 8.34 | 25.0 | 100.0 | 0.35 |
| nemotron-3.5-asr-streaming-0.6b-q4-k-m | 495.8 | **17.12** | 8.28 | 0.0 | 100.0 | **0.234** |
| whisper-large-v3-turbo-arabic-dialectal-v2-q5 | 574.0 | 23.09 | 9.53 | 0.0 | 100.0 | 0.265 |
| whisper-tiny (kept only as the low-resource fallback) | 77.7 | 70.56 | 29.46 | 0.0 | 100.0 | 0.186 |

WER by slice:

| Model | msa | egyptian | latin-mixed |
| --- | ---: | ---: | ---: |
| whisper-large-v3-turbo | 22.09 | 11.03 | 48.96 |
| nemotron-3.5-asr-streaming-0.6b-q4-k-m | **17.83** | **9.11** | 50.00 |
| whisper-large-v3-turbo-arabic-dialectal-v2-q5 | 23.64 | 14.39 | 59.38 |
| whisper-tiny | 72.09 | 64.03 | 94.79 |

Timestamps were produced on 100% of clips by every Whisper/Nemotron model, so the timestamp
gate did not separate them; the WER and code-switching gates did.

## Decisions

### 1. Whisper large-v3-turbo — default stays

Best overall balance: 19.46% WER, 100% timestamps, and the only model that keeps a quarter of
the Latin proper nouns intact (25%) on real code-switched read speech. It remains the default
and the baseline for every future comparison.

### 2. Nemotron 3.5 ASR Streaming 0.6B — curated as an **optional** entry

It wins its dictation slice on the numbers that the council said matter: MSA WER 17.83% vs
22.09% (gain 4.26 pp ≥ 1.0 pp), Egyptian WER 9.11% vs 11.03% (gain 1.92 pp), 100% timestamps,
faster (RTF 0.234 vs 0.35) and 3.3× smaller (496 MB vs 1.62 GB), with punctuation on by default.
It is therefore added to the bundled catalogue (`desktop/src/assets/model-catalog.json`) under
OpenMDW-1.1 with size and SHA-256 verified against the published GGUF
(`41c99fa5…b8fd`, 495,831,520 bytes, mirror `vibe-app/nemotron-3.5-asr-streaming-0.6b-gguf`),
and the app already supplies the Silero VAD file it requires.

It is **not** the default and never replaces Turbo for Arabic/English mixing: it transliterates
Latin technical terms (`GPU` → جي بي يو) and preserved **0%** of Latin proper nouns versus 25%
for Turbo, and it ties Turbo on the latin-mixed slice WER while producing a different (spoken)
error type. Its catalogue description states both facts. The ≥90% acronym gate remains
unmeasurable, so this promotion rests on the dictation-slice clause, not on a passed acronym
gate — this is recorded explicitly rather than hidden.

### 3. Arabic Whisper fine-tunes (oddadmix turbo dialectal v2 q5_0) — **rejected**

It beats nothing: 23.09% overall WER vs 19.46% (−3.63 pp), MSA 23.64% vs 22.09%, Egyptian 14.39%
vs 11.03%, latin-mixed 59.38% vs 48.96%, Latin names 0% vs 25%. No ≥1.0 pp win on any slice, so
it is not curated. It stays a documented experiment; a different fine-tune can be retested with
the same harness by adding a `models.local.json` entry.

### 4. Read-aloud (TTS) — no-go, unchanged

See [docs/READ-ALOUD.md](READ-ALOUD.md): a normal Windows install (even with an Arabic display
language) ships English voices only, Arabic voices are an optional Narrator download that needs
network and usually elevation, and the quality rubric could not be run on the evaluation
machine. No read-aloud code was written; Chatterbox stays suspended.

### 5. Second engine (transcribe.cpp / Qwen3-ASR, Cohere Arabic) — **rejected for now, keep learning**

One-day spike on 2026-11-18, transcribe.cpp v0.4.2 (MIT) built from source for Windows
CPU (Vulkan SDK absent), Qwen3-ASR 0.6B Q8_0 (850 MB, Apache-2.0), single batch invocation over
the same 60 clips (one 269 ms model load, wall 241.9 s, 60/60 transcribed):

| Measure | Qwen3-ASR 0.6B Q8_0 (transcribe.cpp, CPU) | whisper-large-v3-turbo (vibe-server, Vulkan) |
| --- | ---: | ---: |
| WER % overall | 24.38 | 19.46 |
| WER % msa | 20.54 | 22.09 |
| WER % egyptian | 21.10 | 11.03 |
| WER % latin-mixed | 48.96 | 48.96 |
| Latin names kept % | 10.0 | 25.0 |
| Word/segment timestamps | **none** (port: `TIMESTAMPS_NONE`) | 100% words |
| VAD / diarization / translation | none | VAD yes, diarization via the separate model |

Verdict: **do not integrate a second engine in v3.x.** It is close to Turbo on MSA but 10 pp
behind on Egyptian, and — decisively — it has no timestamps, VAD or segments in the current
port, so SRT/VTT export, transcript editing and meeting views would break. The CPU/Vulkan
runtime also adds a second distribution channel and a second upkeep path for a model that does
not win. Cohere Transcribe Arabic 07-2026 advertises Apache-2.0 on its data card but is gated
upstream and is likewise timestamp-free in transcribe.cpp, so it was not downloaded.
Revisit only if a port lands word timestamps plus VAD (transcribe.cpp's Qwen3 forced-aligner
sibling is the thing to watch) or if Arabic WER/terminology support becomes decisive.

## v3.7.0 — dialect coverage and prompt biasing (2026-11-18)

The v3.5.0 record above could not measure Gulf, technical or prompt-biased output. This follow-up
extends the same harness to **90 clips / 5 slices** and answers those questions with numbers. Plan,
licence matrix and reproduction: [docs/P4-PLAN.md](P4-PLAN.md) and
[`benchmarks/arabic-asr/README.md`](../benchmarks/arabic-asr/README.md).

### What was measured

- **New slices:** 15 Gulf (Saudi Najdi/Hijazi) + 15 technical (Egyptian) Arabic–English
  code-switch clips from [Perle-ai/ASR_Code_Switch](https://huggingface.co/datasets/Perle-ai/ASR_Code_Switch)
  (MIT; audio recorded by native voice actors from collected conversational transcripts, human
  references, revision `1cc5950241e02500c43e39e8f37cce93c2dca5fb`, 30 distinct rows). Audio is
  fetched at run time, never committed; the manifest pins row offsets.
- **Prompt variants:** same `ggml-large-v3-turbo.bin` weights with four committed initial-prompt
  styles (none, Arabic+Latin glossary, English-only glossary, Arabic-only instruction) on the
  latin-mixed + MSA slices, then the winning-format candidate across all 90 clips.
- **Rejected corpora (documented so the search does not restart):** QASR (CC BY-NC 2.0), ArSyra
  iraqi/levantine (CC BY-NC-SA 4.0, gated), m6011/sada2022 (card tag CC BY 4.0 vs README
  CC BY-NC-SA 4.0 — contradiction), badrex/MADIS5 (licence "cc" unspecified, dialect-ID labels
  only), pain/MASC and its Whisper-feature derivatives (YouTube provenance; distributed CSVs carry
  no dialect labels), Ghadeer crowd corpus (no explicit data licence found), UFAL North Levantine
  and IWSLT 2024 Levantine (research licences), Lahgtna Levantine TTS (synthetic audio), LDC/ELRA
  (paid research licences), SpeechDataAI Gulf/Levantine (paid vendor licence — owner purchase
  decision, not engineering).

### Results (90 clips, engine v0.6.16-sada.1, Vulkan, 2026-11-18)

| Model | Size MB | WER % | CER % | Latin names kept % | RTF |
| --- | ---: | ---: | ---: | ---: | ---: |
| whisper-large-v3-turbo (baseline, default) | 1624.6 | 30.27 | 18.84 | 27.3 | 0.38 |
| whisper-tiny | 77.7 | 78.48 | 42.28 | 4.4 | 0.188 |
| nemotron-3.5-asr-streaming-0.6b-q4-k-m | 495.8 | 35.16 | 24.06 | 0.0 | 0.215 |
| whisper-large-v3-turbo-arabic-dialectal-v2-q5 | 574.0 | 32.60 | 21.71 | 10.4 | 0.384 |
| whisper-large-v3-turbo + glossary prompt | 1624.6 | 31.44 | 18.95 | 38.8 | 0.352 |

WER % by slice:

| Model | msa | latin-mixed | egyptian | gulf | technical |
| --- | ---: | ---: | ---: | ---: | ---: |
| whisper-large-v3-turbo | 22.09 | 48.96 | 11.03 | 42.74 | 46.18 |
| nemotron-3.5-asr-streaming-0.6b-q4-k-m | **17.83** | 50.00 | **9.11** | 59.83 | 56.22 |
| whisper-large-v3-turbo-arabic-dialectal-v2-q5 | 23.64 | 59.38 | 14.39 | **41.60** | 49.40 |
| whisper-large-v3-turbo + glossary prompt | 23.26 | 55.21 | 11.75 | 42.45 | 48.19 |
| whisper-tiny | 72.09 | 94.79 | 64.03 | 90.31 | 86.35 |

Latin-name preservation % (Gulf / technical): Turbo 22.6 / 34.3, dialectal fine-tune 12.9 / 10.0,
Nemotron 0.0 / 0.0, glossary prompt 35.5 / 47.1.

### Decisions

1. **Whisper large-v3-turbo stays the default** — no measured challenger wins overall, and it is
   still the only model that keeps a meaningful share of Latin terms in any slice.
2. **Nemotron 3.5 keeps its optional catalogue entry, not promotion** — it still wins MSA
   (17.83%) and Egyptian (9.11%) but is 17-19 pp behind Turbo on the new code-switch slices and
   preserves 0% of Latin words there. The v3.5 caveat is now measured, not assumed.
3. **The Arabic dialectal fine-tune is not curated.** It is the only model with a raw Gulf win:
   41.60% vs 42.74% WER = 1.14 pp, clearing the 1.0 pp rule at corpus level. A per-clip bootstrap
   (10,000 resamples) gives a mean delta of -0.90 pp with 95% CI [-10.06, +8.28] — the 15-clip
   slice cannot distinguish it from Turbo — and it loses every other slice (MSA +1.55, Egyptian
   +3.36, latin-mixed +10.42, technical +3.22 pp), with Latin preservation below Turbo. Rule
   technically passed, evidence too weak to ship; recorded instead of promoted.
4. **Prompt biasing is a measured no.** Arabic+Latin glossary 31.92% WER vs 29.38% no-prompt,
   English-only glossary 38.42%, Arabic-only instruction 31.36% on the 40-clip spike; on the full
   corpus the glossary prompt preserves more Latin words (technical 47.1% vs 34.3%) but costs WER
   (+1.17 pp overall, +6.25 pp latin-mixed). The app does **not** ship a prompt preset and does not
   change the user's existing free-text prompt field; the trade-off is documented for users who
   choose to type their own prompt.
5. **No app runtime change in v3.7.0** — engine, models, catalogue and UI behaviour are identical
   to v3.6.0. This is a coverage/evidence release plus the version bump that produces the installer.

### Remaining gaps (stated, not hidden)

- **Iraqi and Levantine are still unmeasured**: no free, commercial-use-permissive corpus with
  human transcripts was found; the candidate list with licence reasons is in
  [docs/P4-PLAN.md](P4-PLAN.md).
- **The Perle slices are scripted code-switch conversation**, not spontaneous dialect speech;
  the Gulf slice is Saudi Najdi/Hijazi only and the technical slice is Egyptian only. They do not
  stand in for Iraqi/Levantine.
- **The ≥90% acronym gate is still not applicable**: none of the 90 reference transcripts contains
  one of the app's tracked acronyms (GPU, PDF, SRT, ...), so it is recorded as n/a rather than
  passed. Latin-name preservation is the honest proxy.
- 15-clip slices give wide confidence intervals; treat slice-level deltas under ~2 pp as
  unresolved unless a bootstrap says otherwise.

## Reproduce

```powershell
cd benchmarks/arabic-asr
python -m sadabench fetch --ffmpeg ffmpeg            # one-time, network
python -m sadabench run --engine "$env:LOCALAPPDATA\Sada\vibe-server.exe" \
  --models models.local.json --out results/results-2026-11-18-v2.json
python -m sadabench report --results results/results-2026-11-18-v2.json
# prompt spike (same weights, prompt variants in models.prompt-spike.json):
python -m sadabench run --manifest manifest.v1.json --slices latin-mixed,msa \
  --models models.prompt-spike.json --engine "$env:LOCALAPPDATA\Sada\vibe-server.exe" \
  --out results/prompt-spike-v1.json
```

The transcribe.cpp spike command, model URLs and hashes are in
[`benchmarks/arabic-asr/README.md`](../benchmarks/arabic-asr/README.md) and the
`results-2026-11-18-transcribe-cpp.json` artefact.

## What would change these decisions

- A commercial-use-permissive Iraqi/Levantine corpus with human transcripts appears (the Gulf and
  code-switch gap is now measured) → extend `manifest.json` and rerun; Nemotron's code-switch
  weakness is already measured, and a corpus with real acronyms would finally exercise the ≥90%
  acronym gate that is n/a today.
- A larger (60+ clip) Gulf corpus becomes available → retest the dialectal fine-tune; its 1.14 pp
  Gulf edge is inside the current confidence interval.
- A different Arabic fine-tune beats Turbo by ≥1.0 pp on a measured slice with timestamps and
  acceptable Latin-term preservation → curate it as an optional entry; the harness is ready.
- transcribe.cpp (or another runtime) exposes word timestamps + VAD for a model that beats Turbo
  by ≥1.0 pp on a measured Arabic slice → reopen the second-engine question with the same
  numbers.
- Windows ships an Arabic TTS voice by default or a quality-verified optional voice path
  becomes acceptable to users → rerun the read-aloud rubric in `docs/READ-ALOUD.md`.

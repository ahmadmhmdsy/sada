# Arabic ASR benchmark results

- Created: 2026-11-18 08:46:03
- Engine: transcribe.cpp 268.9 ms load; CPU backend
- Clips: 60
- Slices: egyptian, latin-mixed, msa
- Baseline: whisper-large-v3-turbo

## Overall

| Model | Size MB | WER % | CER % | Acronyms preserved % | Latin names preserved % | Timestamps ok % | RTF |
| --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3-asr-0.6b-q8-transcribe-cpp | 850.4 | 24.38 | 10.21 | n/a | 10.0 | 0.0 | 0.494 |

## WER % by slice

| Model | egyptian | latin-mixed | msa |
| --- | --- | --- | --- |
| qwen3-asr-0.6b-q8-transcribe-cpp | 21.1 | 48.96 | 20.54 |

## App-level (after the app's Arabic post-processing)

The app normalises Arabic punctuation and restores transliterated technical terms (desktop/src/lib/arabic-text.ts, mirrored by sadabench/postprocess.py) before showing or exporting text. These scores apply the same rules to every hypothesis.

| Model | Raw WER % | App WER % | App CER % | App acronyms preserved % | App Latin names preserved % |
| --- | --- | --- | --- | --- | --- |
| qwen3-asr-0.6b-q8-transcribe-cpp | 24.38 | 24.38 | 10.21 | n/a | 10.0 |

On the committed clips this changes punctuation only: no permissive Arabic technical corpus exists yet, so the reference transcripts carry no Latin acronyms to restore. The section exists so the next technical slice is scored against what users see.

## Method

Reference transcripts are normalised (diacritics, tatweel, hamza forms, alef maqsura, digits, punctuation) before word/character Levenshtein scoring; WER and CER are corpus-level sums. Latency includes one process start and model load per clip. See README.md for sources, licences and the decision rule.

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

## Method

Reference transcripts are normalised (diacritics, tatweel, hamza forms, alef maqsura, digits, punctuation) before word/character Levenshtein scoring; WER and CER are corpus-level sums. Latency includes one process start and model load per clip. See README.md for sources, licences and the decision rule.

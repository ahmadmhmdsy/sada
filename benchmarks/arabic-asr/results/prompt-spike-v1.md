# Arabic ASR benchmark results

- Created: 2026-11-18 11:39:46
- Engine: vibe-server v0.6.16-sada.1
- Clips: 40
- Slices: latin-mixed, msa
- Baseline: turbo-base

## Overall

| Model | Size MB | WER % | CER % | Acronyms preserved % | Latin names preserved % | Timestamps ok % | RTF |
| --- | --- | --- | --- | --- | --- | --- | --- |
| turbo-base | 1624.6 | 29.38 | 15.4 | n/a | 25.0 | 100.0 | 0.407 |
| turbo-glossary | 1624.6 | 31.92 | 17.99 | n/a | 25.0 | 100.0 | 0.431 |
| turbo-english-only | 1624.6 | 38.42 | 23.41 | n/a | 30.0 | 100.0 | 0.468 |
| turbo-arabic-only | 1624.6 | 31.36 | 17.62 | n/a | 25.0 | 100.0 | 0.497 |

## WER % by slice

| Model | latin-mixed | msa |
| --- | --- | --- |
| turbo-base | 48.96 | 22.09 |
| turbo-glossary | 55.21 | 23.26 |
| turbo-english-only | 72.92 | 25.58 |
| turbo-arabic-only | 48.96 | 24.81 |

## Curation rule

A challenger is curated only if it beats the baseline by at least 1.0 pp WER on a slice, keeps word timestamps (100%) and preserves at least 90.0% of Latin acronyms on that slice.

### turbo-glossary

- Does not clear the rule on any measured slice.
- latin-mixed: WER 55.21% vs baseline 48.96% (gain -6.25 pp), timestamps 100.0%, acronyms n/a%, latin names 25.0% -> no
- msa: WER 23.26% vs baseline 22.09% (gain -1.17 pp), timestamps 100.0%, acronyms n/a%, latin names n/a% -> no

### turbo-english-only

- Does not clear the rule on any measured slice.
- latin-mixed: WER 72.92% vs baseline 48.96% (gain -23.96 pp), timestamps 100.0%, acronyms n/a%, latin names 30.0% -> no
- msa: WER 25.58% vs baseline 22.09% (gain -3.49 pp), timestamps 100.0%, acronyms n/a%, latin names n/a% -> no

### turbo-arabic-only

- Does not clear the rule on any measured slice.
- latin-mixed: WER 48.96% vs baseline 48.96% (gain 0.0 pp), timestamps 100.0%, acronyms n/a%, latin names 25.0% -> no
- msa: WER 24.81% vs baseline 22.09% (gain -2.72 pp), timestamps 100.0%, acronyms n/a%, latin names n/a% -> no

## App-level (after the app's Arabic post-processing)

The app normalises Arabic punctuation and restores transliterated technical terms (desktop/src/lib/arabic-text.ts, mirrored by sadabench/postprocess.py) before showing or exporting text. These scores apply the same rules to every hypothesis.

| Model | Raw WER % | App WER % | App CER % | App acronyms preserved % | App Latin names preserved % |
| --- | --- | --- | --- | --- | --- |
| turbo-base | 29.38 | 29.38 | 15.4 | n/a | 25.0 |
| turbo-glossary | 31.92 | 31.92 | 17.99 | n/a | 25.0 |
| turbo-english-only | 38.42 | 38.42 | 23.41 | n/a | 30.0 |
| turbo-arabic-only | 31.36 | 31.36 | 17.62 | n/a | 25.0 |

On the committed clips this changes punctuation only: the code-switched Latin words in the corpus (proper nouns in Common Voice, everyday English such as integrate or deadline in the Perle slices) do not include any tracked acronym from the restoration list (GPU, PDF, SRT, ...), so there is nothing for the term rules to rewrite yet. The section exists so a clip that does carry an acronym is scored against what users see.

## Method

Reference transcripts are normalised (diacritics, tatweel, hamza forms, alef maqsura, digits, punctuation) before word/character Levenshtein scoring; WER and CER are corpus-level sums. Latency includes one process start and model load per clip. See README.md for sources, licences and the decision rule.

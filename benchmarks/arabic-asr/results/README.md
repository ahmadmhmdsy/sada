# Results

Committed measurement artifacts:

- results-DATE.json: raw per-clip transcripts, timings and timestamp flags.
- results-DATE.md: aggregated tables produced by "python -m sadabench report", including the
  app-level section that re-scores the same transcripts after the app's Arabic post-processing
  (punctuation clean-up and transliterated-term restoration).

Audio clips are not committed (they are fetched from the sources in manifest.json).
Model files are not committed; each run records the model file name, family, language and size plus
the engine version, never an absolute local path.

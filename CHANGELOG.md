# Changelog

Sada is an Arabic-first fork of [Vibe](https://github.com/thewh1teagle/vibe) (MIT). The upstream
project keeps its own detailed release history; this file records Sada releases and the fork's
delta from upstream v3.2.2.

## v3.2.2 — 2026-11-16

First public release of Sada, built from Vibe v3.2.2 (commit `23eae78`).

### Added

- **Arabic-first fork**: full Arabic UI catalogue `ar-IQ` (704 keys), RTL shell and settings,
  Arabic-first defaults (display `ar-IQ`, transcription `ar`, no translation, temperature 0,
  beam 5), IBM Plex Sans Arabic typography, Western digits and Iraqi date formats.
- **Arabic transcript normalization**: Arabic punctuation (`، ؟ ؛`), whitespace cleanup and
  restoration of common Latin acronyms in Arabic text.
- **Arabic PDF export** with an embedded Arabic font and correct shaping.
- **New identity**: product name Sada (صدى), `Sada.exe`, identifier `app.sada.desktop`, scheme
  `sada`, new icon set and artwork.
- **Documentation and attestation**: Arabic and English README, PRIVACY, NOTICE,
  THIRD-PARTY-NOTICES, upstream delta list, verification report, licences.
- **Delivery automation**: CI workflow for build/tests, release workflow (tag → Windows installer +
  GitHub Release with checksums), and a bilingual GitHub Pages site with `llms.txt`.

### Changed

- Installation name/paths and Windows version metadata are Sada 3.2.2.
- The hidden meeting-prompt window now shares the same Arabic default, fixing an English-first-paint
  race on a fresh profile.

### Removed

- Telemetry/Aptabase client, auto-updater plugin, and the phone handoff entry point (code path
  remains compiled but unreachable).
- Vibe branding in shipped UI strings; upstream attribution remains in Settings → About and NOTICE.

### Known issues

- Unsigned installer (SmartScreen warning), no bundled model, occasional silence hallucinations
  and acronym/number normalization gaps. See [docs/VERIFICATION.md](docs/VERIFICATION.md).

### Upstream

Based on Vibe v3.2.2 (MIT). See [docs/UPSTREAM-PATCHES.md](docs/UPSTREAM-PATCHES.md) for the full
file-by-file delta.

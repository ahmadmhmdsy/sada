# What this fork changes compared with upstream Vibe v3.2.2

Base: `thewh1teagle/vibe` tag **v3.2.2**, commit `23eae78b864088202e4e3b9987d269fe4da5ebb3`.
Everything below is a deliberate delta. The upstream tree stays untouched in
`upstream/vibe-3.2.2/` for reference; this document is generated from a file-by-file hash
comparison between that snapshot and the fork.

```
106 upstream files differ (54 text/code + 52 generated icon files), 51 new files, 9 upstream files removed
```

## 1. Arabic locale and first-run Arabic

| File | Change |
| --- | --- |
| `i18n/desktop/ar-IQ.json` | **new** — complete Arabic catalogue, 704/704 keys in en-US order, Western digits, MSA with Iraqi date formats |
| `i18n/locales.json` | new locale `ar-IQ` (name `arabic`), desktop only |
| `desktop/project.inlang/settings.json` | `ar-IQ` added; paraglide base locale intentionally stays `en-US` |
| `desktop/index.html` | `<html lang="ar" dir="rtl">`, title `صدى`, new favicon |
| `desktop/src/bootstrap.tsx` | `DEFAULT_DISPLAY_LANGUAGE = 'ar-IQ'`; boot locale applied after config load, before first paint |
| `desktop/src/app.tsx` | `<html lang/dir>` and `<body dir>` kept in sync with the display language |
| `desktop/src/providers/preference.tsx` | first-run defaults: `ar-IQ`, language `ar`, `translate: false`, `temperature: 0`, `beam_size: 5`, `best_of: 5`, `n_threads: 6`, empty `init_prompt`, RTL text area, analytics off |
| `desktop/src/globals.css` | IBM Plex Sans Arabic `@font-face` (400/500/600/700), Arabic-first font stack, Arabic typography rules (tracking, line-height, bidi isolation for numbers and monospace) |
| `desktop/src/assets/fonts/IBMPlexSansArabic-*.ttf` | **new** — four OFL font files |
| `desktop/src/lib/arabic-text.ts` | **new** — Arabic transcript post-processing: ASCII `,`/`?`/`;` → `،`/`؟`/`؛`, space cleanup, Latin acronym restoration (GPU/CPU/PDF/SRT/VTT/JSON/API/FFmpeg/Whisper); idempotent, English text untouched |
| `desktop/src/lib/arabic-text.test.ts` | **new** — 10 unit tests (pass) |
| `desktop/src/pages/main/hooks/use-transcribe-queue.ts` | post-processes live segments, final segments and saved projects |
| `desktop/src/providers/hotkey.tsx` | post-processes dictation output; notification titles use `m.appTitle()` (صدى) |
| `desktop/src/components/handoff-transcript-saver.tsx` | post-processes phone-handoff transcripts (code path kept, UI hidden) |
| `desktop/src/lib/pdf/transcript-pdf.ts`, `pdf/transcript-document.tsx` | IBM Plex Sans Arabic registered for PDF and selected automatically when the document contains Arabic; pure Hebrew/English right-to-left documents keep Rubik (which covers Hebrew, unlike the Arabic face) |
| `i18n/desktop/en-US.json` | two new keys (`privacyLocalOnly`, `aboutUpstream`), `projectLink` reworded; other upstream locales fall back to English for those two keys |

## 2. Rebranding and identity

| File | Change |
| --- | --- |
| `desktop/src-tauri/tauri.conf.json` | `productName: "Sada"`, `mainBinaryName: "Sada"`, `identifier: "app.sada.desktop"`, only NSIS target, no updater artifacts, only the deep-link plugin with scheme `sada` |
| `desktop/src-tauri/Cargo.toml` | crate version `0.0.6` → `3.2.2` so the Windows file version matches the product version; description names the Sada fork |
| `desktop/src-tauri/icons/*` | **new icon set** generated from `desktop/src-tauri/sada-icon.svg` (all Windows/macOS/iOS/Android sizes) |
| `desktop/src-tauri/sada-icon.svg`, `assets/sada-icon.svg` | **new** — Sada artwork (sound-wave mark, not derived from the Vibe logo) |
| `desktop/src-tauri/src/setup.rs` | window title `صدى`; Arabic-first crash dialog (no upstream issue URL); log line `Sada App Running` |
| `desktop/src-tauri/src/tray.rs` | tray tooltip `صدى` |
| `desktop/src-tauri/src/config.rs` | documents subfolder `Vibe` → `Sada` |
| `desktop/src-tauri/src/keepawake.rs` | power-assertion name/reason → Sada |
| `desktop/package.json` | package name `sada`, description updated; updater dependency removed |
| `desktop/src/lib/docx.ts` | DOCX description no longer says "Vibe" |
| `desktop/src/lib/skill.ts` (+ test) | generated agent-skill text rebranded to Sada |
| `desktop/src/lib/transcripts-store.ts` (+ test) | default transcripts folder `Vibe` → `Sada` |
| `desktop/src/lib/config.ts` | help/About/update links point at the upstream GitHub repository/releases instead of Vibe's website, Discord and support pages |
| `desktop/src/pages/settings/sections/general.tsx` | help section reduced to one "original project" link (no Discord/support/upstream update buttons) |
| `desktop/src/components/ui/dialog.tsx` | hard-coded English "Close" now uses the locale catalogue |

## 3. Removing telemetry, updater and phone relay

| File | Change |
| --- | --- |
| `desktop/src-tauri/src/analytics.rs` | replaced with a no-op module: same public functions, always disabled, no Aptabase client at all |
| `desktop/src-tauri/src/main.rs` | Aptabase plugin and updater plugin no longer registered |
| `desktop/src-tauri/Cargo.toml` | `tauri-plugin-updater` and the Aptabase git dependency removed |
| `desktop/src-tauri/capabilities/main.json` | `updater:default` and `aptabase:allow-track-event` permissions removed |
| `desktop/src/providers/updater.tsx` | replaced with a no-op provider (`availableUpdate` always false); update UI cannot appear |
| `desktop/src/pages/settings/sections/privacy.tsx` | rewritten: local-only statement plus the "keep projects" switch; analytics and policy links removed |
| `desktop/src/pages/settings/page.tsx` | phone pairing section removed from settings navigation and routing (handoff code remains compiled but unreachable) |
| `desktop/src/pages/main/components/recents-sidebar.tsx` | the phone-handoff button is removed from the sidebar footer (it opened a settings section that no longer exists); the remaining footer is Settings + optional update badge |
| `Cargo.lock`, `desktop/pnpm-lock.yaml` | regenerated after the dependency removals |

## 4. Documentation, licence and attribution

New: `README.ar.md` (main Arabic README), `NOTICE`, `PRIVACY.md`,
`THIRD-PARTY-NOTICES.md`, `docs/UPSTREAM-PATCHES.md` (this file),
`docs/upstream-README.md` (upstream README snapshot), `docs/licenses/` (GPL-3.0,
Apache-2.0, OFL for IBM Plex Sans Arabic, Rubik and Inter), sidecar README.
`README.md` and `LICENSE` were repurposed: MIT kept with the original copyright notice plus
the fork copyright.

## 5. Packaging, CI, release and discovery (added by Sada)

| File | Change |
| --- | --- |
| `.github/workflows/ci.yml` | **new** — CI: frozen install, frontend build (`pnpm build`), unit tests (`pnpm test`) |
| `.github/workflows/release.yml` | **rewritten** — tag `v*` → Windows build (`chore setup`, Rust, Tauri NSIS) → GitHub Release with installer, `SHA256SUMS.txt`, `LICENSE`, `NOTICE` and `THIRD-PARTY-NOTICES.md`; requires `docs/releases/v<version>.md` |
| `.github/workflows/pages.yml` | **new** — deploys `site/` to GitHub Pages |
| `.github/workflows/{lint_rust,server-libs,server-release,server-test,test-release,website}.yml` | **removed** — upstream workflows that do not apply to this fork (and one of which would run on our release) |
| `.github/FUNDING.yml` | **removed** — upstream author's funding accounts; a fork must not redirect them |
| `.github/ISSUE_TEMPLATE/*`, `.github/pull_request_template.md` | rewritten/added for Sada (Arabic + English) |
| `docs/releases/v3.2.2.md` | **new** — bilingual release notes used by the release workflow |
| `docs/VERIFICATION.md` | **new** — public verification report (build, hashes, ASR evidence, limitations) |
| `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md` | **new/rewritten** — Sada-specific contributing, security and changelog |
| `CITATION.cff`, `llms.txt` | **new** — citation metadata and an agent/research index (llms.txt format) |
| `AGENTS.md` | **rewritten** — Sada repository guide for humans/AI agents, upstream dev notes retained |
| `README.md`, `README.ar.md` | rewritten — badges, screenshots, install, FAQ, verification, attribution and discovery keywords |
| `docs/media/` | **new** — screenshots used by the README and the website |
| `site/` | **new** — bilingual static landing page (Arabic first, English under `/en/`) with JSON-LD (WebSite, SoftwareApplication, FAQPage), Open Graph/Twitter metadata, `robots.txt`, `sitemap.xml`, local OFL fonts and `llms.txt` |

The upstream engine, model handling and audio pipeline remain untouched by this section.

## Deliberately not changed

- The Whisper engine, model handling and audio pipeline are upstream code; no model is bundled.
- The transcription defaults changed only at the application default-config layer
  (`preference.tsx`), not in the engine, so a user can still pick any language/values.
- Upstream i18n catalogues for the other 21 locales are untouched and still selectable.
- No telemetry code was added back; no network endpoint of this fork exists.

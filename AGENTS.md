# Sada — repository guide for humans and AI agents

Sada (صدى) is an Arabic-first, fully offline speech-to-text desktop app for Windows, and an
independent fork of [Vibe](https://github.com/thewh1teagle/vibe) v3.2.2 (MIT). It is a Tauri 2
desktop app (React 19 frontend, Rust shell) around the upstream `vibe-server` sidecar
(whisper.cpp).

## Repository map

| Path | What it is |
| --- | --- |
| `desktop/` | The app: React 19 + Vite frontend, Tauri shell under `desktop/src-tauri/`, icons and fonts |
| `i18n/desktop/` | UI catalogues; `ar-IQ.json` is the Arabic-first catalogue (704 keys, must stay complete) |
| `server/` | `vibe-server` engine (upstream Rust code around whisper.cpp); not modified by this fork |
| `docs/` | Architecture, building, verification, licences, release notes, upstream delta |
| `site/` | Static bilingual landing page deployed to GitHub Pages (includes `llms.txt` for agents) |
| `.github/workflows/` | `ci.yml` (build + tests), `release.yml` (tag → Windows installer + GitHub release), `pages.yml` |

## Commands (Windows)

```powershell
chore setup x86_64-pc-windows-msvc   # fetch pinned vibe-server + ffmpeg sidecars (not in git)
cd desktop
pnpm install
pnpm test                            # vitest, 26 files / 130 tests at release time
pnpm build                           # paraglide compile → tsc → vite build
pnpm exec tauri build                # NSIS installer under target/release/bundle/nsis/
```

CI runs `pnpm install --frozen-lockfile`, `pnpm build` and `pnpm test` on every push and PR.
Do not add a model to the repository: `*.bin` is ignored and models are downloaded by users.

## Invariants of this fork

- **Arabic-first defaults stay the default for a fresh profile**: no stored language ⇒ display
  `ar-IQ`, transcription `ar`, translation off, RTL, Arabic typography. Every window (including
  the hidden meeting-prompt window) must use the shared `DEFAULT_DISPLAY_LANGUAGE`.
- **No telemetry, updater, account or phone relay** may be reintroduced. Analytics is a no-op
  module; the updater provider always reports no update; the phone handoff UI stays unreachable.
- **No hard-coded UI strings**: text goes through paraglide catalogues. `en-US` is the base
  locale; the app still opens `ar-IQ` because the boot config defaults to it.
- **Attribution stays**: MIT copyright of Vibe, `NOTICE`, `THIRD-PARTY-NOTICES.md`, Settings →
  About "built on Vibe". The Sada name and icon are this fork's own.
- **Bundled FFmpeg is GPLv3**: never relicense Sada as GPL; keep the notices and the source offer
  before distributing a build.

## Release process

1. Bump `desktop/src-tauri/tauri.conf.json` version (and `desktop/src-tauri/Cargo.toml`).
2. Write bilingual notes in `docs/releases/v<version>.md` (the release workflow requires the file).
3. Commit, tag `v<version>`, push the tag. The **Release** workflow builds on Windows and creates
   the GitHub release with installer, `SHA256SUMS.txt`, licence and notices. No manual upload.

## Website / discovery

`site/` is deployed by the **Deploy site** workflow to <https://alshahia.github.io/sada/>. Keep
`site/llms.txt`, root `llms.txt`, `site/robots.txt`, `site/sitemap.xml` and the JSON-LD blocks
inside both `index.html` files in sync with the repository facts (version, links, limitations).

## Docs index

- [README English](README.md) · [README Arabic](README.ar.md)
- [Architecture](docs/ARCHITECTURE.md) · [Building](docs/BUILDING.md)
- [Upstream delta](docs/UPSTREAM-PATCHES.md) · [Verification](docs/VERIFICATION.md)
- [Translations](docs/TRANSLATIONS.md) · [Privacy](PRIVACY.md) · [Security](SECURITY.md)
- [Release notes](docs/releases/) · [Third-party notices](THIRD-PARTY-NOTICES.md)

---

# Upstream Vibe development notes (retained for engine work)

## Tooling

- Tasks: `chore` — see `chore list`
- JS: `pnpm` only; Python: `uv` standalone scripts (`uv run`)

## Validation

Plan validation scripts: `plans/<name>/<name>_001.py` (+ `.md`), standalone `uv` scripts.

## Skills

Custom skills live in `.claude/skills/<name>/SKILL.md`.

## Execution mindset

Agent mode: parallel moves, instant iteration, speed by default. Split heavy work until obvious.
Estimate by output size — 300 lines = minutes. Correct over easy: rework is slower than doing it
right once. Plan resolved → execute, don't re-analyze.

## Working in parallel

Split large work across ~4–5 subagents, one disjoint module-group each — no shared files; only the
coordinator touches shared/root config. Fix contracts (interfaces, design docs) up front.

## File size

700 lines max. Split by responsibility into halves — find where the file does two jobs and move one
out whole. Keep the public API where callers expect it; move tests with their code.

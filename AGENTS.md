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
| `server/` | `vibe-server` engine (upstream Rust code around whisper.cpp); the fork's only change is the loopback Host/Origin request guard (see [Security](SECURITY.md)), and the release workflow builds it from source |
| `docs/` | Architecture, building, verification, licences, release notes, upstream delta, MCP guide, Voicebox review |
| `site/` | Static bilingual landing page deployed to GitHub Pages (includes `llms.txt` for agents) |
| `.github/workflows/` | `ci.yml` (build + tests), `release.yml` (tag → Windows installer + GitHub release), `pages.yml` |

## Commands (Windows)

```powershell
chore setup x86_64-pc-windows-msvc   # fetch pinned vibe-server + ffmpeg sidecars (not in git)
cd desktop
pnpm install
pnpm test                            # vitest, 31 files / 193 tests at release time
pnpm build                           # paraglide compile → tsc → vite build
pnpm exec tauri build                # NSIS installer under target/release/bundle/nsis/
```

CI runs `pnpm install --frozen-lockfile`, `pnpm build` and `pnpm test` on every push and PR.
Do not add a model to the repository: `*.bin` is ignored and models are downloaded by users.

The MCP server lives in Rust and must keep working headlessly: `Sada.exe --mcp` is handled
before any Tauri setup, speaks JSON-RPC over stdin/stdout, and must never open a port or touch the
GUI. It is covered by `cargo test --release` (the mcp:: and arabic:: modules). Keep the agent
skill text in `desktop/src/lib/skill.ts` in sync when tool names or registration steps change.

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
3. Commit, tag `v<version>`, push the tag. The **Release** workflow builds on Windows, rebuilds
   the engine from `server/` so the installer ships the guarded sidecar, builds the offline-WebView2
   variant then the default installer, and creates the GitHub release with both assets,
   `SHA256SUMS.txt`, licence and notices. No manual upload. Code signing is wired but dormant until
   the repository variable `SIGNING_ENABLED` is `true` (see [Code signing](docs/SIGNING.md)).

## Website / discovery

`site/` is deployed by the **Deploy site** workflow to <https://alshahia.github.io/sada/>. Keep
`site/llms.txt`, root `llms.txt`, `site/robots.txt`, `site/sitemap.xml` and the JSON-LD blocks
inside both `index.html` files in sync with the repository facts (version, links, limitations).

## Docs index

- [README English](README.md) · [README Arabic](README.ar.md)
- [Architecture](docs/ARCHITECTURE.md) · [Building](docs/BUILDING.md)
- [Models guide](docs/MODELS.md) · [Models guide in Arabic](docs/MODELS.ar.md)
- [MCP guide](docs/AGENT-MCP.md) · [MCP guide in Arabic](docs/AGENT-MCP.ar.md)
- [Upstream delta](docs/UPSTREAM-PATCHES.md) · [Verification](docs/VERIFICATION.md)
- [Voicebox review](docs/VOICEBOX-REVIEW.md) · [Voicebox review in Arabic](docs/VOICEBOX-REVIEW.ar.md)
- [Models council](docs/MODELS-COUNCIL.md) · [Models council in Arabic](docs/MODELS-COUNCIL.ar.md)
- [Model decisions (measured)](docs/MODELS-DECISIONS.md) · [Read-aloud evidence](docs/READ-ALOUD.md)
- [Roadmap](ROADMAP.md) · [P4 plan](docs/P4-PLAN.md) · [P5 plan](docs/P5-PLAN.md)
 · [P6 plan](docs/P6-PLAN.md)
  · [Changelog](CHANGELOG.md)
- [Translations](docs/TRANSLATIONS.md) · [Privacy](PRIVACY.md) · [Security](SECURITY.md)
- [Clean-machine acceptance](docs/ACCEPTANCE.md) · [Production readiness](docs/PRODUCTION-READINESS.md)
  · [Code signing](docs/SIGNING.md)
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

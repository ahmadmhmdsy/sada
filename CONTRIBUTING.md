# Contributing to Sada

Thanks for your interest. Sada is an Arabic-first fork of Vibe; upstream engine code is MIT and
contributions are welcome for the fork-specific parts and for the Arabic experience.

## Before you start

- Open an issue first for anything larger than a small fix, so the change can be discussed.
- For security issues **do not** open a public issue — see [SECURITY.md](SECURITY.md).
- Read [docs/UPSTREAM-PATCHES.md](docs/UPSTREAM-PATCHES.md) to see what this fork changed and why.
- For Arabic translations, read [docs/TRANSLATIONS.md](docs/TRANSLATIONS.md); the fork catalogue is
  [i18n/desktop/ar-IQ.json](i18n/desktop/ar-IQ.json) (704 keys, must stay complete).

## Development setup

Prerequisites: Rust stable, Node.js 22+, pnpm 10.4.1, [chore](https://getchore.github.io/chore/).

```powershell
chore setup x86_64-pc-windows-msvc   # sidecars: vibe-server + ffmpeg (not in git)
cd desktop
pnpm install
pnpm test                            # vitest, must stay green
pnpm build                           # paraglide + tsc + vite
pnpm exec tauri build                # full Windows build (optional)
```

For frontend-only work you can run `pnpm dev` in `desktop/` and use the browser with Tauri mocks.

## Pull requests

1. Branch from `master`; do not PR from your own `master`.
2. Keep the change focused; avoid unrelated formatting/refactors.
3. Run `pnpm test` (and `pnpm build`) before pushing. CI runs both on every PR.
4. Describe **what** changed, **why**, and how you verified it (screenshots for UI changes).
5. UI text must go through the locale catalogues — no hard-coded strings. Arabic-first defaults must
   remain the default for a fresh profile.

## Commit messages

Use a short imperative subject line, optionally with a conventional prefix:

```text
feat: add Arabic punctuation normalization for dictation
fix: apply boot locale before first paint
docs: correct Arabic locale key count
```

## Release process (maintainers)

1. Update `desktop/src-tauri/tauri.conf.json` version and `desktop/src-tauri/Cargo.toml`.
2. Write release notes in `docs/releases/v<version>.md` (bilingual).
3. Commit, tag `v<version>`, push the tag.
4. The **Release** GitHub Actions workflow builds the Windows installer and publishes the GitHub
   release with checksums — no manual upload needed.

## Code of conduct

Be respectful; assume good faith. Arabic and English are both welcome in issues and PRs.

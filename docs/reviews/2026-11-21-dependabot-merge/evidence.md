# Evidence pack — review room: Dependabot merge plan (2026-11-21)

Target: `alshahia/sada`, master `d68c5b1` (2026-11-21), clean tree, 22 open Dependabot PRs (#36–#57), 0 merged.
Decision under review: approve the four-batch merge plan in `docs/DEPENDABOT-TRIAGE.md` as of `d68c5b1` before the review-room corrections.
Reviewers: five role voices + silent Maestro + four independent read-only subagents (auditor, product first-contact, maintenance/process, release/supply-chain).

## Tree and drift
- HEAD `d68c5b1`; `git status --porcelain` = 0 lines.
- PR base `c46809c` = release v3.9.0, 2026-11-19 09:02 +0300; PRs created 2026-11-19 06:03Z.
- `git rev-list --count c46809c..HEAD` = 20 commits, 104 files; includes v3.10.0 version bump `be27bd5` (Cargo.toml, Cargo.lock, tauri.conf.json, CITATION.cff).
- PR check runs last completed 2026-11-19 06:12–06:23Z (six checks per PR, all SUCCESS) — before the 20 commits.
- Master CI: runs of 7–12 minutes; concurrency group `ci-<ref>` with `cancel-in-progress: true`; one cancelled run already in the last 15.
- Branch protection on master: none (HTTP 404; rulesets []). Repo allows squash, merge and rebase; `delete_branch_on_merge=false`.

## Mergeability measured today
- `git merge-tree --write-tree HEAD refs/pull/N/head` for N=36..57: exit 0 for 22/22 individually.
- Chained replay in the printed order (`--merge-base=c46809c`): conflicts at #54 (`desktop/pnpm-lock.yaml`), #48 (`Cargo.lock`), #40 and #46 (`server/Cargo.lock`).
- Pair evidence: #38×#40 and #42×#46 conflict on `server/Cargo.lock`; #52×#54 conflict on `desktop/pnpm-lock.yaml`; #50×#53 conflict on `Cargo.lock` (moot once #53 is held out).

## Server coverage and #44
- `ci.yml` jobs: desktop (windows-latest, pnpm build/test + `cargo test --release` at `desktop/src-tauri`, no `--workspace`) and benchmarks (ubuntu). No job builds `server/` and no job runs `pnpm exec tauri build`.
- `release.yml` builds server and bundles installers but only on tag push or manual dispatch.
- Local: `cargo check --all-targets` at each server PR head (native libs from main checkout) → #38 exit 0 14s, #40 exit 0 6s, #42 exit 0 10s, #46 exit 0 34s, #47 exit 0 26s, #44 exit 101.
- #44 failure: `crates/vibe-server/src/server/mod.rs:149` E0308, multiple utoipa versions.
- Lock resolution verified: master `server/Cargo.lock` has utoipa 5.5.0 + utoipa-gen 5.5.0 + utoipa-axum 0.2.0 + utoipa-swagger-ui 9.0.2; PR #44 branch adds utoipa 6.0.0 + utoipa-gen 6.0.1 + utoipa-swagger-ui 10.0.2.
- `server/Cargo.toml:46` = `utoipa = "5"`; `:48` = `utoipa-axum = "0.2"`. The triage's "pins 6, needs 7" was wrong on both sides; the remedy is 5→6 + a compatible utoipa-axum.

## Workflow and release exposure
- #36 configure-pages 6 only in `pages.yml` (push `site/**`, workflow_dispatch available).
- #37 setup-uv 7 only in `release.yml:88`, guarded by `if: vars.SIGNING_ENABLED == 'true'`; signing is not enabled (owner action A5), so v7 will not run at v3.11.0 either.
- #39 attest-build-provenance 4 in `release.yml:263`, unconditional, before `softprops/action-gh-release` (:284): first exercise is a real publish; failure aborts after ~10 min of builds.
- #41 setup-node 7 in `ci.yml`, `release.yml`, `security.yml`; every later CI run exercises it.
- #45 codeql-action 4 in `security.yml` (pull_request, push dependency paths, schedule, workflow_dispatch) — dispatchable.
- `release.yml` has `workflow_dispatch` with a `tag` input; guards are tag==version and notes-exist only, and the publish step is unconditional `draft: false`, files `release-assets/*`. v3.10.0 is live and `tauri.conf.json` says 3.10.0, so dispatching with `tag=v3.10.0` rebuilds and replaces the 8 live assets + SHA256SUMS.txt under the same tag. **Never dispatch it.**
- Sidecar identity: `release.yml:110` hardcodes `"$version-sada.1"`; ACCEPTANCE.md:152 and SECURITY-WHITEPAPER.md:18 record v3.9.0 and v3.10.0 at the same string; after the server batch v3.11.0 would ship a third binary under it. Release prep must bump to `-sada.2`.
- Attestation subjects (`release.yml:265-268`) omit `SHA256SUMS.txt`, the file SUPPLY-CHAIN.md tells users to verify.

## Product surfaces
- `ui/tabs.tsx` has no importer outside itself (#54 changes a component no user can reach).
- `ui/select` has 7 importers and `ui/button` 33; no `*.test.*` mounts Select/Tabs/Button primitives, so `pnpm test` cannot see their behaviour.
- #50 window-vibrancy is `cfg(target_os="macos")` (`desktop/src-tauri/Cargo.toml:97-104`, `setup.rs:153-159`); no Windows visual surface, no CI compile.
- #48 x11rb is `cfg(linux)` (`crates/meeting-detect/src/window_title.rs`); no CI compile.
- #56 opener: folder reveal is Rust `showfile` (`cmd/files.rs:122`), not the opener plugin; JS `openUrl` body unchanged.
- #57 virtualization: `transcript-view.tsx:417-441` uses `measureElement` with `gap: 4` and `scrollMargin` from `offsetTop` — the math 3.14.11+ patched; test with 60+ rows, End, search remeasure, mid-list row edit.
- #53 is a covert Tauri runtime jump: tauri 2.10.3→2.12.7, wry 0.54.2→0.57.3, tao 0.34.6→0.37.3, webview2-com 0.38.2→0.39.1, tauri-build 2.5.6→2.7.6; 48 packages added, 51 removed. Cause: caret `tauri-plugin-notification = "2"` with 2.8.1 requiring tauri ^2.12. No CI job builds an installer; `desktop/package.json:76` pins `@tauri-apps/cli ~2.10.0`.

## Verification commands used
```bash
git log --oneline -1; git status --porcelain
gh pr list --state open --limit 30 --json number,mergeable,mergeStateStatus,createdAt,updatedAt,baseRefOid,headRefOid
gh pr checks N --json name,state,completedAt
gh run list --workflow ci.yml --branch master --limit 5 --json databaseId,headSha,status,conclusion,createdAt,updatedAt
git fetch origin refs/pull/N/head:refs/depcheck/pr-N
git merge-tree --write-tree --name-only HEAD refs/depcheck/pr-N
git merge-tree --write-tree --merge-base=c46809c <chained refs>   # replay conflicts
git show refs/depcheck/pr-44:server/Cargo.lock   # parse package blocks
gh api repos/alshahia/sada/branches/master/protection
cargo check --all-targets (from server/ at each PR head)
```

## Review artifacts
- `session.json` — structured review-room session (28 blocks, standard mode, check_session exit 0).
- `review-room-transcript.html` — self-contained transcript (build_transcript.py; check_session --html exit 0).
- `ruling.md` — the implementable ruling reproduced for the owner.

## Post-review verification (2026-11-21, crates.io)

- `cargo info utoipa` → 6.0.0 (released; rust-version 1.88).
- `cargo info utoipa-axum@0.3.0` → depends on `utoipa = "6.0.0"` (crate manifest read from the local registry cache).
- `cargo info utoipa-swagger-ui` → 10.0.2; its manifest also requires `utoipa = "6.0.0"`.
- Consequence: the #44 rework is a coordinated three-crate bump (`utoipa` 5→6, `utoipa-axum` 0.2→0.3,
  `utoipa-swagger-ui` 9→10) plus whatever derive/API fallout `cargo check` reports. The trigger written in
  the ruling is met; the upgrade task can start without waiting on upstream.

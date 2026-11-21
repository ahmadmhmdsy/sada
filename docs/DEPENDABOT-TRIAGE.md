# Dependabot triage — 22 open updates (2026-11-21)

Prepared for [OWNER-ACTIONS A9](OWNER-ACTIONS.md#a9--triage-dependabot-prs-36-57). This is the triage
and merge order; **no pull request was merged** — the merge decision stays with the owner.

> **Reviewed by a review room on 2026-11-21** (four independent read-only reviewers + five role voices).
> Verdict: *approve with corrections*. The facts below are the corrected ones; the full ruling, evidence
> pack and transcript are in [docs/reviews/2026-11-21-dependabot-merge/](reviews/2026-11-21-dependabot-merge/).
> What changed: the #44 diagnosis (utoipa 5.5.0 to 6.0.0, not “pins 6, needs 7”), four hidden conflict
> points, the check-age warning, the platform-blind smoke list, #53 moved out of the train as a Tauri
> runtime jump, and a real clock, merge method, checkpoint/revert recipe and kill-date.

## Where the 22 PRs stand

All 22 PRs (#36–#57) passed every check GitHub ran, but those runs last completed **2026-11-19 06:12–06:23Z**
against base `c46809c` (v3.9.0). The v3.10.0 bump `be27bd5` landed at 2026-11-19 11:38 +0300, and master
has moved **20 commits / 104 files** since. No PR check has run against master `d68c5b1`.

Mergeability re-measured 2026-11-21: every PR merges clean **individually** (22/22 `git merge-tree` exit 0),
but a sequential replay in the printed order conflicts at **#54** (`desktop/pnpm-lock.yaml`), **#48**
(`Cargo.lock`), **#40** and **#46** (`server/Cargo.lock`). Conflict pairs: #52×#54, #38×#40, #42×#46 (and
#50×#53, moot once #53 is held out). Rebase at conflict time, re-check the new head, and let the master CI
window after each batch be the gate: `ci.yml:17-19` cancels superseded runs, so 21 merges in one burst
cancel each other.

## The real blocker — #44

[#44](https://github.com/alshahia/sada/pull/44) bumps `utoipa-swagger-ui` 9.0.2 to 10.0.2 in `/server`.
`utoipa-swagger-ui` 10.0.2 pulls **`utoipa` 6.0.0**, while the server pins **`utoipa = "5"`**
(`server/crates/vibe-server/Cargo.toml:46`, lock 5.5.0) and `utoipa-axum = "0.2"` (which depends on 5).
The result is two utoipa versions in the graph and a hard compile error:

```
error[E0308]: mismatched types
  --> crates\vibe-server\src\server\mod.rs:149:61
    .merge(SwaggerUi::new("/docs").url("/openapi.json", ApiDoc::openapi()))
    ^ expected `utoipa::openapi::OpenApi`, found a different `utoipa::openapi::OpenApi`
note: there are multiple different versions of crate `utoipa` in the dependency graph
```

This is a coordinated upgrade (`utoipa` 5 to 6 + a `utoipa-axum` that accepts 6 + `utoipa-swagger-ui` 10 +
the `/docs` route), not a drive-by bump and **not** a “utoipa 7” task. Keep #44 out of this train: close it
(or retitle it) and open one “utoipa 5 to 6 coordinated upgrade” task. The alternative — hold
`utoipa-swagger-ui` at 9 until that task lands — is acceptable too; both options are the owner’s call.

As of 2026-11-21 the coordinated path is **unblocked**: `utoipa` 6.0.0 is released, `utoipa-axum` 0.3.0
requires `utoipa = "6.0.0"`, and `utoipa-swagger-ui` 10.0.2 requires `utoipa = "6.0.0"` (verified with
`cargo info`). Bump all three together in one PR and fix the derive/API fallout there — that PR is the
coordinated upgrade task.

## Why CI did not catch #44

| Coverage | What it proves | Gap |
| --- | --- | --- |
| Desktop build & tests (windows-latest) | frontend `pnpm build` + `pnpm test`, and `cargo test --release` for `desktop/src-tauri` | does not build `server/` and not the root `meeting-detect` (no `--workspace`) |
| Arabic ASR benchmark harness | Python harness tests + regression-gate self-comparison | not Rust |
| npm advisory scan, RustSec scan | no known advisories in either lockfile | does not compile |
| CodeQL | static analysis of JS/TS | not Rust |

`server/` is its own Cargo workspace. Only `.github/workflows/release.yml` builds it (on a tag), so a
server dependency bump can look green on every PR and break the release. A server compile job is the
follow-up at the end of this document.

## Inventory and recommendations

### Group 1 — GitHub Actions (5 PRs, no lockfiles)

| PR | Bump | Where / caveat |
| --- | --- | --- |
| [#36](https://github.com/alshahia/sada/pull/36) | actions/configure-pages 5 to 6 | `pages.yml`; exercised on push `site/**`, dispatchable |
| [#37](https://github.com/alshahia/sada/pull/37) | astral-sh/setup-uv 5 to 7 | `release.yml:88`; **will not run while signing is off** (`vars.SIGNING_ENABLED`), so it cannot be verified by “the next release” |
| [#39](https://github.com/alshahia/sada/pull/39) | actions/attest-build-provenance 2 to 4 | `release.yml:263`; unconditional before the release step — first exercise is a real publish |
| [#41](https://github.com/alshahia/sada/pull/41) | actions/setup-node 4 to 7 | `ci.yml`, `release.yml`, `security.yml`; exercised by every later CI run |
| [#45](https://github.com/alshahia/sada/pull/45) | github/codeql-action 3 to 4 | `security.yml`; dispatchable |

**Recommendation:** merge this group **last**, after the lockfile batches; then dispatch `security.yml` and
`pages.yml` once and confirm green. Do **not** dispatch `release.yml`: with `tag=v3.10.0` the guards pass
(tag == version, notes exist) and it will rebuild and re-publish the live v3.10.0 assets under the same tag
with different digests. #37 and #39 are validated at the v3.11 tag rehearsal, not here.

### Group 2 — desktop npm (5 PRs, `desktop/pnpm-lock.yaml`)

| PR | Bump | Risk |
| --- | --- | --- |
| [#49](https://github.com/alshahia/sada/pull/49) | @radix-ui/react-slot 1.2.4 to 1.5.0 | low; UI primitive |
| [#52](https://github.com/alshahia/sada/pull/52) | @radix-ui/react-select 2.2.6 to 2.4.1 | low; settings selects; **conflicts with #54** |
| [#54](https://github.com/alshahia/sada/pull/54) | @radix-ui/react-tabs 1.1.13 to 1.2.1 | low; no importer of `ui/tabs.tsx` — no user surface |
| [#56](https://github.com/alshahia/sada/pull/56) | @tauri-apps/plugin-opener 2.5.3 to 2.7.3 | low; folder reveal uses Rust `showfile`, this only touches `openUrl` |
| [#57](https://github.com/alshahia/sada/pull/57) | @tanstack/react-virtual 3.14.10 to 3.14.26 | medium-low; transcript scroll math; test with 60+ rows |

**Recommendation:** merge sequentially; on each merge run `pnpm install --frozen-lockfile` before trusting
the lockfile. #52×#54 will conflict on `pnpm-lock.yaml`: comment `@dependabot rebase` on #54 after #52
merges, wait for fresh checks, then merge. Smoke after the batch: main mic select and settings selects by
keyboard only, licence link opens the browser, and a 60-row transcript scrolled to the composer, searched,
and edited mid-list. `pnpm test` does not mount Select/Tabs/Button primitives, so it cannot see these.

### Group 3 — root workspace Rust (6 PRs, `Cargo.lock`) — #53 held out

| PR | Bump | Note |
| --- | --- | --- |
| [#43](https://github.com/alshahia/sada/pull/43) | winreg 0.55.0 to 0.56.0 | 0.x minor; Windows registry reads |
| [#48](https://github.com/alshahia/sada/pull/48) | x11rb 0.13.2 to 0.14.0 | **platform-unverified**: `cfg(linux)` in `meeting-detect`; no Windows compile |
| [#50](https://github.com/alshahia/sada/pull/50) | window-vibrancy 0.6.0 to 0.8.1 | **platform-unverified**: `cfg(macos)`; no Windows visual surface to check |
| [#51](https://github.com/alshahia/sada/pull/51) | serde_json 1.0.149 to 1.0.154 | patch |
| [#53](https://github.com/alshahia/sada/pull/53) | tauri-plugin-notification 2.3.3 to 2.8.1 | **held out — a Tauri runtime jump, see below** |
| [#55](https://github.com/alshahia/sada/pull/55) | uuid 1.21.0 to 1.29.2 | patch-level API use |

The old “CI runs `cargo test --release` on this workspace” claim was false: `ci.yml:70-72` builds
`desktop/src-tauri` only, so `meeting-detect` tests never run. Merge the five sequentially (same
`Cargo.lock` conflict rule; #48 conflicts in the replay), record #48 and #50 as platform-unverified with
their reopening trigger, and do not claim a vibrancy check. Delete the “window transparency” smoke line:
there is no Windows transparency surface and this machine cannot observe macOS.

#### Held out — #53 is a Tauri runtime jump

`tauri-plugin-notification` 2.8.1 requires `tauri ^2.12`, and the caret dependency in
`desktop/src-tauri/Cargo.toml` lets the bump move the whole stack: **tauri 2.10.3 to 2.12.7, wry 0.54.2 to
0.57.3, tao 0.34.6 to 0.37.3, webview2-com 0.38.2 to 0.39.1, tauri-build 2.5.6 to 2.7.6**; 48 packages added,
51 removed, 57 changed. No CI job ever runs `pnpm exec tauri build`, so v3.11.0’s NSIS, MSI and offline
installers would be the first ever built by that stack — and the offline installer is exactly the path that
changed. Also `@tauri-apps/cli` is pinned `~2.10.0` while the crate would be 2.12.7.

**Gate before merging #53 (release prep, before v3.11.0):** rebase it on merged master; build an installer
from the branch (`pnpm exec tauri build`); test the offline installer on a clean machine; align
`@tauri-apps/cli` to 2.12; then merge and smoke launch, one transcription, one toast, tray/menu,
window-state. Do not fold this into a dependency batch.

### Group 4 — server Rust (6 PRs, not built by CI)

Local check: worktree at each PR head, `server/` workspace, `cargo check --all-targets` with the native
libs from the main checkout. Result on 2026-11-21:

| PR | Bump | Local compile |
| --- | --- | --- |
| [#38](https://github.com/alshahia/sada/pull/38) | futures-util 0.3.32 to 0.3.34 | **pass** (exit 0, 14 s); conflicts with #40 |
| [#40](https://github.com/alshahia/sada/pull/40) | clap 4.6.1 to 4.6.7 | **pass** (exit 0, 6 s); conflicts with #38 |
| [#42](https://github.com/alshahia/sada/pull/42) | serde_json 1.0.150 to 1.0.154 | **pass** (exit 0, 10 s); conflicts with #46 |
| [#44](https://github.com/alshahia/sada/pull/44) | utoipa-swagger-ui 9.0.2 to 10.0.2 | **fail** — utoipa 5/6 split (see top) |
| [#46](https://github.com/alshahia/sada/pull/46) | serde 1.0.228 to 1.0.229 | **pass** (exit 0, 34 s); conflicts with #42 |
| [#47](https://github.com/alshahia/sada/pull/47) | tower-http 0.6.11 to 0.7.1 | **pass** (exit 0, 26 s; 0.6.11 stays in the tree for other crates) |

**Recommendation:** merge the five passing PRs after the root batch. Rebase the two conflict pairs first,
then **re-compile the new head** — the pass rows above describe the old heads, not the rebased ones. Then
from `server/` run the full suite, not only the guard subset: `cargo test --release -p vibe-server`,
`cargo check --all-targets`, and `cargo build --release -p vibe-server` (cargo check does not link; the
tag is otherwise the first release-profile compile). Keep #44 out.

## Suggested order (owner; about 2–3 h elapsed, not 30–40 min)

1. **Day 0 — correct the record and freeze the baseline** (45 min): fix this document, record the surface
   baseline (launch, toast, keyboard selects, licence link, 60-row transcript), close/retitle #44 and open
   the coordinated 5 to 6 task.
2. **Batch 1 — npm** (20 min + one 7–12 min CI window): #49, #52, #54, #56, #57 with per-merge freshness.
3. **Batch 2 — root Rust** (20 min): #43, #51, #55, #48, #50. **#53 held out.**
4. **Batch 3 — server** (25 min): rebase #38/#40 and #42/#46, recompile, merge, full suite + release build.
5. **Batch 4 — workflows last** (15 min): #41, #45, #36, #37, #39; dispatch `security.yml` and `pages.yml`.
6. **After each batch:** wait for the surviving `ci.yml` master run, record its SHA as the checkpoint, then
   start the next batch. If a batch fails CI or smoke, `git revert` its squash commits in reverse order the
   same day; do not debug forward on master.
7. **Merge method:** `gh pr merge --squash` throughout (one revert target per PR).
8. **Kill-date:** 2026-11-28 — if the batches are not complete, refresh mergeability and check timestamps for
   every remaining PR and re-run the ruling rather than resuming it.
9. No tag, no version bump, no release and **no `release.yml` dispatch** is part of this work; v3.10.0 assets
   are unaffected.

## Follow-ups (recommended, not blocking)

- **Add a server compile job to CI.** A `server` job in `ci.yml` (`cargo check --all-targets` or
  `cargo test --release -p vibe-server`) would have failed #44 and catches the next release-breaking bump.
- **Group Dependabot updates.** `groups:` (patch/minor per ecosystem) in `.github/dependabot.yml` would turn
  the next 22-PR backlog into 3–4 PRs; validate on the 2026-11-30 cycle.
- **Release-prep fixes before v3.11.0.** Tauri gate for #53 (installer rehearsal + CLI alignment); bump the
  sidecar suffix from `-sada.1` to `-sada.2` (`release.yml:110`, ACCEPTANCE, SECURITY-WHITEPAPER) because a
  third distinct server binary now shares that string; add `SHA256SUMS.txt` to the attestation subjects;
  validate `setup-uv` 7 and `attest` 4 at the tag rehearsal — never dispatch `release.yml` against v3.10.0.
- **Audit the other workflows.** After the workflow batch, dispatch `security.yml` once and confirm one
  green run before the next tag; `pages.yml` once. `release.yml` changes remain untested until v3.11.0.

## Evidence

- PR state, checks and mergeability collected 2026-11-21:
  `gh pr list --state open --limit 30 --json number,mergeable,mergeStateStatus,...`,
  `gh pr checks N --json name,state,completedAt`, `gh run list --workflow ci.yml --branch master`.
- Individual merge checks: `git fetch origin refs/pull/N/head:refs/depcheck/pr-N` then
  `git merge-tree --write-tree HEAD refs/depcheck/pr-N` (22/22 exit 0); chained replay with
  `--merge-base=c46809c` for the conflict list.
- Server compile: worktree at each PR head (fetched from `refs/pull/N/head`), `CARGO_TARGET_DIR` in scratch,
  `cd server && cargo check --all-targets`; native `server/libs` supplied from the main checkout (the
  worktree does not download them). The same local check on `master` itself passes (baseline), so the #44
  failure is caused by the bump.
- Independent review: [docs/reviews/2026-11-21-dependabot-merge/](reviews/2026-11-21-dependabot-merge/)
  (transcript, ruling, evidence pack, session JSON). `session.json` and its HTML transcript pass the
  review-room validator.

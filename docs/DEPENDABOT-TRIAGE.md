# Dependabot triage — 22 open updates (2026-11-21)

Prepared for [OWNER-ACTIONS A9](OWNER-ACTIONS.md#a9--triage-dependabot-prs-36-57). This is the triage
and merge order; **no pull request was merged** — the merge decision stays with the owner.

All 22 PRs (#36–#57) were green on every check GitHub ran when the triage was taken (2026-11-21):
Desktop build & tests, Arabic ASR benchmark harness, npm advisory scan, RustSec advisory scan and
CodeQL. That is not enough to merge all of them: the checks have a real blind spot for `server/`
(see below), and one PR does not compile.

## The one real blocker — #44

[#44](https://github.com/alshahia/sada/pull/44) bumps `utoipa-swagger-ui` 9.0.2 → 10.0.2 in `/server`.
It **fails a local compile**:

```
error[E0308]: mismatched types
  --> crates\vibe-server\src\server\mod.rs:149:61
    .merge(SwaggerUi::new("/docs").url("/openapi.json", ApiDoc::openapi()))
    ^ expected `utoipa::openapi::OpenApi`, found a different `utoipa::openapi::OpenApi`
note: there are multiple different versions of crate `utoipa` in the dependency graph
```

`utoipa-swagger-ui` 10 needs `utoipa` 7, while the server pins `utoipa` 6 through `utoipa-axum` 0.2.
This is a coordinated upgrade (`utoipa` + `utoipa-axum` + `utoipa-swagger-ui` + the `/docs` route),
not a drive-by bump. **Do not merge.** Either close it and open one "utoipa 7 upgrade" task, or rebase
it into that task when the trio is compatible.

## Why CI did not catch #44

| Coverage | What it proves | Gap |
| --- | --- | --- |
| Desktop build & tests (windows-latest) | frontend `pnpm build` + `pnpm test`, and `cargo test --release` for `desktop/src-tauri` and the root workspace | does not build `server/` |
| Arabic ASR benchmark harness | Python harness tests + regression-gate self-comparison | not Rust |
| npm advisory scan, RustSec scan | no known advisories in either lockfile | does not compile |
| CodeQL | static analysis of JS/TS | not Rust |

`server/` is its own Cargo workspace. Only `.github/workflows/release.yml` builds it (on a tag), so a
server dependency bump can look green on every PR and break the release. Follow-up is recorded at the
end of this document.

## Inventory and recommendations

### Group 1 — GitHub Actions (5 PRs, no lockfiles, merge first)

| PR | Bump | File(s) | Note |
| --- | --- | --- | --- |
| [#36](https://github.com/alshahia/sada/pull/36) | actions/configure-pages 5 → 6 | pages.yml | node24 runtime; GH-hosted runner |
| [#37](https://github.com/alshahia/sada/pull/37) | astral-sh/setup-uv 5 → 7 | release.yml | node24; drops deprecated `server-url` input (unused here) |
| [#39](https://github.com/alshahia/sada/pull/39) | actions/attest-build-provenance 2 → 4 | release.yml | signature input/output behaviour unchanged for our use |
| [#41](https://github.com/alshahia/sada/pull/41) | actions/setup-node 4 → 7 | ci.yml, release.yml, security.yml | node24 runtime; Node 22 toolchain unchanged |
| [#45](https://github.com/alshahia/sada/pull/45) | github/codeql-action 3 → 4 | security.yml | CodeQL v4 requires current runner images — GH-hosted is fine |

**Recommendation:** merge in any order; they touch no shared lockfile. Verify by watching the next CI
run, the scheduled security workflow and the next release run (attest/pages/setup-uv paths only execute
there).

### Group 2 — desktop npm (5 PRs, `desktop/pnpm-lock.yaml`)

| PR | Bump | Risk |
| --- | --- | --- |
| [#49](https://github.com/alshahia/sada/pull/49) | @radix-ui/react-slot 1.2.4 → 1.5.0 | low; UI primitive |
| [#52](https://github.com/alshahia/sada/pull/52) | @radix-ui/react-select 2.2.6 → 2.4.1 | low; settings selects |
| [#54](https://github.com/alshahia/sada/pull/54) | @radix-ui/react-tabs 1.1.13 → 1.2.1 | low; settings tabs |
| [#56](https://github.com/alshahia/sada/pull/56) | @tauri-apps/plugin-opener 2.5.3 → 2.7.3 | low; open-folder action |
| [#57](https://github.com/alshahia/sada/pull/57) | @tanstack/react-virtual 3.14.10 → 3.14.26 | low; transcript list |

**Recommendation:** merge sequentially; later PRs will conflict on `pnpm-lock.yaml` because each branch
was cut from an older lockfile — comment `@dependabot rebase` on the rest after the first merge, or
resolve once with `pnpm install --lockfile-only`. Smoke after the batch: settings tabs and selects, the
transcript list scroll, and "open folder".

### Group 3 — root workspace Rust (6 PRs, `Cargo.lock`)

| PR | Bump | Note |
| --- | --- | --- |
| [#43](https://github.com/alshahia/sada/pull/43) | winreg 0.55.0 → 0.56.0 | 0.x minor; Windows registry reads |
| [#48](https://github.com/alshahia/sada/pull/48) | x11rb 0.13.2 → 0.14.0 | Linux-only (`meeting-detect`); Windows build unaffected |
| [#50](https://github.com/alshahia/sada/pull/50) | window-vibrancy 0.6.0 → 0.8.1 | 0.x minor; **visual check** of window vibrancy/transparency |
| [#51](https://github.com/alshahia/sada/pull/51) | serde_json 1.0.149 → 1.0.154 | patch |
| [#53](https://github.com/alshahia/sada/pull/53) | tauri-plugin-notification 2.3.3 → 2.8.1 | notification delivery needs a manual check |
| [#55](https://github.com/alshahia/sada/pull/55) | uuid 1.21.0 → 1.29.2 | patch-level API use |

CI already runs `cargo test --release` on this workspace on every PR, so compile and unit tests are
covered. **Recommendation:** merge sequentially (same `Cargo.lock` conflict rule), then run one full
CI and smoke: window transparency, a notification, and the Linux path is compile-only (not shipped).

### Group 4 — server Rust (6 PRs, not built by CI)

Local check: worktree at each PR head, `server/` workspace, `cargo check --all-targets` with the native
libs from the main checkout. Result on 2026-11-21:

| PR | Bump | Local compile |
| --- | --- | --- |
| [#38](https://github.com/alshahia/sada/pull/38) | futures-util 0.3.32 → 0.3.34 | **pass** (exit 0, 14 s) |
| [#40](https://github.com/alshahia/sada/pull/40) | clap 4.6.1 → 4.6.7 | **pass** (exit 0, 6 s) |
| [#42](https://github.com/alshahia/sada/pull/42) | serde_json 1.0.150 → 1.0.154 | **pass** (exit 0, 10 s) |
| [#44](https://github.com/alshahia/sada/pull/44) | utoipa-swagger-ui 9.0.2 → 10.0.2 | **fail** — utoipa 6/7 split (see top) |
| [#46](https://github.com/alshahia/sada/pull/46) | serde 1.0.228 → 1.0.229 | **pass** (exit 0, 34 s) |
| [#47](https://github.com/alshahia/sada/pull/47) | tower-http 0.6.11 → 0.7.1 | **pass** (exit 0, 26 s; 0.6.11 stays in the tree for other crates) |

**Recommendation:** merge the five passing PRs after the other groups; keep #44 out. Then run
`cargo test --release -p vibe-server guard::` once from `server/`, and let the next release tag be the
full end-to-end server build (as it already is).

## Suggested order (owner, ~30–40 min)

1. **Group 1** (Actions) — any order.
2. **Group 2** (npm) — sequential, rebase the rest, then `pnpm build` + `pnpm test`.
3. **Group 3** (root Rust) — sequential, then one full CI run.
4. **Group 4** (server) — merge the five verified PRs; close #44 with a link to a new "utoipa 7
   upgrade" tracking issue (or leave it open and retitle it into that task).
5. After each group: CI on `master` green. No tag, no version bump and no release is part of this work;
   v3.10.0 assets are unaffected.

## Follow-ups (recommended, not blocking)

- **Add a server compile job to CI.** A `server` job in `ci.yml` (`cargo check --all-targets` or
  `cargo test --release -p vibe-server`) would have failed #44 on the PR. The release workflow already
  knows how to fetch the server's native libs; the new job needs the same setup and a decision about
  cost (~5–10 min per PR vs. catching a release-breaking bump).
- **Group Dependabot updates.** Adding `groups:` (patch/minor per ecosystem) to `.github/dependabot.yml`
  would turn the next 22-PR backlog into 3–4 PRs. Validate on the next schedule.
- **Audit the other workflows.** `pages.yml`, `release.yml` and `security.yml` changes are only exercised
  when those workflows run; after merging Group 1, dispatch `security.yml` once (or wait for its
  schedule) and confirm one green run before the next tag.

## Evidence

- PR state, checks and release notes collected 2026-11-21 with `gh pr view 36..57 --json ...`.
- Local server checks 2026-11-21: `git worktree` at each PR head (fetched from `refs/pull/N/head`),
  `CARGO_TARGET_DIR` in scratch, `cd server && cargo check --all-targets`; native `server/libs` supplied
  from the main checkout (the worktree does not download them).
- The same local check on `master` itself passes (baseline), so the #44 failure is caused by the bump.

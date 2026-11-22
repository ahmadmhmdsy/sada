# Execution report — Dependabot merge train (2026-11-21)

Status: **executed, final CI green.** Option A was approved, the reviewed plan in [ruling.md](ruling.md)
ran on 2026-11-21, and the outcome is: 20 of the 20 cleared PRs merged, #44 closed and replaced by the
coordinated upgrade #68 (also merged), #53 stays open and held. No tag, no version bump, no release and no
`release.yml` dispatch — v3.10.0 is untouched.

Master moved from `d68c5b1` (start) to **`c2b8012`** (final). Final CI run
[44907699041](https://github.com/alshahia/sada/actions/runs/44907699041) is green on `c2b8012`; the earlier
master gate run [44906549587](https://github.com/alshahia/sada/actions/runs/44906549587) is green on `74c9f1f`.

## What merged, in order

### 1. npm — `desktop/pnpm-lock.yaml` (checkpoint `1b3b310`)

| PR | Squash commit | Note |
| --- | --- | --- |
| #49 | `5bec797` | @radix-ui/react-slot 1.2.4 to 1.5.0 |
| #52 | `b91c13c` | @radix-ui/react-select 2.2.6 to 2.4.1 |
| #54 | `767b1f2` | conflicted with #52 on the lockfile — rebased via @dependabot, all checks green on the new head (Desktop 11m56s), then merged |
| #56 | `f4209ed` | @tauri-apps/plugin-opener 2.5.3 to 2.7.3 |
| #57 | `1b3b310` | @tanstack/react-virtual 3.14.10 to 3.14.26 |

### 2. root Rust — `Cargo.lock`, #53 excluded (checkpoint `4cc449a`)

| PR | Squash commit | Note |
| --- | --- | --- |
| #43 | `e6e258e` | winreg 0.55.0 to 0.56.0 |
| #51 | `9ce2b40` | serde_json 1.0.149 to 1.0.154 |
| #55 | `4dabf4c` | uuid 1.21.0 to 1.29.2 |
| #48 | `87fe97d` | conflicted on `Cargo.lock` — rebased, checks green, merged; **platform-unverified** (cfg(linux)) |
| #50 | `4cc449a` | window-vibrancy 0.6.0 to 0.8.1; **platform-unverified** (cfg(macos)), no Windows visual surface exists |

### 3. server — `server/Cargo.lock`, #44 excluded (checkpoint `3d6ec36`)

| PR | Squash commit | Note |
| --- | --- | --- |
| #38 | `8299239` | futures-util 0.3.32 to 0.3.34 |
| #40 | `9ed261a` | clap 4.6.1 to 4.6.7; conflicted, rebased, re-checked, merged |
| #42 | `5db57af` | serde_json 1.0.150 to 1.0.154 |
| #46 | `8169271` | serde 1.0.228 to 1.0.229; conflicted, rebased, re-checked, merged |
| #47 | `3d6ec36` | tower-http 0.6.11 to 0.7.1 |

Post-batch gate on the merged tree: `cargo test --release -p vibe-server` — **17 passed, 0 failed**;
`cargo check --all-targets` exit 0; `cargo build --release -p vibe-server` exit 0.

### 4. workflows last (checkpoint `74c9f1f`)

| PR | Squash commit | Note |
| --- | --- | --- |
| #41 | `acd688a` | actions/setup-node 4 to 7 |
| #45 | `e6c53e5` | github/codeql-action 3 to 4 |
| #36 | `222c7ec` | actions/configure-pages 5 to 6 |
| #37 | `2706983` | astral-sh/setup-uv 5 to 7 (inert until signing is enabled) |
| #39 | `74c9f1f` | actions/attest-build-provenance 2 to 4 (first exercised at a real tag) |

After the last merge: `security.yml` dispatch run 44906572973 — success; `pages.yml` dispatch run
44906577556 — success. `release.yml` was **not** dispatched.

### 5. #44 Option A to issue #67 to PR #68 (also merged)

- #44 closed 2026-11-21 12:27Z with the measured diagnosis: the server pinned `utoipa = "5"` (lock 5.5.0),
  while `utoipa-swagger-ui` 10.0.2 pulls `utoipa` 6.0.0 — a two-version graph and a hard `E0308`.
- Tracking task **#67** opened: coordinated utoipa 5 to 6 upgrade.
- PR **#68** `chore(server): coordinated utoipa 5 to 6 upgrade` — `utoipa` 6.0.0, `utoipa-gen` 6.0.1,
  `utoipa-axum` 0.3.0, `utoipa-swagger-ui` 10.0.2. No source changes were needed; the duplicate-utoipa
  error disappears once the trio moves together.
- Local gates on the branch: check exit 0, 17 tests passed, release build exit 0. PR checks green after a
  rebase onto `74c9f1f`; merged as `c2b8012`.

## Deviations from the ruling (recorded honestly)

1. **CI gates were compressed, not skipped.** Batches 2-4 merged back-to-back, so intermediate master CI
   runs were cancelled by the concurrency group (`ci.yml`, `cancel-in-progress: true`) before proving
   themselves. The surviving final run on `c2b8012` (all merges plus the workflow bumps) is green, and the
   batch checkpoint SHAs above allow a bisect if a regression appears. This is the main process compromise
   against the ruling requirement to wait for the run at the end of each batch.
2. **Interactive smoke was not performed by the agent.** Merges ran headlessly and this machine has no UI
   automation harness for the Tauri window. Automated gates used instead: CI desktop job (`pnpm build`,
   `pnpm test`, `cargo test --release`), local server suite and build on the merged tree, all PR checks.
   Owner spot-check recommended on next launch (5 minutes): settings selects by keyboard, licence link,
   60-row transcript scroll/search/mid-list edit, one notification toast.
3. **#48 and #50 are platform-unverified** by design (cfg(linux) / cfg(macos)); merged as hygiene, no
   vibrancy claim made.
4. The kill-date (2026-11-28) was not needed — the train finished the same afternoon.

## Remaining

- **#53** is the only open dependency PR. It stays held for the Tauri gate: rebase, installer build from
  the branch (`pnpm exec tauri build`), clean-machine offline-installer test, `@tauri-apps/cli` aligned to
  2.12, then merge before v3.11.0. The Dependabot scheduled run rebased it to `f902d43` on 2026-11-21; it
  remains unmerged.
- Follow-ups unchanged: server compile job in CI; Dependabot groups; release-prep fixes (`-sada.2` sidecar
  suffix, `SHA256SUMS.txt` in the attestation subjects, setup-uv/attest validation at the v3.11 tag).
- Owner-only items unaffected (A1/A2/A3/A5/A12, Ollama install for FC-5, the five-user gate).

## Evidence

- Final master log: `f1d16eb` (docs) to `c2b8012` (#68), 21 dependency/upgrade commits.
- Final CI: 44907699041 success on `c2b8012`; master gate: 44906549587 success on `74c9f1f`.
- Dispatches: security.yml 44906572973 success; pages.yml 44906577556 success.
- Server gates: 17/17 tests, check exit 0, release build exit 0 — on the merged tree and on the #68 branch.
- v3.10.0 unchanged: tag object `ab6b1de` to commit `be27bd5`; release created 2026-11-19 12:40Z with
  8 assets; no release workflow was run.

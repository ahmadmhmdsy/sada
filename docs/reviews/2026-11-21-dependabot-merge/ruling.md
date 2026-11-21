# Review room ruling — the Dependabot merge train (2026-11-21)

**Target:** `alshahia/sada` master `d68c5b1` (2026-11-21), 22 open Dependabot PRs (#36–#57), 0 merged.
**Reviewed by:** a review room (five role voices, silent Maestro) over an evidence pack, with four independent read-only subagents: auditor, product first-contact, maintenance/process, release/supply-chain.
**Artifacts:** [session.json](session.json) · [review-room-transcript.html](review-room-transcript.html) · [evidence.md](evidence.md)
**Verdict:** approve with corrections — do not execute the triage as originally written.

## Decision

**Correct the record, then merge 20 of the 22 pull requests in four gated batches; hold #53 for its Tauri gate, never merge #44, and dispatch no release.**

The merge decision remains the owner's (OWNER-ACTIONS A9). One sentence from the owner starts the train: “approved, merge batches” (or a named batch order), or “hold”.

## What the room proved wrong in the triage

1. `docs/DEPENDABOT-TRIAGE.md:24,26,98,111` — the #44 diagnosis is wrong on both sides: the server pins `utoipa = "5"` (`server/crates/vibe-server/Cargo.toml:46`, lock 5.5.0), and `utoipa-swagger-ui` 10.0.2 pulls `utoipa` 6.0.0. The remedy is a coordinated 5→6 upgrade with a `utoipa-axum` that accepts 6, not a “utoipa 7” task.
2. `:11` — “the one real blocker” is false. A sequential replay of the printed order conflicts at #54 (`desktop/pnpm-lock.yaml`), #48 (`Cargo.lock`), #40 and #46 (`server/Cargo.lock`). Individually all 22 merge cleanly; cumulatively they do not.
3. `:6` — the “green” checks are from 2026-11-19 06:12–06:23Z, before `be27bd5` (v3.10.0). master has moved 20 commits and 104 files since. No PR check has run against the current tree.
4. `:84` — “CI already runs `cargo test --release` on this workspace” is false: `ci.yml:70-72` builds the desktop crate only (no `--workspace`); `meeting-detect` tests never run.
5. `:79` — #48 is `cfg(linux)` code and #50 is `cfg(macos)` code; windows-latest compiles neither. The promised “window transparency” check has no Windows surface (there is no transparent window setting in `tauri.conf.json`).
6. `:81` — #53 is not a notification bump: it moves 57 packages, including tauri 2.10.3→2.12.7, wry 0.54.2→0.57.3, tao 0.34.6→0.37.3 and webview2-com 0.38.2→0.39.1, because `tauri-plugin-notification` 2.8.1 requires tauri ^2.12. No CI job ever runs `pnpm exec tauri build` — v3.11.0 installers would be the first built by that stack.
7. `:55` and `:113` — the CI gate as written cannot fire: `ci.yml:17-19` uses `cancel-in-progress: true`, so 21 merges in 30–40 minutes cancel each other; and the plan has no checkpoint, revert recipe, merge method or kill-date.
8. `:130` — the evidence line “`gh pr view 36..57 --json …`” is not a runnable command.

Release-side findings that shaped the plan: dispatching `release.yml` against v3.10.0 does not dry-run — it re-publishes the live tag with different digests; `setup-uv` v7 will not run while signing is disabled (`vars.SIGNING_ENABLED`, owner action A5); `attest-build-provenance` v4 runs before the release step, so its first exercise is a real publish; the sidecar suffix `-sada.1` would cover a third distinct binary and the attestation subject list omits `SHA256SUMS.txt`.

## Preconditions

| check | command / evidence | state |
| --- | --- | --- |
| clean tree | `git status --porcelain`, master `d68c5b1` | done |
| triage record corrected | the lines above fixed and committed | in flight |
| conflict points written down | #54, #48, #40, #46; rebase rule for every batch | decision, this ruling |
| mergeability re-measured per merge | `git merge-tree` + `gh pr view --json mergeable` before each merge | done once, repeat per merge |
| #44 disposition | close with measured 5.5.0/6.0.0 split; open coordinated 5→6 upgrade | owner action |
| merge method | `gh pr merge --squash` (one revert target per PR) | decision, this ruling |
| checkpoint + rollback | record `git rev-parse HEAD` per batch; `git revert` batch in reverse order | decision, this ruling |
| surface baseline | app launch, toast, keyboard selects, licence link, 60-row transcript | in flight |
| release dispatch forbidden | `gh workflow run release.yml` re-publishes v3.10.0 with new digests | decision, this ruling |
| no release in scope | no tag, no version bump, no release | scope fence |

## Batches (merge method: squash; one CI window per batch, 7–12 min each; plan 2–3 h elapsed)

### Phase 1 — Correct the record and freeze the baseline (day 0, 45 min)
- Fix the triage lines above; add merge method, rebase rule, checkpoint, revert recipe, kill-date.
- Record the surface baseline: app launches; notification toast observed in Action Center; main mic select and settings selects driven by keyboard only; licence link opens the browser; 60-row transcript scrolled to the composer and a row edited mid-list.
- Close #44 (or retitle it) and open the coordinated utoipa 5→6 upgrade task.
- **AC-1:** the cited triage lines are corrected and committed; measured 5.5.0/6.0.0 split stated.
- **AC-2:** baseline artefacts exist under `docs/reviews/2026-11-21-dependabot-merge/`.
- **AC-3:** #44 closed/retitled and the 5→6 upgrade task exists.

### Phase 2 — npm batch (day 0, 20 min + one CI window)
- #49, #52, #54, #56, #57. Before each merge: fresh `merge-tree` and `mergeable`; on conflict `@dependabot rebase`, wait for fresh checks, re-verify. #52×#54 is a known conflict.
- After the batch: wait for the surviving master CI run; smoke selects, licence link, transcript virtualization (End → last row above composer; search remeasure; row edit anchored).
- **AC-4:** 5/5 merged after per-merge freshness (or rebase + fresh checks).
- **AC-5:** master CI green for the post-batch checkpoint SHA.
- **AC-6:** three smoke lines recorded pass/fail with before/after artefacts.

### Phase 3 — root Rust batch, #53 excluded (day 0, 20 min + one CI window)
- #43, #51, #55, #48, #50. `#48` and `#50` are platform-unverified (cfg(linux)/cfg(macos); no CI compiles them) and are recorded as such — no vibrancy claim is made.
- **AC-7:** 5/5 merged and post-batch master CI green.
- **AC-8:** #48/#50 recorded platform-unverified with their reopening trigger.

### Phase 4 — server batch (day 0-1, 25 min + one CI window)
- #38×#40 and #42×#46 conflict on `server/Cargo.lock`: rebase first, then re-compile the new head (the earlier pass rows no longer describe it). Merge #38 #40 #42 #46 #47; #44 out.
- Then from `server/`: `cargo test --release -p vibe-server` (full suite, not only guard), `cargo check --all-targets`, and `cargo build --release -p vibe-server` (release profile links; release.yml is otherwise the first release compile).
- **AC-9:** 5/5 merged after rebase + recompile; post-batch master CI green.
- **AC-10:** full server test suite, check and release build exit 0 on the merged tree.

### Phase 5 — workflow batch last (day 1, 15 min + dispatch runs)
- Merge #41, #45, #36, #37, #39; then `gh workflow run security.yml --ref master` and `gh workflow run pages.yml --ref master`.
- Do not dispatch `release.yml`; its #37/#39 validation is deferred to the v3.11 tag rehearsal.
- **AC-11:** 5/5 merged and following master CI green.
- **AC-12:** security.yml and pages.yml dispatch runs succeed.
- **AC-13:** release.yml not dispatched; the v3.10.0 re-publish hazard and the deferred validation are recorded.

## What waits, and why (trigger = external evidence that reopens it)

| item | when | trigger |
| --- | --- | --- |
| Server compile job in CI | next workflow change, before the utoipa upgrade | a second server bump escapes the local matrix, or the v3.11 tag fails building server/ |
| Linux/macOS compile validation for #48/#50 | first non-Windows build or cross-target job | a platform build fails on x11rb or window-vibrancy |
| Tauri upgrade gate for #53 | before v3.11.0, release prep | installer build fails, offline installer fails on a clean machine, or the CLI stays at 2.10 while the crate is 2.12 |
| Coordinated utoipa 5→6 upgrade (#44 rework) | now unblocked — can start immediately | utoipa 6.0.0 + utoipa-axum 0.3.0 + utoipa-swagger-ui 10.0.2 are published and all align on utoipa 6.0.0 (verified 2026-11-21); the task is a bump of all three plus derive/API fixes |
| setup-uv 7 (#37) and attest v4 (#39) validation | first signed release; v3.11 tag rehearsal | signing enabled without a green setup-uv 7 run; tag run fails after builds (fix and re-run, no assets published) |
| Sidecar suffix `-sada.2` + SHA256SUMS attestation subject | v3.11.0 release prep | third binary under the same `-sada.1`; user cannot `gh attestation verify SHA256SUMS.txt` |
| Dependabot grouping (patch/minor per ecosystem) | after this train, next cycle 2026-11-30 | backlog returns above 5 PRs in one ecosystem |
| Dead tabs component removal | next UI cleanup | someone imports `ui/tabs` |

## Command sequence

```bash
# from E:/rea/vibe_app/app, master, clean tree
git status --porcelain && git log -1 --format=%h

# freshness: repeat BEFORE EVERY merge (example #49)
git fetch origin refs/pull/49/head:refs/depcheck/pr-49
git merge-tree --write-tree HEAD refs/depcheck/pr-49
gh pr view 49 --json mergeable,mergeStateStatus

# expected conflicts (#52x#54, #38x#40, #42x#46): rebase, wait for fresh checks, re-verify
gh pr comment 54 --body "@dependabot rebase"
gh pr checks 54 --watch
git fetch origin refs/pull/54/head:refs/depcheck/pr-54
git merge-tree --write-tree HEAD refs/depcheck/pr-54

# batch 1 - npm
gh pr merge 49 --squash && gh pr merge 52 --squash && gh pr merge 54 --squash
gh pr merge 56 --squash && gh pr merge 57 --squash
gh run list --workflow ci.yml --branch master --limit 1 --json databaseId,status,conclusion,headSha
gh run watch <databaseId> --exit-status && git rev-parse HEAD

# batch 2 - root Rust, #53 excluded
gh pr merge 43 --squash && gh pr merge 51 --squash && gh pr merge 55 --squash
gh pr merge 48 --squash && gh pr merge 50 --squash

# batch 3 - server, rebase conflicts and recompile at the new head
gh pr comment 38 --body "@dependabot rebase"
gh pr merge 38 --squash && gh pr merge 40 --squash && gh pr merge 42 --squash
gh pr merge 46 --squash && gh pr merge 47 --squash
cd server && cargo test --release -p vibe-server && cargo check --all-targets && cargo build --release -p vibe-server && cd ..

# batch 4 - workflows last, then dispatch only these two
gh pr merge 41 --squash && gh pr merge 45 --squash && gh pr merge 36 --squash
gh pr merge 37 --squash && gh pr merge 39 --squash
gh workflow run security.yml --ref master
gh workflow run pages.yml --ref master
# never: gh workflow run release.yml (it re-publishes v3.10.0 with new digests)

# rollback a failing batch: revert its squash commits in reverse order
git revert <last-squash-sha> <prev-squash-sha> && git push origin master
```

## Scope fence

- No tag, version bump, release or `release.yml` dispatch.
- No merge of #44 and no merge of #53 in this train.
- No up-front rebase of all 20 branches: rebase at conflict time and re-verify the new head.
- No new CI job in this pass (server job is a follow-up with a trigger).
- No macOS/Linux smoke claim for #48/#50; no sidecar, attestation-subject or branch-protection changes.
- No documentation scope beyond the corrected facts, the baseline record and this report.

## Kill-criterion

**2026-11-28** — if the four batches are not complete by then, refresh mergeability and check timestamps for every remaining PR and re-run this ruling instead of resuming it. If a batch fails CI or smoke, revert it the same day; a batch that stays red on master for a working day means the gate is decorative and the plan is wrong.

## Owner confirmation

The report does not merge anything. Reply **“approved, merge batches”** (or a named order) to start at phase 1, or **“hold”** to keep the PRs open. The record corrections and the baseline are worth committing either way.

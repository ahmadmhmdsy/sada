# P5 plan — distribution, offline install and benchmark regression gate (v3.8.0)

Status: **in progress** (2026-11-18). Milestone
[#6](https://github.com/alshahia/sada/milestone/6) · issues
[#22](https://github.com/alshahia/sada/issues/22) ·
[#23](https://github.com/alshahia/sada/issues/23) ·
[#24](https://github.com/alshahia/sada/issues/24) ·
[#25](https://github.com/alshahia/sada/issues/25) ·
[#26](https://github.com/alshahia/sada/issues/26). Predecessor: [P4 plan](P4-PLAN.md).

## Why this release

v3.7.0 finished the *measurement* story: 90 clips, five model variants, a recorded negative
prompt result and an honest unmeasured-dialect list. What still stands between the release and a
user who just wants to install it is **distribution trust**, and what stands between today and a
future silent accuracy regression is a **gate**. P5 is deliberately not a feature release:

1. **Offline install.** The 45 MB NSIS installer uses Tauri's `downloadBootstrapper`, so a
   Windows 10 machine that has never run a modern app is asked to download WebView2 — impossible
   when the target is an offline lab. Build a second installer variant with
   `webviewInstallMode = offlineInstaller` and publish it as an extra asset. The small installer
   stays the default.
2. **Signing staged, not switched on.** The owner decided on 2026-11-18 to keep releases **unsigned
   while the project is open-source-only**; the SignPath/Azure application (issue #18) comes later.
   Stage the workflow steps behind `SIGNING_ENABLED` so enabling is configuration, not a redesign.
3. **Production-readiness answer.** "Is it production ready?" cannot be answered with a slogan.
   Write `docs/PRODUCTION-READINESS.md` with per-audience verdicts and links to the evidence that
   exists — including what is *not* covered (clean-machine rows B–E, Iraqi/Levantine accuracy,
   unsigned binary, no telemetry/crash reporting by design).
4. **Regression gate.** `sadabench compare` diffs a fresh run against the committed 90-clip
   baseline, prints overall/per-slice deltas, and exits non-zero past a tolerance. It is used in
   the release checklist; the CI job exercises it on the committed report.

## Out of scope

- No engine, model-catalogue or transcription-behaviour change; no new UI feature.
- No signing application and no purchase (owner decision later; #18 stays open).
- No new corpora (Iraqi/Levantine stay unmeasured until a commercial-use corpus is bought or found).
- No upstream rebase (planned as v3.9.0; see ROADMAP backlog).

## Design

### Offline WebView2 installer variant (#22)

- Add `desktop/src-tauri/tauri.offline.conf.json` — a Tauri config **overlay**, merged by
  `tauri build --config`, that only changes
  `bundle.windows.webviewInstallMode` to `offlineInstaller`. The base config keeps the small
  bootstrap installer as the default, so nothing changes for normal downloads.
- Release workflow: build the offline variant first, copy it out as
  `Sada_<version>_x64-setup-offline.exe`, then build the default installer and copy it as
  `Sada_<version>_x64-setup.exe`; `SHA256SUMS.txt` gets one line per installer.
- Docs: README/BUILDING explain which file to pick (online vs offline), release notes list both
  sizes and hashes, and `docs/VERIFICATION.md` records a silent install of each.

### Dormant signing (#23)

- Release workflow gets `if: vars.SIGNING_ENABLED == 'true'` steps: submit the unsigned installer
  to SignPath, then verify the returned Authenticode signature with
  `Get-AuthenticodeSignature`. With the variable unset (today) the steps are skipped and the
  release is exactly as before.
- `docs/SIGNING.md` gets a **Status** section: deferred by owner, unsigned OSS releases, exact
  variables/secrets to set later, verification command.

### Regression gate (#25)

- `sadabench/compare.py`: `compare_reports(baseline, candidate, tolerance_pp)` validates that the
  reports are the same manifest/suite (same clips and model ids; engine and version differences are
  warnings), then computes `candidate - baseline` deltas for overall and per-slice WER/CER/Latin
  preservation. Regression = delta **> tolerance** (higher is worse); baseline deletes are errors.
- CLI: `python -m sadabench compare --baseline results/results-2026-11-18-v2.json --candidate
  <run.json> [--tolerance-pp 1.0] [--json]`. Exit codes: 0 within tolerance, 1 regression,
  2 unusable input.
- The committed v2 report is the baseline. Release checklist: run the benchmark, compare against
  the baseline, attach both; a regression blocks the release until understood.

### Production readiness (#24)

`docs/PRODUCTION-READINESS.md` categories: release pipeline, tests, security/privacy, data
handling, Arabic accuracy, installation, maintenance, field evidence. Verdicts:
**personal/small-team use — ready with named caveats**; **managed/enterprise deployment — not yet**
(blockers: unsigned installer, clean-machine rows B–E, no managed-install/backup story). Arabic
summary included; no claim without a link to committed evidence.

## Acceptance criteria

- [ ] Both installers are produced and published with distinct names and SHA-256 lines; the offline
      variant installs silently on a machine and the default variant behaves as before.
- [ ] With `SIGNING_ENABLED` unset, CI/release are unchanged and green; `docs/SIGNING.md` states
      the deferred decision and the switch-on procedure.
- [ ] `docs/PRODUCTION-READINESS.md` exists, is linked from README and release notes, and every
      claim traces to evidence (no unmeasured dialect/acronym claim).
- [ ] `sadabench compare` has tests for identical reports, a real regression, the tolerance
      boundary and incompatible inputs; the CI benchmark job runs it on the committed report.
- [ ] Full test matrix green (pnpm test/build, cargo test 101+, guard 8, cargo check --tests, i18n
      audit, Python suite), v3.8.0 tagged, release verified and recorded in
      `docs/VERIFICATION.md` / `docs/ACCEPTANCE.md`.

## Reproduction

```powershell
cd app/benchmarks/arabic-asr
python -m unittest discover -s tests
python -m sadabench compare `
  --baseline results/results-2026-11-18-v2.json `
  --candidate results/results-2026-11-18-v2.json
```

```powershell
cd app/desktop
# default small installer
pnpm exec tauri build --bundles nsis
# offline WebView2 variant (second asset)
pnpm exec tauri build --bundles nsis --config src-tauri/tauri.offline.conf.json
```

## Risks

- WebView2 offline installer adds roughly 218 MB (the finished asset is about 250 MB instead of
  about 45 MB) and build time: the config overlay changes the embedded app config, so the second
  pass recompiles the app (about 5 minutes with cached dependencies) and then runs NSIS on a large
  already-compressed installer. The release job has a 90-minute timeout; measured local build was
  about 8 minutes for the default installer and about 9 minutes for the offline one.
- A dormant signing step that is never executed can rot. It is guarded and documented, and the
  verification command is runnable locally, but it stays untested until #18 is enabled — recorded
  as such in SIGNING.md.
- The compare tool can only catch changes it runs on; per-push benchmarking stays too expensive
  (model + 90 clips). The gate is a release gate, not a PR gate — say that explicitly.

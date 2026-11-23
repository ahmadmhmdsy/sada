# Upstream rebase assessment — Vibe v3.2.2 → latest (v3.3.8)

**Status: assessment, 2026-11-23. No upstream code was ported by this document.** Base: upstream
`thewh1teagle/vibe` tag **v3.2.2**, commit `23eae78b` (2026-09-05). Target: **v3.3.8**, commit
`218520d0` (2026-11-21) — the latest upstream release. ROADMAP still named v3.3.5; the newer tags
(v3.3.6, v3.3.7, v3.3.8) exist and v3.3.8 is the right target. The evidence commands are in §8 and
were run against a fetched `upstream` remote on 2026-11-23.

## 1. Executive summary

- **Upstream delta:** 50 commits, 445 files changed, +23,366 / −8,007 lines between v3.2.2 and v3.3.8.
- **A git rebase is the wrong tool.** The fork's history was rewritten at creation, the fork made
  deliberate removals (telemetry, updater, phone relay) that conflict with upstream direction, and 66
  files are changed on both sides. Port **feature groups as PRs against `master`**, not a tree merge.
- **Highest-value item is also the most urgent: the engine source tree is older than the version
  label the installer reports** (§3). Since v3.4.0 the release builds `server/` from source, but that
  tree is the pre-0.6.13 engine; the `v0.6.16-sada.N` string comes from `.server-version` via
  `VIBE_SERVER_VERSION`. The shipped engine therefore lacks the 0.6.13+ code, including the
  `nemotron-diarize-rs` path that the app's shipped diarization model depends on. **Speaker labels are
  a likely silent regression and must be reproduced before the next release.**
- **Second:** desktop reliability fixes from v3.3.1–v3.3.6 (large files, Vulkan errors, microphone
  selection, cancel, ffmpeg errors) are not ported.
- **Third:** the v3.3.x desktop UX work (sentence/paragraph transcript, preparing state, CPU-variant
  setting, model deep links) collides with Wave 2 and the 4.0 identity plans; decide its order rather
  than mixing it in by accident.
- **Estimated effort:** 4–7 agent days for the two P1 groups (engine sync + reliability), plus 2–4 days
  for selected UX. Two releases, not one.

## 2. What the fork already has (do not re-port)

- The v3.3.6 security hardening (downloads, yt-dlp, webview, keystroke permit) is already ported —
  see [UPSTREAM-PATCHES.md](UPSTREAM-PATCHES.md) §10.
- Own equivalents of upstream's 3.3.3 "Get models" work: verified model catalogue, install flow,
  capability probing, MCP ([UPSTREAM-PATCHES.md](UPSTREAM-PATCHES.md) §9).
- MCP server, the loopback engine guard, Arabic-first locale and rebranding (fork-only work).
- Tauri 2.12 stack and the 2026-11-21 dependency set, newer than upstream v3.3.8.
- Upstream engine source at the v3.2.2/v3.3.1 snapshot (see §3) plus the guard.

## 3. Finding — engine source vs engine label

| Check | Result |
| --- | --- |
| `git diff --name-only v3.3.1 master -- server/` | **4 files**: `server/Cargo.lock`, `server/crates/vibe-server/Cargo.toml`, `src/server/guard.rs`, `src/server/mod.rs` (the guard and its wiring) |
| Upstream `server/` changes v3.2.2 → v3.3.1 | **0 files** (the engine tree in this monorepo was unchanged across those releases) |
| Upstream `server/` changes v3.3.1 → v3.3.2 | **61 files**: `diarize-rs` removed, `nemotron-diarize-rs` added, `zipformer-rs` added, whisper compression gate, new CPU patches, sentence-timing support, … |
| Upstream `server/` changes from the fork tree to v3.3.8 | **89 files** |
| Fork `server/Cargo.toml` workspace members | `diarize-rs`, `nemotron-rs`, `parakeet-rs`, `vibe-server`, `vad-rs`, `ggml-rs-sys`, `whisper-rs` — **no `nemotron-diarize-rs`, no `zipformer-rs`** |
| `.server-version` | `v0.6.16`; the release workflow sets `VIBE_SERVER_VERSION="$(.server-version)-sada.2"` and runs `chore server-build` = `cargo build -p vibe-server --release` in `server/` |
| Diarization code in the fork | `server/crates/vibe-server/src/server/diarization.rs` → `diarize_rs::Diarizer` (Sortformer). On failure it logs `diarization failed, skipping speakers` and returns no speakers. There is no Nemotron diarization loader. |
| App-side diarization | `desktop/src/lib/config.ts` pins `nemotron-3-diarization-Q8_0.gguf` (108,541,632 B); `desktop/src-tauri/src/cmd/transcribe.rs` passes `diarize_model`; README/CLAIM-LEDGER still describe "~25 MB" speaker labels |

**What this means:** a build labelled `vibe-server v0.6.16-sada.2` is compiled from a tree that is
materially older than upstream 0.6.16. The v3.3.1 E1 evidence ("Nemotron-3 diarization 12/12
segments") was recorded against the **fetched upstream v0.6.16 binary**; from v3.4.0 the installer
ships a source-built engine that cannot load that GGUF with the Sortformer diarizer. Speaker labels
are therefore likely absent (silently) from v3.4.0 through v3.11.0, and the downloaded 108 MB model
is unused.

**Required actions (owner decision on order):**

1. Reproduce speaker labels on the current 3.11.0 installer with the Nemotron GGUF; record the result.
2. If confirmed: port the upstream engine tree (§4, group 1) as the next patch/minor release, then
   correct the claims (README/CLAIM-LEDGER/release notes) or mark speaker labels as "being restored"
   until the port ships.
3. Fix the version label: `v0.6.16-sada.N` must mean upstream source parity, not just a workflow
   string. Either port 0.6.16+ source before the next build or rename the label to
   `sada-engine-<date>` so SBOM/AV-EDR/verification records stay truthful.
4. Correct [UPSTREAM-PATCHES.md](UPSTREAM-PATCHES.md) §9 ("engine tree is otherwise upstream v0.6.16
   code") — it is the v3.2.2/v3.3.1 snapshot plus the guard.

## 4. Port matrix

| # | Group | Upstream evidence | Conflict risk | Recommendation | Effort |
| --- | --- | --- | --- | --- | --- |
| 1 | **Engine tree sync** — `nemotron-diarize-rs`, `zipformer-rs`, whisper compression gate, CPU SSE4.2 patches 0004/0005, sentence-timing support, large-file/Vulkan engine fixes, server 0.6.17 | `ce17e693`…`218520d0`; server tree diff 89 files | Medium: reapply the guard on `server/mod.rs`, `Cargo.lock`, libs fetch, workflow versioning | **P1, own release before more UI** | 2–3 days + release verification |
| 2 | **Desktop reliability fixes** — crashes on large files, Vulkan errors, wrong microphone, cancel; ffmpeg error reporting; repetitive-window retry; temperature 0 | `81648cc3`, `ee496264`, `57632b19` | Medium: transcribe/audio/server process paths are fork-modified | **P1/P2** | 1–2 days |
| 3 | **Desktop UX from 3.3.x** — sentence/paragraph transcript rebuild and earlier start, preparing/progress state, transcript row/highlight/segment editor, CPU-variant setting + relaunch | `57632b19`, `c5f5b31b`, `ea96407c`, `3522a80e`, `bceab42c` | High: overlaps Wave 2, `globals.css`, transcript UI, i18n keys, identity plans | P2/P3 — fold into a UI release the owner picks, one item per PR | 2–4 days |
| 4 | **Model catalogue additions** — Orukeet, Slovak, Hebrew Zipformer; Nemotron-3 diarization entry | `c7444d9e`, `be58cbb2`, `2c98259d`, `3db86e1b` | Low | Only what Arabic scope needs; Arabic models unchanged | 0.5 day |
| 5 | **Model deep links, e2e harness, legacy-temperature migration** | `c7444d9e`, `e2e`, `799f4e6a` | Low | Optional, after P1/P2 | 0.5–1 day |

**Deliberately not ported:** the analytics client and telemetry, the updater (channels, policy,
background downloads, update banner), stable/beta switch, phone relay/handoff WASM, Linux/macOS paths,
the upstream React website and model pages, upstream i18n changelog pages (135 files), and upstream
version bumps. They contradict fork invariants ([AGENTS.md](../AGENTS.md)) or do not apply to a
bilingual Windows-only fork.

## 5. Conflict hotspots (the 66 files changed on both sides)

| Area | Files | Note |
| --- | --- | --- |
| UI shell | `globals.css`, `transcript-view.tsx`, `layout.tsx`, `recents-sidebar.tsx`, settings pages | Every change needs Arabic review; identity work (4.0) should land either before or after, not interleaved |
| Transcript/queue logic | `use-transcribe-queue.ts`, `session.tsx`, `transcript-toolbar.tsx`, `transcript-export-dialog.tsx` | Fork already post-processes Arabic text; upstream sentence grouping must compose with it |
| Rust app | `cmd/audio.rs`, `cmd/transcribe.rs`, `cmd/download.rs`, `server/process.rs`, `handoff/transcribe.rs` | Fork removed relay/updater paths; keep those removals |
| i18n | `i18n/desktop/en-US.json` (+ `ar-IQ.json`) | ~786 keys each today; every port adds keys to both, Arabic first |
| Config/build | `tauri.conf.json`, `Cargo.lock`, `.server-version`, workflows | Tauri 2.12 and the fork's release chain are deliberately ahead; do not downgrade |
| Server | `server/crates/vibe-server/src/server/mod.rs`, `Cargo.toml`, `Cargo.lock` | Guard must be re-applied on every engine sync |
| Docs | `README.md`, `docs/BUILDING.md`, `docs/ARCHITECTURE.md` | Fork-owned wording; take facts, not text |

## 6. Recommended sequence

1. **Verify the speaker-label regression** on the current installer (§3, action 1). This decides
   whether the engine sync is a hotfix or a planned release.
2. **Engine sync release (P1)** — one branch, server tree replaced from upstream v3.3.8, guard
   re-applied, model catalogue aligned to the real engine, `VIBE_SERVER_VERSION` label made truthful.
   Verification: benchmark 90-clip suite vs the committed baseline (Arabic text must not regress),
   Nemotron-3 diarization smoke (12/12 target), guard tests, CPU/GPU smoke, install rehearsal.
3. **Reliability fixes (P1/P2)** — port as small PRs on top of the synced engine.
4. **UI release (P2/P3)** — the chosen 3.12 scope; sentence/paragraph transcript work enters only if
   the owner picks it and the five-user gate does not contradict it.
5. Update [UPSTREAM-PATCHES.md](UPSTREAM-PATCHES.md) with a new section and re-run
   `node scripts/seo/check-seo.mjs`.

Do not attempt a full tree rebase: the fork's removals, rebranding, Arabic-first i18n and release
chain make the merge larger and riskier than the incremental port, and it would silently resurrect
telemetry/updater code that is contractually removed.

## 7. Decisions needed

- Reproduce and confirm the speaker-label regression (agent can run this).
- Choose the engine-sync release vehicle (recommended: before more UI).
- Approve the claims correction if the regression is confirmed.
- Decide the order of engine parity vs Wave 2/identity.

## 8. Evidence commands (reproducible)

```powershell
cd app
git remote add upstream https://github.com/thewh1teagle/vibe.git   # once
git fetch upstream --tags
git log --oneline 23eae78b..v3.3.8            # 50 commits
git diff --shortstat 23eae78b..v3.3.8         # 445 files, +23366/-8007
git diff --name-only v3.3.1 master -- server/ # 4 files (guard)
git diff --name-only v3.2.2 v3.3.1 -- server/ # 0 (source unchanged across those tags)
git diff --name-status v3.3.1 v3.3.2 -- server/ | Measure-Object -Line  # 61
git show v3.3.8:server/Cargo.toml             # nemotron-diarize-rs, zipformer-rs
```

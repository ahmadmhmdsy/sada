# Gate run pack — 3.11.0

**Status 2026-11-23: ready to run.** The [GATE-KIT](GATE-KIT.md) was refreshed from the 3.10 build to
the published, verified **3.11.0** installer. Everything that can be prepared in the repository is
prepared; the five sessions themselves are the owner's to run ([OWNER-ACTIONS A17](../../OWNER-ACTIONS.md)).

Why 3.11.0 is the right build: 3.11.0 is a maintenance cut — dependency refresh, CI and Tauri 2.12,
with **no UI, engine, model or transcription change** ([release notes](../../releases/v3.11.0.md)).
The 3.10-era tasks, thresholds and decision text therefore still apply, and the installer is the
asset that was re-downloaded, hash-checked and attestation-verified on 2026-11-22.

## What changed from the 3.10 kit

- Installer row: published `Sada_3.11.0_x64-setup.exe` — 44,013,711 bytes, SHA-256
  `57742cf25cc73bbf62e2775035658b1d5194fb2f5de8252b04676e5d083d2929` (verified
  [VERIFICATION.md](../../VERIFICATION.md)).
- Decision wording now targets 3.12 Wave 2 / the 4.0 preview instead of "3.11 Wave 2".
- Thresholds, tasks, task order, scoring and evidence rules are unchanged.

## 1. Pre-flight (30–45 min)

1. **Get the installer and verify the hash**:

   ```powershell
   $asset = "$env:USERPROFILE\Downloads\Sada_3.11.0_x64-setup.exe"
   (Get-FileHash $asset -Algorithm SHA256).Hash -eq '57742CF25CC73BBF62E2775035658B1D5194FB2F5DE8252B04676E5D083D2929'
   ```

   The full verifier also covers the attestation:
   `pwsh -File scripts/verify-release.ps1 -Version 3.11.0 -Download` (see
   [release verification](../../VERIFICATION.md)).
2. **Copy to USB** (two copies, in case a participant's device blocks the file): the installer and
   `sample-ar-30s.m4a` (30–60 s Arabic clip for task 3).
3. **Build the broken model**: create a folder with a fake `ggml-medium.bin` (a few KB text file
   renamed). This produces a real model-kind error without touching participant files.
4. **Print**: five observation sheets ([GATE-KIT §4](GATE-KIT.md)), five sets of task cards
   ([§3](GATE-KIT.md)), one scoring table ([§5](GATE-KIT.md)), and the consent line at the top of the
   observation sheet. Keep results anonymised as P1…P5.
5. **Book the room and people**: 5 Iraqi-Arabic speakers (none who has seen the boards; at least 3
   installing Sada for the first time on their own Windows 10/11 device), one moderator and one
   note-taker for all sessions, five 45-minute slots.
6. **Optional smoke**: install the 3.11.0 asset once on a scratch device and uninstall it, so the
   session does not discover an installer problem.

## 2. Session agenda (45 minutes each)

| Time | Step |
| --- | --- |
| 0–5 | Welcome, consent, write the installer SHA-256 and "first install?" on the sheet |
| 5–17 | Task 1 — install, first run, trust question (12 min) |
| 17–19 | Task 2 — find Settings (2 min) |
| 19–27 | Task 3 — finish a transcript and get the text out (8 min) |
| 27–33 | Task 4 — deliberately broken model, recovery (6 min) |
| 33–38 | Task 5 — Arabic UI read-through (5 min) |
| 38–45 | Thank the participant, clean the device, finish notes while fresh |

Rules of engagement are in [GATE-KIT §2](GATE-KIT.md): read the card verbatim, think-aloud, rescue
only after 60 s (rescued = failure), answer questions with questions, never mention the repairs.

## 3. Scoring and the decision

1. Fill the five-row scoring table in [GATE-KIT §5](GATE-KIT.md) from the sheets.
2. Outcome: **pass** = all five rows pass; **partial** = one or two rows fail; **fail** = three or
   more rows fail, or any critical trust failure.
3. Write the anonymised appendix into [DECISIONS.md](DECISIONS.md) §6 using the template in GATE-KIT
   §5 (participants P1…P5, outcome, row results, quotes, chosen fix, decision applied).
4. Keep the filled sheets for six months; do not publish participant names or faces.

## 4. What each outcome unlocks

| Outcome | Next |
| --- | --- |
| **Pass** | Owner picks the 3.12 scope ([v3.12.0-plan.md](../../releases/v3.12.0-plan.md)): Wave 2 repairs and/or FC-4/FC-5; the Echo 4.0 preview goes to the owner for a separate go, then implementation. |
| **Partial** | Fix only the failing task; retest with the next five participants. 3.12 and identity wait. |
| **Fail** | Stop; re-open the relevant Q1 family with the council. No UI release until re-decided. |

## 5. What the agent cannot do

The gate is human evidence: five live sessions with Iraqi-Arabic speakers. Nothing in this pack
should be simulated, fabricated or filled in from the repository. The agent prepared the build,
hash, kit, thresholds, scoring and plan; the sessions and the decision are the owner's.

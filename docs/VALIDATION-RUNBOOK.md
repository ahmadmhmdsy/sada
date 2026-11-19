# Validation runbook — rows B–E

The clean-machine matrix in `ACCEPTANCE.md` defines four rows this repository cannot execute
without physical or virtual hardware: offline Windows 10, CPU-only, AVX-only and SSE4.2-without-AVX.
This runbook is the procedure plus the script and evidence template so anyone with such a machine
(project owner, a partner, a customer's test lab) can execute the rows and publish the evidence.

Status for v3.9.0: **rows B–E unexecuted — blocked on hardware** (no Hyper-V/VM tooling or physical
pre-2013 hardware on the maintainer machine). This is recorded honestly in `VERIFICATION.md`
and `ACCEPTANCE.md` rather than implied to pass.

Last updated: 2026-11-19.

## Script

`scripts/acceptance/run-row-b-e.ps1` automates what can be automated on the target machine:

- collects OS build, CPU model, AVX/AVX2 flags (PowerShell 7+), WebView2 version and network
  adapters,
- verifies a local installer against `SHA256SUMS.txt`,
- optionally silent-installs the offline NSIS installer (`-Install`) and records the
  installed app version and sidecar hash,
- prints the manual UI checklist and writes a Markdown evidence block to `-EvidenceOut`.

Usage on the target machine (copy the verified installer assets first):

```powershell
# Row B: Windows 10 22H2, network disconnected, offline installer
.\scripts\acceptance\run-row-b-e.ps1 -Slot B -AssetDir .\assets -Install -EvidenceOut .\evidence-b.md

# Row C: CPU only (disable/remove the GPU or use a VM without a GPU)
.\scripts\acceptance\run-row-b-e.ps1 -Slot C -AssetDir .\assets -EvidenceOut .\evidence-c.md

# Row D: AVX-only VM (e.g. Hyper-V VM with a Sandy Bridge-era CPU model)
.\scripts\acceptance\run-row-b-e.ps1 -Slot D -AssetDir .\assets -Install -EvidenceOut .\evidence-d.md

# Row E: SSE4.2 without AVX
.\scripts\acceptance\run-row-b-e.ps1 -Slot E -AssetDir .\assets -Install -EvidenceOut .\evidence-e.md
```

The script exits non-zero if any automated check fails. It never downloads anything; use the
verified release assets.

## Row preconditions

| Row | Machine | Preconditions |
|-----|---------|---------------|
| B | Windows 10 22H2 x64, no dev tools | Network adapters disabled after install prerequisites (WebView2 offline via the offline installer; VC++ runtime preinstalled if missing — see `ACCEPTANCE.md`) |
| C | Same as B, CPU only | No Vulkan device or driver; app must select CPU |
| D | VM with AVX but no AVX2 (or any pre-2013 x64 CPU) | Baseline CPU build must run |
| E | VM with SSE4.2 but no AVX | Expected graceful failure with a clear message; must not crash silently |

Prepare the model files on a connected machine and copy them to
`%LOCALAPPDATA%\app.sada.desktop\models` (or the folder shown in Settings → Models).
Use the 30-second Arabic clip from the benchmark corpus or any Arabic clip; record its SHA-256 so the
evidence is reproducible.

## Manual checklist (identical for all rows)

1. Install (or verify the preinstalled build) from the published installer; confirm the version in
   Settings → About matches the release.
2. Launch; the window is Arabic RTL, no error dialog, no CSP violation in DevTools.
3. Load the sideloaded model; transcribe the clinical 30-second Arabic clip; confirm Arabic text.
4. Export SRT and PDF; open both; confirm the text is correct and the PDF has Arabic shaping.
5. Dictation via the global shortcut (if the machine has a microphone): record, stop, confirm the
   text is typed once into Notepad.
6. Set a 7-day retention window, plant an old transcript folder, relaunch, confirm the purge
   removes only the old transcript and logs the count.
7. Apply a managed policy (registry or JSON) and confirm Settings → Privacy shows the managed
   banner and the network controls are gone; remove the policy afterwards.
8. Record every result as PASS / FAIL / BLOCKED in the evidence table; attach the script output.

## Evidence template

Copy this block into `docs/VERIFICATION.md` (or a new row in `ACCEPTANCE.md`'s evidence table),
replacing the placeholders. Do not mark a row PASS for steps that were not executed.

```markdown
### Row B — Windows 10 22H2, offline install and transcription

- Date: YYYY-MM-DD
- Machine: <VM/physical, Windows build>
- Installer: Sada_<version>_x64-setup-offline.exe — SHA-256 <hash> (matches SHA256SUMS.txt)
- WebView2: <version or "bundled offline installer">
- CPU/GPU: <model> / <none or model>
- Offline proof: all network adapters disabled before launch; no outbound connections observed
- Notes: <anything unusual, e.g. VC++ preinstall needed>

| Step | Result | Evidence |
| --- | --- | --- |
| Install (silent/silent flags) | PASS/FAIL | <log excerpt, app version> |
| Launch Arabic RTL, no errors | PASS/FAIL | <screenshot name> |
| Transcribe 30 s Arabic clip | PASS/FAIL | <output excerpt, timing> |
| Export SRT + PDF | PASS/FAIL | <file hashes/screens> |
| Dictation | PASS/FAIL/BLOCKED | <note> |
| Retention purge | PASS/FAIL | <count and folder> |
| Managed policy banner/controls | PASS/FAIL | <policy used> |
```

Store screenshots/logs next to the release evidence (the project keeps text evidence in
`VERIFICATION.md`; large files can be attached to the tracking issue instead of committed).

## Recording the result

1. Commit the updated `VERIFICATION.md`/`ACCEPTANCE.md` evidence table (or attach it to issue
   #34 and link it).
2. If a row FAILS: open an issue with the script output, app version, install variant and the
   failing step; keep the row marked FAIL until fixed and re-run.
3. Only then change the row from "blocked" to the recorded date and pass/fail state.

When all four rows are executed, the managed-enterprise readiness statement in
`PRODUCTION-READINESS.md` can move from "pilot-ready" to "ready for managed pilots" for the
hardware/OS matrix it covers. Until then the limitation is stated, not hidden.

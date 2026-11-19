# Enterprise deployment guide — Sada 3.9.0

How to deploy Sada on managed Windows machines: packaging, silent install, managed policy, model
pre-provisioning, detection/uninstall and offline operation. This guide is written for Intune,
SCCM/MECM, GPO and similar tools; every step uses documented Windows mechanisms, not custom
installer tricks.

Related: `NETWORK.md` (egress + policy enforcement), `AV-EDR.md` (allow-listing),
`DATA-HANDLING.md` (retention/cleanup), `SECURITY-WHITEPAPER.md` (assurance).

## 1. Choose a package

| Package | Scope | Admin rights | Use when |
|---------|-------|--------------|----------|
| `Sada_<version>_x64-setup.exe` (NSIS, default) | Per-user install in `%LOCALAPPDATA%\Sada` | No | Unmanaged or lightly managed users; user can install/update themselves |
| `Sada_<version>_x64-setup-offline.exe` (NSIS offline) | Same, plus an embedded WebView2 installer | No | Machines with no internet access at install time (WebView2 must not need a download) |
| `Sada_<version>_x64_en-US.msi` (WiX) | **Per-machine** in `C:\Program Files\Sada` | **Yes** (UAC/MSI elevation) | Managed fleets: install as SYSTEM via Intune/SCCM, machine-wide policy, standard user cannot uninstall |

The offline installer matters on air-gapped machines: the default NSIS asset uses the WebView2
bootstrapper, which needs network the first time. The offline variant embeds the Evergreen
standalone installer. MSI also needs WebView2 to be present (Windows 10/11 usually has it; if not,
deploy the Evergreen runtime first or use the offline NSIS for initial provisioning).

## 2. Silent install / uninstall

MSI (recommended for fleets):

```powershell
# Install per-machine, no UI, log to a file
Start-Process msiexec.exe -Wait -ArgumentList '/i', '"\\fileserver\Sada\Sada_3.9.0_x64_en-US.msi"', '/qn', '/norestart', '/l*v', 'C:\Windows\Temp\sada-msi.log'

# Uninstall (same product code family; /x with the MSI or product code)
Start-Process msiexec.exe -Wait -ArgumentList '/x', '{PRODUCT-CODE}', '/qn', '/norestart'
```

Find the product code after install:

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall' |
  ForEach-Object { Get-ItemProperty $_.PSPath } |
  Where-Object { $_.DisplayName -like 'Sada*' } |
  Select-Object DisplayName, DisplayVersion, PSChildName, InstallLocation
```

NSIS silent install (per-user):

```powershell
Start-Process 'Sada_3.9.0_x64-setup.exe' -Wait -ArgumentList '/S'
```

NSIS installs to `"$env:LOCALAPPDATA\Sada"` and needs to run **as the target user**, not
SYSTEM. In Intune this is a "user" context or a requirement/script run in user context.

## 3. Detection rules

Intune (Win32 app or MSI) detection — file version:

```powershell
$path = 'C:\Program Files\Sada\Sada.exe'
if (Test-Path $path) {
  $version = (Get-Item $path).VersionInfo.ProductVersion
  if ($version -like '3.9.0*') { Write-Output 'installed'; exit 0 }
}
exit 1
```

SCCM: use an MSI product-code detection rule after import, or the same file-version script.

Note: the per-user NSIS copy reports under `%LOCALAPPDATA%\Sada\Sada.exe`; do not mix
detection rules between the two package types. Pick one per device population.

## 4. Managed policy (the important part)

Sada reads a machine-wide policy from two places, registry first, then JSON file; restrictions are
OR-ed (a value set to 1 in either place cannot be unset by the other). The Rust command layer
re-reads it on every guarded action, so enforcement does not depend on the UI.

### 4.1 Registry (recommended)

```powershell
New-Item -Path 'HKLM:\SOFTWARE\Sada\Policy' -Force | Out-Null
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Sada\Policy' -Name 'OfflineMode' -Type DWord -Value 1
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Sada\Policy' -Name 'DisableAi' -Type DWord -Value 1
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Sada\Policy' -Name 'DisableUrlImport' -Type DWord -Value 1
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Sada\Policy' -Name 'DisableModelDownloads' -Type DWord -Value 1
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Sada\Policy' -Name 'TranscriptsDir' -Type String -Value 'D:\Sada\transcripts'
```

Values (all optional; missing = enabled):

| Value | Type | Meaning |
|-------|------|---------|
| `OfflineMode` | DWORD 1 | No network features at all; the connectivity probe stops too |
| `DisableAi` | DWORD 1 | No Claude/OpenAI/Ollama calls; AI settings hidden |
| `DisableUrlImport` | DWORD 1 | No yt-dlp downloads/version check; media-link tab hidden |
| `DisableModelDownloads` | DWORD 1 | No model downloads; installed models still work |
| `TranscriptsDir` | SZ | Pins the transcripts/output folder (read-only setting) |

GPO: create a registry preference item under Computer Configuration → Preferences → Windows
Settings → Registry, or deploy the script above as a startup script.

### 4.2 JSON file (alternative)

```json
{
  "offlineMode": true,
  "disableAi": true,
  "disableUrlImport": true,
  "disableModelDownloads": true,
  "transcriptsDir": "D:\\Sada\\transcripts"
}
```

Deploy to `C:\ProgramData\Sada\policy.json` (create the folder; machine ACLs protect it).
`SADA_POLICY_PATH` can override the path for testing. Malformed JSON is ignored with a
warning — treat the file as an administrator artifact and keep it valid.

### 4.3 Recommended profiles

| Profile | Values | Effect |
|---------|--------|--------|
| Maximum privacy / air-gap | `OfflineMode=1` | App runs fully local: transcription, export, MCP; every network feature refused |
| Managed offline with AI by exception | `DisableModelDownloads=1`, `DisableUrlImport=1`, `DisableAi=1` | Models pre-provisioned; no imports, no AI |
| Light touch | none | Consumer behaviour; document that egress is user-triggered |

Remember: policy is enforced inside the app; a local administrator can change HKLM. Use Windows
user-rights/AppLocker to prevent non-admins from running arbitrary installers, and keep policy
deployment under change control.

## 5. Model pre-provisioning

Model files are large (a few hundred MB to ~1.6 GB) and graph-inert data. To avoid downloads on
managed machines:

1. Download the models once on a staging machine (or from the release catalog), verify their
   SHA-256 against `docs/MODELS.md` / the catalog.
2. Copy them into each user's model folder:
   `%LOCALAPPDATA%\app.sada.desktop\models` (create it; the file name must match the
   catalog, e.g. `ggml-large-v3-turbo.bin`).
3. Deploy via a user-context login script or a per-profile provisioning step (the folder is
   per-user even under MSI). Alternatively let the app point at a shared folder if that setting is
   supported in your build; the supported path is the per-user models folder.
4. With `DisableModelDownloads=1` the setup screen skips downloads and uses installed
   models; if no model is present it explains that a model must be installed.

For `TranscriptsDir` pinned folders, ensure the folder exists and users can write to it
(e.g. a subfolder under their Documents or a mapped drive with offline files enabled).

## 6. Updates

There is no auto-updater and no update check. Upgrade by deploying the next MSI/NSIS over the
existing install (same upgrade code; MSI performs a major upgrade). Keep the same product name
("Sada") and upgrade code so the MSI replaces the old version instead of installing side by side.
Test policy persistence across upgrades (policy is machine-wide and survives).

## 7. Uninstall and data cleanup

Uninstalling removes the application only. User data stays by design:

- `%APPDATA%\app.sada.desktop` — settings, sealed AI keys, logs
- `%LOCALAPPDATA%\app.sada.desktop\models` — models
- the transcripts folder (default `%USERPROFILE%\Documents\Sada` or the pinned folder)

For device retirement or user offboarding, remove them explicitly:

```powershell
Remove-Item "$env:APPDATA\app.sada.desktop" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\app.sada.desktop" -Recurse -Force -ErrorAction SilentlyContinue
# Only with the user's data-owner approval:
# Remove-Item (Join-Path $env:USERPROFILE 'Documents\Sada') -Recurse -Force
```

## 8. Requirements and compatibility

- Windows 10 1809+ or Windows 11, x64. Windows 11 ARM runs x64 emulation but is not validated.
- WebView2 Evergreen runtime (preinstalled on current Windows 10/11; offline installer variant
  covers air-gapped clean installs).
- No .NET runtime, no Java, no Visual C++ redistributable needed by the app itself.
- Per-user install needs no admin; per-machine MSI needs admin.
- Disk: ~150 MB app + 150 MB-1.6 GB per model + transcription temp space.
- GPU: optional; CPU works. The app selects available hardware at runtime.

## 9. Pilot checklist

1. Install via the chosen package on a non-admin test user; confirm version in Settings → About.
2. Apply the maximum-privacy policy; confirm Settings → Privacy shows "Managed by your
   organization" and the AI/URL/download controls are gone.
3. Transcribe a sample Arabic file offline; confirm transcripts land in `TranscriptsDir`.
4. Confirm no outbound connections while idle (see `NETWORK.md` verification).
5. Confirm retention purge works with a 7-day window and a test file.
6. Confirm silent uninstall and that user data cleanup script removes only the intended folders.
7. Record results with the evidence template in `docs/VALIDATION-RUNBOOK.md`.

# Automated helper for the clean-machine acceptance rows B-E (offline, CPU-only, AVX-only, SSE4.2).
# It collects machine facts, verifies a local installer against SHA256SUMS.txt, records the installed
# version, and writes an evidence block for docs/VALIDATION-RUNBOOK.md. It does NOT replace the
# manual transcription/UI steps; it prints them as a checklist and never installs without -Install.
# Usage:
#   .\scripts\acceptance\run-row-b-e.ps1 -Slot B -AssetDir .\release-verify\v3.9.0 -EvidenceOut .\evidence-b.md
#   .\scripts\acceptance\run-row-b-e.ps1 -Slot D -AssetDir .\assets -Install
param(
  [Parameter(Mandatory = $true)][ValidateSet('B','C','D','E')][string]$Slot,
  [string]$AssetDir = '',
  [switch]$Install,
  [string]$EvidenceOut = '',
  [string]$ClipPath = ''
)

$ErrorActionPreference = 'Stop'
$now = Get-Date -Format 'yyyy-MM-dd HH:mm K'
$rows = New-Object System.Collections.Generic.List[string]
function Add-Row([string]$Check, [string]$Result, [string]$Details = '') {
  $rows.Add("| $Check | $Result | $Details |") | Out-Null
}

$os = Get-CimInstance Win32_OperatingSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$avx = 'unknown'
$avx2 = 'unknown'
try {
  # PowerShell 7 / .NET 8 exposes intrinsic checks; Windows PowerShell 5.1 does not.
  if ($PSVersionTable.PSEdition -eq 'Core') {
    $avx = [System.Runtime.Intrinsics.X86.Avx]::IsSupported
    $avx2 = [System.Runtime.Intrinsics.X86.Avx2]::IsSupported
  }
} catch {
  $avx = 'unknown (use coreinfo.exe -f)'
  $avx2 = 'unknown'
}
$webview = (Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -ErrorAction SilentlyContinue).pv

Add-Row 'OS' 'info' "$($os.Caption) $($os.Version) build $($os.BuildNumber)"
Add-Row 'CPU' 'info' "$($cpu.Name) / AVX=$avx AVX2=$avx2"
Add-Row 'WebView2' 'info' "$webview"
Add-Row 'Network' 'info' (@(Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -ExpandProperty Name) -join ', ')

if ($AssetDir) {
  $sums = Join-Path $AssetDir 'SHA256SUMS.txt'
  if (-not (Test-Path $sums)) { throw "SHA256SUMS.txt not found in $AssetDir" }
  $expected = @{}
  foreach ($line in Get-Content $sums) {
    if ($line -match '^([0-9a-fA-F]{64})\s{2,}(\S.*)$') { $expected[$matches[2].Trim()] = $matches[1].ToLowerInvariant() }
  }
  foreach ($name in ($expected.Keys | Sort-Object)) {
    $file = Join-Path $AssetDir $name
    if (-not (Test-Path $file)) { Add-Row "hash $name" 'BLOCKED' 'asset not present'; continue }
    $actual = (Get-FileHash $file -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -eq $expected[$name]) { Add-Row "hash $name" 'PASS' 'sha256 matches' }
    else { Add-Row "hash $name" 'FAIL' "expected $($expected[$name]) got $actual" }
  }
}

$installer = $null
if ($AssetDir) {
  $installer = Get-ChildItem $AssetDir -Filter '*setup-offline.exe' -File -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $installer) { $installer = Get-ChildItem $AssetDir -Filter '*setup.exe' -File -ErrorAction SilentlyContinue | Select-Object -First 1 }
}
if ($Install) {
  if (-not $installer) { throw '-Install requires an installer asset in -AssetDir' }
  Write-Host "installing $($installer.Name) silently"
  Start-Process $installer.FullName -Wait -ArgumentList '/S'
}

$app = @('C:\Program Files\Sada\Sada.exe', (Join-Path $env:LOCALAPPDATA 'Sada\Sada.exe')) |
  Where-Object { Test-Path $_ } | Select-Object -First 1
if ($app) {
  Add-Row 'installed app' 'PASS' "$app version $((Get-Item $app).VersionInfo.ProductVersion)"
  $sidecar = Join-Path (Split-Path $app -Parent) 'vibe-server.exe'
  if (Test-Path $sidecar) {
    $sidecarHash = (Get-FileHash $sidecar -Algorithm SHA256).Hash
    Add-Row 'sidecar' 'info' "vibe-server.exe sha256 $sidecarHash"
  }
} else {
  Add-Row 'installed app' 'FAIL' 'Sada.exe not found after install'
}

Write-Host ''
Write-Host 'Manual steps (record Pass/Fail/Blocked):'
Write-Host '  1. Launch with network disconnected; window is Arabic RTL, no error dialog.'
Write-Host '  2. Load the sideloaded model and transcribe the 30-second Arabic clip.'
Write-Host '  3. Export SRT and open it; confirm Arabic text and no startup crash.'
Write-Host '  4. Dictation via the global shortcut: record, stop, type into Notepad.'
Write-Host '  5. Settings -> Privacy shows the managed policy banner when a policy is set.'
Write-Host '  6. GPU-less machine: transcription falls back to CPU (Settings -> General).'
Write-Host '  7. SSE4.2/no-AVX machine: the app may refuse to start the engine; it must show a'
Write-Host '     clear error, not crash silently.'
if ($ClipPath) { Write-Host "Clip to use: $ClipPath" }

$header = @(
  "### Row $Slot - automated evidence $now",
  '',
  '| Check | Result | Details |',
  '| --- | --- | --- |'
) -join [Environment]::NewLine
$report = $header + [Environment]::NewLine + ($rows -join [Environment]::NewLine)
Write-Host ''
Write-Host $report
if ($EvidenceOut) {
  $dir = Split-Path -Parent $EvidenceOut
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
  Set-Content -Path $EvidenceOut -Value $report -Encoding UTF8
  Write-Host "evidence written to $EvidenceOut"
}

$failed = $rows | Where-Object { $_ -match '\| FAIL \|' }
if ($failed) { Write-Host 'AUTOMATED CHECKS FAILED' -ForegroundColor Red; exit 1 }
Write-Host 'automated checks passed (manual steps still required)' -ForegroundColor Green
exit 0

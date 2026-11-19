# Remove Sada user data for the current user (device retirement / offboarding).
# Uninstall the application first (MSI/NSIS), then run this.
param(
  [switch]$IncludeTranscripts,
  [string]$TranscriptsDir = "$env:USERPROFILE\Documents\Sada",
  [switch]$WhatIfOnly
)
$ErrorActionPreference = 'Stop'
$targets = @(
  "$env:APPDATA\app.sada.desktop",
  "$env:LOCALAPPDATA\app.sada.desktop"
)
if ($IncludeTranscripts) { $targets += $TranscriptsDir }
foreach ($target in $targets) {
  if (-not (Test-Path $target)) { Write-Host "absent: $target"; continue }
  if ($WhatIfOnly) {
    Write-Host "would remove: $target"
  } else {
    Remove-Item $target -Recurse -Force
    Write-Host "removed: $target"
  }
}

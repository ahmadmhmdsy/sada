# Set a Sada machine-wide managed policy (registry, optional JSON file).
# Usage:
#   .\scripts\enterprise\set-sada-policy.ps1 -OfflineMode -DisableAi -TranscriptsDir 'D:\Sada\transcripts'
#   .\scripts\enterprise\set-sada-policy.ps1 -JsonFile .\policy.json -WritePolicyFile
# Requires administrator for the registry hive. Idempotent; only manages the values below.
param(
  [switch]$OfflineMode,
  [switch]$DisableAi,
  [switch]$DisableUrlImport,
  [switch]$DisableModelDownloads,
  [string]$TranscriptsDir = '',
  [string]$JsonFile = '',
  [switch]$WritePolicyFile,
  [string]$PolicyFilePath = "$env:ProgramData\Sada\policy.json"
)

$ErrorActionPreference = 'Stop'
$root = 'HKLM:\SOFTWARE\Sada\Policy'

function Set-Dword([string]$Name, [bool]$Enabled) {
  if ($Enabled) {
    New-Item -Path $root -Force | Out-Null
    New-ItemProperty -Path $root -Name $Name -PropertyType DWord -Value 1 -Force | Out-Null
    Write-Host "registry: $Name=1"
  } elseif (Test-Path $root) {
    Remove-ItemProperty -Path $root -Name $Name -ErrorAction SilentlyContinue
    Write-Host "registry: $Name cleared"
  }
}

Set-Dword 'OfflineMode' $OfflineMode
Set-Dword 'DisableAi' $DisableAi
Set-Dword 'DisableUrlImport' $DisableUrlImport
Set-Dword 'DisableModelDownloads' $DisableModelDownloads

if ($TranscriptsDir) {
  New-Item -Path $root -Force | Out-Null
  New-ItemProperty -Path $root -Name 'TranscriptsDir' -PropertyType String -Value $TranscriptsDir -Force | Out-Null
  Write-Host "registry: TranscriptsDir=$TranscriptsDir"
}

if ($JsonFile) {
  $policy = Get-Content $JsonFile -Raw | ConvertFrom-Json
  if ($policy.offlineMode) { New-Item -Path $root -Force | Out-Null; New-ItemProperty -Path $root -Name 'OfflineMode' -PropertyType DWord -Value 1 -Force | Out-Null }
  if ($policy.disableAi) { New-Item -Path $root -Force | Out-Null; New-ItemProperty -Path $root -Name 'DisableAi' -PropertyType DWord -Value 1 -Force | Out-Null }
  if ($policy.disableUrlImport) { New-Item -Path $root -Force | Out-Null; New-ItemProperty -Path $root -Name 'DisableUrlImport' -PropertyType DWord -Value 1 -Force | Out-Null }
  if ($policy.disableModelDownloads) { New-Item -Path $root -Force | Out-Null; New-ItemProperty -Path $root -Name 'DisableModelDownloads' -PropertyType DWord -Value 1 -Force | Out-Null }
  if ($policy.transcriptsDir) { New-Item -Path $root -Force | Out-Null; New-ItemProperty -Path $root -Name 'TranscriptsDir' -PropertyType String -Value $policy.transcriptsDir -Force | Out-Null }
  Write-Host "registry: applied from $JsonFile"
}

if ($WritePolicyFile) {
  $dir = Split-Path -Parent $PolicyFilePath
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
  $filePolicy = [ordered]@{}
  if ($OfflineMode) { $filePolicy.offlineMode = $true }
  if ($DisableAi) { $filePolicy.disableAi = $true }
  if ($DisableUrlImport) { $filePolicy.disableUrlImport = $true }
  if ($DisableModelDownloads) { $filePolicy.disableModelDownloads = $true }
  if ($TranscriptsDir) { $filePolicy.transcriptsDir = $TranscriptsDir }
  if ($JsonFile) {
    $fromFile = Get-Content $JsonFile -Raw | ConvertFrom-Json
    foreach ($prop in $fromFile.PSObject.Properties) { $filePolicy[$prop.Name] = $prop.Value }
  }
  ($filePolicy | ConvertTo-Json -Depth 5) | Set-Content -Path $PolicyFilePath -Encoding UTF8
  Write-Host "policy file: $PolicyFilePath"
}

Write-Host 'Effective policy:'
if (Test-Path $root) {
  Get-ItemProperty -Path $root | Format-List
} else {
  Write-Host '(none)'
}

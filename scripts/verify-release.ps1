# Verify a Sada release: SHA-256 sums, optional GitHub attestations.
# Usage:
#   .\scripts\verify-release.ps1 -Version 3.9.0 -Repo alshahia/sada
#   .\scripts\verify-release.ps1 -Path .\Sada_3.9.0_x64-setup.exe
#   .\scripts\verify-release.ps1 -Version 3.9.0 -Download
# The script exits non-zero on any mismatch. It never installs anything.
param(
  [string]$Version = '',
  [string]$Repo = 'alshahia/sada',
  [string]$Path = '',
  [switch]$Download,
  [switch]$SkipAttestation,
  [string]$WorkDir = "$PSScriptRoot\..\release-verify"
)

$ErrorActionPreference = 'Stop'
$failures = New-Object System.Collections.Generic.List[string]

function Assert-Ok([string]$Message) {
  Write-Host "OK   $Message" -ForegroundColor Green
}

function Assert-Fail([string]$Message) {
  Write-Host "FAIL $Message" -ForegroundColor Red
  $script:failures.Add($Message) | Out-Null
}

function Resolve-Assets {
  if ($Path) {
    $dir = Split-Path -Parent (Resolve-Path $Path)
    return @(Get-ChildItem $dir -File | Where-Object { $_.Name -match '\.(exe|msi)$' -or $_.Name -eq 'SHA256SUMS.txt' })
  }
  if ($Download) {
    if (-not $Version) { throw 'Version is required with -Download' }
    $tag = "v$Version"
    $target = Join-Path $WorkDir $tag
    New-Item -ItemType Directory -Force $target | Out-Null
    $urls = @(
      "https://github.com/$Repo/releases/download/$tag/SHA256SUMS.txt",
      "https://github.com/$Repo/releases/download/$tag/Sada_${Version}_x64-setup.exe",
      "https://github.com/$Repo/releases/download/$tag/Sada_${Version}_x64-setup-offline.exe",
      "https://github.com/$Repo/releases/download/$tag/Sada_${Version}_x64_en-US.msi"
    )
    foreach ($url in $urls) {
      $name = Split-Path $url -Leaf
      $dest = Join-Path $target $name
      if (Test-Path $dest) {
        Write-Host "already downloaded: $name"
        continue
      }
      Write-Host "downloading $name"
      curl.exe -L --fail --retry 3 --silent --show-error -o $dest $url
      if ($LASTEXITCODE -ne 0) {
        Write-Host "not available: $name" -ForegroundColor Yellow
        if (Test-Path $dest) { Remove-Item $dest -Force }
      }
    }
    $sums = Join-Path $target 'SHA256SUMS.txt'
    if (-not (Test-Path $sums)) { throw "SHA256SUMS.txt was not downloaded from $tag" }
    return @(Get-ChildItem $target -File)
  }
  throw 'Provide -Version with -Download, or -Path to a local asset'
}

$assets = Resolve-Assets
$sumsFile = $assets | Where-Object { $_.Name -eq 'SHA256SUMS.txt' } | Select-Object -First 1
if (-not $sumsFile) { throw 'SHA256SUMS.txt is required next to the assets' }

$expected = @{}
foreach ($line in Get-Content $sumsFile.FullName) {
  if ($line -match '^([0-9a-fA-F]{64})\s{2,}(\S.*)$') {
    $expected[$matches[2].Trim()] = $matches[1].ToLowerInvariant()
  }
}
if ($expected.Count -eq 0) { throw 'SHA256SUMS.txt contains no entries' }

foreach ($name in ($expected.Keys | Sort-Object)) {
  $file = $assets | Where-Object { $_.Name -eq $name } | Select-Object -First 1
  if (-not $file) {
    Assert-Fail "missing asset: $name"
    continue
  }
  $actual = (Get-FileHash $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($actual -eq $expected[$name]) {
    Assert-Ok ("sha256 {0} ({1:N0} bytes)" -f $name, $file.Length)
  } else {
    Assert-Fail "sha256 mismatch for $name (expected $($expected[$name]), got $actual)"
  }
}

$installers = $assets | Where-Object { $_.Name -match '\.(exe|msi)$' }
if ($installers.Count -eq 0) { Assert-Fail 'no installer assets found' }

if ($SkipAttestation) {
  Write-Host 'attestation check skipped by request'
} else {
  $gh = Get-Command gh -ErrorAction SilentlyContinue
  if (-not $gh) {
    Write-Host 'gh not found: skipping attestation verification (install GitHub CLI to verify provenance)' -ForegroundColor Yellow
  } else {
    foreach ($file in $installers) {
      $output = & gh attestation verify $file.FullName --repo $Repo 2>&1
      if ($LASTEXITCODE -eq 0) {
        Assert-Ok "attestation $($file.Name)"
      } else {
        Assert-Fail "attestation failed for $($file.Name): $output"
      }
    }
  }
}

Write-Host ''
if ($failures.Count -gt 0) {
  Write-Host "VERIFICATION FAILED: $($failures.Count) problem(s)" -ForegroundColor Red
  $failures | ForEach-Object { Write-Host " - $_" }
  exit 1
}
Write-Host 'VERIFICATION PASSED: all hashes and attestations match' -ForegroundColor Green
exit 0

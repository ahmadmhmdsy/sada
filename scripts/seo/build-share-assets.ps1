# Build the static share assets used by README, Open Graph, Twitter cards and the favicon set:
#   site/assets/social-card-ar.png   1200x630  (Open Graph / Twitter, Arabic)
#   site/assets/social-card-en.png   1200x630  (Open Graph / Twitter, English)
#   site/assets/apple-touch-icon.png  180x180  (iOS bookmark / share sheet)
#   site/assets/icon-512.png           512x512  (PNG fallback, structured data)
#
# Rendered with locally installed Microsoft Edge (headless): no network, no image editor, no telemetry.
# Sources: docs/seo/*.html  Usage: pwsh -File scripts/seo/build-share-assets.ps1
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path (Join-Path $repo 'desktop\src-tauri\tauri.conf.json'))) { throw "Run from a Sada checkout; repo root not found at $repo" }
$edge = @("$env:ProgramFiles (x86)\Microsoft\Edge\Application\msedge.exe", "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe", "$env:ProgramFiles\Google\Chrome\Application\chrome.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw 'Microsoft Edge or Google Chrome is required to render the share assets.' }
$page = 'file:///' + ($repo -replace '\\', '/')

function Render([string]$file, [string]$out, [int]$width, [int]$height) {
  $outPath = Join-Path $repo $out
  $profile = Join-Path $env:TEMP ('sada-share-' + [guid]::NewGuid().ToString('N'))
  try {
    & $edge --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --virtual-time-budget=3000 --user-data-dir="$profile" --window-size="$width,$height" --screenshot="$outPath" "$page/$file" 2>$null | Out-Null
  } finally { Remove-Item -Recurse -Force $profile -ErrorAction SilentlyContinue }
  if (-not (Test-Path $outPath)) { throw "Edge did not write $outPath" }
  Add-Type -AssemblyName System.Drawing
  $image = [System.Drawing.Image]::FromFile($outPath)
  try {
    if ($image.Width -ne $width -or $image.Height -ne $height) { throw "$out is $($image.Width)x$($image.Height), expected ${width}x${height}" }
  } finally { $image.Dispose() }
  Write-Host ("OK {0} - {1}x{2}, {3:N0} bytes" -f $out, $width, $height, (Get-Item $outPath).Length)
}

Render 'docs/seo/social-card-ar.html' 'site/assets/social-card-ar.png' 1200 630
Render 'docs/seo/social-card-en.html' 'site/assets/social-card-en.png' 1200 630
Render 'docs/seo/icons/icon-180.html' 'site/assets/apple-touch-icon.png' 180 180
Render 'docs/seo/icons/icon-512.html' 'site/assets/icon-512.png' 512 512

Write-Host 'Share assets rebuilt. Commit the four PNG files under site/assets/.'

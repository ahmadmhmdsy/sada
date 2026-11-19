# Enrich the CycloneDX SBOM produced by syft for a Sada release.
# Adds the non-package components the app ships or fetches: FFmpeg, WebView2, the vibe-server
# sidecar and yt-dlp. Usage (release workflow):
#   pwsh scripts/generate-sbom.ps1 -SbomPath release-assets/sbom-cyclonedx.json -AppVersion 3.9.0
param(
  [Parameter(Mandatory = $true)][string]$SbomPath,
  [Parameter(Mandatory = $true)][string]$AppVersion,
  [string]$SidecarVersion = '',
  [string]$FfmpegPath = ''
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path $SbomPath)) { throw "SBOM not found: $SbomPath" }
$sbom = Get-Content $SbomPath -Raw | ConvertFrom-Json

$ffmpegVersion = 'bundled'
if ($FfmpegPath -and (Test-Path $FfmpegPath)) {
  $firstLine = (& $FfmpegPath -version 2>&1 | Select-Object -First 1)
  if ($firstLine -match 'ffmpeg version (\S+)') { $ffmpegVersion = $matches[1] }
}

$external = @(
  [ordered]@{
    type = 'application'
    'bom-ref' = 'external:ffmpeg'
    name = 'ffmpeg'
    version = $ffmpegVersion
    scope = 'required'
    description = 'Bundled audio/video decoder, shipped as a separate GPLv3 executable.'
    licenses = @(@{ license = @{ name = 'GPL-3.0-only' } })
    properties = @(@{ name = 'sada:component-kind'; value = 'bundled-executable' })
  },
  [ordered]@{
    type = 'framework'
    'bom-ref' = 'external:webview2'
    name = 'Microsoft Edge WebView2 Runtime'
    version = 'evergreen'
    scope = 'optional'
    description = 'WebView2 Evergreen Runtime (Microsoft), preinstalled or supplied by the offline installer.'
    licenses = @(@{ license = @{ name = 'Proprietary' } })
    properties = @(@{ name = 'sada:component-kind'; value = 'platform-runtime' })
  },
  [ordered]@{
    type = 'application'
    'bom-ref' = 'external:vibe-server'
    name = 'vibe-server'
    version = $(if ($SidecarVersion) { $SidecarVersion } else { 'pinned-sidecar' })
    scope = 'required'
    description = 'Transcription engine sidecar built from server/ (whisper.cpp/GGML).'
    licenses = @(@{ license = @{ name = 'MIT' } })
    properties = @(@{ name = 'sada:component-kind'; value = 'bundled-sidecar' })
  },
  [ordered]@{
    type = 'application'
    'bom-ref' = 'external:yt-dlp'
    name = 'yt-dlp'
    version = 'runtime-download'
    scope = 'optional'
    description = 'Media downloader fetched at runtime for URL import only, verified against the release SHA2-256SUMS.'
    licenses = @(@{ license = @{ name = 'Unlicense' } })
    properties = @(@{ name = 'sada:component-kind'; value = 'runtime-download' })
  }
)

$existing = @()
if ($sbom.PSObject.Properties.Name -contains 'components' -and $sbom.components) { $existing = @($sbom.components) }
$sbom | Add-Member -NotePropertyName components -NotePropertyValue ($existing + $external) -Force

$metadataComponent = [ordered]@{
  type = 'application'
  'bom-ref' = 'sada'
  name = 'Sada'
  version = $AppVersion
  description = 'Arabic-first offline transcription app (Windows desktop)'
  licenses = @(@{ license = @{ name = 'MIT' } })
}
if ($null -eq $sbom.metadata) {
  $sbom | Add-Member -NotePropertyName metadata -NotePropertyValue ([ordered]@{ component = $metadataComponent }) -Force
} else {
  $sbom.metadata | Add-Member -NotePropertyName component -NotePropertyValue $metadataComponent -Force
}

$json = $sbom | ConvertTo-Json -Depth 30
[System.IO.File]::WriteAllText((Resolve-Path $SbomPath), $json, (New-Object System.Text.UTF8Encoding $false))
Write-Output "SBOM enriched: $SbomPath (ffmpeg $ffmpegVersion, sidecar $SidecarVersion)"

# Detect an installed Sada and print version + paths (Intune/SCCM detection helper).
# Exit 0 when found (and RequiredVersion matches when given), 1 when not found.
param(
  [string]$RequiredVersion = ''
)
$candidates = @(
  'C:\Program Files\Sada\Sada.exe',
  (Join-Path $env:LOCALAPPDATA 'Sada\Sada.exe')
)
foreach ($path in $candidates) {
  if (Test-Path $path) {
    $item = Get-Item $path
    $version = $item.VersionInfo.ProductVersion
    Write-Output "found: $path"
    Write-Output "version: $version"
    if ($RequiredVersion -and -not $version.StartsWith($RequiredVersion)) {
      Write-Output "required version $RequiredVersion not matched"
      exit 1
    }
    exit 0
  }
}
Write-Output 'Sada is not installed'
exit 1

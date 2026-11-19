# Remove the Sada machine-wide managed policy and report what remains.
param(
  [switch]$RemovePolicyFile,
  [string]$PolicyFilePath = "$env:ProgramData\Sada\policy.json"
)
$ErrorActionPreference = 'Stop'
$root = 'HKLM:\SOFTWARE\Sada\Policy'
if (Test-Path $root) {
  Remove-Item -Path $root -Recurse -Force
  Write-Host "removed registry policy: $root"
} else {
  Write-Host 'no registry policy present'
}
if ($RemovePolicyFile -and (Test-Path $PolicyFilePath)) {
  Remove-Item $PolicyFilePath -Force
  Write-Host "removed policy file: $PolicyFilePath"
}
exit 0

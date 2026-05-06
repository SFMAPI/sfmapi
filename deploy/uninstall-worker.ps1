param([string]$ServiceName = "sfmapi-worker")

$ErrorActionPreference = "Stop"

if (-not (Get-Command nssm -ErrorAction SilentlyContinue)) {
    throw "nssm not found on PATH"
}
if (-not (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue)) {
    Write-Host "Service '$ServiceName' is not installed."
    exit 0
}

& nssm stop $ServiceName confirm | Out-Null
& nssm remove $ServiceName confirm | Out-Null
Write-Host "Removed service '$ServiceName'." -ForegroundColor Green

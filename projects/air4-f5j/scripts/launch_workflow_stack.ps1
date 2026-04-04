param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8787,
    [switch]$InstallNodeDeps
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if ($InstallNodeDeps -or -not (Test-Path (Join-Path $repoRoot "node_modules"))) {
    npm install
}

python -m src.orchestrator.cli serve --host $Host --port $Port

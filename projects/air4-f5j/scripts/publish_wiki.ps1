param(
    [string]$TargetPath
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$wikiSource = Join-Path $repoRoot "wiki"

if (-not (Test-Path $wikiSource)) {
    throw "Wiki source folder not found: $wikiSource"
}

if (-not $TargetPath) {
    Write-Host "Usage: .\\scripts\\publish_wiki.ps1 -TargetPath <path-to-local-aeroforge.wiki-clone>"
    Write-Host "This script copies the repo-managed wiki pages from /wiki into the target folder."
    exit 1
}

if (-not (Test-Path $TargetPath)) {
    New-Item -ItemType Directory -Force -Path $TargetPath | Out-Null
}

Get-ChildItem $wikiSource -File -Filter *.md | ForEach-Object {
    $destination = Join-Path $TargetPath $_.Name
    Copy-Item $_.FullName $destination -Force
}

Write-Host "Copied wiki pages from $wikiSource to $TargetPath"
Write-Host "Review the target clone and publish from there."

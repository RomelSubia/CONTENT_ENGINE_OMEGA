Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = "D:\CONTENT_ENGINE_OMEGA"
$expected = [System.IO.Path]::GetFullPath($root)
$current = [System.IO.Path]::GetFullPath((Get-Location).Path)

if ($current -ne $expected) {
    Write-Output "BLOCKED: root validation failed"
    exit 1
}

$gitDir = Join-Path $root ".git"
if (-not (Test-Path -LiteralPath $gitDir -PathType Container)) {
    Write-Output "BLOCKED: .git not found"
    exit 1
}

$statusShortBefore = git status --short 2>&1
if ($LASTEXITCODE -ne 0) {
    $statusShortBefore | ForEach-Object { Write-Output $_ }
    Write-Output "BLOCKED: git status --short failed"
    exit 1
}

if ($statusShortBefore) {
    $statusShortBefore | ForEach-Object { Write-Output $_ }
    Write-Output "BLOCKED: git status --short is not clean before closure"
    exit 1
}

$remoteOrigin = git remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Output "REVIEW_REQUIRED: remote origin is not configured"
    exit 1
}

$fetchOutput = git fetch origin 2>&1
if ($LASTEXITCODE -ne 0) {
    $fetchOutput | ForEach-Object { Write-Output $_ }
    Write-Output "BLOCKED: git fetch failed"
    exit 1
}

$localHead = (git rev-parse HEAD 2>&1).Trim()
if ($LASTEXITCODE -ne 0) {
    Write-Output "BLOCKED: failed to resolve local HEAD"
    exit 1
}

$upstreamHead = (git rev-parse "@{u}" 2>&1).Trim()
if ($LASTEXITCODE -ne 0) {
    Write-Output "BLOCKED: upstream for current branch is not configured"
    exit 1
}

if ($localHead -ne $upstreamHead) {
    Write-Output "BLOCKED: local HEAD and upstream differ"
    exit 1
}

Write-Output "PC LOCAL = GIT LOCAL = GIT REMOTO = VALID"

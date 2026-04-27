Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = "D:\CONTENT_ENGINE_OMEGA"
$expected = [System.IO.Path]::GetFullPath($root)
$current = [System.IO.Path]::GetFullPath((Get-Location).Path)
$bundledPython = "C:\Users\romel\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if ($current -ne $expected) {
    Write-Error "Root validation failed. Expected $expected but got $current"
    exit 1
}

$pythonScript = Join-Path $root "04_SCRIPTS\python\core\validate_phase_a.py"
if (-not (Test-Path -LiteralPath $pythonScript -PathType Leaf)) {
    Write-Error "Missing validator: $pythonScript"
    exit 1
}

$pythonExe = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = "python"
} elseif (Test-Path -LiteralPath $bundledPython -PathType Leaf) {
    $pythonExe = $bundledPython
}

if (-not $pythonExe) {
    Write-Error "No Python runtime available"
    exit 1
}

$pythonOutput = & $pythonExe $pythonScript 2>&1
if ($LASTEXITCODE -ne 0) {
    $pythonOutput | ForEach-Object { Write-Output $_ }
    Write-Error "Phase A python validation failed"
    exit 1
}

Write-Output "PHASE A AUDIT: PASS"

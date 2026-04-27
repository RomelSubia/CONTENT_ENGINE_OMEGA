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

$pythonScript = Join-Path $root "04_SCRIPTS\python\core\validate_phase0.py"
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
$pythonExit = $LASTEXITCODE
if ($pythonExit -ne 0) {
    $pythonOutput | ForEach-Object { Write-Output $_ }
    Write-Error "Python validation failed"
    exit 1
}

$reportPath = Join-Path $root "00_SYSTEM\core\reports\PHASE_0_AUDIT_REPORT.md"
$timestamp = (Get-Date).ToString("s")
$report = @"
# PHASE 0 AUDIT REPORT

- Timestamp: $timestamp
- Root: $root
- Python Validator: PASS
- Python Output: $($pythonOutput -join '; ')
- Result: PHASE 0 AUDIT: PASS
"@
Set-Content -LiteralPath $reportPath -Value $report -Encoding UTF8

Write-Output "PHASE 0 AUDIT: PASS"

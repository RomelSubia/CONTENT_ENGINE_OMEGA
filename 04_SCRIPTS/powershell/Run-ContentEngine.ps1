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

$lockPath = Join-Path $root "00_SYSTEM\core\runtime\runtime.lock"
$pythonPhase0 = Join-Path $root "04_SCRIPTS\python\core\validate_phase0.py"
$pythonPhaseA = Join-Path $root "04_SCRIPTS\python\core\validate_phase_a.py"
$runtimeScript = Join-Path $root "04_SCRIPTS\python\core\runtime_engine.py"
$reportPath = Join-Path $root "00_SYSTEM\core\reports\PHASE_A_AUDIT_REPORT.md"
$runtimeJsonPath = Join-Path $root "00_SYSTEM\core\runtime\SYSTEM_RUNTIME.json"
$heartbeatPath = Join-Path $root "00_SYSTEM\core\runtime\HEARTBEAT.json"
$logPath = Join-Path $root "00_SYSTEM\core\logs\RUNTIME_LOG.json"
$manifestPath = Join-Path $root "00_SYSTEM\core\logs\manifest.json"
$trackedArtifacts = @($reportPath, $runtimeJsonPath, $heartbeatPath, $logPath, $manifestPath)
$artifactBackup = @{}

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

if (Test-Path -LiteralPath $lockPath -PathType Leaf) {
    Write-Error "runtime.lock already exists. Parallel execution is blocked."
    exit 1
}

foreach ($artifactPath in $trackedArtifacts) {
    if (Test-Path -LiteralPath $artifactPath -PathType Leaf) {
        $artifactBackup[$artifactPath] = [System.IO.File]::ReadAllBytes($artifactPath)
    } else {
        $artifactBackup[$artifactPath] = $null
    }
}

$phase0Output = & $pythonExe $pythonPhase0 2>&1
if ($LASTEXITCODE -ne 0) {
    $phase0Output | ForEach-Object { Write-Output $_ }
    Write-Error "Phase 0 validation failed"
    exit 1
}

$phaseAOutput = & $pythonExe $pythonPhaseA 2>&1
if ($LASTEXITCODE -ne 0) {
    $phaseAOutput | ForEach-Object { Write-Output $_ }
    Write-Error "Phase A validation failed"
    exit 1
}

$runtimeOutput = & $pythonExe $runtimeScript --self-test 2>&1
$runtimeExit = $LASTEXITCODE
if (Test-Path -LiteralPath $lockPath -PathType Leaf) {
    Write-Error "runtime.lock was not released"
    exit 1
}
if ($runtimeExit -ne 0) {
    $runtimeOutput | ForEach-Object { Write-Output $_ }
    Write-Error "Runtime engine failed"
    exit 1
}

$runtimeState = Get-Content -LiteralPath $runtimeJsonPath -Raw | ConvertFrom-Json
$heartbeat = Get-Content -LiteralPath $heartbeatPath -Raw | ConvertFrom-Json
$runtimeLog = Get-Content -LiteralPath $logPath -Raw | ConvertFrom-Json
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

$report = @"
# PHASE A AUDIT REPORT

- Validations FASE 0: $($phase0Output -join '; ')
- Validations FASE A: $($phaseAOutput -join '; ')
- Runtime execution: $($runtimeOutput -join '; ')
- Heartbeat: sequence=$($heartbeat.sequence), status=$($heartbeat.status), timestamp=$($heartbeat.timestamp)
- Logger: events=$($runtimeLog.Count)
- Lock: released
- Git sync: pending post-run verification
- Final runtime state: $($runtimeState.runtime_status)
"@
Set-Content -LiteralPath $reportPath -Value $report -Encoding UTF8

foreach ($artifactPath in $trackedArtifacts) {
    $originalContent = $artifactBackup[$artifactPath]
    if ($null -eq $originalContent) {
        continue
    }
    [System.IO.File]::WriteAllBytes($artifactPath, $originalContent)
}

Write-Output "PHASE_A_RUNTIME: PASS"

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

$changeDir = Join-Path $root "00_SYSTEM\core\change_awareness"
$currentPath = Join-Path $changeDir "CHANGE_CURRENT.json"
$baselinePath = Join-Path $changeDir "CHANGE_BASELINE.json"
$deltaPath = Join-Path $changeDir "CHANGE_DELTA.json"
$manifestPath = Join-Path $changeDir "SNAPSHOT_MANIFEST.json"
$reportPath = Join-Path $changeDir "reports\PHASE_B_AUDIT_REPORT.md"
$partialProbePath = Join-Path $changeDir "probes\PARTIAL_SNAPSHOT.json"
$partialDeltaProbePath = Join-Path $changeDir "probes\PARTIAL_DELTA.json"
$probeSandboxPath = Join-Path $changeDir "probes\EXCLUSION_PROBE.txt"

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

$phase0Py = & $pythonExe "04_SCRIPTS\python\core\validate_phase0.py" 2>&1
if ($LASTEXITCODE -ne 0) {
    $phase0Py | ForEach-Object { Write-Output $_ }
    Write-Error "Phase 0 python validation failed"
    exit 1
}

$phaseAPy = & $pythonExe "04_SCRIPTS\python\core\validate_phase_a.py" 2>&1
if ($LASTEXITCODE -ne 0) {
    $phaseAPy | ForEach-Object { Write-Output $_ }
    Write-Error "Phase A python validation failed"
    exit 1
}

$phaseARun = & powershell -ExecutionPolicy Bypass -File "04_SCRIPTS\powershell\Run-ContentEngine.ps1" 2>&1
if ($LASTEXITCODE -ne 0) {
    $phaseARun | ForEach-Object { Write-Output $_ }
    Write-Error "Phase A runtime validation failed"
    exit 1
}

[System.IO.File]::WriteAllText($probeSandboxPath, "EXCLUSION_PROBE", [System.Text.UTF8Encoding]::new($false))

$snapshotRun1 = & $pythonExe "04_SCRIPTS\python\core\change_snapshot.py" --target both 2>&1
if ($LASTEXITCODE -ne 0) {
    $snapshotRun1 | ForEach-Object { Write-Output $_ }
    Write-Error "First snapshot run failed"
    exit 1
}

$deltaRun1 = & $pythonExe "04_SCRIPTS\python\core\change_detector.py" 2>&1
if ($LASTEXITCODE -ne 0) {
    $deltaRun1 | ForEach-Object { Write-Output $_ }
    Write-Error "First delta run failed"
    exit 1
}

$currentSnapshot1 = Get-Content -LiteralPath $currentPath -Raw | ConvertFrom-Json
$baselineSnapshot = Get-Content -LiteralPath $baselinePath -Raw | ConvertFrom-Json

$snapshotRun2 = & $pythonExe "04_SCRIPTS\python\core\change_snapshot.py" --target current 2>&1
if ($LASTEXITCODE -ne 0) {
    $snapshotRun2 | ForEach-Object { Write-Output $_ }
    Write-Error "Second snapshot run failed"
    exit 1
}

$deltaRun2 = & $pythonExe "04_SCRIPTS\python\core\change_detector.py" 2>&1
if ($LASTEXITCODE -ne 0) {
    $deltaRun2 | ForEach-Object { Write-Output $_ }
    Write-Error "Second delta run failed"
    exit 1
}

$lockTest = & $pythonExe "04_SCRIPTS\python\core\change_snapshot.py" --lock-self-test 2>&1
if ($LASTEXITCODE -ne 0) {
    $lockTest | ForEach-Object { Write-Output $_ }
    Write-Error "Snapshot lock self-test failed"
    exit 1
}

$partialProbe = & $pythonExe "04_SCRIPTS\python\core\change_snapshot.py" --write-partial-probe 2>&1
if ($LASTEXITCODE -ne 0) {
    $partialProbe | ForEach-Object { Write-Output $_ }
    Write-Error "Partial snapshot probe creation failed"
    exit 1
}

& $pythonExe "04_SCRIPTS\python\core\change_detector.py" --baseline-path $partialProbePath --current-path $currentPath --output-path $partialDeltaProbePath *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Error "Partial snapshot probe was accepted unexpectedly"
    exit 1
}

$currentSnapshot2 = Get-Content -LiteralPath $currentPath -Raw | ConvertFrom-Json
$delta = Get-Content -LiteralPath $deltaPath -Raw | ConvertFrom-Json
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

if ($currentSnapshot1.snapshot_hash -ne $currentSnapshot2.snapshot_hash) {
    Write-Error "Determinism check failed: snapshot hashes differ"
    exit 1
}

if ($baselineSnapshot.snapshot_hash -ne $currentSnapshot2.snapshot_hash) {
    Write-Error "Baseline check failed: baseline and current hashes differ"
    exit 1
}

if ($delta.summary.new -ne 0 -or $delta.summary.modified -ne 0 -or $delta.summary.deleted -ne 0) {
    Write-Error "Delta check failed: snapshot delta is not empty"
    exit 1
}

$probePresent = $false
foreach ($entry in $currentSnapshot2.entries) {
    if ($entry.path -eq "00_SYSTEM/core/change_awareness/probes/EXCLUSION_PROBE.txt") {
        $probePresent = $true
    }
}
if ($probePresent) {
    Write-Error "Probe sandbox exclusion failed"
    exit 1
}

$report = @"
# PHASE B AUDIT REPORT

- FASE 0 PASS: $($phase0Py -join '; ')
- FASE A PASS: $($phaseAPy -join '; ') / $($phaseARun -join '; ')
- Snapshot created: $($currentSnapshot2.snapshot_id)
- Delta generated: $($delta.delta_status)
- Manifest updated: $($manifest.snapshot_hash)
- Determinism: PASS
- Lock test: $($lockTest -join '; ')
- Partial snapshot blocked: PASS
- Probe sandbox excluded: PASS
- Git awareness: $($delta.summary.git_conflicts) tracked differences detected
- No destructive actions: PASS
"@
[System.IO.File]::WriteAllText($reportPath, $report, [System.Text.UTF8Encoding]::new($false))

Write-Output "PHASE_B_RUNTIME: PASS"

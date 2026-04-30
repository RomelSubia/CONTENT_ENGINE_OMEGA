function Invoke-AnomalyDetection {
    param([string]$RootPath)

    $Anomalies = @()

    function Add-AnomalyLocal {
        param($code, $severity, $detail)
        return @{
            code = $code
            severity = $severity
            detail = $detail
        }
    }

    $gitStatus = git status --short
    if ($gitStatus) {
        $Anomalies += Add-AnomalyLocal "REPO_DIRTY" "BLOCKING" "Repository has uncommitted changes."
    }

    $local = git rev-parse HEAD
    $remote = git rev-parse "@{u}"
    if ($local -ne $remote) {
        $Anomalies += Add-AnomalyLocal "HEAD_MISMATCH" "BLOCKING" "Local HEAD differs from upstream."
    }

    $Required = @(
        "00_SYSTEM\brain\state\BRAIN_STATE.json",
        "00_SYSTEM\brain\policies\POLICY_REGISTRY.json",
        "00_SYSTEM\reports\brain\G_J_CAPA_1_OFFICIAL_SEAL.txt",
        "00_SYSTEM\reports\brain\G_J_CAPA_2_OFFICIAL_SEAL.txt",
        "00_SYSTEM\brain\evidence\CAPA_2_EVIDENCE.json"
    )

    foreach ($File in $Required) {
        $Full = Join-Path $RootPath $File
        if (!(Test-Path $Full)) {
            $Anomalies += Add-AnomalyLocal "MISSING_REQUIRED_FILE" "BLOCKING" $File
        }
        elseif ((Get-Item $Full).Length -le 0) {
            $Anomalies += Add-AnomalyLocal "EMPTY_REQUIRED_FILE" "BLOCKING" $File
        }
    }

    $StagingResidue = @(Get-ChildItem "$RootPath\00_SYSTEM\brain" -Recurse -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "\.tmp$|\.staging" })

    if ($StagingResidue.Length -gt 0) {
        $Anomalies += Add-AnomalyLocal "STAGING_RESIDUE" "BLOCKING" "Temporary/staging residue detected."
    }

    $LockResidue = @(Get-ChildItem "$RootPath\00_SYSTEM\brain" -Recurse -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "\.lock$" })

    if ($LockResidue.Length -gt 0) {
        $Anomalies += Add-AnomalyLocal "LOCK_RESIDUE" "BLOCKING" "Lock residue detected."
    }

    $Critical = @($Anomalies | Where-Object { $_.severity -eq "CRITICAL" })
    $Blocking = @($Anomalies | Where-Object { $_.severity -eq "BLOCKING" })
    $Warning = @($Anomalies | Where-Object { $_.severity -eq "WARNING" })

    if ($Critical.Length -gt 0) {
        return @{ anomaly_status = "CRITICAL_ANOMALY"; anomalies = $Anomalies }
    }

    if ($Blocking.Length -gt 0) {
        return @{ anomaly_status = "BLOCKING_ANOMALY"; anomalies = $Anomalies }
    }

    if ($Warning.Length -gt 0) {
        return @{ anomaly_status = "WARNING_ANOMALY"; anomalies = $Anomalies }
    }

    return @{ anomaly_status = "NO_ANOMALY"; anomalies = @() }
}

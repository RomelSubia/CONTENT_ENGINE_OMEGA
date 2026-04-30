. "$PSScriptRoot\layer2_runner.ps1"
. "$PSScriptRoot\anomaly_detection.ps1"
. "$PSScriptRoot\policy_enforcement.ps1"
. "$PSScriptRoot\trust_model.ps1"

function Invoke-BrainLayer3Check {
    param(
        [string]$RootPath,
        [string]$RequestType = "AUDIT"
    )

    $Layer2 = Invoke-BrainLayer2Check -RootPath $RootPath
    if ($Layer2.result -ne "PASS") {
        return @{
            result = "BLOCK"
            reason = "LAYER2_NOT_VALID"
            details = $Layer2
        }
    }

    $Anomaly = Invoke-AnomalyDetection -RootPath $RootPath

    if ($Anomaly.anomaly_status -eq "CRITICAL_ANOMALY") {
        return @{
            result = "LOCK"
            reason = "CRITICAL_ANOMALY"
            anomalies = $Anomaly.anomalies
        }
    }

    if ($Anomaly.anomaly_status -eq "BLOCKING_ANOMALY") {
        return @{
            result = "BLOCK"
            reason = "BLOCKING_ANOMALY"
            anomalies = $Anomaly.anomalies
        }
    }

    $Policy = Invoke-PolicyEnforcement -RootPath $RootPath -RequestType $RequestType

    if ($Policy.policy_result -eq "POLICY_LOCK") {
        return @{
            result = "LOCK"
            reason = "POLICY_LOCK"
            policy = $Policy
        }
    }

    if ($Policy.policy_result -eq "POLICY_BLOCK") {
        return @{
            result = "BLOCK"
            reason = "POLICY_BLOCK"
            policy = $Policy
        }
    }

    $Trust = Invoke-TrustModel -AnomalyResult $Anomaly -PolicyResult $Policy

    if ($Trust.trust_state -eq "LOCKED") {
        return @{
            result = "LOCK"
            reason = $Trust.reason
            trust = $Trust
        }
    }

    if ($Trust.trust_state -eq "UNTRUSTED") {
        return @{
            result = "BLOCK"
            reason = $Trust.reason
            trust = $Trust
        }
    }

    return @{
        result = "PASS"
        message = "CAPA_3_VALID"
        anomaly_status = $Anomaly.anomaly_status
        policy_result = $Policy.policy_result
        trust_state = $Trust.trust_state
    }
}

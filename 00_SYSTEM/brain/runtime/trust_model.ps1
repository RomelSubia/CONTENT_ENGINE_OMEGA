function Invoke-TrustModel {
    param(
        [hashtable]$AnomalyResult,
        [hashtable]$PolicyResult
    )

    if ($AnomalyResult.anomaly_status -eq "CRITICAL_ANOMALY") {
        return @{
            trust_state = "LOCKED"
            reason = "CRITICAL_ANOMALY"
        }
    }

    if ($PolicyResult.policy_result -eq "POLICY_LOCK") {
        return @{
            trust_state = "LOCKED"
            reason = "POLICY_LOCK"
        }
    }

    if ($AnomalyResult.anomaly_status -eq "BLOCKING_ANOMALY") {
        return @{
            trust_state = "UNTRUSTED"
            reason = "BLOCKING_ANOMALY"
        }
    }

    if ($PolicyResult.policy_result -eq "POLICY_BLOCK") {
        return @{
            trust_state = "UNTRUSTED"
            reason = "POLICY_BLOCK"
        }
    }

    if ($AnomalyResult.anomaly_status -eq "WARNING_ANOMALY") {
        return @{
            trust_state = "CAUTION"
            reason = "WARNING_ANOMALY"
        }
    }

    return @{
        trust_state = "TRUSTED"
        reason = "NO_ANOMALY_POLICY_PASS"
    }
}

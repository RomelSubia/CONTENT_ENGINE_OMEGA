function Invoke-AdaptiveSafetyGate {
    param(
        [hashtable]$Recommendation
    )

    if ($Recommendation.action_allowed -eq $true) {
        return @{
            safety_status = "BLOCK"
            reason = "ADAPTIVE_AUTO_ACTION_NOT_ALLOWED"
        }
    }

    if ($Recommendation.requires_approval -eq $true) {
        return @{
            safety_status = "REQUIRE_APPROVAL"
            reason = "ADAPTATION_REQUIRES_HUMAN_APPROVAL"
        }
    }

    return @{
        safety_status = "PASS"
        reason = "NO_ACTION_SAFE"
    }
}

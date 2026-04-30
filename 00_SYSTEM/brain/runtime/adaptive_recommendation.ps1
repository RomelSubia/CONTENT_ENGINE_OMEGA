function Invoke-AdaptiveRecommendation {
    param(
        [string]$SignalType,
        [string]$SignalValue
    )

    if ($SignalType -eq "FAILURE_PATTERN") {
        return @{
            adaptive_status = "RECOMMENDATION_READY"
            recommendation = "REVIEW_PATTERN_AND_PROPOSE_SAFE_FIX"
            action_allowed = $false
            requires_approval = $true
        }
    }

    if ($SignalType -eq "PERFORMANCE_PATTERN") {
        return @{
            adaptive_status = "RECOMMENDATION_READY"
            recommendation = "OPTIMIZATION_REVIEW_REQUIRED"
            action_allowed = $false
            requires_approval = $true
        }
    }

    return @{
        adaptive_status = "NO_ACTION"
        recommendation = "NO_SAFE_ADAPTATION_REQUIRED"
        action_allowed = $false
        requires_approval = $false
    }
}

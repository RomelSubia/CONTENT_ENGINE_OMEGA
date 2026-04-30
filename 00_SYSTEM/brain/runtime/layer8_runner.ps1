. "$PSScriptRoot\layer7_runner.ps1"
. "$PSScriptRoot\adaptive_recommendation.ps1"
. "$PSScriptRoot\adaptive_safety_gate.ps1"
. "$PSScriptRoot\adaptive_memory_review.ps1"

function Invoke-BrainLayer8Check {
    param([string]$RootPath)

    $Layer7 = Invoke-BrainLayer7Check -RootPath $RootPath
    if ($Layer7.result -ne "PASS") {
        return @{
            result = "BLOCK"
            reason = "LAYER7_NOT_VALID"
        }
    }

    $MemoryReview = Invoke-AdaptiveMemoryReview -RootPath $RootPath
    if ($MemoryReview.review_status -ne "PASS") {
        return @{
            result = "BLOCK"
            reason = $MemoryReview.reason
        }
    }

    $Recommendation = Invoke-AdaptiveRecommendation -SignalType "FAILURE_PATTERN" -SignalValue "TEST_PATTERN"
    if ($Recommendation.adaptive_status -ne "RECOMMENDATION_READY") {
        return @{
            result = "BLOCK"
            reason = "ADAPTIVE_RECOMMENDATION_FAILED"
        }
    }

    $Safety = Invoke-AdaptiveSafetyGate -Recommendation $Recommendation
    if ($Safety.safety_status -ne "REQUIRE_APPROVAL") {
        return @{
            result = "BLOCK"
            reason = "ADAPTIVE_SAFETY_GATE_FAILED"
        }
    }

    $NoAction = Invoke-AdaptiveRecommendation -SignalType "NONE" -SignalValue "SAFE"
    $NoActionSafety = Invoke-AdaptiveSafetyGate -Recommendation $NoAction
    if ($NoActionSafety.safety_status -ne "PASS") {
        return @{
            result = "BLOCK"
            reason = "NO_ACTION_SAFETY_FAILED"
        }
    }

    return @{
        result = "PASS"
        message = "CAPA_8_VALID"
        adaptive_status = $Recommendation.adaptive_status
        safety_status = $Safety.safety_status
        memory_review = $MemoryReview.review_status
        auto_action_allowed = $Recommendation.action_allowed
    }
}

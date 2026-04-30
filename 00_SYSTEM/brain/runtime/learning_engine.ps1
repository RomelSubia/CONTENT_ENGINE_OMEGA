function Invoke-LearningEngine {
    param(
        [hashtable]$DecisionResult
    )

    if ($DecisionResult.decision -eq "BLOCK") {
        return @{
            learning_status = "SKIPPED"
            reason = "NO_LEARNING_FROM_BLOCK"
        }
    }

    return @{
        learning_status = "RECORDED"
        insight = $DecisionResult.reason
    }
}

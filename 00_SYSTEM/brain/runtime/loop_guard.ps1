function Invoke-LoopIsolationGuard {
    param(
        [int]$IterationCount = 1,
        [int]$RetryCount = 0,
        [int]$RecursiveDepth = 0
    )

    if ($IterationCount -gt 3) {
        return @{
            loop_status = "BLOCK"
            reason = "MAX_INTERNAL_ITERATIONS_EXCEEDED"
        }
    }

    if ($RetryCount -gt 1) {
        return @{
            loop_status = "BLOCK"
            reason = "MAX_RETRIES_EXCEEDED"
        }
    }

    if ($RecursiveDepth -gt 0) {
        return @{
            loop_status = "BLOCK"
            reason = "RECURSION_NOT_ALLOWED"
        }
    }

    return @{
        loop_status = "PASS"
        reason = "LOOP_SAFE"
    }
}

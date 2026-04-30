function Invoke-TimeoutPolicy {
    param(
        [int]$ElapsedMs,
        [int]$BudgetMs = 3000
    )

    if ($ElapsedMs -gt $BudgetMs) {
        return @{
            timeout_status = "BLOCK"
            reason = "TIMEOUT_EXCEEDED"
            elapsed_ms = $ElapsedMs
            budget_ms = $BudgetMs
        }
    }

    return @{
        timeout_status = "PASS"
        elapsed_ms = $ElapsedMs
        budget_ms = $BudgetMs
    }
}

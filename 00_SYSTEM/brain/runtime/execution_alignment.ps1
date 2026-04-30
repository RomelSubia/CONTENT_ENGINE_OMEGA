function Invoke-ExecutionAlignment {
    param(
        [Parameter(Mandatory=$true)][hashtable]$DecisionResult
    )

    switch ($DecisionResult.decision) {
        "ALLOW" {
            return @{
                alignment_status = "ALIGNED"
                required_next_gate = "NONE"
                execution_allowed = $true
                mutation_allowed = $false
                commit_allowed = $false
            }
        }
        "REQUIRE_DRY_RUN" {
            return @{
                alignment_status = "NOT_ALIGNED"
                required_next_gate = "DRY_RUN"
                execution_allowed = $false
                mutation_allowed = $false
                commit_allowed = $false
            }
        }
        "REQUIRE_APPROVAL" {
            return @{
                alignment_status = "NOT_ALIGNED"
                required_next_gate = "APPROVAL"
                execution_allowed = $false
                mutation_allowed = $false
                commit_allowed = $false
            }
        }
        "REQUIRE_AUDIT" {
            return @{
                alignment_status = "NOT_ALIGNED"
                required_next_gate = "AUDIT"
                execution_allowed = $false
                mutation_allowed = $false
                commit_allowed = $false
            }
        }
        "BLOCK" {
            return @{
                alignment_status = "BLOCKED"
                required_next_gate = "NONE"
                execution_allowed = $false
                mutation_allowed = $false
                commit_allowed = $false
            }
        }
        default {
            return @{
                alignment_status = "ESCALATE"
                required_next_gate = "REVIEW"
                execution_allowed = $false
                mutation_allowed = $false
                commit_allowed = $false
            }
        }
    }
}

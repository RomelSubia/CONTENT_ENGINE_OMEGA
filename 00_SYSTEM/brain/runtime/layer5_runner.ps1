. "$PSScriptRoot\layer4_runner.ps1"
. "$PSScriptRoot\decision_engine.ps1"
. "$PSScriptRoot\execution_alignment.ps1"

function Invoke-BrainLayer5Check {
    param(
        [string]$RootPath,
        [string]$RequestType = "AUDIT"
    )

    $Layer4 = Invoke-BrainLayer4Check -RootPath $RootPath
    if ($Layer4.result -ne "PASS") {
        return @{
            result = "BLOCK"
            reason = "LAYER4_NOT_VALID"
            details = $Layer4
        }
    }

    $Decision = Invoke-DecisionEngine -RequestType $RequestType -Layer4Result $Layer4
    $Alignment = Invoke-ExecutionAlignment -DecisionResult $Decision

    if ($RequestType -eq "EXECUTION" -and $Decision.decision -ne "REQUIRE_DRY_RUN") {
        return @{ result = "BLOCK"; reason = "EXECUTION_NOT_GATED_BY_DRY_RUN" }
    }

    if ($RequestType -eq "MUTATION" -and $Decision.decision -ne "REQUIRE_APPROVAL") {
        return @{ result = "BLOCK"; reason = "MUTATION_NOT_GATED_BY_APPROVAL" }
    }

    if ($RequestType -eq "COMMIT" -and $Decision.decision -ne "REQUIRE_AUDIT") {
        return @{ result = "BLOCK"; reason = "COMMIT_NOT_GATED_BY_AUDIT" }
    }

    if ($RequestType -eq "MANUAL_CONNECTION" -and $Decision.decision -ne "BLOCK") {
        return @{ result = "BLOCK"; reason = "MANUAL_CONNECTION_NOT_BLOCKED" }
    }

    return @{
        result = "PASS"
        message = "CAPA_5_VALID"
        request_type = $RequestType
        decision = $Decision.decision
        reason = $Decision.reason
        alignment_status = $Alignment.alignment_status
        required_next_gate = $Alignment.required_next_gate
        execution_allowed = $Alignment.execution_allowed
        mutation_allowed = $Alignment.mutation_allowed
        commit_allowed = $Alignment.commit_allowed
    }
}

. "$PSScriptRoot\orchestrator.ps1"

function Invoke-BrainLayer6Check {
    param([string]$RootPath)

    $Audit = Invoke-Orchestrator -RootPath $RootPath -RequestType "AUDIT"
    if ($Audit.orchestration_status -ne "PASS") {
        return @{ result = "BLOCK"; reason = "AUDIT_FAILED" }
    }

    $Exec = Invoke-Orchestrator -RootPath $RootPath -RequestType "EXECUTION"
    if ($Exec.autonomy_mode -ne "SIMULATION_ONLY") {
        return @{ result = "BLOCK"; reason = "EXECUTION_NOT_SIMULATION" }
    }

    $Mut = Invoke-Orchestrator -RootPath $RootPath -RequestType "MUTATION"
    if ($Mut.autonomy_mode -ne "WAIT_APPROVAL") {
        return @{ result = "BLOCK"; reason = "MUTATION_NOT_GATED" }
    }

    return @{
        result = "PASS"
        message = "CAPA_6_VALID"
        audit_mode = $Audit.autonomy_mode
        execution_mode = $Exec.autonomy_mode
        mutation_mode = $Mut.autonomy_mode
    }
}

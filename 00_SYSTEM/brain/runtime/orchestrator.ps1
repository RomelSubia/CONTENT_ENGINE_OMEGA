. "$PSScriptRoot\layer5_runner.ps1"
. "$PSScriptRoot\autonomy_policy.ps1"

function Invoke-Orchestrator {
    param(
        [string]$RootPath,
        [string]$RequestType = "AUDIT"
    )

    $Layer5 = Invoke-BrainLayer5Check -RootPath $RootPath -RequestType $RequestType

    if ($Layer5.result -ne "PASS") {
        return @{
            orchestration_status = "BLOCK"
            reason = "LAYER5_BLOCK"
            details = $Layer5
        }
    }

    $Autonomy = Invoke-AutonomyPolicy -Decision $Layer5.decision

    return @{
        orchestration_status = "PASS"
        decision = $Layer5.decision
        autonomy_mode = $Autonomy.autonomy_mode
        execution_permitted = $Autonomy.execution_permitted
        next_gate = $Layer5.required_next_gate
    }
}

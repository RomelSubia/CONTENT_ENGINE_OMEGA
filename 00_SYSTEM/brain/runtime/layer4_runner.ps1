. "$PSScriptRoot\layer3_runner.ps1"
. "$PSScriptRoot\determinism_engine.ps1"
. "$PSScriptRoot\input_hardening.ps1"
. "$PSScriptRoot\loop_guard.ps1"
. "$PSScriptRoot\timeout_control.ps1"

function Invoke-BrainLayer4Check {
    param([string]$RootPath)

    $Layer3 = Invoke-BrainLayer3Check -RootPath $RootPath -RequestType "AUDIT"
    if ($Layer3.result -ne "PASS") {
        return @{
            result = "BLOCK"
            reason = "LAYER3_NOT_VALID"
            details = $Layer3
        }
    }

    $Input = [pscustomobject]@{
        request_type = "AUDIT"
        target_phase = "G-J.x v2.2"
        requested_action = "CAPA_4_VALIDATION"
        evidence_required = $true
    }

    $Hardening = Invoke-InputHardening -InputObject $Input
    if ($Hardening.hardening_status -ne "PASS") {
        return @{
            result = "BLOCK"
            reason = $Hardening.reason
            details = $Hardening
        }
    }

    $Loop = Invoke-LoopIsolationGuard -IterationCount 1 -RetryCount 0 -RecursiveDepth 0
    if ($Loop.loop_status -ne "PASS") {
        return @{
            result = "BLOCK"
            reason = $Loop.reason
            details = $Loop
        }
    }

    $Timeout = Invoke-TimeoutPolicy -ElapsedMs 1 -BudgetMs 3000
    if ($Timeout.timeout_status -ne "PASS") {
        return @{
            result = "BLOCK"
            reason = $Timeout.reason
            details = $Timeout
        }
    }

    $Determinism = Test-Determinism -InputObject $Input -Repeat 10
    if ($Determinism.determinism_status -ne "PASS") {
        return @{
            result = "BLOCK"
            reason = $Determinism.reason
            details = $Determinism
        }
    }

    $BadInput = [pscustomobject]@{
        request_type = "EXECUTION"
        target_phase = "..\outside"
        requested_action = "Remove-Item C:\"
    }

    $BadCheck = Invoke-InputHardening -InputObject $BadInput
    if ($BadCheck.hardening_status -ne "BLOCK") {
        return @{
            result = "BLOCK"
            reason = "BAD_INPUT_NOT_BLOCKED"
            details = $BadCheck
        }
    }

    return @{
        result = "PASS"
        message = "CAPA_4_VALID"
        determinism_hash = $Determinism.hash
        hardening_status = $Hardening.hardening_status
        bad_input_blocked = $true
        loop_guard = $Loop.loop_status
        timeout_control = $Timeout.timeout_status
    }
}

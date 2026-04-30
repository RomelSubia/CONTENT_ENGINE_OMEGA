. "$PSScriptRoot\self_audit.ps1"
. "$PSScriptRoot\state_awareness.ps1"

function Invoke-BrainLayer1Check {
    param([string]$RootPath)

    $audit = Invoke-SelfAudit -RootPath $RootPath
    if ($audit.status -ne "PASS") {
        return @{
            result = "BLOCK"
            reason = "SELF_AUDIT_FAILED"
            details = $audit
        }
    }

    $state = Invoke-StateAwareness -RootPath $RootPath
    if ($state.state -ne "VALID") {
        return @{
            result = "BLOCK"
            reason = $state.reason
            details = $state
        }
    }

    return @{
        result = "PASS"
        message = "CAPA_1_VALID"
    }
}

. "$PSScriptRoot\layer6_runner.ps1"
. "$PSScriptRoot\memory_engine.ps1"
. "$PSScriptRoot\context_engine.ps1"
. "$PSScriptRoot\learning_engine.ps1"

function Invoke-BrainLayer7Check {
    param([string]$RootPath)

    $Layer6 = Invoke-BrainLayer6Check -RootPath $RootPath
    if ($Layer6.result -ne "PASS") {
        return @{ result = "BLOCK"; reason = "LAYER6_NOT_VALID" }
    }

    $Mem = Invoke-MemoryEngine -RootPath $RootPath -Key "last_check" -Value "CAPA7"
    if ($Mem.memory_status -ne "WRITE_OK") {
        return @{ result = "BLOCK"; reason = "MEMORY_FAIL" }
    }

    $Ctx = Invoke-ContextEngine -RootPath $RootPath -RequestType "AUDIT"
    if ($Ctx.context -ne "AVAILABLE" -and $Ctx.context -ne "EMPTY") {
        return @{ result = "BLOCK"; reason = "CONTEXT_FAIL" }
    }

    $Learn = Invoke-LearningEngine -DecisionResult @{ decision = "ALLOW"; reason = "TEST" }
    if ($Learn.learning_status -ne "RECORDED") {
        return @{ result = "BLOCK"; reason = "LEARNING_FAIL" }
    }

    return @{
        result = "PASS"
        message = "CAPA_7_VALID"
        memory = $Mem.memory_status
        context = $Ctx.context
        learning = $Learn.learning_status
    }
}

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\source_resolver\manual_source_resolver_v2_1_3.ps1"
. "00_SYSTEM\bridge\brain_adapter\brain_read_only_check_v2_1_3.ps1"

function Test-ManualBrainBridgeV213 {
    param([string]$RootPath = "D:\CONTENT_ENGINE_OMEGA")

    $manual = Test-ManualSourceOfTruthV213 -RootPath $RootPath
    $brain = Test-BrainReadOnlyStatusV213 -RootPath $RootPath

    if ($manual.status -ne "PASS") {
        return @{
            status = "BLOCK"
            reason = "MANUAL_SOURCE_RESOLVER_NOT_PASS"
            manual = $manual
            brain = $brain
        }
    }

    if ($brain.status -ne "PASS") {
        return @{
            status = "BLOCK"
            reason = "BRAIN_READ_ONLY_CHECK_NOT_PASS"
            manual = $manual
            brain = $brain
        }
    }

    return @{
        status = "PASS"
        reason = "MANUAL_BRAIN_BRIDGE_V2_1_3_VALID"
        manual = $manual
        brain = $brain
    }
}
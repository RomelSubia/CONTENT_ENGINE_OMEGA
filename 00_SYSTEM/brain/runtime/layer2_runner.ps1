. "$PSScriptRoot\..\runtime\layer1_runner.ps1"
. "$PSScriptRoot\..\integrity\runtime_integrity.ps1"
. "$PSScriptRoot\..\evidence\evidence_trace.ps1"

function Invoke-BrainLayer2Check {
    param([string]$RootPath)

    $Layer1 = Invoke-BrainLayer1Check -RootPath $RootPath
    if ($Layer1.result -ne "PASS") {
        return @{
            result = "BLOCK"
            reason = "LAYER1_NOT_VALID"
            details = $Layer1
        }
    }

    $Integrity = Test-BrainIntegrity -RootPath $RootPath
    if ($Integrity.integrity_status -ne "PASS") {
        return @{
            result = "BLOCK"
            reason = "INTEGRITY_FAILED"
            details = $Integrity
        }
    }

    $Payload = @{
        brain_layer = "CAPA_2"
        status = "EVIDENCE_INTEGRITY_VALID"
        integrity = $Integrity
        deterministic = $true
    } | ConvertTo-Json -Depth 10

    $EvidencePath = Join-Path $RootPath "00_SYSTEM\brain\evidence\CAPA_2_EVIDENCE.json"

    $Trace = Write-AtomicEvidence -Path $EvidencePath -Content $Payload

    if ($Trace.status -ne "TRACE_RECORDED") {
        return @{
            result = $Trace.status
            reason = $Trace.reason
            details = $Trace
        }
    }

    return @{
        result = "PASS"
        message = "CAPA_2_VALID"
        evidence_hash = $Trace.evidence_hash
        integrity = $Integrity
    }
}

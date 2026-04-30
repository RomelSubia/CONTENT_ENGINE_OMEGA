. "$PSScriptRoot\..\evidence\evidence_trace.ps1"

function Test-BrainIntegrity {
    param([string]$RootPath)

    $Critical = @(
        "00_SYSTEM\brain\state\BRAIN_STATE.json",
        "00_SYSTEM\brain\policies\POLICY_REGISTRY.json",
        "00_SYSTEM\reports\brain\G_J_CAPA_1_OFFICIAL_SEAL.txt"
    )

    $Results = @()
    $Failed = @()

    foreach ($File in $Critical) {
        $Full = Join-Path $RootPath $File

        if (!(Test-Path $Full)) {
            $Failed += @{
                file = $File
                reason = "MISSING_CRITICAL_FILE"
            }
            continue
        }

        if ((Get-Item $Full).Length -le 0) {
            $Failed += @{
                file = $File
                reason = "EMPTY_CRITICAL_FILE"
            }
            continue
        }

        $Content = Get-Content $Full -Raw
        $Hash = Get-StableHash -Text $Content

        $Results += @{
            file = $File
            hash = $Hash
            status = "OK"
        }
    }

    if ($Failed.Count -gt 0) {
        return @{
            integrity_status = "BLOCK"
            failed = $Failed
            files = $Results
        }
    }

    return @{
        integrity_status = "PASS"
        files = $Results
    }
}

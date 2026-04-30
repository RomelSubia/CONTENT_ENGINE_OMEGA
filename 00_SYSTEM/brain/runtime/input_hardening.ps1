function Invoke-InputHardening {
    param(
        [Parameter(Mandatory=$true)]$InputObject
    )

    $AllowedRequestTypes = @(
        "AUDIT",
        "DRY_RUN",
        "APPROVAL",
        "EXECUTION",
        "FREEZE",
        "PHASE_TRANSITION",
        "MANUAL_CONNECTION"
    )

    $BlockedPatterns = @(
        "\.\.",
        "[;&|]",
        "Invoke-Expression",
        "Start-Process",
        "Remove-Item",
        "Set-ExecutionPolicy",
        "curl ",
        "wget ",
        "powershell.exe",
        "cmd.exe"
    )

    $RequiredFields = @(
        "request_type",
        "target_phase",
        "requested_action"
    )

    $Failed = @()

    foreach ($Field in $RequiredFields) {
        if (-not ($InputObject.PSObject.Properties.Name -contains $Field)) {
            $Failed += "MISSING_FIELD:$Field"
        }
    }

    if ($Failed.Length -gt 0) {
        return @{
            hardening_status = "BLOCK"
            reason = "SCHEMA_INVALID"
            failed = $Failed
        }
    }

    if ($AllowedRequestTypes -notcontains $InputObject.request_type) {
        return @{
            hardening_status = "BLOCK"
            reason = "INVALID_REQUEST_TYPE"
            failed = @("request_type")
        }
    }

    $Raw = ($InputObject | ConvertTo-Json -Depth 30 -Compress)

    if ($Raw.Length -gt 10000) {
        return @{
            hardening_status = "BLOCK"
            reason = "INPUT_TOO_LARGE"
        }
    }

    foreach ($Pattern in $BlockedPatterns) {
        if ($Raw -match $Pattern) {
            return @{
                hardening_status = "BLOCK"
                reason = "BLOCKED_TOKEN_DETECTED"
                pattern = $Pattern
            }
        }
    }

    if ($Raw -match "[\u202E\u202D\u202B\u202A]") {
        return @{
            hardening_status = "BLOCK"
            reason = "DANGEROUS_UNICODE_DIRECTIONAL_MARK"
        }
    }

    return @{
        hardening_status = "PASS"
        reason = "INPUT_VALID"
    }
}

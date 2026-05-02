$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function New-BridgeResult {
    param(
        [string]$Status,
        [string]$Reason,
        [hashtable]$Data = @{}
    )

    return @{
        status = $Status
        reason = $Reason
        data = $Data
    }
}

function Test-BridgeFoundation {
    param([string]$RootPath = "D:\CONTENT_ENGINE_OMEGA")

    $required = @(
        "00_SYSTEM\bridge\config\BRIDGE_POLICY.json",
        "00_SYSTEM\bridge\config\BRIDGE_READ_WHITELIST.json",
        "00_SYSTEM\bridge\config\BRIDGE_WRITE_WHITELIST.json",
        "00_SYSTEM\bridge\config\BRIDGE_EXIT_CODES.json",
        "00_SYSTEM\bridge\contracts\MANUAL_CURRENT_CONTRACT.json",
        "00_SYSTEM\bridge\contracts\BRAIN_READ_ONLY_CONTRACT.json",
        "00_SYSTEM\bridge\manifests\BRIDGE_ARTIFACT_MANIFEST.json",
        "00_SYSTEM\bridge\reports\BRIDGE_TRACEABILITY_MATRIX.json",
        "00_SYSTEM\bridge\reports\BRIDGE_BUILD_READINESS_REPORT.json"
    )

    foreach ($rel in $required) {
        $p = Join-Path $RootPath $rel

        if (!(Test-Path -LiteralPath $p)) {
            return New-BridgeResult -Status "BLOCK" -Reason "MISSING_REQUIRED_FILE" -Data @{ path = $rel }
        }

        try {
            $raw = Get-Content -LiteralPath $p -Raw

            if ([string]::IsNullOrWhiteSpace($raw)) {
                return New-BridgeResult -Status "BLOCK" -Reason "EMPTY_REQUIRED_FILE" -Data @{ path = $rel }
            }

            $null = $raw | ConvertFrom-Json
        }
        catch {
            return New-BridgeResult -Status "BLOCK" -Reason "INVALID_JSON" -Data @{ path = $rel; error = $_.Exception.Message }
        }
    }

    $policyPath = Join-Path $RootPath "00_SYSTEM\bridge\config\BRIDGE_POLICY.json"
    $policy = Get-Content -LiteralPath $policyPath -Raw | ConvertFrom-Json

    if ($policy.execution_allowed -ne $false) {
        return New-BridgeResult -Status "LOCK" -Reason "EXECUTION_ALLOWED_TRUE"
    }

    if ($policy.external_side_effects_allowed -ne $false) {
        return New-BridgeResult -Status "LOCK" -Reason "EXTERNAL_SIDE_EFFECTS_TRUE"
    }

    if ($policy.brain_write_allowed -ne $false) {
        return New-BridgeResult -Status "LOCK" -Reason "BRAIN_WRITE_ALLOWED_TRUE"
    }

    if ($policy.auto_action_allowed -ne $false) {
        return New-BridgeResult -Status "LOCK" -Reason "AUTO_ACTION_ALLOWED_TRUE"
    }

    if ($policy.fail_closed_required -ne $true) {
        return New-BridgeResult -Status "LOCK" -Reason "FAIL_CLOSED_NOT_REQUIRED"
    }

    if ($policy.no_capa_9 -ne $true) {
        return New-BridgeResult -Status "LOCK" -Reason "CAPA_9_NOT_BLOCKED"
    }

    return New-BridgeResult -Status "PASS" -Reason "BRIDGE_FOUNDATION_VALID"
}
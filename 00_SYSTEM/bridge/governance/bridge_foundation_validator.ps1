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

function Get-FileSha256LowerLocal {
    param([Parameter(Mandatory=$true)][string]$Path)

    if (!(Test-Path -LiteralPath $Path)) {
        throw "Missing file for hash: $Path"
    }

    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-BridgeFoundation {
    param([string]$RootPath = "D:\CONTENT_ENGINE_OMEGA")

    $requiredJson = @(
        "00_SYSTEM\bridge\config\BRIDGE_POLICY.json",
        "00_SYSTEM\bridge\config\BRIDGE_READ_WHITELIST.json",
        "00_SYSTEM\bridge\config\BRIDGE_WRITE_WHITELIST.json",
        "00_SYSTEM\bridge\config\BRIDGE_EXIT_CODES.json",
        "00_SYSTEM\bridge\contracts\MANUAL_CURRENT_CONTRACT.json",
        "00_SYSTEM\bridge\contracts\BRAIN_READ_ONLY_CONTRACT.json",
        "00_SYSTEM\bridge\manifests\BRIDGE_ARTIFACT_MANIFEST.json",
        "00_SYSTEM\bridge\manifests\BRIDGE_MANIFEST_SEAL.json",
        "00_SYSTEM\bridge\reports\BRIDGE_TRACEABILITY_MATRIX.json",
        "00_SYSTEM\bridge\reports\BRIDGE_BUILD_READINESS_REPORT.json",
        "00_SYSTEM\bridge\tests\BRIDGE_TEST_MATRIX.json"
    )

    foreach ($rel in $requiredJson) {
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

    $manifestPath = Join-Path $RootPath "00_SYSTEM\bridge\manifests\BRIDGE_ARTIFACT_MANIFEST.json"
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

    if ($null -eq $manifest.artifacts) {
        return New-BridgeResult -Status "BLOCK" -Reason "MANIFEST_ARTIFACTS_MISSING"
    }

    foreach ($artifact in @($manifest.artifacts)) {
        if ([string]::IsNullOrWhiteSpace($artifact.relative_path)) {
            return New-BridgeResult -Status "BLOCK" -Reason "MANIFEST_ARTIFACT_PATH_EMPTY"
        }

        if ([string]::IsNullOrWhiteSpace($artifact.hash_sha256)) {
            return New-BridgeResult -Status "BLOCK" -Reason "MANIFEST_ARTIFACT_HASH_EMPTY" -Data @{ artifact = $artifact.artifact_id }
        }

        $artifactFull = Join-Path $RootPath ($artifact.relative_path.Replace("/","\"))
        if (!(Test-Path -LiteralPath $artifactFull)) {
            return New-BridgeResult -Status "BLOCK" -Reason "MANIFEST_ARTIFACT_FILE_MISSING" -Data @{ path = $artifact.relative_path }
        }

        $realHash = Get-FileSha256LowerLocal -Path $artifactFull
        if ($realHash -ne $artifact.hash_sha256) {
            return New-BridgeResult -Status "BLOCK" -Reason "MANIFEST_ARTIFACT_HASH_MISMATCH" -Data @{ path = $artifact.relative_path; expected = $artifact.hash_sha256; actual = $realHash }
        }
    }

    $sealPath = Join-Path $RootPath "00_SYSTEM\bridge\manifests\BRIDGE_MANIFEST_SEAL.json"
    $seal = Get-Content -LiteralPath $sealPath -Raw | ConvertFrom-Json

    if ([string]::IsNullOrWhiteSpace($seal.manifest_hash_sha256)) {
        return New-BridgeResult -Status "BLOCK" -Reason "MANIFEST_SEAL_HASH_EMPTY"
    }

    $manifestRealHash = Get-FileSha256LowerLocal -Path $manifestPath
    if ($manifestRealHash -ne $seal.manifest_hash_sha256) {
        return New-BridgeResult -Status "BLOCK" -Reason "MANIFEST_SEAL_HASH_MISMATCH" -Data @{ expected = $seal.manifest_hash_sha256; actual = $manifestRealHash }
    }

    return New-BridgeResult -Status "PASS" -Reason "BRIDGE_FOUNDATION_VALID"
}
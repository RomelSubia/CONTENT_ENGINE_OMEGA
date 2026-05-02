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

function Test-ManualSourceOfTruthV213 {
    param([string]$RootPath = "D:\CONTENT_ENGINE_OMEGA")

    $manualRel = "00_SYSTEM\manual\current\MANUAL_MASTER_CURRENT.md"
    $manifestRel = "00_SYSTEM\manual\manifest\MANUAL_SOURCE_MANIFEST.json"

    $manualPath = Join-Path -Path $RootPath -ChildPath $manualRel
    $manifestPath = Join-Path -Path $RootPath -ChildPath $manifestRel

    if (!(Test-Path -LiteralPath $manualPath)) {
        return New-BridgeResult -Status "BLOCK" -Reason "MANUAL_CURRENT_MISSING" -Data @{ path = $manualRel }
    }

    if (!(Test-Path -LiteralPath $manifestPath)) {
        return New-BridgeResult -Status "BLOCK" -Reason "MANUAL_MANIFEST_MISSING" -Data @{ path = $manifestRel }
    }

    $manualRaw = Get-Content -LiteralPath $manualPath -Raw

    if ([string]::IsNullOrWhiteSpace($manualRaw)) {
        return New-BridgeResult -Status "BLOCK" -Reason "MANUAL_EMPTY" -Data @{ path = $manualRel }
    }

    try {
        $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    }
    catch {
        return New-BridgeResult -Status "BLOCK" -Reason "MANUAL_MANIFEST_INVALID_JSON" -Data @{ error = $_.Exception.Message }
    }

    $manualHash = Get-FileSha256LowerLocal -Path $manualPath

    if (-not ($manifest.PSObject.Properties.Name -contains "manual_hash_sha256")) {
        return New-BridgeResult -Status "BLOCK" -Reason "MANUAL_HASH_FIELD_MISSING"
    }

    $manifestHash = ([string]$manifest.manual_hash_sha256).Replace("sha256:","").ToLowerInvariant()

    if ([string]::IsNullOrWhiteSpace($manifestHash)) {
        return New-BridgeResult -Status "BLOCK" -Reason "MANUAL_HASH_EMPTY_IN_MANIFEST"
    }

    if ($manifestHash -ne $manualHash) {
        return New-BridgeResult -Status "BLOCK" -Reason "MANUAL_HASH_MISMATCH" -Data @{ expected = $manifestHash; actual = $manualHash }
    }

    if ($manifest.manual_status -ne "CURRENT_VALID") {
        return New-BridgeResult -Status "BLOCK" -Reason "MANUAL_NOT_CURRENT_VALID" -Data @{ status = $manifest.manual_status }
    }

    if ($manifest.approved_for_bridge -ne $true) {
        return New-BridgeResult -Status "BLOCK" -Reason "MANUAL_NOT_APPROVED_FOR_BRIDGE"
    }

    if ($manifest.is_historical -ne $false) {
        return New-BridgeResult -Status "BLOCK" -Reason "MANUAL_MARKED_HISTORICAL"
    }

    if ($manifest.is_mixed_chat_transcript -ne $false) {
        return New-BridgeResult -Status "BLOCK" -Reason "MANUAL_MARKED_MIXED_CHAT_TRANSCRIPT"
    }

    $requiredTokens = @(
        "CONTENT ENGINE",
        "MANUAL_MASTER_CURRENT",
        "CURRENT_VALID",
        "OFFICIAL_MASTER_CURRENT",
        "APPROVED_FOR_BRIDGE"
    )

    $missingTokens = @()

    foreach ($token in $requiredTokens) {
        if ($manualRaw -notlike "*$token*") {
            $missingTokens += $token
        }
    }

    if ($missingTokens.Count -gt 0) {
        return New-BridgeResult -Status "REQUIRE_REVIEW" -Reason "MANUAL_REQUIRED_TOKENS_MISSING" -Data @{ missing = $missingTokens }
    }

    # [FAIL CLOSED], FAIL-CLOSED, BLOCK and LOCK are valid system governance terms.
    $noisePatterns = @(
        "PS D:\CONTENT_ENGINE_OMEGA>",
        "User uploaded file",
        "Pasted text",
        "tool call",
        "file_search",
        "Skipped ",
        "Presiona ENTER",
        "La ventana no se cerrará",
        "Copia esta salida completa"
    )

    $noiseHits = @()

    foreach ($pat in $noisePatterns) {
        if ($manualRaw -like "*$pat*") {
            $noiseHits += $pat
        }
    }

    if ($noiseHits.Count -gt 0) {
        return New-BridgeResult -Status "BLOCK" -Reason "MANUAL_CHAT_NOISE_DETECTED" -Data @{ patterns = $noiseHits }
    }

    return New-BridgeResult -Status "PASS" -Reason "MANUAL_SOURCE_CURRENT_VALID" -Data @{
        manual_path = $manualRel
        manifest_path = $manifestRel
        manual_hash_sha256 = $manualHash
        manual_status = $manifest.manual_status
        manual_scope = $manifest.manual_scope
        source_type = $manifest.source_type
        approved_for_bridge = $manifest.approved_for_bridge
        valid_fail_closed_terms_allowed = $true
    }
}
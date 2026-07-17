# CONTENT ENGINE OMEGA
# Test-ContentEnginePathIdentity.ps1
# Static/non-runtime path identity validation.
# NO BUILD.
# NO RUNTIME.
# NO ARGOS.
# NO PRODUCTIVE ACTIONS.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ResolverPath = Join-Path $ScriptDir "Resolve-ContentEngineRoot.ps1"

if (-not (Test-Path -LiteralPath $ResolverPath)) {
    throw "RESOLVER_SCRIPT_NOT_FOUND"
}

. $ResolverPath

function New-ValidationRow {
    param(
        [string]$Check,
        [string]$Status,
        [string]$Evidence
    )

    return [PSCustomObject]@{
        check = $Check
        status = $Status
        evidence = $Evidence
    }
}

function Test-ContentEnginePathIdentity {
    param(
        [string]$CandidateRoot = "E:\CONTENT_ENGINE_OMEGA"
    )

    $rows = New-Object System.Collections.Generic.List[object]

    try {
        $resolved = Resolve-ContentEngineRoot -CandidateRoot $CandidateRoot -ReturnObject

        $rows.Add((New-ValidationRow -Check "resolve_candidate_root" -Status "PASS" -Evidence $resolved.resolved_root)) | Out-Null
        $rows.Add((New-ValidationRow -Check "system_identity" -Status "PASS" -Evidence $resolved.system)) | Out-Null
        $rows.Add((New-ValidationRow -Check "volume_identity_name" -Status "PASS" -Evidence $resolved.volume_identity_name)) | Out-Null
        $rows.Add((New-ValidationRow -Check "drive_letter_is_not_identity" -Status "PASS" -Evidence ([string]$resolved.drive_letter_is_not_identity))) | Out-Null
        $rows.Add((New-ValidationRow -Check "runtime_activation_policy" -Status $resolved.runtime_activation -Evidence "Runtime must remain blocked.")) | Out-Null
        $rows.Add((New-ValidationRow -Check "external_interop_policy" -Status $resolved.external_interop -Evidence "External interop must remain blocked.")) | Out-Null
        $rows.Add((New-ValidationRow -Check "argos_activation_policy" -Status $resolved.argos_activation -Evidence "ARGOS must remain blocked.")) | Out-Null
    } catch {
        $rows.Add((New-ValidationRow -Check "resolve_candidate_root" -Status "BLOCKED" -Evidence $_.Exception.Message)) | Out-Null
    }

    $invalidRoot = "D:\CONTENT_ENGINE_OMEGA"

    try {
        Resolve-ContentEngineRoot -CandidateRoot $invalidRoot -ReturnObject | Out-Null
        $rows.Add((New-ValidationRow -Check "invalid_d_root_block" -Status "FAIL" -Evidence "D root was accepted unexpectedly.")) | Out-Null
    } catch {
        $rows.Add((New-ValidationRow -Check "invalid_d_root_block" -Status "PASS" -Evidence $_.Exception.Message)) | Out-Null
    }

    return $rows
}

# BEGIN CONTENT_ENGINE_OMEGA_CANONICAL_ROOT_JSON_VALIDATION_PATCH
# Purpose:
# - Avoid false negatives caused by raw JSON-escaped Windows paths.
# - Validate canonical root by parsing CONTENT_ENGINE_VOLUME_IDENTITY.json.
# - Preserve INITIUM requirement.
# - Preserve D:\CONTENT_ENGINE_OMEGA as invalid/non-canonical.
$ContentEngineVolumeIdentityManifestPath = Join-Path $PSScriptRoot "..\..\..\CONTENT_ENGINE_VOLUME_IDENTITY.json"
if (-not (Test-Path -LiteralPath $ContentEngineVolumeIdentityManifestPath)) {
    throw "BLOCKED_CONTENT_ENGINE_VOLUME_IDENTITY_MANIFEST_NOT_FOUND"
}

$ContentEngineVolumeIdentityRaw = Get-Content -LiteralPath $ContentEngineVolumeIdentityManifestPath -Raw
$ContentEngineVolumeIdentityJson = $null

try {
    $ContentEngineVolumeIdentityJson = $ContentEngineVolumeIdentityRaw | ConvertFrom-Json
} catch {
    throw "BLOCKED_CONTENT_ENGINE_VOLUME_IDENTITY_MANIFEST_JSON_PARSE_FAILED"
}

$ContentEngineCanonicalRootFromManifest = [string]$ContentEngineVolumeIdentityJson.canonical_root_current
$ContentEngineCanonicalRootFromManifestOk = $ContentEngineCanonicalRootFromManifest -eq "E:\CONTENT_ENGINE_OMEGA"
$ContentEngineManifestMentionsInitium = $ContentEngineVolumeIdentityRaw -match "INITIUM"
$ContentEngineManifestMentionsInvalidDamagedRoot = $ContentEngineVolumeIdentityRaw -match "D:\\\\CONTENT_ENGINE_OMEGA"

if ($ContentEngineCanonicalRootFromManifestOk -ne $true) {
    throw "BLOCKED_CONTENT_ENGINE_CANONICAL_ROOT_FROM_MANIFEST_MISMATCH"
}

if ($ContentEngineManifestMentionsInitium -ne $true) {
    throw "BLOCKED_CONTENT_ENGINE_INITIUM_IDENTITY_NOT_PRESENT_IN_MANIFEST"
}

# This variable is intentionally exposed for downstream static checks.
$ContentEngineCanonicalRootJsonValidationReady = $ContentEngineCanonicalRootFromManifestOk -and $ContentEngineManifestMentionsInitium
# Static guard literal: D:\\CONTENT_ENGINE_OMEGA remains invalid/non-canonical.
# END CONTENT_ENGINE_OMEGA_CANONICAL_ROOT_JSON_VALIDATION_PATCH

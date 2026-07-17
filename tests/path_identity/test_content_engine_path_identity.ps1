# CONTENT ENGINE OMEGA
# test_content_engine_path_identity.ps1
# Static path identity guard checks.
# NO BUILD.
# NO RUNTIME.
# NO ARGOS.
# NO PRODUCTIVE ACTIONS.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

$ManifestPath = Join-Path $RepoRoot "CONTENT_ENGINE_VOLUME_IDENTITY.json"
$ResolverPath = Join-Path $RepoRoot "04_SCRIPTS\powershell\path_identity\Resolve-ContentEngineRoot.ps1"
$ValidatorPath = Join-Path $RepoRoot "04_SCRIPTS\powershell\path_identity\Test-ContentEnginePathIdentity.ps1"
$PolicyPath = Join-Path $RepoRoot "00_SYSTEM\docs\path_identity\CONTENT_ENGINE_CANONICAL_ROOT_POLICY.md"

$Failures = New-Object System.Collections.Generic.List[string]

if (-not (Test-Path -LiteralPath $ManifestPath)) {
    $Failures.Add("MISSING_CONTENT_ENGINE_VOLUME_IDENTITY_JSON") | Out-Null
}

if (-not (Test-Path -LiteralPath $ResolverPath)) {
    $Failures.Add("MISSING_RESOLVE_CONTENT_ENGINE_ROOT") | Out-Null
}

if (-not (Test-Path -LiteralPath $ValidatorPath)) {
    $Failures.Add("MISSING_TEST_CONTENT_ENGINE_PATH_IDENTITY") | Out-Null
}

if (-not (Test-Path -LiteralPath $PolicyPath)) {
    $Failures.Add("MISSING_CANONICAL_ROOT_POLICY") | Out-Null
}

if (Test-Path -LiteralPath $ManifestPath) {
    $manifest = (Get-Content -LiteralPath $ManifestPath -Raw) | ConvertFrom-Json

    if ($manifest.system -ne "CONTENT_ENGINE_OMEGA") {
        $Failures.Add("SYSTEM_IDENTITY_MISMATCH") | Out-Null
    }

    if ($manifest.volume_identity_name -ne "INITIUM") {
        $Failures.Add("VOLUME_IDENTITY_NAME_MISMATCH") | Out-Null
    }

    if ($manifest.drive_letter_is_not_identity -ne $true) {
        $Failures.Add("DRIVE_LETTER_IDENTITY_POLICY_NOT_TRUE") | Out-Null
    }

    if (-not (@($manifest.invalid_canonical_roots) -contains "D:\CONTENT_ENGINE_OMEGA")) {
        $Failures.Add("D_BACKSLASH_ROOT_NOT_BLOCKED") | Out-Null
    }

    if (-not (@($manifest.invalid_canonical_roots) -contains "D:/CONTENT_ENGINE_OMEGA")) {
        $Failures.Add("D_SLASH_ROOT_NOT_BLOCKED") | Out-Null
    }

    if ($manifest.activation_policy.runtime_activation -ne "BLOCKED") {
        $Failures.Add("RUNTIME_NOT_BLOCKED") | Out-Null
    }

    if ($manifest.activation_policy.argos_activation -ne "BLOCKED") {
        $Failures.Add("ARGOS_NOT_BLOCKED") | Out-Null
    }

    if ($manifest.activation_policy.external_interop -ne "BLOCKED") {
        $Failures.Add("EXTERNAL_INTEROP_NOT_BLOCKED") | Out-Null
    }

    if ($manifest.activation_policy.productive_actions -ne "BLOCKED") {
        $Failures.Add("PRODUCTIVE_ACTIONS_NOT_BLOCKED") | Out-Null
    }
}

if ($Failures.Count -gt 0) {
    [PSCustomObject]@{
        status = "FAIL_CONTENT_ENGINE_PATH_IDENTITY_STATIC_CHECK"
        failures = @($Failures)
        build_executed = $false
        runtime_executed = $false
        argos_activated = $false
        productive_actions_executed = $false
    } | ConvertTo-Json -Depth 10

    exit 1
}

[PSCustomObject]@{
    status = "PASS_CONTENT_ENGINE_PATH_IDENTITY_STATIC_CHECK"
    checked_manifest = $ManifestPath
    checked_resolver = $ResolverPath
    checked_validator = $ValidatorPath
    checked_policy = $PolicyPath
    build_executed = $false
    runtime_executed = $false
    argos_activated = $false
    productive_actions_executed = $false
} | ConvertTo-Json -Depth 10
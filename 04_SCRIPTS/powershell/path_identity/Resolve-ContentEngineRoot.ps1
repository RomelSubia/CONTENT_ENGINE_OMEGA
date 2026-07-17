# CONTENT ENGINE OMEGA
# Resolve-ContentEngineRoot.ps1
# Safe canonical root resolver.
# NO RUNTIME ACTIVATION.
# NO ARGOS ACTIVATION.
# NO EXTERNAL INTEROPERABILITY.
# NO PRODUCTIVE ACTIONS.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Normalize-ContentEnginePath {
    param([string]$PathValue)

    if ($null -eq $PathValue) {
        return ""
    }

    return ([string]$PathValue).Trim().Replace("/", "\").TrimEnd("\")
}

function Read-ContentEngineVolumeIdentity {
    param([string]$ManifestPath)

    if (-not (Test-Path -LiteralPath $ManifestPath)) {
        throw "CONTENT_ENGINE_VOLUME_IDENTITY_MANIFEST_NOT_FOUND"
    }

    $raw = [System.IO.File]::ReadAllText($ManifestPath)
    return ($raw | ConvertFrom-Json)
}

function Test-ForbiddenContentEngineRoot {
    param(
        [string]$ResolvedRoot,
        [object]$Identity
    )

    $normalizedRoot = Normalize-ContentEnginePath $ResolvedRoot

    foreach ($badRoot in $Identity.invalid_canonical_roots) {
        $normalizedBad = Normalize-ContentEnginePath ([string]$badRoot)

        if ($normalizedRoot.ToLowerInvariant() -eq $normalizedBad.ToLowerInvariant()) {
            throw "CONTENT_ENGINE_ROOT_FORBIDDEN_INVALID_CANONICAL_ROOT"
        }
    }

    foreach ($badPart in $Identity.forbidden_resolved_root_contains) {
        $part = Normalize-ContentEnginePath ([string]$badPart)

        if ($normalizedRoot.ToLowerInvariant().Contains($part.ToLowerInvariant())) {
            throw "CONTENT_ENGINE_ROOT_FORBIDDEN_ARGOS_PATH_COLLISION"
        }
    }

    return $true
}

function Resolve-ContentEngineRoot {
    param(
        [string]$CandidateRoot = "E:\CONTENT_ENGINE_OMEGA",
        [switch]$ReturnObject
    )

    $candidate = Normalize-ContentEnginePath $CandidateRoot

    if ([string]::IsNullOrWhiteSpace($candidate)) {
        throw "CONTENT_ENGINE_ROOT_CANDIDATE_EMPTY"
    }

    if (-not (Test-Path -LiteralPath $candidate)) {
        throw "CONTENT_ENGINE_ROOT_CANDIDATE_NOT_FOUND"
    }

    $manifestPath = Join-Path $candidate "CONTENT_ENGINE_VOLUME_IDENTITY.json"
    $identity = Read-ContentEngineVolumeIdentity -ManifestPath $manifestPath

    if ($identity.system -ne "CONTENT_ENGINE_OMEGA") {
        throw "CONTENT_ENGINE_VOLUME_IDENTITY_SYSTEM_MISMATCH"
    }

    if ($identity.volume_identity_name -ne "INITIUM") {
        throw "CONTENT_ENGINE_VOLUME_IDENTITY_NAME_MISMATCH"
    }

    if ($identity.drive_letter_is_not_identity -ne $true) {
        throw "CONTENT_ENGINE_DRIVE_LETTER_POLICY_NOT_ENFORCED"
    }

    Test-ForbiddenContentEngineRoot -ResolvedRoot $candidate -Identity $identity | Out-Null

    $canonical = Normalize-ContentEnginePath ([string]$identity.canonical_root_current)

    if ($candidate.ToLowerInvariant() -ne $canonical.ToLowerInvariant()) {
        throw "CONTENT_ENGINE_ROOT_CANDIDATE_NOT_CANONICAL"
    }

    $gitDir = Join-Path $candidate ".git"
    if (-not (Test-Path -LiteralPath $gitDir)) {
        throw "CONTENT_ENGINE_ROOT_NOT_A_GIT_REPOSITORY"
    }

    $branch = ([string](& git -C $candidate branch --show-current 2>$null)).Trim()
    if ($branch -ne $identity.expected_git.branch) {
        throw "CONTENT_ENGINE_ROOT_GIT_BRANCH_MISMATCH"
    }

    $headShort = ([string](& git -C $candidate rev-parse --short HEAD 2>$null)).Trim()
    if (-not $headShort.StartsWith([string]$identity.expected_git.head_family)) {
        throw "CONTENT_ENGINE_ROOT_GIT_HEAD_FAMILY_MISMATCH"
    }

    $upstream = ([string](& git -C $candidate rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>$null)).Trim()
    if ($upstream -ne $identity.expected_git.upstream) {
        throw "CONTENT_ENGINE_ROOT_GIT_UPSTREAM_MISMATCH"
    }

    $result = [PSCustomObject]@{
        resolved_root = $candidate
        system = $identity.system
        volume_identity_name = $identity.volume_identity_name
        canonical_root_current = $canonical
        drive_letter_is_not_identity = [bool]$identity.drive_letter_is_not_identity
        fail_closed = [bool]$identity.fail_closed
        runtime_activation = $identity.activation_policy.runtime_activation
        external_interop = $identity.activation_policy.external_interop
        productive_actions = $identity.activation_policy.productive_actions
        argos_activation = $identity.activation_policy.argos_activation
        credentials_access = $identity.activation_policy.credentials_access
        branch = $branch
        head_short = $headShort
        upstream = $upstream
        status = "PASS_CONTENT_ENGINE_ROOT_RESOLVED_BY_INITIUM_IDENTITY"
    }

    if ($ReturnObject) {
        return $result
    }

    return $candidate
}
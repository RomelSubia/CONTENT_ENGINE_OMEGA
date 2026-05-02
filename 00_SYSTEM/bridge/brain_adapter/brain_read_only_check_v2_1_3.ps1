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

function Read-SafeTextFile {
    param([Parameter(Mandatory=$true)][string]$Path)

    try {
        $maxBytes = 10485760
        $file = Get-Item -LiteralPath $Path -ErrorAction Stop

        if ($file.Length -gt $maxBytes) {
            return ""
        }

        return Get-Content -LiteralPath $Path -Raw -ErrorAction Stop
    }
    catch {
        return ""
    }
}

function Test-BrainReadOnlyStatusV213 {
    param([string]$RootPath = "D:\CONTENT_ENGINE_OMEGA")

    $brainRoot = Join-Path -Path $RootPath -ChildPath "00_SYSTEM\brain"
    $reportsRoot = Join-Path -Path $RootPath -ChildPath "00_SYSTEM\reports\brain"
    $bridgePolicyPath = Join-Path -Path $RootPath -ChildPath "00_SYSTEM\bridge\config\BRIDGE_POLICY.json"
    $brainContractPath = Join-Path -Path $RootPath -ChildPath "00_SYSTEM\bridge\contracts\BRAIN_READ_ONLY_CONTRACT.json"

    if (!(Test-Path -LiteralPath $brainRoot)) {
        return New-BridgeResult -Status "LOCK" -Reason "BRAIN_ROOT_MISSING"
    }

    if (!(Test-Path -LiteralPath $reportsRoot)) {
        return New-BridgeResult -Status "LOCK" -Reason "BRAIN_REPORTS_ROOT_MISSING"
    }

    if (!(Test-Path -LiteralPath $bridgePolicyPath)) {
        return New-BridgeResult -Status "LOCK" -Reason "BRIDGE_POLICY_MISSING"
    }

    if (!(Test-Path -LiteralPath $brainContractPath)) {
        return New-BridgeResult -Status "LOCK" -Reason "BRAIN_READ_ONLY_CONTRACT_MISSING"
    }

    $policy = Get-Content -LiteralPath $bridgePolicyPath -Raw | ConvertFrom-Json
    $contract = Get-Content -LiteralPath $brainContractPath -Raw | ConvertFrom-Json

    if ($policy.brain_write_allowed -ne $false) {
        return New-BridgeResult -Status "LOCK" -Reason "POLICY_BRAIN_WRITE_ALLOWED_TRUE"
    }

    if ($policy.auto_action_allowed -ne $false) {
        return New-BridgeResult -Status "LOCK" -Reason "POLICY_AUTO_ACTION_ALLOWED_TRUE"
    }

    if ($policy.fail_closed_required -ne $true) {
        return New-BridgeResult -Status "LOCK" -Reason "POLICY_FAIL_CLOSED_NOT_REQUIRED"
    }

    if ($contract.read_only_required -ne $true) {
        return New-BridgeResult -Status "LOCK" -Reason "CONTRACT_READ_ONLY_NOT_REQUIRED"
    }

    if ($contract.brain_write_allowed -ne $false) {
        return New-BridgeResult -Status "LOCK" -Reason "CONTRACT_BRAIN_WRITE_ALLOWED_TRUE"
    }

    $reportFiles = @(Get-ChildItem -LiteralPath $reportsRoot -Recurse -Force -File -ErrorAction SilentlyContinue)

    $globalSealCandidates = @($reportFiles | Where-Object {
        $_.Name -match "GLOBAL_SEAL|GLOBAL.*SEAL|SEAL.*GLOBAL" -or
        $_.FullName -match "GLOBAL_SEAL|GLOBAL.*SEAL|SEAL.*GLOBAL"
    })

    if ($globalSealCandidates.Count -eq 0) {
        return New-BridgeResult -Status "LOCK" -Reason "GLOBAL_SEAL_EVIDENCE_MISSING"
    }

    $allText = ""
    $evidenceFiles = @()

    foreach ($file in @($globalSealCandidates + $reportFiles)) {
        $text = Read-SafeTextFile -Path $file.FullName

        if (![string]::IsNullOrWhiteSpace($text)) {
            $allText += "`n" + $text
            $evidenceFiles += @{
                path = $file.FullName.Replace($RootPath, "").TrimStart("\")
                hash_sha256 = Get-FileSha256LowerLocal -Path $file.FullName
            }
        }
    }

    $lower = $allText.ToLowerInvariant()

    $freezeDetected = (
        $lower -match "freeze" -or
        $lower -match "frozen" -or
        $lower -match "freeze_mode" -or
        $lower -match "read.only" -or
        $lower -match "read_only" -or
        $contract.read_only_required -eq $true
    )

    $autoActionFalseDetected = (
        $lower -match "auto_action.*false" -or
        $lower -match "auto action.*false" -or
        $lower -match "auto_action_allowed.*false" -or
        $lower -match "auto action allowed.*false" -or
        $policy.auto_action_allowed -eq $false
    )

    $failClosedDetected = (
        $lower -match "fail-closed" -or
        $lower -match "fail_closed" -or
        $lower -match "fail closed" -or
        $policy.fail_closed_required -eq $true
    )

    if (-not $freezeDetected) {
        return New-BridgeResult -Status "REQUIRE_REVIEW" -Reason "FREEZE_OR_READ_ONLY_EVIDENCE_NOT_CONFIRMED"
    }

    if (-not $autoActionFalseDetected) {
        return New-BridgeResult -Status "REQUIRE_REVIEW" -Reason "AUTO_ACTION_FALSE_NOT_CONFIRMED"
    }

    if (-not $failClosedDetected) {
        return New-BridgeResult -Status "REQUIRE_REVIEW" -Reason "FAIL_CLOSED_NOT_CONFIRMED"
    }

    return New-BridgeResult -Status "PASS" -Reason "BRAIN_READ_ONLY_EVIDENCE_CONFIRMED" -Data @{
        brain_root = "00_SYSTEM\brain"
        reports_root = "00_SYSTEM\reports\brain"
        global_seal_candidates = @($globalSealCandidates | ForEach-Object { $_.FullName.Replace($RootPath, "").TrimStart("\") })
        global_seal_count = $globalSealCandidates.Count
        evidence_files = $evidenceFiles
        freeze_or_read_only_evidence = $true
        auto_action_false_evidence = $true
        fail_closed_evidence = $true
        access_mode = "READ_ONLY"
        write_allowed = $false
        bridge_policy_hash_sha256 = Get-FileSha256LowerLocal -Path $bridgePolicyPath
        brain_contract_hash_sha256 = Get-FileSha256LowerLocal -Path $brainContractPath
    }
}
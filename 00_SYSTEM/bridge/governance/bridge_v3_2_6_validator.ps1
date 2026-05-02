$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\rule_extractor\manual_rule_extractor_v3_2_6.ps1"
. "00_SYSTEM\bridge\conflict_detector\manual_brain_conflict_detector_v3_2_6.ps1"

function Get-FileSha256LowerValidatorV326 {
    param([string]$Path)

    if (!(Test-Path -LiteralPath $Path)) { throw "Missing file for hash: $Path" }

    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-FalsePositiveGuardV326 {
    $safeTerms=@(
        "[FAIL CLOSED]","FAIL-CLOSED","FAIL_CLOSED","BLOCK","LOCK","PASS",
        "CURRENT_VALID","READ_ONLY","GLOBAL_SEAL","NO_CAPA_9","AUTO_ACTION_FALSE"
    )

    $testText=($safeTerms -join "`n")
    $scan=Test-ManualContaminationV326 -ManualText $testText

    if ($scan.status -ne "PASS") {
        return @{status="LOCK"; reason="FALSE_POSITIVE_GUARD_FAILED"; scan=$scan}
    }

    return @{status="PASS"; reason="FALSE_POSITIVE_GUARD_PASS"; safe_terms=$safeTerms}
}

function Test-AntiRegressionV326 {
    param([string]$RootPath,[hashtable]$InitialHashes)

    $paths=@{
        manual_current_hash=Join-Path $RootPath "00_SYSTEM\manual\current\MANUAL_MASTER_CURRENT.md"
        manual_manifest_hash=Join-Path $RootPath "00_SYSTEM\manual\manifest\MANUAL_SOURCE_MANIFEST.json"
        brain_readonly_v213_hash=Join-Path $RootPath "00_SYSTEM\bridge\reports\BRIDGE_BRAIN_READ_ONLY_REPORT_V2_1_3.json"
        source_resolver_v213_hash=Join-Path $RootPath "00_SYSTEM\bridge\reports\BRIDGE_SOURCE_RESOLVER_REPORT_V2_1_3.json"
    }

    $mismatches=@()

    foreach ($k in $paths.Keys) {
        $real=Get-FileSha256LowerValidatorV326 -Path $paths[$k]

        if ($InitialHashes[$k] -ne $real) {
            $mismatches += @{key=$k; expected=$InitialHashes[$k]; actual=$real}
        }
    }

    if ($mismatches.Count -gt 0) {
        return @{status="LOCK"; reason="REGRESSION_OR_NO_TOUCH_VIOLATION"; mismatches=$mismatches}
    }

    return @{status="PASS"; reason="ANTI_REGRESSION_PASS"; checked=$paths.Keys}
}

function Test-BridgeV326 {
    param([string]$RootPath="D:\CONTENT_ENGINE_OMEGA",[hashtable]$InitialHashes=@{})

    $dryRun=$true

    if ($dryRun -ne $true) {
        return @{status="LOCK"; reason="DRY_RUN_FALSE"}
    }

    $manualPath=Join-Path $RootPath "00_SYSTEM\manual\current\MANUAL_MASTER_CURRENT.md"
    $manualText=Get-Content -LiteralPath $manualPath -Raw

    $manualIntegrity=Test-ManualIntegrityV326 -RootPath $RootPath
    $contamination=Test-ManualContaminationV326 -ManualText $manualText
    $coverage=Measure-ManualCoverageV326 -ManualText $manualText
    $registry=Build-ManualRulesRegistryV326 -RootPath $RootPath
    $conflicts=Find-ManualBrainConflictsV326 -RuleRegistry $registry -RootPath $RootPath
    $falsePositive=Test-FalsePositiveGuardV326
    $antiRegression=Test-AntiRegressionV326 -RootPath $RootPath -InitialHashes $InitialHashes
    $riskValues=@()

    foreach ($rule in @($registry.rules)) {
        $score=0

        try {
            if ($null -ne $rule -and $rule -is [System.Collections.IDictionary] -and $rule.Contains("risk_score")) {
                $score=[int]$rule["risk_score"]
            }
            elseif ($null -ne $rule -and $rule.PSObject.Properties.Name -contains "risk_score") {
                $score=[int]$rule.risk_score
            }
            else {
                $score=0
            }
        }
        catch {
            $score=0
        }

        $riskValues += $score
    }

    $maxRisk=0
    $criticalRules=0
    $highRules=0

    if ($riskValues.Count -gt 0) {
        $maxRisk=($riskValues | Measure-Object -Maximum).Maximum
        $criticalRules=@($riskValues | Where-Object { $_ -ge 81 }).Count
        $highRules=@($riskValues | Where-Object { $_ -ge 61 -and $_ -lt 81 }).Count
    }

    $riskReport=@{
        status="PASS"
        reason="RISK_SCORING_GENERATED"
        rules_count=$registry.rules_count
        max_rule_risk=$maxRisk
        critical_rules=$criticalRules
        high_rules=$highRules
        risk_score_reader="ORDERED_DICTIONARY_SAFE"
    }

    $blockingStates=@(
        $manualIntegrity.status,
        $contamination.status,
        $coverage.status,
        $registry.status,
        $conflicts.status,
        $falsePositive.status,
        $antiRegression.status
    )

    if ($blockingStates -contains "LOCK") {
        $finalStatus="LOCK"
        $finalReason="LOCK_STATE_DETECTED"
    } elseif ($blockingStates -contains "BLOCK") {
        $finalStatus="BLOCK"
        $finalReason="BLOCK_STATE_DETECTED"
    } elseif ($blockingStates -contains "REQUIRE_REVIEW") {
        $finalStatus="REQUIRE_REVIEW"
        $finalReason="REQUIRE_REVIEW_STATE_DETECTED"
    } elseif ($blockingStates -contains "PASS_WITH_WARNINGS" -or $conflicts.warnings_count -gt 0) {
        $finalStatus="PASS_WITH_WARNINGS"
        $finalReason="PASS_WITH_WARNINGS_STATE"
    } else {
        $finalStatus="PASS"
        $finalReason="BRIDGE_V3_2_6_VALID"
    }

    return @{
        status=$finalStatus
        reason=$finalReason
        dry_run=$dryRun
        manual_integrity=$manualIntegrity
        contamination=$contamination
        coverage=$coverage
        rule_registry=$registry
        conflict_report=$conflicts
        risk_scoring=$riskReport
        false_positive_guard=$falsePositive
        anti_regression=$antiRegression
        final_decision=@{
            status=$finalStatus
            reason=$finalReason
            commit_allowed=($finalStatus -eq "PASS" -or $finalStatus -eq "PASS_WITH_WARNINGS")
        }
    }
}
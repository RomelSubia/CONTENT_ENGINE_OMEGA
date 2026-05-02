$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\governance\bridge_v3_3_validator.ps1"

$Root = "D:\CONTENT_ENGINE_OMEGA"

function Assert-Test {
    param(
        [string]$Name,
        [bool]$Condition,
        [string]$Details = ""
    )

    if (-not $Condition) {
        throw "TEST_FAILED: $Name :: $Details"
    }

    Write-Host "[OK] $Name" -ForegroundColor Green
}

$InitialHashes = @{
    manual_current = (Get-FileHash -LiteralPath "$Root\00_SYSTEM\manual\current\MANUAL_MASTER_CURRENT.md" -Algorithm SHA256).Hash.ToLowerInvariant()
    manual_manifest = (Get-FileHash -LiteralPath "$Root\00_SYSTEM\manual\manifest\MANUAL_SOURCE_MANIFEST.json" -Algorithm SHA256).Hash.ToLowerInvariant()
    rules_registry_v326 = (Get-FileHash -LiteralPath "$Root\00_SYSTEM\bridge\reports\MANUAL_RULES_REGISTRY_V3_2_6.json" -Algorithm SHA256).Hash.ToLowerInvariant()
    conflict_report_v326 = (Get-FileHash -LiteralPath "$Root\00_SYSTEM\bridge\reports\MANUAL_BRAIN_CONFLICT_REPORT_V3_2_6.json" -Algorithm SHA256).Hash.ToLowerInvariant()
    risk_report_v326 = (Get-FileHash -LiteralPath "$Root\00_SYSTEM\bridge\reports\RISK_SCORING_REPORT_V3_2_6.json" -Algorithm SHA256).Hash.ToLowerInvariant()
    warning_gate_v326 = (Get-FileHash -LiteralPath "$Root\00_SYSTEM\bridge\reports\WARNING_ACCEPTANCE_GATE_REPORT_V3_2_6.json" -Algorithm SHA256).Hash.ToLowerInvariant()
    readiness_map_v326 = (Get-FileHash -LiteralPath "$Root\00_SYSTEM\bridge\reports\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_V3_2_6.json" -Algorithm SHA256).Hash.ToLowerInvariant()
    brain_readonly_v213 = (Get-FileHash -LiteralPath "$Root\00_SYSTEM\bridge\reports\BRIDGE_BRAIN_READ_ONLY_REPORT_V2_1_3.json" -Algorithm SHA256).Hash.ToLowerInvariant()
    source_resolver_v213 = (Get-FileHash -LiteralPath "$Root\00_SYSTEM\bridge\reports\BRIDGE_SOURCE_RESOLVER_REPORT_V2_1_3.json" -Algorithm SHA256).Hash.ToLowerInvariant()
}

$result = Test-BridgeV33 -RootPath $Root -InitialHashes $InitialHashes

Assert-Test "T001 Load v3.2.6 registry" ($result.source_integrity.status -eq "PASS") $result.source_integrity.reason
Assert-Test "T002 Required reports present" ($result.source_integrity.source_ready_for_canonicalization -eq $true) ""
Assert-Test "T003 Build status allowed" ($result.status -eq "PASS" -or $result.status -eq "PASS_WITH_WARNINGS") $result.status
Assert-Test "T004 Source rules total = 54" ([int]$result.coverage_invariant.source_rules_total -eq 54) $result.coverage_invariant.source_rules_total
Assert-Test "T005 Canonical rules generated" ([int]$result.canonical_registry.canonical_rules_count -gt 0) $result.canonical_registry.canonical_rules_count
Assert-Test "T006 Source rule ids preserved" ([int]$result.coverage_invariant.source_rules_accounted_for -eq 54) $result.coverage_invariant.source_rules_accounted_for
Assert-Test "T007 Source hashes preserved" ([int]$result.coverage_invariant.source_rules_without_evidence -eq 0) $result.coverage_invariant.source_rules_without_evidence
Assert-Test "T008 Source rules lost = 0" ([int]$result.coverage_invariant.source_rules_lost -eq 0) $result.coverage_invariant.source_rules_lost
Assert-Test "T009 Dedup report generated" ($null -ne $result.canonical_deduplication.records) ""
Assert-Test "T010 No merge performed" ([int]$result.canonical_deduplication.merge_performed_count -eq 0) $result.canonical_deduplication.merge_performed_count
Assert-Test "T011 Dedup preserves source ids" ($result.canonical_deduplication.source_rule_ids_preserved -eq $true) ""
Assert-Test "T012 Dedup no source loss" ([int]$result.coverage_invariant.source_rules_lost -eq 0) ""
Assert-Test "T013 Semantic audit generated" ($null -ne $result.semantic_preservation_audit.records) ""
Assert-Test "T014 Semantic loss blocked count zero" ([int]$result.semantic_preservation_audit.semantic_loss_detected -eq 0) $result.semantic_preservation_audit.semantic_loss_detected
# T015 Conditional Brain Binding Contract v3.3.4
function Test-BrainTextT015 {
    param([Parameter(Mandatory=$false)][AllowNull()]$Text)

    if ($null -eq $Text) { return $false }

    $s = ([string]$Text).ToUpperInvariant()

    return (
        $s -match "BRAIN" -or
        $s -match "CEREBRO" -or
        $s -match "READ_ONLY" -or
        $s -match "READ-ONLY" -or
        $s -match "SOLO LECTURA" -or
        $s -match "RULE_BRAIN" -or
        $s -match "NO_BRAIN_WRITE" -or
        $s -match "REPORTS_BRAIN" -or
        $s -match "REPORTS/BRAIN"
    )
}

$sourceBrainCandidatesForT015 = @()

foreach ($sr in @($result.source_integrity.reports.rules.rules)) {
    $combinedT015 = (
        [string]$sr.rule_id + " " +
        [string]$sr.raw_excerpt + " " +
        [string]$sr.normalized_text + " " +
        [string]$sr.category + " " +
        [string]$sr.section_title
    )

    if (Test-BrainTextT015 -Text $combinedT015) {
        $sourceBrainCandidatesForT015 += $sr
    }
}

$brainPolicyMatchesT015 = @(
    $result.policy_binding.policy_binding_records |
        Where-Object {
            $_.domain -eq "BRAIN" -and
            ($_.policy_bindings -contains "POLICY_NO_BRAIN_WRITE")
        }
)

$brainPolicyAnyDomainT015 = @(
    $result.policy_binding.policy_binding_records |
        Where-Object {
            $_.policy_bindings -contains "POLICY_NO_BRAIN_WRITE"
        }
)

$T015Pass = (
    ($sourceBrainCandidatesForT015.Count -eq 0) -or
    ($brainPolicyMatchesT015.Count -ge 1)
)

Assert-Test "T015 Conditional Brain policy binding contract" $T015Pass "source_brain_candidates=$($sourceBrainCandidatesForT015.Count); brain_policy_domain_matches=$($brainPolicyMatchesT015.Count); brain_policy_any_domain=$($brainPolicyAnyDomainT015.Count)"
Assert-Test "T016 Manual policy binding exists when needed" (@($result.policy_binding.policy_binding_records | Where-Object { $_.domain -eq "MANUAL" -and ($_.policy_bindings -contains "POLICY_NO_MANUAL_WRITE") }).Count -ge 1) ""
Assert-Test "T017 reports/brain write disabled" ([int]$result.no_execution_permission_audit.reports_brain_write_allowed_rules -eq 0) ""
Assert-Test "T018 Evidence policy present" (@($result.policy_binding.policy_binding_records | Where-Object { $_.policy_bindings -contains "POLICY_EVIDENCE_REQUIRED" }).Count -ge 1) ""
Assert-Test "T019 Repo policy present" (@($result.policy_binding.policy_binding_records | Where-Object { $_.policy_bindings -contains "POLICY_REPO_SYNC_REQUIRED" }).Count -ge 1) ""
Assert-Test "T020 Production claim policy can exist" ($null -ne $result.policy_binding.policy_binding_records) ""
# T021 Conditional CAPA9 Binding Contract v3.3.5
function Test-Capa9TextT021 {
    param([Parameter(Mandatory=$false)][AllowNull()]$Text)

    if ($null -eq $Text) { return $false }

    $s = ([string]$Text).ToUpperInvariant()

    return (
        $s -match "CAPA\s*9" -or
        $s -match "CAPA9" -or
        $s -match "LAYER\s*9" -or
        $s -match "LAYER9" -or
        $s -match "NO_CAPA_9" -or
        $s -match "RULE_NO_CAPA_9" -or
        $s -match "POLICY_NO_CAPA_9" -or
        $s -match "CAPA_CONTROL"
    )
}

$sourceCapa9CandidatesForT021 = @()

foreach ($sr in @($result.source_integrity.reports.rules.rules)) {
    $combinedT021 = (
        [string]$sr.rule_id + " " +
        [string]$sr.raw_excerpt + " " +
        [string]$sr.normalized_text + " " +
        [string]$sr.category + " " +
        [string]$sr.section_title
    )

    if (Test-Capa9TextT021 -Text $combinedT021) {
        $sourceCapa9CandidatesForT021 += $sr
    }
}

$capa9PolicyMatchesT021 = @(
    $result.policy_binding.policy_binding_records |
        Where-Object {
            $_.domain -eq "CAPA_CONTROL" -and
            ($_.policy_bindings -contains "POLICY_NO_CAPA_9")
        }
)

$capa9PolicyAnyDomainT021 = @(
    $result.policy_binding.policy_binding_records |
        Where-Object {
            $_.policy_bindings -contains "POLICY_NO_CAPA_9"
        }
)

$T021Pass = (
    ($sourceCapa9CandidatesForT021.Count -eq 0) -or
    ($capa9PolicyMatchesT021.Count -ge 1)
)

Assert-Test "T021 Conditional CAPA9 policy binding contract" $T021Pass "source_capa9_candidates=$($sourceCapa9CandidatesForT021.Count); capa9_policy_domain_matches=$($capa9PolicyMatchesT021.Count); capa9_policy_any_domain=$($capa9PolicyAnyDomainT021.Count)"
Assert-Test "T022 External execution blocked by policy when present" (@($result.policy_binding.policy_binding_records | Where-Object { $_.policy_bindings -contains "POLICY_NO_EXTERNAL_EXECUTION" }).Count -ge 1) ""
Assert-Test "T023 Future gate required default" (@($result.rule_approval_matrix.records | Where-Object { $_.future_gate_required -ne $true }).Count -eq 0) ""
Assert-Test "T024 All execution permissions default false" ([int]$result.no_execution_permission_audit.execution_allowed_rules -eq 0) ""
Assert-Test "T025 execution_allowed true fails absent" ([int]$result.no_execution_permission_audit.execution_allowed_rules -eq 0) ""
Assert-Test "T026 brain_write_allowed true absent" ([int]$result.no_execution_permission_audit.brain_write_allowed_rules -eq 0) ""
Assert-Test "T027 reports_brain_write_allowed true absent" ([int]$result.no_execution_permission_audit.reports_brain_write_allowed_rules -eq 0) ""
Assert-Test "T028 manual_write_allowed true absent" ([int]$result.no_execution_permission_audit.manual_write_allowed_rules -eq 0) ""
Assert-Test "T029 Inherit all 5 warnings" ([int]$result.warning_inheritance.warnings_inherited_from_v3_2_6 -eq 5) $result.warning_inheritance.warnings_inherited_from_v3_2_6
Assert-Test "T030 Hidden warnings zero" ([int]$result.warning_inheritance.warnings_hidden -eq 0) $result.warning_inheritance.warnings_hidden
Assert-Test "T031 PASS_WITH_WARNINGS if warnings remain" ($result.status -eq "PASS_WITH_WARNINGS") $result.status
Assert-Test "T032 PASS clean not forced" ($result.final_decision.production_clean_pass -eq $false) ""
Assert-Test "T033 Approval matrix generated" ([int]$result.rule_approval_matrix.approval_records_count -eq [int]$result.canonical_registry.canonical_rules_count) ""
Assert-Test "T034 Policy enforcement matrix generated" ([int]$result.policy_enforcement_matrix.records_count -eq [int]$result.canonical_registry.canonical_rules_count) ""
Assert-Test "T035 Semantic preservation audit generated" ($result.semantic_preservation_audit.status -eq "PASS" -or $result.semantic_preservation_audit.status -eq "PASS_WITH_WARNINGS") $result.semantic_preservation_audit.status
Assert-Test "T036 Coverage invariant pass" ($result.coverage_invariant.status -eq "PASS") $result.coverage_invariant.status
Assert-Test "T037 No manual mutation" ($result.no_touch.status -eq "PASS") $result.no_touch.status
Assert-Test "T038 No brain mutation by design" ([int]$result.no_execution_permission_audit.brain_write_allowed_rules -eq 0) ""
Assert-Test "T039 No reports/brain mutation by design" ([int]$result.no_execution_permission_audit.reports_brain_write_allowed_rules -eq 0) ""
Assert-Test "T040 No CAPA 9 creation by validator" (!(Test-Path -LiteralPath "$Root\00_SYSTEM\brain\CAPA_9")) ""
Assert-Test "T041 No external execution permission" ([int]$result.no_execution_permission_audit.external_execution_allowed_rules -eq 0) ""
Assert-Test "T042 Policy binding records exist" ([int]$result.policy_binding.canonical_rules_count -eq [int]$result.canonical_registry.canonical_rules_count) ""
Assert-Test "T043 Generated canonical hashes exist" (@($result.canonical_registry.canonical_rules | Where-Object { [string]::IsNullOrWhiteSpace([string]$_.canonical_hash_sha256) }).Count -eq 0) ""
Assert-Test "T044 Runtime validator status allowed" ($result.status -eq "PASS_WITH_WARNINGS" -or $result.status -eq "PASS") $result.status
Assert-Test "T045 Commit allowed status" ($result.final_decision.commit_allowed -eq $true) ""
Assert-Test "T046 No review required" ([int]$result.coverage_invariant.source_rules_without_canonical_mapping -eq 0) ""
Assert-Test "T047 Commit allowed only PASS/PASS_WITH_WARNINGS" ($result.status -eq "PASS" -or $result.status -eq "PASS_WITH_WARNINGS") ""
Assert-Test "T048 No REQUIRE_REVIEW global" ($result.status -ne "REQUIRE_REVIEW") $result.status
Assert-Test "T049 No BLOCK global" ($result.status -ne "BLOCK") $result.status
Assert-Test "T050 No LOCK global" ($result.status -ne "LOCK") $result.status

Write-Host "[OK] BRIDGE V3.3 TEST HARNESS PASS" -ForegroundColor Green
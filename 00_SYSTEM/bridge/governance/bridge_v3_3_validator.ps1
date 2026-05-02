$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\canonical_registry\canonical_rule_registry_v3_3.ps1"
. "00_SYSTEM\bridge\policy_binding\policy_binding_engine_v3_3.ps1"

function Read-JsonFileV33 {
    param([Parameter(Mandatory=$true)][string]$Path)

    if (!(Test-Path -LiteralPath $Path)) {
        throw "JSON requerido no existe: $Path"
    }

    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Get-FileSha256LowerV33 {
    param([Parameter(Mandatory=$true)][string]$Path)

    if (!(Test-Path -LiteralPath $Path)) {
        throw "Archivo requerido no existe: $Path"
    }

    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-SourceIntegrityV33 {
    param([string]$RootPath = "D:\CONTENT_ENGINE_OMEGA")

    $paths = @{
        rules = "00_SYSTEM\bridge\reports\MANUAL_RULES_REGISTRY_V3_2_6.json"
        conflicts = "00_SYSTEM\bridge\reports\MANUAL_BRAIN_CONFLICT_REPORT_V3_2_6.json"
        risk = "00_SYSTEM\bridge\reports\RISK_SCORING_REPORT_V3_2_6.json"
        build = "00_SYSTEM\bridge\reports\BRIDGE_BUILD_READINESS_REPORT_V3_2_6.json"
        audit = "00_SYSTEM\bridge\reports\POST_BUILD_AUDIT_REPORT_V3_2_6.json"
        warning_gate = "00_SYSTEM\bridge\reports\WARNING_ACCEPTANCE_GATE_REPORT_V3_2_6.json"
        readiness_map = "00_SYSTEM\bridge\reports\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_V3_2_6.json"
    }

    foreach ($k in $paths.Keys) {
        if (!(Test-Path -LiteralPath (Join-Path $RootPath $paths[$k]))) {
            return @{ status = "BLOCK"; reason = "MISSING_SOURCE_ARTIFACT"; missing = $paths[$k] }
        }
    }

    $rules = Read-JsonFileV33 (Join-Path $RootPath $paths.rules)
    $conflicts = Read-JsonFileV33 (Join-Path $RootPath $paths.conflicts)
    $risk = Read-JsonFileV33 (Join-Path $RootPath $paths.risk)
    $build = Read-JsonFileV33 (Join-Path $RootPath $paths.build)
    $audit = Read-JsonFileV33 (Join-Path $RootPath $paths.audit)
    $warningGate = Read-JsonFileV33 (Join-Path $RootPath $paths.warning_gate)
    $readinessMap = Read-JsonFileV33 (Join-Path $RootPath $paths.readiness_map)

    $issues = @()

    if ([int]$build.rules_count -ne 54) { $issues += "rules_count_not_54" }
    if ([int]$build.conflicts_count -ne 0) { $issues += "conflicts_count_not_0" }
    if ([int]$build.warnings_count -ne 5) { $issues += "warnings_count_not_5" }
    if ([int]$build.review_required_count -ne 0) { $issues += "review_required_not_0" }
    if ($build.status -ne "PASS_WITH_WARNINGS") { $issues += "build_status_not_PASS_WITH_WARNINGS" }
    if ($audit.audit_status -ne "PASS_WITH_WARNINGS_AUDITED") { $issues += "audit_status_invalid" }
    if ($warningGate.gate_status -ne "WARNING_ACCEPTANCE_GATE_ACCEPTED") { $issues += "warning_gate_not_accepted" }
    if ($readinessMap.current_layer.status -ne "SEALED_AUDITED_WARNINGS_ACCEPTED") { $issues += "readiness_map_current_layer_invalid" }
    if ($readinessMap.next_layer.blueprint_allowed_next -ne $true) { $issues += "blueprint_not_allowed" }
    if ($readinessMap.next_layer.build_allowed_now -ne $false) { $issues += "unexpected_build_allowed" }
    if ([int]$risk.critical_rules -ne 0) { $issues += "critical_rules_not_0" }

    if ($issues.Count -gt 0) {
        return @{
            status = "BLOCK"
            reason = "SOURCE_INTEGRITY_FAILED"
            issues = $issues
        }
    }

    return @{
        status = "PASS"
        reason = "SOURCE_INTEGRITY_PASS"
        source_rules_total = [int]$build.rules_count
        warnings_inherited = [int]$build.warnings_count
        source_ready_for_canonicalization = $true
        reports = @{
            rules = $rules
            conflicts = $conflicts
            risk = $risk
            build = $build
            audit = $audit
            warning_gate = $warningGate
            readiness_map = $readinessMap
        }
    }
}

function Test-NoTouchV33 {
    param(
        [string]$RootPath,
        [hashtable]$InitialHashes
    )

    $paths = @{
        manual_current = "00_SYSTEM\manual\current\MANUAL_MASTER_CURRENT.md"
        manual_manifest = "00_SYSTEM\manual\manifest\MANUAL_SOURCE_MANIFEST.json"
        rules_registry_v326 = "00_SYSTEM\bridge\reports\MANUAL_RULES_REGISTRY_V3_2_6.json"
        conflict_report_v326 = "00_SYSTEM\bridge\reports\MANUAL_BRAIN_CONFLICT_REPORT_V3_2_6.json"
        risk_report_v326 = "00_SYSTEM\bridge\reports\RISK_SCORING_REPORT_V3_2_6.json"
        warning_gate_v326 = "00_SYSTEM\bridge\reports\WARNING_ACCEPTANCE_GATE_REPORT_V3_2_6.json"
        readiness_map_v326 = "00_SYSTEM\bridge\reports\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_V3_2_6.json"
        brain_readonly_v213 = "00_SYSTEM\bridge\reports\BRIDGE_BRAIN_READ_ONLY_REPORT_V2_1_3.json"
        source_resolver_v213 = "00_SYSTEM\bridge\reports\BRIDGE_SOURCE_RESOLVER_REPORT_V2_1_3.json"
    }

    $mismatches = @()

    foreach ($k in $paths.Keys) {
        $actual = Get-FileSha256LowerV33 -Path (Join-Path $RootPath $paths[$k])
        if ($InitialHashes[$k] -ne $actual) {
            $mismatches += @{
                key = $k
                expected = $InitialHashes[$k]
                actual = $actual
            }
        }
    }

    if ($mismatches.Count -gt 0) {
        return @{
            status = "LOCK"
            reason = "NO_TOUCH_VIOLATION"
            mismatches = $mismatches
        }
    }

    return @{
        status = "PASS"
        reason = "NO_TOUCH_PASS"
        checked = $paths.Keys
    }
}

function Test-BridgeV33 {
    param(
        [string]$RootPath = "D:\CONTENT_ENGINE_OMEGA",
        [hashtable]$InitialHashes = @{}
    )

    $dryRun = $true

    if ($dryRun -ne $true) {
        return @{ status = "LOCK"; reason = "DRY_RUN_FALSE" }
    }

    $sourceIntegrity = Test-SourceIntegrityV33 -RootPath $RootPath

    if ($sourceIntegrity.status -ne "PASS") {
        return @{
            status = $sourceIntegrity.status
            reason = $sourceIntegrity.reason
            source_integrity = $sourceIntegrity
        }
    }

    $ruleRegistry = $sourceIntegrity.reports.rules
    $conflictReport = $sourceIntegrity.reports.conflicts
    $warningGate = $sourceIntegrity.reports.warning_gate
    $readinessMap = $sourceIntegrity.reports.readiness_map

    $canonicalRegistry = Build-CanonicalRegistryV33 -RuleRegistry $ruleRegistry -ConflictReport $conflictReport -WarningGate $warningGate -ReadinessMap $readinessMap
    $deduplication = Build-CanonicalDeduplicationReportV33 -CanonicalRules $canonicalRegistry.canonical_rules
    $boundRules = Apply-PolicyBindingV33 -CanonicalRules $canonicalRegistry.canonical_rules

    $policyBinding = Build-PolicyBindingReportV33 -CanonicalRules $boundRules
    $approvalMatrix = Build-ApprovalMatrixV33 -CanonicalRules $boundRules
    $enforcementMatrix = Build-PolicyEnforcementMatrixV33 -CanonicalRules $boundRules
    $semanticAudit = Build-SemanticPreservationAuditV33 -CanonicalRules $boundRules
    $warningInheritance = Build-WarningInheritanceReportV33 -CanonicalRules $boundRules -ConflictReport $conflictReport
    $coverage = Build-CoverageInvariantReportV33 -RuleRegistry $ruleRegistry -CanonicalRules $boundRules
    $noExecution = Build-NoExecutionPermissionAuditV33 -CanonicalRules $boundRules
    $noTouch = if ($InitialHashes.Count -gt 0) {
        Test-NoTouchV33 -RootPath $RootPath -InitialHashes $InitialHashes
    } else {
        @{ status = "PASS"; reason = "NO_TOUCH_NOT_PROVIDED_FOR_UNIT_CONTEXT" }
    }

    $statuses = @(
        $sourceIntegrity.status,
        $canonicalRegistry.status,
        $deduplication.status,
        $policyBinding.status,
        $approvalMatrix.status,
        $enforcementMatrix.status,
        $semanticAudit.status,
        $warningInheritance.status,
        $coverage.status,
        $noExecution.status,
        $noTouch.status
    )

    $global = Get-GlobalBridgeStatusV33 -Statuses $statuses -WarningsRemaining ([int]$warningInheritance.warnings_remaining)

    return @{
        status = $global.status
        reason = $global.reason
        dry_run = $dryRun
        source_integrity = $sourceIntegrity
        canonical_registry = $canonicalRegistry
        canonical_deduplication = $deduplication
        policy_binding = $policyBinding
        rule_approval_matrix = $approvalMatrix
        policy_enforcement_matrix = $enforcementMatrix
        semantic_preservation_audit = $semanticAudit
        warning_inheritance = $warningInheritance
        coverage_invariant = $coverage
        no_execution_permission_audit = $noExecution
        no_touch = $noTouch
        final_decision = @{
            status = $global.status
            reason = $global.reason
            commit_allowed = ($global.status -eq "PASS" -or $global.status -eq "PASS_WITH_WARNINGS")
            production_clean_pass = ($global.status -eq "PASS")
            production_with_warnings = ($global.status -eq "PASS_WITH_WARNINGS")
        }
    }
}
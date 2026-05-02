$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Get-BridgePropV33 {
    param(
        [Parameter(Mandatory=$false)][AllowNull()]$Object,
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$false)]$Default = $null
    )

    if ($null -eq $Object) { return $Default }

    if ($Object -is [System.Collections.IDictionary]) {
        if ($Object.Contains($Name)) { return $Object[$Name] }
        return $Default
    }

    $prop = $Object.PSObject.Properties | Where-Object { $_.Name -eq $Name } | Select-Object -First 1

    if ($null -ne $prop) { return $prop.Value }

    return $Default
}

function Get-PolicyBindingsForCanonicalRuleV33 {
    param([Parameter(Mandatory=$true)]$CanonicalRule)

    $policies = @(
        "POLICY_TRACEABILITY_REQUIRED",
        "POLICY_FUTURE_GATE_REQUIRED",
        "POLICY_NO_AUTO_ACTION"
    )

    $text = (
        ([string]$CanonicalRule.canonical_text) + " " +
        ([string]$CanonicalRule.normalized_intent) + " " +
        ([string]$CanonicalRule.domain) + " " +
        ([string]$CanonicalRule.category) + " " +
        ([string]$CanonicalRule.enforcement) + " " +
        ([string]$CanonicalRule.modality)
    ).ToUpperInvariant()

    if ($CanonicalRule.domain -eq "REPORTS_BRAIN" -or $text -match "REPORTS_BRAIN|REPORTS/BRAIN|REPORTES.*CEREBRO|RULE_NO_REPORTS_BRAIN_WRITE") {
        $policies += "POLICY_NO_REPORTS_BRAIN_WRITE"
        $policies += "POLICY_NO_BRAIN_WRITE"
    }

    if ($CanonicalRule.domain -eq "BRAIN" -or $text -match "BRAIN|CEREBRO|RULE_BRAIN|READ_ONLY|READ-ONLY|SOLO LECTURA") {
        $policies += "POLICY_NO_BRAIN_WRITE"
    }

    if ($CanonicalRule.domain -eq "MANUAL" -or $text -match "MANUAL|RULE_MANUAL|MANIFEST|SOURCE") {
        $policies += "POLICY_NO_MANUAL_WRITE"
    }

    if ($CanonicalRule.domain -eq "CAPA_CONTROL" -or $text -match "CAPA_9|CAPA 9|LAYER 9|RULE_NO_CAPA_9") {
        $policies += "POLICY_NO_CAPA_9"
    }

    if ($CanonicalRule.domain -eq "EXTERNAL" -or $text -match "EXTERNAL|API|APIS|N8N|YOUTUBE|TIKTOK|INSTAGRAM|PUBLICAR|EMAIL|RULE_EXTERNAL") {
        $policies += "POLICY_NO_EXTERNAL_EXECUTION"
    }

    if ($CanonicalRule.domain -eq "EVIDENCE" -or $text -match "EVIDENCE|EVIDENCIA|HASH|MANIFEST|SEAL|VALIDACI|RULE_EVIDENCE") {
        $policies += "POLICY_EVIDENCE_REQUIRED"
    }

    if ($CanonicalRule.domain -eq "REPO" -or $text -match "GIT|COMMIT|PUSH|SYNC|REMOTO|REPO|RULE_REPO") {
        $policies += "POLICY_REPO_SYNC_REQUIRED"
    }

    if ($text -match "FAIL_CLOSED|FAIL-CLOSED|FAIL CLOSED|BLOCK|LOCK") {
        $policies += "POLICY_FAIL_CLOSED"
    }

    if ($text -match "PRODUCTION|PRODUCCI|SELLADO|SISTEMA TERMINADO|PRODUCTION_CLAIM") {
        $policies += "POLICY_PRODUCTION_CLAIM_REQUIRES_EVIDENCE"
    }

    if ($CanonicalRule.warning_inheritance.inherits_warning -eq $true) {
        $policies += "POLICY_WARNING_ACCEPTANCE_REQUIRED"
    }

    $policies += "POLICY_NO_SEMANTIC_LOSS"
    $policies += "POLICY_NO_UNAPPROVED_RULE_MERGE"

    return @($policies | Sort-Object -Unique)
}

function Get-PolicyPriorityResultV33 {
    param([Parameter(Mandatory=$true)]$CanonicalRule)

    $permissions = $CanonicalRule.permissions
    $policies = @($CanonicalRule.policy_bindings)

    if ($permissions.brain_write_allowed -eq $true -or $permissions.reports_brain_write_allowed -eq $true) {
        return "LOCK"
    }

    if ($permissions.execution_allowed -eq $true -or $permissions.external_execution_allowed -eq $true -or $permissions.manual_write_allowed -eq $true) {
        return "BLOCK"
    }

    if ($CanonicalRule.semantic_preservation_status -eq "SEMANTIC_LOSS_DETECTED") {
        return "BLOCK"
    }

    if ($CanonicalRule.semantic_preservation_status -eq "POTENTIAL_SEMANTIC_LOSS") {
        return "REQUIRE_REVIEW"
    }

    if ($CanonicalRule.warning_inheritance.inherits_warning -eq $true) {
        return "PASS_WITH_WARNINGS"
    }

    if ($policies.Count -eq 0) {
        return "REQUIRE_REVIEW"
    }

    return "PASS"
}

function Get-ApprovalStateV33 {
    param([Parameter(Mandatory=$true)]$CanonicalRule)

    $priority = [string]$CanonicalRule.policy_priority_result

    if ($priority -eq "LOCK") { return "LOCKED" }
    if ($priority -eq "BLOCK") { return "BLOCKED" }
    if ($priority -eq "REQUIRE_REVIEW") { return "REQUIRES_REVIEW" }
    if ($priority -eq "PASS_WITH_WARNINGS") { return "BOUND_WITH_WARNING" }

    if ($CanonicalRule.modality -eq "INFO") {
        return "INFO_ONLY"
    }

    if ($CanonicalRule.risk_score -ge 61) {
        return "APPROVED_FOR_GOVERNANCE"
    }

    return "APPROVED_FOR_PLANNING_ONLY"
}

function Apply-PolicyBindingV33 {
    param([Parameter(Mandatory=$true)][object[]]$CanonicalRules)

    $bound = @()

    foreach ($rule in @($CanonicalRules)) {
        $policies = Get-PolicyBindingsForCanonicalRuleV33 -CanonicalRule $rule

        $newRule = [ordered]@{}

        foreach ($p in $rule.Keys) {
            $newRule[$p] = $rule[$p]
        }

        $newRule["policy_bindings"] = @($policies)
        $newRule["policy_priority_result"] = "PENDING"
        $newRule["approval_state"] = "PENDING"

        $priority = Get-PolicyPriorityResultV33 -CanonicalRule $newRule
        $newRule["policy_priority_result"] = $priority
        $newRule["approval_state"] = Get-ApprovalStateV33 -CanonicalRule $newRule

        $bound += $newRule
    }

    return @($bound)
}

function Build-PolicyBindingReportV33 {
    param([Parameter(Mandatory=$true)][object[]]$CanonicalRules)

    $withoutBinding = @($CanonicalRules | Where-Object { @($_.policy_bindings).Count -eq 0 })
    $blocked = @($CanonicalRules | Where-Object { $_.policy_priority_result -eq "BLOCK" })
    $locked = @($CanonicalRules | Where-Object { $_.policy_priority_result -eq "LOCK" })
    $review = @($CanonicalRules | Where-Object { $_.policy_priority_result -eq "REQUIRE_REVIEW" })
    $warnings = @($CanonicalRules | Where-Object { $_.policy_priority_result -eq "PASS_WITH_WARNINGS" })

    $status = "PASS"
    $reason = "POLICY_BINDING_PASS"

    if ($locked.Count -gt 0) {
        $status = "LOCK"
        $reason = "LOCKED_POLICY_BINDING_DETECTED"
    }
    elseif ($blocked.Count -gt 0) {
        $status = "BLOCK"
        $reason = "BLOCKED_POLICY_BINDING_DETECTED"
    }
    elseif ($review.Count -gt 0 -or $withoutBinding.Count -gt 0) {
        $status = "REQUIRE_REVIEW"
        $reason = "POLICY_BINDING_REVIEW_REQUIRED"
    }
    elseif ($warnings.Count -gt 0) {
        $status = "PASS_WITH_WARNINGS"
        $reason = "POLICY_BINDING_PASS_WITH_WARNINGS"
    }

    return @{
        status = $status
        reason = $reason
        canonical_rules_count = $CanonicalRules.Count
        rules_without_policy_binding = $withoutBinding.Count
        locked_count = $locked.Count
        blocked_count = $blocked.Count
        review_required_count = $review.Count
        warning_count = $warnings.Count
        policy_binding_records = @($CanonicalRules | ForEach-Object {
            [ordered]@{
                canonical_rule_id = $_.canonical_rule_id
                source_rule_ids = $_.source_rule_ids
                domain = $_.domain
                category = $_.category
                policy_bindings = $_.policy_bindings
                policy_priority_result = $_.policy_priority_result
                approval_state = $_.approval_state
            }
        })
    }
}

function Build-ApprovalMatrixV33 {
    param([Parameter(Mandatory=$true)][object[]]$CanonicalRules)

    $records = @($CanonicalRules | ForEach-Object {
        [ordered]@{
            canonical_rule_id = $_.canonical_rule_id
            source_rule_ids = $_.source_rule_ids
            approval_state = $_.approval_state
            policy_priority_result = $_.policy_priority_result
            execution_allowed = $_.permissions.execution_allowed
            brain_write_allowed = $_.permissions.brain_write_allowed
            manual_write_allowed = $_.permissions.manual_write_allowed
            reports_brain_write_allowed = $_.permissions.reports_brain_write_allowed
            external_execution_allowed = $_.permissions.external_execution_allowed
            future_gate_required = $_.permissions.future_gate_required
        }
    })

    $forbiddenStates = @(
        "APPROVED_FOR_EXECUTION",
        "APPROVED_FOR_AUTO_ACTION",
        "APPROVED_FOR_BRAIN_WRITE",
        "APPROVED_FOR_MANUAL_WRITE",
        "APPROVED_FOR_REPORTS_BRAIN_WRITE",
        "APPROVED_FOR_EXTERNAL_EXECUTION"
    )

    $forbidden = @($records | Where-Object { $forbiddenStates -contains $_.approval_state })

    return @{
        status = if ($forbidden.Count -gt 0) { "BLOCK" } else { "PASS" }
        reason = if ($forbidden.Count -gt 0) { "FORBIDDEN_APPROVAL_STATE_DETECTED" } else { "APPROVAL_MATRIX_PASS" }
        approval_records_count = $records.Count
        forbidden_approval_states_count = $forbidden.Count
        records = $records
    }
}

function Build-PolicyEnforcementMatrixV33 {
    param([Parameter(Mandatory=$true)][object[]]$CanonicalRules)

    $records = @($CanonicalRules | ForEach-Object {
        [ordered]@{
            canonical_rule_id = $_.canonical_rule_id
            policy_priority_result = $_.policy_priority_result
            enforcement = $_.enforcement
            approval_state = $_.approval_state
            final_enforcement = if ($_.policy_priority_result -eq "LOCK") { "LOCK" }
                                elseif ($_.policy_priority_result -eq "BLOCK") { "BLOCK" }
                                elseif ($_.policy_priority_result -eq "REQUIRE_REVIEW") { "REQUIRE_REVIEW" }
                                elseif ($_.policy_priority_result -eq "PASS_WITH_WARNINGS") { "PASS_WITH_WARNINGS" }
                                else { "PASS" }
        }
    })

    return @{
        status = "PASS"
        reason = "POLICY_ENFORCEMENT_MATRIX_GENERATED"
        records_count = $records.Count
        records = $records
    }
}

function Build-SemanticPreservationAuditV33 {
    param([Parameter(Mandatory=$true)][object[]]$CanonicalRules)

    $semanticLoss = @($CanonicalRules | Where-Object { $_.semantic_preservation_status -eq "SEMANTIC_LOSS_DETECTED" })
    $potentialLoss = @($CanonicalRules | Where-Object { $_.semantic_preservation_status -eq "POTENTIAL_SEMANTIC_LOSS" })
    $warning = @($CanonicalRules | Where-Object { $_.semantic_preservation_status -eq "PRESERVED_WITH_WARNING" })

    $status = "PASS"
    $reason = "SEMANTIC_PRESERVATION_PASS"

    if ($semanticLoss.Count -gt 0) {
        $status = "BLOCK"
        $reason = "SEMANTIC_LOSS_DETECTED"
    }
    elseif ($potentialLoss.Count -gt 0) {
        $status = "REQUIRE_REVIEW"
        $reason = "POTENTIAL_SEMANTIC_LOSS"
    }
    elseif ($warning.Count -gt 0) {
        $status = "PASS_WITH_WARNINGS"
        $reason = "SEMANTIC_PRESERVATION_WITH_WARNINGS"
    }

    return @{
        status = $status
        reason = $reason
        semantic_loss_detected = $semanticLoss.Count
        potential_semantic_loss = $potentialLoss.Count
        preserved_with_warning = $warning.Count
        records = @($CanonicalRules | ForEach-Object {
            [ordered]@{
                canonical_rule_id = $_.canonical_rule_id
                source_rule_ids = $_.source_rule_ids
                semantic_preservation_status = $_.semantic_preservation_status
                semantic_loss_risk = $_.semantic_loss_risk
                semantic_reason = $_.semantic_reason
            }
        })
    }
}

function Build-WarningInheritanceReportV33 {
    param(
        [Parameter(Mandatory=$true)][object[]]$CanonicalRules,
        [Parameter(Mandatory=$true)]$ConflictReport
    )

    $sourceWarnings = @($ConflictReport.warnings)
    $warningIds = @($sourceWarnings | ForEach-Object { [string](Get-BridgePropV33 -Object $_ -Name "conflict_id" -Default "") } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $mappedWarningIds = @()

    foreach ($rule in @($CanonicalRules)) {
        foreach ($wid in @($rule.warning_inheritance.warning_ids)) {
            if (-not [string]::IsNullOrWhiteSpace([string]$wid)) {
                $mappedWarningIds += [string]$wid
            }
        }
    }

    $hidden = @($warningIds | Where-Object { $mappedWarningIds -notcontains $_ })
    $remaining = @($mappedWarningIds | Sort-Object -Unique)

    $status = "PASS"

    if ($hidden.Count -gt 0) {
        $status = "BLOCK"
        $reason = "WARNINGS_HIDDEN"
    }
    elseif ($mappedWarningIds.Count -lt $warningIds.Count) {
        $status = "REQUIRE_REVIEW"
        $reason = "WARNINGS_NOT_FULLY_MAPPED"
    }
    elseif ($remaining.Count -gt 0) {
        $status = "PASS_WITH_WARNINGS"
        $reason = "WARNINGS_INHERITED_AND_VISIBLE"
    }
    else {
        $reason = "NO_WARNINGS_REMAINING"
    }

    return @{
        status = $status
        reason = $reason
        warnings_inherited_from_v3_2_6 = $warningIds.Count
        warnings_mapped_to_canonical_rules = (@($mappedWarningIds | Sort-Object -Unique)).Count
        warnings_hidden = $hidden.Count
        warnings_resolved_by_v3_3 = 0
        warnings_remaining = $remaining.Count
        hidden_warning_ids = @($hidden)
        mapped_warning_ids = @($mappedWarningIds | Sort-Object -Unique)
    }
}

function Build-CoverageInvariantReportV33 {
    param(
        [Parameter(Mandatory=$true)]$RuleRegistry,
        [Parameter(Mandatory=$true)][object[]]$CanonicalRules
    )

    $sourceRules = @($RuleRegistry.rules)
    $sourceRuleIds = @($sourceRules | ForEach-Object { [string](Get-BridgePropV33 -Object $_ -Name "rule_id" -Default "") } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $mapped = @()
    $withoutPolicy = @()
    $withoutEvidence = @()

    foreach ($rule in @($CanonicalRules)) {
        foreach ($id in @($rule.source_rule_ids)) {
            if (-not [string]::IsNullOrWhiteSpace([string]$id)) {
                $mapped += [string]$id
            }
        }

        if (@($rule.policy_bindings).Count -eq 0 -and $rule.approval_state -ne "INFO_ONLY") {
            $withoutPolicy += $rule.canonical_rule_id
        }

        if (@($rule.source_hashes).Count -eq 0 -or @($rule.source_excerpt_hashes).Count -eq 0) {
            $withoutEvidence += $rule.canonical_rule_id
        }
    }

    $lost = @($sourceRuleIds | Where-Object { $mapped -notcontains $_ })
    $withoutMapping = $lost

    $status = "PASS"
    $reason = "COVERAGE_INVARIANT_PASS"

    if ($lost.Count -gt 0 -or $withoutEvidence.Count -gt 0) {
        $status = "BLOCK"
        $reason = "COVERAGE_INVARIANT_BLOCK"
    }
    elseif ($sourceRules.Count -ne 54 -or $withoutMapping.Count -gt 0 -or $withoutPolicy.Count -gt 0) {
        $status = "REQUIRE_REVIEW"
        $reason = "COVERAGE_INVARIANT_REVIEW_REQUIRED"
    }

    return @{
        status = $status
        reason = $reason
        source_rules_total = $sourceRules.Count
        source_rules_accounted_for = (@($mapped | Sort-Object -Unique)).Count
        source_rules_lost = $lost.Count
        source_rules_without_canonical_mapping = $withoutMapping.Count
        source_rules_without_policy_binding = $withoutPolicy.Count
        source_rules_without_evidence = $withoutEvidence.Count
        lost_source_rule_ids = @($lost)
        without_policy_binding = @($withoutPolicy)
        without_evidence = @($withoutEvidence)
    }
}

function Build-NoExecutionPermissionAuditV33 {
    param([Parameter(Mandatory=$true)][object[]]$CanonicalRules)

    $execution = @($CanonicalRules | Where-Object { $_.permissions.execution_allowed -eq $true })
    $brain = @($CanonicalRules | Where-Object { $_.permissions.brain_write_allowed -eq $true })
    $manual = @($CanonicalRules | Where-Object { $_.permissions.manual_write_allowed -eq $true })
    $reportsBrain = @($CanonicalRules | Where-Object { $_.permissions.reports_brain_write_allowed -eq $true })
    $external = @($CanonicalRules | Where-Object { $_.permissions.external_execution_allowed -eq $true })

    $status = "PASS"
    $reason = "NO_EXECUTION_PERMISSION_AUDIT_PASS"

    if ($brain.Count -gt 0 -or $reportsBrain.Count -gt 0) {
        $status = "LOCK"
        $reason = "WRITE_PERMISSION_LOCK"
    }
    elseif ($execution.Count -gt 0 -or $manual.Count -gt 0 -or $external.Count -gt 0) {
        $status = "BLOCK"
        $reason = "EXECUTION_PERMISSION_BLOCK"
    }

    return @{
        status = $status
        reason = $reason
        execution_allowed_rules = $execution.Count
        brain_write_allowed_rules = $brain.Count
        manual_write_allowed_rules = $manual.Count
        reports_brain_write_allowed_rules = $reportsBrain.Count
        external_execution_allowed_rules = $external.Count
    }
}

function Get-GlobalBridgeStatusV33 {
    param(
        [Parameter(Mandatory=$true)][object[]]$Statuses,
        [Parameter(Mandatory=$true)][int]$WarningsRemaining
    )

    if ($Statuses -contains "LOCK") { return @{ status = "LOCK"; reason = "LOCK_STATE_DETECTED" } }
    if ($Statuses -contains "BLOCK") { return @{ status = "BLOCK"; reason = "BLOCK_STATE_DETECTED" } }
    if ($Statuses -contains "REQUIRE_REVIEW") { return @{ status = "REQUIRE_REVIEW"; reason = "REQUIRE_REVIEW_STATE_DETECTED" } }
    if ($Statuses -contains "PASS_WITH_WARNINGS" -or $WarningsRemaining -gt 0) { return @{ status = "PASS_WITH_WARNINGS"; reason = "PASS_WITH_WARNINGS_STATE" } }

    return @{ status = "PASS"; reason = "BRIDGE_V3_3_VALID" }
}
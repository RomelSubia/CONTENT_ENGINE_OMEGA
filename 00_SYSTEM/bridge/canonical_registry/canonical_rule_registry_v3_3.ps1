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

function Get-StableSha256LocalV33 {
    param([AllowEmptyString()][string]$Text)

    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $hash = $sha.ComputeHash($bytes)

    return ([BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
}

function New-CanonicalRuleIdV33 {
    param(
        [string]$NormalizedIntent,
        [string]$Category,
        [string]$Domain,
        [object[]]$SourceRuleIds
    )

    $ids = (@($SourceRuleIds) | Sort-Object) -join ","
    $seed = "$NormalizedIntent|$Category|$Domain|$ids"
    $hash = Get-StableSha256LocalV33 -Text $seed

    return "CRV332-$Category-$($hash.Substring(0,10))"
}

function Get-DomainV33 {
    param(
        [string]$Text,
        [string]$Category
    )

    $combined = (([string]$Text) + " " + ([string]$Category)).ToLowerInvariant()
    $cat = ([string]$Category).ToUpperInvariant()

    if ($combined -match "reports/brain|reportes del cerebro|reportes.*cerebro|rule_no_reports_brain_write") {
        return "REPORTS_BRAIN"
    }

    if (
        $cat -eq "BRAIN" -or
        $combined -match "rule_brain|cerebro|brain|memoria del cerebro|read_only|read-only|solo lectura"
    ) {
        return "BRAIN"
    }

    if (
        $cat -eq "MANUAL" -or
        $combined -match "rule_manual|manual|manifest|source|fuente"
    ) {
        return "MANUAL"
    }

    if (
        $combined -match "rule_no_capa_9|capa\s*9|layer\s*9|capa9|no_capa_9"
    ) {
        return "CAPA_CONTROL"
    }

    if (
        $cat -eq "AUTOMATION" -or
        $combined -match "rule_external|api|apis|n8n|youtube|tiktok|instagram|publicar|externa|emails|external"
    ) {
        return "EXTERNAL"
    }

    if (
        $cat -eq "REPO" -or
        $combined -match "rule_repo|git|commit|push|sync|remoto|repo"
    ) {
        return "REPO"
    }

    if (
        $cat -eq "EVIDENCE" -or
        $combined -match "rule_evidence|evidencia|evidence|hash|seal|manifest|validaci"
    ) {
        return "EVIDENCE"
    }

    return "GOVERNANCE"
}

function Get-NormalizedIntentV33 {
    param(
        [string]$Text,
        [string]$ExistingNormalized = ""
    )

    $upper = ([string]$Text).Trim().ToUpperInvariant()

    if (![string]::IsNullOrWhiteSpace($ExistingNormalized)) {
        $existing = ([string]$ExistingNormalized).Trim().ToUpperInvariant()

        if ($existing.StartsWith("RULE_")) {
            return $existing
        }
    }

    if ($upper -match "CAPA\s*9|LAYER\s*9|NO_CAPA_9") { return "RULE_NO_CAPA_9_OR_CAPA_9_REFERENCE" }
    if ($upper -match "REPORTS/BRAIN|REPORTES.*CEREBRO") { return "RULE_NO_REPORTS_BRAIN_WRITE" }
    if ($upper -match "CEREBRO|BRAIN") { return "RULE_BRAIN_GOVERNANCE_OR_READ_ONLY" }
    if ($upper -match "MANUAL|MANIFEST|SOURCE") { return "RULE_MANUAL_SOURCE_GOVERNANCE" }
    if ($upper -match "EVIDENCIA|EVIDENCE|HASH|MANIFEST|SEAL") { return "RULE_EVIDENCE_REQUIRED" }
    if ($upper -match "VALIDAR|VALIDATION|ANTES DE CONTINUAR") { return "RULE_VALIDATE_BEFORE_ADVANCE" }
    if ($upper -match "GIT|COMMIT|PUSH|REMOTO|SYNC") { return "RULE_REPO_SYNC_REQUIRED" }
    if ($upper -match "PUBLICAR|YOUTUBE|TIKTOK|INSTAGRAM|N8N|API|APIS|EMAIL") { return "RULE_EXTERNAL_EXECUTION_CONTROL" }
    if ($upper -match "FAIL-CLOSED|\[FAIL CLOSED\]|BLOCK|LOCK") { return "RULE_FAIL_CLOSED_GOVERNANCE" }
    if ($upper -match "PRODUCCI|PRODUCTION|SELLADO|SISTEMA TERMINADO") { return "RULE_PRODUCTION_CLAIM_REQUIRES_EVIDENCE" }

    return ("RULE_" + (($upper -replace "[^A-Z0-9]+","_").Trim("_")))
}

function Get-SemanticPreservationStatusV33 {
    param(
        [string]$RawText,
        [string]$CanonicalText,
        [string]$NormalizedIntent
    )

    $raw = ([string]$RawText).ToLowerInvariant()
    $canon = ([string]$CanonicalText).ToLowerInvariant()

    if ($raw -match "no ejecutar|sin autorizaci|no publicar|no usar api|no external") {
        if ($canon -match "allowed true|permitida|habilitada") {
            return @{
                status = "SEMANTIC_LOSS_DETECTED"
                risk = "HIGH"
                reason = "NEGATIVE_EXECUTION_RULE_INVERTED"
            }
        }
    }

    if ($raw -match "no modificar|no tocar|solo lectura|read.only|read_only") {
        if ($canon -match "write allowed|modificaci[oó]n permitida") {
            return @{
                status = "SEMANTIC_LOSS_DETECTED"
                risk = "HIGH"
                reason = "NO_WRITE_RULE_INVERTED"
            }
        }
    }

    if ($NormalizedIntent -like "RULE_*") {
        return @{
            status = "PRESERVED_WITH_NORMALIZATION"
            risk = "LOW"
            reason = "NORMALIZED_INTENT_PRESERVED"
        }
    }

    return @{
        status = "PRESERVED"
        risk = "NONE"
        reason = "TEXT_PRESERVED"
    }
}

function Get-DefaultPermissionsV33 {
    return [ordered]@{
        execution_allowed = $false
        brain_write_allowed = $false
        manual_write_allowed = $false
        reports_brain_write_allowed = $false
        external_execution_allowed = $false
        future_gate_required = $true
    }
}

function New-CanonicalRuleV33 {
    param(
        [Parameter(Mandatory=$true)]$Rule,
        [Parameter(Mandatory=$false)][object[]]$Warnings = @()
    )

    $ruleId = [string](Get-BridgePropV33 -Object $Rule -Name "rule_id" -Default "")
    $raw = [string](Get-BridgePropV33 -Object $Rule -Name "raw_excerpt" -Default "")
    $existingNormalized = [string](Get-BridgePropV33 -Object $Rule -Name "normalized_text" -Default "")
    $category = [string](Get-BridgePropV33 -Object $Rule -Name "category" -Default "GOVERNANCE")
    $severity = [string](Get-BridgePropV33 -Object $Rule -Name "severity" -Default "INFO")
    $risk = [int](Get-BridgePropV33 -Object $Rule -Name "risk_score" -Default 0)
    $modality = [string](Get-BridgePropV33 -Object $Rule -Name "modality" -Default "INFO")
    $enforcement = [string](Get-BridgePropV33 -Object $Rule -Name "enforcement" -Default "INFO_ONLY")
    $scope = [string](Get-BridgePropV33 -Object $Rule -Name "scope" -Default "GLOBAL")
    $sourceFile = [string](Get-BridgePropV33 -Object $Rule -Name "source_file" -Default "")
    $sourceHash = [string](Get-BridgePropV33 -Object $Rule -Name "source_hash_sha256" -Default "")
    $excerptHash = [string](Get-BridgePropV33 -Object $Rule -Name "raw_excerpt_hash_sha256" -Default "")
    $section = [string](Get-BridgePropV33 -Object $Rule -Name "section_title" -Default "")
    $lineStart = [int](Get-BridgePropV33 -Object $Rule -Name "line_start" -Default 0)
    $lineEnd = [int](Get-BridgePropV33 -Object $Rule -Name "line_end" -Default 0)

    $normalizedIntent = Get-NormalizedIntentV33 -Text $raw -ExistingNormalized $existingNormalized
    $domain = Get-DomainV33 -Text ($raw + " " + $existingNormalized + " " + $normalizedIntent) -Category $category
    $canonicalText = $normalizedIntent
    $semantic = Get-SemanticPreservationStatusV33 -RawText $raw -CanonicalText $canonicalText -NormalizedIntent $normalizedIntent
    $warningObjects = @($Warnings | Where-Object { ([string](Get-BridgePropV33 -Object $_ -Name "rule_id" -Default "")) -eq $ruleId })
    $warningIds = @()
    $warningReasons = @()

    foreach ($w in $warningObjects) {
        $warningIds += [string](Get-BridgePropV33 -Object $w -Name "conflict_id" -Default "")
        $warningReasons += [string](Get-BridgePropV33 -Object $w -Name "reason" -Default "")
    }

    $canonicalId = New-CanonicalRuleIdV33 -NormalizedIntent $normalizedIntent -Category $category -Domain $domain -SourceRuleIds @($ruleId)
    $permissions = Get-DefaultPermissionsV33

    $seedObject = [ordered]@{
        canonical_rule_id = $canonicalId
        source_rule_ids = @($ruleId)
        normalized_intent = $normalizedIntent
        category = $category
        domain = $domain
        risk_score = $risk
        enforcement = $enforcement
        permissions = $permissions
    }

    $canonicalHash = Get-StableSha256LocalV33 -Text ($seedObject | ConvertTo-Json -Depth 50 -Compress)

    return [ordered]@{
        canonical_rule_id = $canonicalId
        canonical_hash_sha256 = $canonicalHash
        source_rule_ids = @($ruleId)
        source_rule_count = 1
        source_hashes = @($sourceHash)
        source_excerpt_hashes = @($excerptHash)
        source_line_ranges = @([ordered]@{ start = $lineStart; end = $lineEnd })
        source_sections = @($section)
        source_files = @($sourceFile)
        canonical_text = $canonicalText
        normalized_intent = $normalizedIntent
        semantic_preservation_status = $semantic.status
        semantic_loss_risk = $semantic.risk
        semantic_reason = $semantic.reason
        category = $category
        domain = $domain
        scope = $scope
        severity = $severity
        risk_score = $risk
        modality = $modality
        enforcement = $enforcement
        policy_bindings = @()
        policy_priority_result = "PENDING_POLICY_BINDING"
        approval_state = "PENDING_POLICY_BINDING"
        warning_inheritance = [ordered]@{
            inherits_warning = (@($warningObjects).Count -gt 0)
            warning_ids = @($warningIds | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
            warning_reasons = @($warningReasons | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
            warning_acceptance_status = if (@($warningObjects).Count -gt 0) { "ACCEPTED_IN_V3_2_6_GATE" } else { "NONE" }
        }
        permissions = $permissions
        evidence = [ordered]@{
            source_registry = "MANUAL_RULES_REGISTRY_V3_2_6.json"
            source_conflict_report = "MANUAL_BRAIN_CONFLICT_REPORT_V3_2_6.json"
            source_warning_gate = "WARNING_ACCEPTANCE_GATE_REPORT_V3_2_6.json"
            source_readiness_map = "GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_V3_2_6.json"
            source_rule_id = $ruleId
            source_hash_sha256 = $sourceHash
            raw_excerpt_hash_sha256 = $excerptHash
        }
        status = "ACTIVE_GOVERNED"
    }
}

function Build-CanonicalRegistryV33 {
    param(
        [Parameter(Mandatory=$true)]$RuleRegistry,
        [Parameter(Mandatory=$true)]$ConflictReport,
        [Parameter(Mandatory=$true)]$WarningGate,
        [Parameter(Mandatory=$true)]$ReadinessMap
    )

    $sourceRules = @($RuleRegistry.rules)
    $warnings = @($ConflictReport.warnings)
    $canonicalRules = @()

    foreach ($rule in $sourceRules) {
        $canonicalRules += New-CanonicalRuleV33 -Rule $rule -Warnings $warnings
    }

    $sourceRuleIds = @($sourceRules | ForEach-Object { [string](Get-BridgePropV33 -Object $_ -Name "rule_id" -Default "") } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $mappedRuleIds = @()

    foreach ($cr in $canonicalRules) {
        foreach ($id in @($cr.source_rule_ids)) {
            if (-not [string]::IsNullOrWhiteSpace([string]$id)) {
                $mappedRuleIds += [string]$id
            }
        }
    }

    $lost = @($sourceRuleIds | Where-Object { $mappedRuleIds -notcontains $_ })
    $withoutEvidence = @($canonicalRules | Where-Object {
        @($_.source_hashes).Count -eq 0 -or
        @($_.source_excerpt_hashes).Count -eq 0 -or
        [string]::IsNullOrWhiteSpace([string]$_.evidence.source_rule_id)
    })

    $status = "PASS"
    $reason = "CANONICAL_REGISTRY_BUILT"

    if ($lost.Count -gt 0) {
        $status = "BLOCK"
        $reason = "SOURCE_RULES_LOST"
    }
    elseif ($withoutEvidence.Count -gt 0) {
        $status = "BLOCK"
        $reason = "CANONICAL_RULE_WITHOUT_EVIDENCE"
    }
    elseif ($sourceRules.Count -ne 54) {
        $status = "REQUIRE_REVIEW"
        $reason = "SOURCE_RULES_TOTAL_NOT_54"
    }

    return @{
        status = $status
        reason = $reason
        source_rules_total = $sourceRules.Count
        canonical_rules_count = $canonicalRules.Count
        source_rules_accounted_for = (@($mappedRuleIds | Sort-Object -Unique)).Count
        source_rules_lost = $lost.Count
        source_rules_without_canonical_mapping = $lost.Count
        source_rules_without_evidence = $withoutEvidence.Count
        canonical_rules = @($canonicalRules | Sort-Object canonical_rule_id)
    }
}

function Build-CanonicalDeduplicationReportV33 {
    param([Parameter(Mandatory=$true)][object[]]$CanonicalRules)

    $groups = @($CanonicalRules | Group-Object normalized_intent)
    $dedupRecords = @()
    $mergeAllowedCount = 0
    $reviewDuplicateCount = 0

    foreach ($g in $groups) {
        $items = @($g.Group)

        if ($items.Count -eq 1) {
            $dedupRecords += [ordered]@{
                normalized_intent = $g.Name
                deduplication_type = "UNIQUE"
                canonical_rule_ids = @($items | ForEach-Object { $_.canonical_rule_id })
                source_rule_ids = @($items | ForEach-Object { $_.source_rule_ids } | ForEach-Object { $_ })
                merge_performed = $false
                source_rule_ids_preserved = $true
            }
            continue
        }

        $categories = @($items | ForEach-Object { $_.category } | Sort-Object -Unique)
        $domains = @($items | ForEach-Object { $_.domain } | Sort-Object -Unique)
        $enforcements = @($items | ForEach-Object { $_.enforcement } | Sort-Object -Unique)
        $modalities = @($items | ForEach-Object { $_.modality } | Sort-Object -Unique)
        $risks = @($items | ForEach-Object { [int]$_.risk_score })
        $riskDelta = 0

        if ($risks.Count -gt 0) {
            $riskDelta = (($risks | Measure-Object -Maximum).Maximum) - (($risks | Measure-Object -Minimum).Minimum)
        }

        $hasWarningConflict = (@($items | Where-Object { $_.warning_inheritance.inherits_warning -eq $true }).Count -gt 0 -and @($items | Where-Object { $_.warning_inheritance.inherits_warning -eq $false }).Count -gt 0)
        $mergeAllowed = (
            $categories.Count -eq 1 -and
            $domains.Count -eq 1 -and
            $enforcements.Count -eq 1 -and
            $modalities.Count -eq 1 -and
            $riskDelta -le 10 -and
            -not $hasWarningConflict
        )

        if ($mergeAllowed) {
            $type = "DUPLICATE_SAME_MEANING"
            $mergeAllowedCount++
        }
        else {
            $type = "REQUIRES_REVIEW_DUPLICATE"
            $reviewDuplicateCount++
        }

        $dedupRecords += [ordered]@{
            normalized_intent = $g.Name
            deduplication_type = $type
            canonical_rule_ids = @($items | ForEach-Object { $_.canonical_rule_id })
            source_rule_ids = @($items | ForEach-Object { $_.source_rule_ids } | ForEach-Object { $_ })
            category_count = $categories.Count
            domain_count = $domains.Count
            enforcement_count = $enforcements.Count
            modality_count = $modalities.Count
            risk_score_delta = $riskDelta
            warning_conflict = $hasWarningConflict
            merge_allowed = $mergeAllowed
            merge_performed = $false
            source_rule_ids_preserved = $true
        }
    }

    return @{
        status = if ($reviewDuplicateCount -gt 0) { "PASS_WITH_WARNINGS" } else { "PASS" }
        reason = if ($reviewDuplicateCount -gt 0) { "DUPLICATES_REQUIRE_FUTURE_REVIEW_BUT_NO_SOURCE_LOSS" } else { "DEDUPLICATION_GUARD_PASS" }
        unique_count = @($dedupRecords | Where-Object { $_.deduplication_type -eq "UNIQUE" }).Count
        duplicate_same_meaning_count = @($dedupRecords | Where-Object { $_.deduplication_type -eq "DUPLICATE_SAME_MEANING" }).Count
        requires_review_duplicate_count = $reviewDuplicateCount
        merge_allowed_count = $mergeAllowedCount
        merge_performed_count = 0
        source_rule_ids_preserved = $true
        records = @($dedupRecords)
    }
}
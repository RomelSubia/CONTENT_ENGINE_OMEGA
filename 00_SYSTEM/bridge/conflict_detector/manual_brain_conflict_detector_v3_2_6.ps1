$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Get-StableSha256ConflictV326 {
    param([AllowEmptyString()][string]$Text)

    $sha=[System.Security.Cryptography.SHA256]::Create()
    $bytes=[System.Text.Encoding]::UTF8.GetBytes($Text)
    $hash=$sha.ComputeHash($bytes)

    return ([BitConverter]::ToString($hash)).Replace("-","").ToLowerInvariant()
}

function New-ConflictIdV326 {
    param([string]$Type,[string]$RuleId,[string]$Reason)

    $h=Get-StableSha256ConflictV326 -Text "$Type|$RuleId|$Reason"

    return ("CFV326-{0}-{1}" -f $Type,$h.Substring(0,8))
}

function New-ManualConflictV326 {
    param(
        [object]$Rule,
        [string]$ConflictType,
        [string]$Severity,
        [int]$RiskScore,
        [string]$Decision,
        [string]$Reason,
        [string]$PolicySource="bridge_policy"
    )

    $cid=New-ConflictIdV326 -Type $ConflictType -RuleId $Rule.rule_id -Reason $Reason

    return [ordered]@{
        conflict_id=$cid
        conflict_type=$ConflictType
        severity=$Severity
        risk_score=$RiskScore
        decision=$Decision
        rule_id=$Rule.rule_id
        policy_source=$PolicySource
        reason=$Reason
        evidence=@{
            manual_rule_hash=$Rule.raw_excerpt_hash_sha256
            source_section=$Rule.section_title
            source_line=$Rule.line_start
        }
        status="ACTIVE"
    }
}

function Test-Capa9IntentV326 {
    param([AllowEmptyString()][string]$Text)

    $l=$Text.ToLowerInvariant()

    $negative=($l -match "no\s+(se\s+debe\s+)?crear\s+capa\s*9|capa\s*9.*prohib|no_capa_9|no\s+capa\s*9|bloquear\s+capa\s*9")
    $positive=($l -match "crear\s+capa\s*9|agregar\s+layer\s*9|crear\s+layer\s*9|extender.*cerebro.*capa|nueva capa cerebral")

    if ($negative) { return "CAPA_9_NEGATIVE_POLICY" }
    if ($positive) { return "CAPA_9_POSITIVE_INTENT" }
    if ($l -match "capa\s*9|layer\s*9|capa9") { return "CAPA_9_AMBIGUOUS_REFERENCE" }

    return "NONE"
}

function Test-BrainMutationIntentV326 {
    param([AllowEmptyString()][string]$Text)

    $l=$Text.ToLowerInvariant()

    if ($l -match "modificar.*cerebro|reescribir.*cerebro|actualizar memoria del cerebro|escribir.*reports/brain|alterar.*global seal|crear nueva capa cerebral|brain write|brain mutation|modificar.*reports/brain") {
        if ($l -match "no modificar|no tocar|read.only|read_only|solo lectura|prohib|no escribir") {
            return "BRAIN_READ_ONLY_REFERENCE"
        }

        return "BRAIN_MUTATION_DIRECT"
    }

    return "NONE"
}

function Test-ExternalExecutionIntentV326 {
    param([AllowEmptyString()][string]$Text)

    $l=$Text.ToLowerInvariant()

    $external=($l -match "publicar\s+autom[aá]ticamente|subir.*youtube|enviar.*tiktok|enviar.*instagram|ejecutar\s+n8n|activar\s+campa.a|usar\s+api[s]?\s+externa[s]?|api[s]?\s+externa[s]?|enviar\s+emails?\s+autom|automatizar\s+publicaci|ejecutar.*api[s]?.*externa")
    $safe=($l -match "futuro|dise.o futuro|requiere aprobaci|con autorizaci|no ejecutar|no publicar|solo despu[eé]s de autorizaci|controlad")

    if ($external -and -not $safe) { return "EXTERNAL_EXECUTION_DIRECT" }
    if ($external -and $safe) { return "EXTERNAL_EXECUTION_GOVERNED_REFERENCE" }

    return "NONE"
}

function Test-ProductionClaimEvidenceV326 {
    param([AllowEmptyString()][string]$Text,[bool]$EvidenceAvailable)

    $l=$Text.ToLowerInvariant()
    $claim=($l -match "production-ready|producci[oó]n real|sellado final|validado|completo|ejecutable real|listo para operar|sistema terminado")

    if (-not $claim) { return "NONE" }
    if ($EvidenceAvailable) { return "PRODUCTION_CLAIM_WITH_EVIDENCE" }

    return "PRODUCTION_CLAIM_WITHOUT_EVIDENCE"
}

function Find-ManualBrainConflictsV326 {
    param(
        [Parameter(Mandatory=$true)]$RuleRegistry,
        [string]$RootPath="D:\CONTENT_ENGINE_OMEGA"
    )

    $conflicts=@()
    $warnings=@()
    $reviewRequired=@()
    $technicalDebt=@()

    $evidenceAvailable=(
        (Test-Path -LiteralPath (Join-Path $RootPath "00_SYSTEM\bridge\reports\BRIDGE_SOURCE_RESOLVER_REPORT_V2_1_3.json")) -and
        (Test-Path -LiteralPath (Join-Path $RootPath "00_SYSTEM\bridge\reports\BRIDGE_BRAIN_READ_ONLY_REPORT_V2_1_3.json")) -and
        (Test-Path -LiteralPath (Join-Path $RootPath "00_SYSTEM\bridge\manifests\BRIDGE_MANIFEST_SEAL_V2_1_3.json"))
    )

    foreach ($rule in @($RuleRegistry.rules)) {
        $text=[string]$rule.raw_excerpt

        $capa=Test-Capa9IntentV326 -Text $text

        if ($capa -eq "CAPA_9_POSITIVE_INTENT") {
            $conflicts += New-ManualConflictV326 -Rule $rule -ConflictType "POLICY_VIOLATION" -Severity "CRITICAL" -RiskScore 95 -Decision "BLOCK" -Reason "CAPA_9_POSITIVE_INTENT"
        } elseif ($capa -eq "CAPA_9_AMBIGUOUS_REFERENCE") {
            $reviewRequired += New-ManualConflictV326 -Rule $rule -ConflictType "AMBIGUOUS_RULE" -Severity "HIGH" -RiskScore 70 -Decision "REQUIRE_REVIEW" -Reason "CAPA_9_AMBIGUOUS_REFERENCE"
        }

        $brain=Test-BrainMutationIntentV326 -Text $text

        if ($brain -eq "BRAIN_MUTATION_DIRECT") {
            $conflicts += New-ManualConflictV326 -Rule $rule -ConflictType "HARD_CONFLICT" -Severity "CRITICAL" -RiskScore 100 -Decision "LOCK" -Reason "BRAIN_MUTATION_DIRECT" -PolicySource "BRAIN_READ_ONLY_CONTRACT.json"
        }

        $external=Test-ExternalExecutionIntentV326 -Text $text

        if ($external -eq "EXTERNAL_EXECUTION_DIRECT") {
            $conflicts += New-ManualConflictV326 -Rule $rule -ConflictType "HARD_CONFLICT" -Severity "CRITICAL" -RiskScore 90 -Decision "BLOCK" -Reason "EXTERNAL_EXECUTION_DIRECT"
        } elseif ($external -eq "EXTERNAL_EXECUTION_GOVERNED_REFERENCE") {
            $warnings += New-ManualConflictV326 -Rule $rule -ConflictType "SOFT_CONFLICT" -Severity "LOW" -RiskScore 35 -Decision "PASS_WITH_WARNINGS" -Reason "EXTERNAL_EXECUTION_GOVERNED_REFERENCE"
        }

        $prod=Test-ProductionClaimEvidenceV326 -Text $text -EvidenceAvailable $evidenceAvailable

        if ($prod -eq "PRODUCTION_CLAIM_WITHOUT_EVIDENCE") {
            $reviewRequired += New-ManualConflictV326 -Rule $rule -ConflictType "PRODUCTION_CLAIM_WITHOUT_EVIDENCE" -Severity "HIGH" -RiskScore 75 -Decision "REQUIRE_REVIEW" -Reason "PRODUCTION_CLAIM_WITHOUT_EVIDENCE"
        } elseif ($prod -eq "PRODUCTION_CLAIM_WITH_EVIDENCE") {
            $warnings += New-ManualConflictV326 -Rule $rule -ConflictType "ALLOW_WITH_TRACE" -Severity "LOW" -RiskScore 30 -Decision "PASS_WITH_WARNINGS" -Reason "PRODUCTION_CLAIM_WITH_EVIDENCE"
        }
    }

    $groups=@($RuleRegistry.rules | Group-Object normalized_text | Where-Object { $_.Count -gt 1 })

    foreach ($g in $groups) {
        $first=$g.Group | Select-Object -First 1

        $warnings += New-ManualConflictV326 -Rule $first -ConflictType "DUPLICATE_RULE" -Severity "LOW" -RiskScore 35 -Decision "PASS_WITH_WARNINGS" -Reason "DUPLICATE_SAME_MEANING"
    }

    $hasLock=@($conflicts | Where-Object { $_.decision -eq "LOCK" }).Count -gt 0
    $hasBlock=@($conflicts | Where-Object { $_.decision -eq "BLOCK" }).Count -gt 0
    $hasReview=@($reviewRequired).Count -gt 0
    $hasWarnings=@($warnings).Count -gt 0

    if ($hasLock) {
        $status="LOCK"
        $reason="LOCK_CONFLICTS_DETECTED"
    } elseif ($hasBlock) {
        $status="BLOCK"
        $reason="BLOCK_CONFLICTS_DETECTED"
    } elseif ($hasReview) {
        $status="REQUIRE_REVIEW"
        $reason="REVIEW_REQUIRED_ITEMS_DETECTED"
    } elseif ($hasWarnings) {
        $status="PASS_WITH_WARNINGS"
        $reason="NO_HARD_CONFLICTS_WITH_WARNINGS"
    } else {
        $status="PASS"
        $reason="NO_CONFLICTS_DETECTED"
    }

    return @{
        status=$status
        reason=$reason
        conflicts=@($conflicts)
        warnings=@($warnings)
        review_required=@($reviewRequired)
        technical_debt=@($technicalDebt)
        conflicts_count=@($conflicts).Count
        warnings_count=@($warnings).Count
        review_required_count=@($reviewRequired).Count
        technical_debt_count=@($technicalDebt).Count
    }
}
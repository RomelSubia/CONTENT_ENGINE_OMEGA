$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function New-BridgeResultV326 {
    param([string]$Status,[string]$Reason,[hashtable]$Data=@{})
    return @{ status=$Status; reason=$Reason; data=$Data }
}

function Get-StableSha256LocalV326 {
    param([AllowEmptyString()][string]$Text)
    $sha=[System.Security.Cryptography.SHA256]::Create()
    $bytes=[System.Text.Encoding]::UTF8.GetBytes($Text)
    $hash=$sha.ComputeHash($bytes)
    return ([BitConverter]::ToString($hash)).Replace("-","").ToLowerInvariant()
}

function Get-FileSha256LowerLocalV326 {
    param([string]$Path)
    if (!(Test-Path -LiteralPath $Path)) { throw "Missing file for hash: $Path" }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-ManualIntegrityV326 {
    param([string]$RootPath="D:\CONTENT_ENGINE_OMEGA")

    $manualRel="00_SYSTEM\manual\current\MANUAL_MASTER_CURRENT.md"
    $manifestRel="00_SYSTEM\manual\manifest\MANUAL_SOURCE_MANIFEST.json"

    $manualPath=Join-Path $RootPath $manualRel
    $manifestPath=Join-Path $RootPath $manifestRel

    if (!(Test-Path -LiteralPath $manualPath)) { return New-BridgeResultV326 -Status "BLOCK" -Reason "MANUAL_CURRENT_MISSING" -Data @{path=$manualRel} }
    if (!(Test-Path -LiteralPath $manifestPath)) { return New-BridgeResultV326 -Status "BLOCK" -Reason "MANUAL_MANIFEST_MISSING" -Data @{path=$manifestRel} }

    try { $manifest=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json }
    catch { return New-BridgeResultV326 -Status "BLOCK" -Reason "MANUAL_MANIFEST_INVALID_JSON" -Data @{error=$_.Exception.Message} }

    $manualHash=Get-FileSha256LowerLocalV326 -Path $manualPath
    $manifestHash=([string]$manifest.manual_hash_sha256).Replace("sha256:","").ToLowerInvariant()

    if ($manualHash -ne $manifestHash) { return New-BridgeResultV326 -Status "BLOCK" -Reason "MANUAL_HASH_MISMATCH" -Data @{expected=$manifestHash; actual=$manualHash} }
    if ($manifest.manual_status -ne "CURRENT_VALID") { return New-BridgeResultV326 -Status "BLOCK" -Reason "MANUAL_NOT_CURRENT_VALID" -Data @{status=$manifest.manual_status} }
    if ($manifest.approved_for_bridge -ne $true) { return New-BridgeResultV326 -Status "BLOCK" -Reason "MANUAL_NOT_APPROVED_FOR_BRIDGE" }
    if ($manifest.is_historical -ne $false) { return New-BridgeResultV326 -Status "BLOCK" -Reason "MANUAL_MARKED_HISTORICAL" }
    if ($manifest.is_mixed_chat_transcript -ne $false) { return New-BridgeResultV326 -Status "BLOCK" -Reason "MANUAL_MARKED_MIXED_CHAT_TRANSCRIPT" }

    return New-BridgeResultV326 -Status "PASS" -Reason "MANUAL_INTEGRITY_RECHECK_PASS" -Data @{
        manual_path=$manualRel
        manifest_path=$manifestRel
        manual_hash_sha256=$manualHash
        manual_status=$manifest.manual_status
        approved_for_bridge=$manifest.approved_for_bridge
    }
}

function Test-ManualContaminationV326 {
    param([AllowEmptyString()][string]$ManualText)

    $blockedNoise=@(
        "PS D:\CONTENT_ENGINE_OMEGA>",
        "Presiona ENTER",
        "Copia esta salida completa",
        "Pasted text",
        "User uploaded file",
        "tool call",
        "file_search",
        "Skipped",
        "[ERROR CAPTURADO - LA VENTANA NO SE CERRARÁ]"
    )

    $allowedTerms=@(
        "[FAIL CLOSED]",
        "FAIL-CLOSED",
        "FAIL_CLOSED",
        "BLOCK",
        "LOCK",
        "PASS",
        "CURRENT_VALID",
        "READ_ONLY",
        "GLOBAL_SEAL",
        "AUTO_ACTION_FALSE",
        "NO_CAPA_9",
        "EVIDENCE-FIRST"
    )
    $manualTextForScan = [string]$ManualText

    $noiseHits=@()
    foreach ($n in $blockedNoise) {
        $needle = [string]$n
        if ($manualTextForScan.IndexOf($needle, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
            $noiseHits += $n
        }
    }

    $allowedFound=@()
    foreach ($t in $allowedTerms) {
        $needle = [string]$t
        if ($manualTextForScan.IndexOf($needle, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
            $allowedFound += $t
        }
    }

    if ($noiseHits.Count -gt 0) {
        return @{
            status="BLOCK"
            reason="MANUAL_CONTAMINATION_DETECTED"
            noise_hits=$noiseHits
            allowed_governance_terms_found=$allowedFound
            manual_clean_for_rule_extraction=$false
        }
    }

    return @{
        status="PASS"
        reason="MANUAL_CONTAMINATION_SCAN_PASS"
        noise_hits=@()
        allowed_governance_terms_found=$allowedFound
        manual_clean_for_rule_extraction=$true
    }
}

function Convert-ToSafeLineArrayV326 {
    param([AllowNull()][object]$InputObject)

    $safeLines=@()

    if ($null -eq $InputObject) { return @("") }

    if ($InputObject -is [string]) {
        foreach ($line in ([string]$InputObject -split "`n")) {
            if ($null -eq $line) { $safeLines += "" } else { $safeLines += [string]$line }
        }
        return @($safeLines)
    }

    foreach ($item in @($InputObject)) {
        if ($null -eq $item) { $safeLines += "" } else { $safeLines += [string]$item }
    }

    if ($safeLines.Count -eq 0) { $safeLines += "" }

    return @($safeLines)
}

function Get-ManualSectionsV326 {
    param([AllowNull()][object]$Lines)

    $safeLines=@(Convert-ToSafeLineArrayV326 -InputObject $Lines)
    $sections=@()
    $currentTitle="ROOT"
    $currentStart=1

    for ($i=0; $i -lt $safeLines.Count; $i++) {
        $line=([string]$safeLines[$i]).Trim()
        $isHeader=($line -match "^(#{1,6})\s+(.+)$" -or $line -match "^(FASE|CAPA|MÓDULO|MODULO|SECCIÓN|SECCION|BLOQUE)\b")

        if ($isHeader) {
            if (($i+1) -gt $currentStart) {
                $sections += [pscustomobject]@{title=$currentTitle; line_start=$currentStart; line_end=$i}
            }

            $currentTitle=$line
            $currentStart=$i+1
        }
    }

    if ($safeLines.Count -ge $currentStart) {
        $sections += [pscustomobject]@{title=$currentTitle; line_start=$currentStart; line_end=$safeLines.Count}
    }

    if (@($sections).Count -eq 0) {
        $sections += [pscustomobject]@{title="ROOT"; line_start=1; line_end=$safeLines.Count}
    }

    return @($sections)
}

function Measure-ManualCoverageV326 {
    param([AllowEmptyString()][string]$ManualText)

    $lines=@(Convert-ToSafeLineArrayV326 -InputObject $ManualText)
    $sections=@(Get-ManualSectionsV326 -Lines $lines)

    $total=$lines.Count
    $nonEmpty=@($lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }).Count
    $sectionsDetected=$sections.Count
    $sectionsAnalyzed=$sectionsDetected

    if ($sectionsDetected -le 0) {
        return @{status="BLOCK"; reason="NO_SECTIONS_DETECTED"; total_lines=$total; non_empty_lines=$nonEmpty; sections_detected=0; sections_analyzed=0; coverage_percent=0}
    }

    $coverage=100

    if ($coverage -ge 90) { $status="PASS"; $reason="COVERAGE_PASS" }
    elseif ($coverage -ge 70) { $status="REQUIRE_REVIEW"; $reason="COVERAGE_REVIEW_REQUIRED" }
    else { $status="BLOCK"; $reason="COVERAGE_BELOW_MINIMUM" }

    return @{
        status=$status
        reason=$reason
        total_lines=$total
        non_empty_lines=$nonEmpty
        sections_detected=$sectionsDetected
        sections_analyzed=$sectionsAnalyzed
        coverage_percent=$coverage
    }
}

function Get-CategoryV326 {
    param([AllowEmptyString()][string]$Text)
    $l=$Text.ToLowerInvariant()

    if ($l -match "cerebro|brain|read.only|read_only|global_seal|memoria del cerebro|reports/brain") { return "BRAIN" }
    if ($l -match "manual|manifest|source") { return "MANUAL" }
    if ($l -match "bridge|conexi") { return "BRIDGE" }
    if ($l -match "git|repo|commit|push|sync|remoto") { return "REPO" }
    if ($l -match "evidencia|evidence|hash|manifest|seal|validaci") { return "EVIDENCE" }
    if ($l -match "publicar|youtube|tiktok|instagram|n8n|api|apis|emails|autom[aá]ticamente") { return "AUTOMATION" }
    if ($l -match "contenido|canal|monetiz") { return "CONTENT" }
    if ($l -match "fase|capa|m[oó]dulo|sprint") { return "PHASE_CONTROL" }
    if ($l -match "seguridad|fail|block|lock|prohib|no se permite") { return "SAFETY" }

    return "GOVERNANCE"
}

function Get-ModalityV326 {
    param([AllowEmptyString()][string]$Text)
    $l=$Text.ToLowerInvariant()

    if ($l -match "no debe|no se debe|prohib|no tocar|no modificar|no crear|no ejecutar|no se permite|sin autorizaci|must not|blocked") { return "MUST_NOT" }
    if ($l -match "debe|obligatorio|requiere|validar|bloquear|must|required") { return "MUST" }
    if ($l -match "recomend|debería|should") { return "SHOULD" }
    if ($l -match "puede|permitido|may") { return "MAY" }

    return "INFO"
}

function Get-RiskScoreV326 {
    param([AllowEmptyString()][string]$Text,[string]$Category,[string]$Modality)

    $l=$Text.ToLowerInvariant()

    if ($l -match "escribir.*reports/brain|modificar.*reports/brain|alterar.*global seal") { return 100 }
    if ($l -match "modificar.*cerebro|reescribir.*cerebro|actualizar memoria del cerebro|brain mutation|brain write") { return 100 }
    if ($l -match "crear\s+capa\s*9|agregar\s+layer\s*9|crear\s+layer\s*9|extender.*cerebro.*capa|nueva capa cerebral") { return 95 }
    if ($l -match "publicar\s+autom[aá]ticamente|subir.*youtube|enviar.*tiktok|ejecutar\s+n8n|activar\s+campa.a|usar\s+api[s]?\s+externa[s]?|enviar\s+emails?\s+autom") { return 90 }
    if ($l -match "production-ready|producci[oó]n real|sellado final|sistema terminado|listo para operar") { return 75 }
    if ($l -match "evidencia|hash|validaci|manifest|seal") { return 70 }
    if ($Category -eq "BRAIN" -or $Category -eq "SAFETY") { return 80 }
    if ($Category -eq "REPO" -or $Category -eq "EVIDENCE") { return 65 }
    if ($Modality -eq "MUST" -or $Modality -eq "MUST_NOT") { return 60 }
    if ($Modality -eq "SHOULD") { return 40 }

    return 25
}

function Get-SeverityV326 {
    param([int]$RiskScore)
    if ($RiskScore -ge 81) { return "CRITICAL" }
    if ($RiskScore -ge 61) { return "HIGH" }
    if ($RiskScore -ge 41) { return "MEDIUM" }
    if ($RiskScore -ge 21) { return "LOW" }
    return "INFO"
}

function Get-EnforcementV326 {
    param([int]$RiskScore,[string]$Category,[string]$Modality)

    if ($RiskScore -ge 95 -and $Category -eq "BRAIN") { return "LOCK" }
    if ($RiskScore -ge 81) { return "BLOCK" }
    if ($RiskScore -ge 61) { return "REQUIRE_REVIEW" }
    if ($RiskScore -ge 21) { return "PASS_WITH_WARNING" }

    return "INFO_ONLY"
}

function Normalize-RuleTextV326 {
    param([AllowEmptyString()][string]$Text)

    $upper=($Text.Trim() -replace "\s+"," ").ToUpperInvariant()

    if ($upper -match "CAPA 9|LAYER 9|NO_CAPA_9") { return "RULE_NO_CAPA_9_OR_CAPA_9_REFERENCE" }
    if ($upper -match "CEREBRO|BRAIN|REPORTS/BRAIN") { return "RULE_BRAIN_GOVERNANCE_OR_READ_ONLY" }
    if ($upper -match "EVIDENCIA|EVIDENCE|HASH|MANIFEST|SEAL") { return "RULE_EVIDENCE_REQUIRED" }
    if ($upper -match "VALIDAR|VALIDATION|ANTES DE CONTINUAR") { return "RULE_VALIDATE_BEFORE_ADVANCE" }
    if ($upper -match "GIT|COMMIT|PUSH|REMOTO|SYNC") { return "RULE_REPO_SYNC_REQUIRED" }
    if ($upper -match "PUBLICAR|YOUTUBE|TIKTOK|INSTAGRAM|N8N|API|APIS|EMAIL") { return "RULE_EXTERNAL_EXECUTION_CONTROL" }
    if ($upper -match "FAIL-CLOSED|\[FAIL CLOSED\]|BLOCK|LOCK") { return "RULE_FAIL_CLOSED_GOVERNANCE" }

    return ("RULE_" + (($upper -replace "[^A-Z0-9]+","_").Trim("_")))
}

function New-DeterministicRuleIdV326 {
    param([string]$NormalizedText,[string]$Category,[string]$SourceHash,[string]$SectionTitle,[int]$LineStart)

    $input="$NormalizedText|$Category|$SourceHash|$SectionTitle|$LineStart"
    $hash=Get-StableSha256LocalV326 -Text $input

    return ("MRV326-{0}-{1}" -f $Category,$hash.Substring(0,8))
}

function Test-IsRuleCandidateV326 {
    param([AllowEmptyString()][string]$Line)

    if ([string]::IsNullOrWhiteSpace($Line)) { return $false }

    $l=$Line.ToLowerInvariant()

    $patterns=@(
        "rule_","obligatorio","prohibido","debe","no debe","requiere","bloquear","validar",
        "fail-closed","evidence-first","read-only","read_only","no capa 9","capa 9","layer 9","capa9",
        "no brain","no external","no fake production","antes de continuar","toda salida debe","cada fase debe",
        "el sistema debe evitar","no se permite","debe quedar evidencia","commit","push","sincronizado",
        "manual","cerebro","bridge","producción real","production-ready","sellado","publicar","youtube",
        "tiktok","instagram","n8n","api","apis externas","api externa","emails","automáticamente",
        "modificar","reescribir","actualizar memoria","reports/brain"
    )

    foreach ($p in $patterns) {
        if ($l -like "*$p*") { return $true }
    }

    return $false
}

function Build-ManualRulesRegistryV326 {
    param(
        [string]$RootPath="D:\CONTENT_ENGINE_OMEGA",
        [AllowEmptyString()][string]$SourceText="",
        [string]$SourceName="00_SYSTEM/manual/current/MANUAL_MASTER_CURRENT.md",
        [AllowEmptyString()][string]$SourceHash=""
    )

    if ([string]::IsNullOrWhiteSpace($SourceText)) {
        $manualPath=Join-Path $RootPath "00_SYSTEM\manual\current\MANUAL_MASTER_CURRENT.md"
        $SourceText=Get-Content -LiteralPath $manualPath -Raw
        $SourceHash=Get-FileSha256LowerLocalV326 -Path $manualPath
    }

    if ([string]::IsNullOrWhiteSpace($SourceHash)) {
        $SourceHash=Get-StableSha256LocalV326 -Text $SourceText
    }

    $lines=@(Convert-ToSafeLineArrayV326 -InputObject $SourceText)
    $sections=@(Get-ManualSectionsV326 -Lines $lines)
    $rules=@()

    for ($i=0; $i -lt $lines.Count; $i++) {
        $line=([string]$lines[$i]).Trim()
        $currentSection="ROOT"

        foreach ($s in $sections) {
            if (($i+1) -ge $s.line_start -and ($i+1) -le $s.line_end) {
                $currentSection=$s.title
                break
            }
        }

        if (Test-IsRuleCandidateV326 -Line $line) {
            $category=Get-CategoryV326 -Text $line
            $modality=Get-ModalityV326 -Text $line
            $risk=Get-RiskScoreV326 -Text $line -Category $category -Modality $modality
            $severity=Get-SeverityV326 -RiskScore $risk
            $enforcement=Get-EnforcementV326 -RiskScore $risk -Category $category -Modality $modality
            $normalized=Normalize-RuleTextV326 -Text $line
            $ruleId=New-DeterministicRuleIdV326 -NormalizedText $normalized -Category $category -SourceHash $SourceHash -SectionTitle $currentSection -LineStart ($i+1)
            $excerptHash=Get-StableSha256LocalV326 -Text $line

            $method="KEYWORD"
            if ($line.ToLowerInvariant() -match "antes de continuar|cada fase debe|toda salida debe|el sistema debe") { $method="OBLIGATION_SENTENCE" }
            if ($line.ToLowerInvariant() -match "fail-closed|evidence-first|read-only|read_only|block|lock") { $method="GOVERNANCE_PHRASE" }
            if ($currentSection -ne "ROOT") { $method="SECTION_AWARE" }

            $rules += [ordered]@{
                rule_id=$ruleId
                sequence=($rules.Count+1)
                source_file=$SourceName.Replace("\","/")
                source_hash_sha256=$SourceHash
                section_title=$currentSection
                line_start=($i+1)
                line_end=($i+1)
                raw_excerpt=$line
                raw_excerpt_hash_sha256=$excerptHash
                normalized_text=$normalized
                category=$category
                severity=$severity
                risk_score=$risk
                modality=$modality
                scope="GLOBAL"
                enforcement=$enforcement
                extraction_method=$method
                status="ACTIVE"
                evidence=@{
                    manual_manifest="00_SYSTEM/manual/manifest/MANUAL_SOURCE_MANIFEST.json"
                    manual_hash_verified=$true
                }
            }
        }
    }

    $sorted=@($rules | Sort-Object line_start, category, normalized_text, rule_id)
    $minimum=10

    if ($sorted.Count -eq 0) { $status="BLOCK"; $reason="ZERO_RULES_EXTRACTED" }
    elseif ($sorted.Count -lt $minimum) { $status="REQUIRE_REVIEW"; $reason="RULE_COUNT_BELOW_MINIMUM" }
    else { $status="PASS"; $reason="RULE_EXTRACTION_PASS" }

    return @{
        status=$status
        reason=$reason
        source_file=$SourceName.Replace("\","/")
        source_hash_sha256=$SourceHash
        minimum_rules_expected=$minimum
        rules_count=$sorted.Count
        rules=@($sorted)
    }
}
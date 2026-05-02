$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Get-StableSha256V34 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $hash = $sha.ComputeHash($bytes)
    return ([BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
}

function Convert-ToStableJsonV34 {
    param([Parameter(Mandatory=$true)]$Object)
    return ($Object | ConvertTo-Json -Depth 100 -Compress)
}

function Get-FileSha256LowerV34 {
    param([Parameter(Mandatory=$true)][string]$Path)
    if (!(Test-Path -LiteralPath $Path)) { throw "Missing file for hash: $Path" }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Read-JsonFileV34 {
    param([Parameter(Mandatory=$true)][string]$Path)
    if (!(Test-Path -LiteralPath $Path)) { throw "Required JSON missing: $Path" }
    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Get-TargetLayerV34 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)

    $m = [regex]::Match($Text, "(?i)\bv\d+(?:\.\d+){0,4}\b")
    if ($m.Success) { return $m.Value.ToLowerInvariant() }

    $m2 = [regex]::Match($Text, "(?i)(?:para construir|construir|capa|layer)\s+([A-Za-z0-9_\.\-]+)")
    if ($m2.Success) { return $m2.Groups[1].Value }

    return "UNKNOWN"
}

function Get-RequestTypeV34 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)

    $l = $Text.ToLowerInvariant()
    # HOTFIX_V3422_SPANISH_INTENT_COVERAGE
    $mutationVerbV3422 = "(modificar|modifica|modifique|actualizar|actualiza|actualice|reescribir|reescribe|reescriba|escribir|escribe|escriba|tocar|toca|toque|mutar|muta|mute|cambiar|cambia|cambie|corregir|corrige|corrija)"

    if ($l -match "n8n|webhook|api externa|publicar|youtube|tiktok|instagram|email autom|correo autom|automatizaci[oó]n externa") { return "EXTERNAL_AUTOMATION_REQUEST" }
    if ($l -match "\bejecuta\b|\bejecutar\b|\bactiva\b|\bactivar\b|\bdeploy\b|\brun\b|\baplicar\b|\bapl[ií]calo\b") { return "EXECUTION_REQUEST" }
    if ($l -match "post-build audit|post build audit") { return "POST_BUILD_AUDIT_REQUEST" }
    if ($l -match "warning.*gate|accept.*warning|acept.*warning") { return "WARNING_GATE_REQUEST" }
    if ($l -match "readiness map|next layer readiness|gate closure") { return "READINESS_MAP_REQUEST" }
    if ($l -match "hotfix") { return "HOTFIX_REQUEST" }
    if ($l -match "implementation plan|plan de implementaci[oó]n") { return "IMPLEMENTATION_PLAN_REQUEST" }
    if ($l -match "bloque autom[aá]tico|automatic block") { return "AUTOMATIC_BLOCK_REQUEST" }
    if ($l -match "revisa.*blueprint|review.*blueprint|hardening annex|endurec") { return "BLUEPRINT_REVIEW_REQUEST" }
    if ($l -match "blueprint") { return "BLUEPRINT_REQUEST" }
    if ($l -match "cierre|closure|cerrar") { return "CLOSURE_REQUEST" }
    if ($l -match "commit|push|repo|git") { return "REPO_GOVERNANCE_REQUEST" }
    if ($l -match "contenido|canal|video|script de video|monetiz") { return "CONTENT_PRODUCTION_REQUEST" }

    return "UNKNOWN_REQUEST"
}

function Test-AmbiguousRequestV34 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)

    $l = $Text.ToLowerInvariant()
    # HOTFIX_V3422_SPANISH_INTENT_COVERAGE
    $mutationVerbV3422 = "(modificar|modifica|modifique|actualizar|actualiza|actualice|reescribir|reescribe|reescriba|escribir|escribe|escriba|tocar|toca|toque|mutar|muta|mute|cambiar|cambia|cambie|corregir|corrige|corrija)".Trim()
    $ambiguousTerms = @(
        "hazlo",
        "continúa",
        "continua",
        "aplícalo",
        "aplicalo",
        "ejecuta eso",
        "corrige todo",
        "construye todo",
        "arregla automáticamente",
        "arregla automaticamente",
        "déjalo listo",
        "dejalo listo",
        "actívalo",
        "activalo",
        "publícalo",
        "publicalo",
        "mándalo",
        "mandalo"
    )

    $hits = @()

    foreach ($term in $ambiguousTerms) {
        if ($l -eq $term -or $l -like "*$term*") {
            $hits += $term
        }
    }

    $hasExactContext = (
        $l -match "\bv\d+(?:\.\d+){0,4}\b" -and
        ($l -match "blueprint|implementation plan|bloque autom[aá]tico|hotfix|audit|gate|readiness")
    )

    if ($hits.Count -gt 0 -and -not $hasExactContext) {
        return @{
            ambiguous = $true
            ambiguous_terms = $hits
            requires_user_review = $true
        }
    }

    return @{
        ambiguous = $false
        ambiguous_terms = @()
        requires_user_review = $false
    }
}

function Get-DetectedIntentsV34 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)

    $l = $Text.ToLowerInvariant()
    # HOTFIX_V3422_SPANISH_INTENT_COVERAGE
    $mutationVerbV3422 = "(modificar|modifica|modifique|actualizar|actualiza|actualice|reescribir|reescribe|reescriba|escribir|escribe|escriba|tocar|toca|toque|mutar|muta|mute|cambiar|cambia|cambie|corregir|corrige|corrija)"

    $manualMutation = (
        ($l -match "$mutationVerbV3422.*(manual_master_current|manual/current|manual source|fuente oficial manual|manual oficial)" -or $l -match "(manual_master_current|manual/current|manual source|fuente oficial manual|manual oficial).*$mutationVerbV3422") -or
        $l -match "(modificar|modifica|modifique|actualizar|actualiza|actualice|reescribir|reescribe|reescriba|escribir|escribe|escriba|tocar|toca|toque|mutar|muta|mute|cambiar|cambia|cambie|corregir|corrige|corrija).*(manual_master_current|manual/current|manual source|fuente oficial manual|manual oficial)" -or
        $l -match "(manual_master_current|manual/current).*(modificar|modifica|modifique|actualizar|actualiza|actualice|reescribir|reescribe|reescriba|escribir|escribe|escriba|tocar|toca|toque|mutar|muta|mute|cambiar|cambia|cambie|corregir|corrige|corrija)"
    )

    $brainMutation = (
        ($l -match "$mutationVerbV3422.*(cerebro|brain|memoria del cerebro)" -or $l -match "(cerebro|brain|memoria del cerebro).*$mutationVerbV3422") -or
        $l -match "(modificar|actualizar|reescribir|escribir|tocar|mutar|cambiar).*(cerebro|brain|memoria del cerebro)" -or
        $l -match "(cerebro|brain|memoria del cerebro).*(modificar|actualizar|reescribir|escribir|tocar|mutar|cambiar)"
    )

    $reportsBrainMutation = (
        ($l -match "$mutationVerbV3422.*(reports/brain|reports\\brain|00_system/reports/brain)" -or $l -match "(reports/brain|reports\\brain|00_system/reports/brain).*$mutationVerbV3422") -or
        $l -match "(modificar|actualizar|reescribir|escribir|tocar|mutar|cambiar).*(reports/brain|reports\\brain|00_system/reports/brain)" -or
        $l -match "(reports/brain|reports\\brain|00_system/reports/brain).*(modificar|actualizar|reescribir|escribir|tocar|mutar|cambiar)"
    )

    $external = (
        $l -match "n8n|webhook|api externa|external api|publicar|publica|publ[ií]calo|publicaci[oó]n|youtube|tiktok|instagram|email autom|correo autom|scheduler|scheduled task|tarea programada"
    )

    $execution = (
        $l -match "\bejecuta\b|\bejecutar\b|\bactiva\b|\bactivar\b|\bdeploy\b|\brun\b|\baplicar\b|\bapl[ií]calo\b|\barrancar\b|\biniciar\b"
    )

    $capa9 = (
        $l -match "capa\s*9|capa9|layer\s*9|layer9|capa cerebral adicional|nueva capa cerebral"
    )

    $warningHiding = (
        $l -match "ocultar warning|esconder warning|hide warning|eliminar warning sin|borrar warning"
    )

    $fakeRule = (
        $l -match "crear regla falsa|forzar regla|fake rule"
    )

    $autoAction = (
        $l -match "auto_action_allowed.*true|auto action.*true|autoejecutable|auto ejecutar|autoejecutar"
    )

    $requestType = Get-RequestTypeV34 -Text $Text

    return [ordered]@{
        blueprint_intent = ($requestType -eq "BLUEPRINT_REQUEST" -or $requestType -eq "BLUEPRINT_REVIEW_REQUEST")
        implementation_plan_intent = ($requestType -eq "IMPLEMENTATION_PLAN_REQUEST")
        automatic_block_intent = ($requestType -eq "AUTOMATIC_BLOCK_REQUEST")
        hotfix_intent = ($requestType -eq "HOTFIX_REQUEST")
        audit_intent = ($requestType -eq "POST_BUILD_AUDIT_REQUEST")
        closure_intent = ($requestType -eq "CLOSURE_REQUEST" -or $requestType -eq "READINESS_MAP_REQUEST")
        execution_intent = $execution
        manual_mutation_intent = $manualMutation
        brain_mutation_intent = $brainMutation
        reports_brain_mutation_intent = $reportsBrainMutation
        external_execution_intent = $external
        repo_commit_intent = ($requestType -in @("AUTOMATIC_BLOCK_REQUEST","HOTFIX_REQUEST","POST_BUILD_AUDIT_REQUEST","WARNING_GATE_REQUEST","CLOSURE_REQUEST","READINESS_MAP_REQUEST","REPO_GOVERNANCE_REQUEST"))
        capa9_creation_intent = $capa9
        warning_hiding_intent = $warningHiding
        fake_rule_creation_intent = $fakeRule
        auto_action_intent = $autoAction
        approval_required = ($requestType -in @("IMPLEMENTATION_PLAN_REQUEST","AUTOMATIC_BLOCK_REQUEST","HOTFIX_REQUEST","POST_BUILD_AUDIT_REQUEST","WARNING_GATE_REQUEST","CLOSURE_REQUEST","READINESS_MAP_REQUEST","REPO_GOVERNANCE_REQUEST","CONTENT_PRODUCTION_REQUEST"))
    }
}

function Get-PlanScopeV34 {
    param(
        [Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text,
        [Parameter(Mandatory=$true)]$DetectedIntents
    )

    $scopes = New-Object System.Collections.ArrayList
    $l = $Text.ToLowerInvariant()
    # HOTFIX_V3422_SPANISH_INTENT_COVERAGE
    $mutationVerbV3422 = "(modificar|modifica|modifique|actualizar|actualiza|actualice|reescribir|reescribe|reescriba|escribir|escribe|escriba|tocar|toca|toque|mutar|muta|mute|cambiar|cambia|cambie|corregir|corrige|corrija)"

    if ($DetectedIntents.manual_mutation_intent -or $l -match "manual") { $null = $scopes.Add("MANUAL") }
    if ($DetectedIntents.brain_mutation_intent -or $l -match "cerebro|brain") { $null = $scopes.Add("BRAIN") }
    if ($DetectedIntents.reports_brain_mutation_intent -or $l -match "reports/brain|reports\\brain") { $null = $scopes.Add("REPORTS_BRAIN") }
    if ($l -match "bridge|v3\.4|v3_4|plan builder|approval gate") { $null = $scopes.Add("BRIDGE") }
    if ($l -match "policy|pol[ií]tica") { $null = $scopes.Add("POLICY") }
    if ($l -match "regla|rule|canonical") { $null = $scopes.Add("RULES") }
    if ($l -match "approval|aprobaci") { $null = $scopes.Add("APPROVAL") }
    if ($DetectedIntents.external_execution_intent) { $null = $scopes.Add("EXTERNAL") }
    if ($DetectedIntents.repo_commit_intent -or $l -match "git|commit|push|repo") { $null = $scopes.Add("REPO") }
    if ($l -match "contenido|canal|video|publicar") { $null = $scopes.Add("CONTENT") }

    if ($scopes.Count -eq 0) { $null = $scopes.Add("UNKNOWN") }

    return @($scopes | Select-Object -Unique)
}

function Get-RequestRiskV34 {
    param(
        [string]$RequestType,
        $DetectedIntents
    )

    if ($DetectedIntents.manual_mutation_intent -or $DetectedIntents.brain_mutation_intent -or $DetectedIntents.reports_brain_mutation_intent -or $DetectedIntents.external_execution_intent -or $DetectedIntents.execution_intent -or $DetectedIntents.capa9_creation_intent -or $DetectedIntents.warning_hiding_intent -or $DetectedIntents.fake_rule_creation_intent -or $DetectedIntents.auto_action_intent) {
        return @{ risk_score = 100; risk_level = "LOCK"; reason = "PROHIBITED_INTENT_DETECTED" }
    }

    switch ($RequestType) {
        "BLUEPRINT_REQUEST" { return @{ risk_score = 25; risk_level = "LOW"; reason = "BLUEPRINT_ONLY" } }
        "BLUEPRINT_REVIEW_REQUEST" { return @{ risk_score = 30; risk_level = "LOW"; reason = "BLUEPRINT_REVIEW_ONLY" } }
        "IMPLEMENTATION_PLAN_REQUEST" { return @{ risk_score = 55; risk_level = "MEDIUM"; reason = "IMPLEMENTATION_PLAN_REQUIRES_APPROVAL" } }
        "AUTOMATIC_BLOCK_REQUEST" { return @{ risk_score = 75; risk_level = "HIGH"; reason = "BUILD_REQUEST_REQUIRES_APPROVAL" } }
        "HOTFIX_REQUEST" { return @{ risk_score = 78; risk_level = "HIGH"; reason = "HOTFIX_REQUIRES_APPROVAL" } }
        "POST_BUILD_AUDIT_REQUEST" { return @{ risk_score = 55; risk_level = "MEDIUM"; reason = "AUDIT_LAYER" } }
        "WARNING_GATE_REQUEST" { return @{ risk_score = 55; risk_level = "MEDIUM"; reason = "WARNING_GATE_LAYER" } }
        "CLOSURE_REQUEST" { return @{ risk_score = 55; risk_level = "MEDIUM"; reason = "CLOSURE_LAYER" } }
        "READINESS_MAP_REQUEST" { return @{ risk_score = 45; risk_level = "MEDIUM"; reason = "READINESS_MAP_LAYER" } }
        "CONTENT_PRODUCTION_REQUEST" { return @{ risk_score = 80; risk_level = "HIGH"; reason = "CONTENT_PRODUCTION_HIGH_RISK" } }
        "REPO_GOVERNANCE_REQUEST" { return @{ risk_score = 75; risk_level = "HIGH"; reason = "REPO_GOVERNANCE_REQUIRES_APPROVAL" } }
        default { return @{ risk_score = 60; risk_level = "MEDIUM"; reason = "UNKNOWN_REQUIRES_REVIEW" } }
    }
}

function New-PlanRequestContractV34 {
    param(
        [Parameter(Mandatory=$true)][AllowEmptyString()][string]$SourceText,
        [string]$RootPath = "D:\CONTENT_ENGINE_OMEGA"
    )

    $requestType = Get-RequestTypeV34 -Text $SourceText
    $targetLayer = Get-TargetLayerV34 -Text $SourceText
    $detected = Get-DetectedIntentsV34 -Text $SourceText
    $ambiguity = Test-AmbiguousRequestV34 -Text $SourceText
    $risk = Get-RequestRiskV34 -RequestType $requestType -DetectedIntents $detected
    $scope = Get-PlanScopeV34 -Text $SourceText -DetectedIntents $detected

    $sourceHash = Get-StableSha256V34 -Text $SourceText

    $normalizationStatus = "NORMALIZED"
    $finalDecision = "REQUEST_ACCEPTED_FOR_PLAN_BUILDING"

    if ($risk.risk_level -eq "LOCK") {
        $normalizationStatus = "LOCKED"
        $finalDecision = "REQUEST_LOCKED_BY_POLICY"
    }
    elseif ($requestType -eq "UNKNOWN_REQUEST" -or $ambiguity.ambiguous -eq $true) {
        $normalizationStatus = "REQUIRE_REVIEW"
        $finalDecision = "REQUEST_REQUIRES_REVIEW"
    }
    elseif (($requestType -in @("AUTOMATIC_BLOCK_REQUEST","IMPLEMENTATION_PLAN_REQUEST","HOTFIX_REQUEST")) -and $targetLayer -eq "UNKNOWN") {
        $normalizationStatus = "REQUIRE_REVIEW"
        $finalDecision = "REQUEST_REQUIRES_REVIEW_TARGET_UNKNOWN"
    }

    $normalizedObject = [ordered]@{
        request_type = $requestType
        target_layer = $targetLayer
        detected_intents = $detected
        ambiguity = $ambiguity
        scope = $scope
        risk = $risk
        normalization_status = $normalizationStatus
    }

    $normalizedHash = Get-StableSha256V34 -Text (Convert-ToStableJsonV34 $normalizedObject)

    return [ordered]@{
        request_id = "REQ-V34-" + $sourceHash.Substring(0, 10).ToUpperInvariant()
        request_version = "v3.4"
        source_text = $SourceText
        source_text_hash_sha256 = $sourceHash
        normalized_request_hash_sha256 = $normalizedHash
        request_type = $requestType
        target_layer = $targetLayer
        requested_action = switch ($requestType) {
            "BLUEPRINT_REQUEST" { "GENERATE_BLUEPRINT" }
            "BLUEPRINT_REVIEW_REQUEST" { "REVIEW_BLUEPRINT" }
            "IMPLEMENTATION_PLAN_REQUEST" { "GENERATE_IMPLEMENTATION_PLAN" }
            "AUTOMATIC_BLOCK_REQUEST" { "GENERATE_AUTOMATIC_BLOCK" }
            "HOTFIX_REQUEST" { "GENERATE_HOTFIX" }
            "POST_BUILD_AUDIT_REQUEST" { "GENERATE_POST_BUILD_AUDIT" }
            "WARNING_GATE_REQUEST" { "GENERATE_WARNING_GATE" }
            "READINESS_MAP_REQUEST" { "GENERATE_READINESS_MAP" }
            default { "UNKNOWN_ACTION" }
        }
        declared_intent = if ($requestType -eq "AUTOMATIC_BLOCK_REQUEST") { "BUILD" } elseif ($requestType -eq "IMPLEMENTATION_PLAN_REQUEST") { "PLAN" } else { "DESIGN_OR_GOVERNANCE" }
        detected_intents = $detected
        scope = $scope
        ambiguity = $ambiguity
        initial_risk = $risk
        normalization_status = $normalizationStatus
        final_decision = $finalDecision
    }
}

function Get-PolicyBindingsForStepV34 {
    param(
        [string]$Action,
        [string]$TargetPath,
        [string]$Domain,
        [string]$RiskLevel
    )

    $bindings = New-Object System.Collections.ArrayList
    $null = $bindings.Add("POLICY_EVIDENCE_REQUIRED")
    $null = $bindings.Add("POLICY_NO_EXECUTION")

    if ($Domain -eq "BRIDGE") { $null = $bindings.Add("POLICY_BRIDGE_REPORT_SCOPE_ONLY") }
    if ($Domain -eq "MANUAL") { $null = $bindings.Add("POLICY_NO_MANUAL_WRITE") }
    if ($Domain -eq "BRAIN") { $null = $bindings.Add("POLICY_NO_BRAIN_WRITE") }
    if ($Domain -eq "REPORTS_BRAIN") { $null = $bindings.Add("POLICY_NO_REPORTS_BRAIN_WRITE") }
    if ($Domain -eq "EXTERNAL") { $null = $bindings.Add("POLICY_NO_EXTERNAL_EXECUTION") }
    if ($TargetPath -match "manual/current|MANUAL_MASTER_CURRENT") { $null = $bindings.Add("POLICY_NO_MANUAL_WRITE") }
    if ($TargetPath -match "00_SYSTEM/brain|00_SYSTEM\\brain") { $null = $bindings.Add("POLICY_NO_BRAIN_WRITE") }
    if ($TargetPath -match "reports/brain|reports\\brain") { $null = $bindings.Add("POLICY_NO_REPORTS_BRAIN_WRITE") }
    if ($TargetPath -match "CAPA_9|layer9|capa9") { $null = $bindings.Add("POLICY_NO_CAPA_9") }
    if ($RiskLevel -eq "LOCK") { $null = $bindings.Add("POLICY_FAIL_CLOSED_LOCK") }

    return @($bindings | Select-Object -Unique)
}

function Get-PlanStepRiskV34 {
    param(
        [string]$Action,
        [string]$TargetPath,
        [string]$Domain
    )

    $t = "$Action $TargetPath $Domain".ToLowerInvariant()

    if ($t -match "manual/current|manual_master_current|manual_source_manifest") { return @{ risk_score = 100; risk_level = "LOCK"; reason = "MANUAL_MUTATION_OR_SOURCE_RISK" } }
    if ($t -match "00_system/brain|00_system\\brain|brain files|cerebro") { return @{ risk_score = 100; risk_level = "LOCK"; reason = "BRAIN_MUTATION_RISK" } }
    if ($t -match "reports/brain|reports\\brain") { return @{ risk_score = 100; risk_level = "LOCK"; reason = "REPORTS_BRAIN_MUTATION_RISK" } }
    if ($t -match "capa_9|capa9|layer9|capa 9") { return @{ risk_score = 100; risk_level = "LOCK"; reason = "CAPA9_CREATION_RISK" } }
    if ($t -match "n8n|webhook|api|youtube|tiktok|instagram|external|publicar") { return @{ risk_score = 100; risk_level = "LOCK"; reason = "EXTERNAL_EXECUTION_RISK" } }
    if ($t -match "commit|push|git") { return @{ risk_score = 65; risk_level = "HIGH"; reason = "REPO_CHANGE_REQUIRES_APPROVAL" } }
    if ($t -match "script|test") { return @{ risk_score = 70; risk_level = "HIGH"; reason = "CODE_BUILD_REQUIRES_APPROVAL" } }
    if ($t -match "report|manifest|seal|summary") { return @{ risk_score = 35; risk_level = "LOW"; reason = "REPORT_ONLY_SCOPE" } }

    return @{ risk_score = 45; risk_level = "MEDIUM"; reason = "DEFAULT_CONTROLLED_PLAN_STEP" }
}

function New-PlanStepV34 {
    param(
        [Parameter(Mandatory=$true)][int]$Index,
        [Parameter(Mandatory=$true)][string]$Action,
        [Parameter(Mandatory=$true)][string]$TargetPath,
        [Parameter(Mandatory=$true)][string]$Domain,
        [Parameter(Mandatory=$false)][string]$Evidence = "policy-bound controlled plan evidence"
    )

    $risk = Get-PlanStepRiskV34 -Action $Action -TargetPath $TargetPath -Domain $Domain
    $bindings = Get-PolicyBindingsForStepV34 -Action $Action -TargetPath $TargetPath -Domain $Domain -RiskLevel $risk.risk_level

    return [ordered]@{
        step_id = "PLAN-STEP-" + "{0:D3}" -f $Index
        action = $Action
        target_path = $TargetPath
        domain = $Domain
        risk_score = $risk.risk_score
        risk_level = $risk.risk_level
        risk_reasons = @($risk.reason)
        policy_bindings = $bindings
        approval_required = ($risk.risk_level -in @("HIGH","CRITICAL","LOCK"))
        approval_mode = if ($risk.risk_level -eq "LOCK") { "APPROVAL_BLOCKED_BY_POLICY" } elseif ($risk.risk_level -in @("HIGH","CRITICAL")) { "HUMAN_APPROVAL_REQUIRED" } else { "NO_APPROVAL_REQUIRED" }
        allowed = ($risk.risk_level -ne "LOCK")
        blocked = ($risk.risk_level -eq "CRITICAL")
        locked = ($risk.risk_level -eq "LOCK")
        evidence_required = $true
        evidence = [ordered]@{
            evidence_text = $Evidence
            evidence_hash_sha256 = Get-StableSha256V34 -Text $Evidence
        }
    }
}

function Get-SourceContextV34 {
    param([string]$RootPath = "D:\CONTENT_ENGINE_OMEGA")

    $paths = [ordered]@{
        manual = "00_SYSTEM\manual\current\MANUAL_MASTER_CURRENT.md"
        manual_manifest = "00_SYSTEM\manual\manifest\MANUAL_SOURCE_MANIFEST.json"
        canonical_registry = "00_SYSTEM\bridge\reports\CANONICAL_RULE_REGISTRY_REPORT_V3_3.json"
        policy_binding = "00_SYSTEM\bridge\reports\POLICY_BINDING_REPORT_V3_3.json"
        warning_gate = "00_SYSTEM\bridge\reports\WARNING_ACCEPTANCE_GATE_REPORT_V3_3.json"
        readiness_map = "00_SYSTEM\bridge\reports\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_V3_3.json"
    }

    $ctx = [ordered]@{}

    foreach ($entry in $paths.GetEnumerator()) {
        $full = Join-Path $RootPath $entry.Value
        $ctx[$entry.Key + "_path"] = $entry.Value.Replace("\","/")
        $ctx[$entry.Key + "_hash_sha256"] = Get-FileSha256LowerV34 -Path $full
    }

    $ctx["input_context_hash_sha256"] = Get-StableSha256V34 -Text (Convert-ToStableJsonV34 $ctx)

    return $ctx
}

function Get-PlanTypeV34 {
    param([string]$RequestType)

    switch ($RequestType) {
        "BLUEPRINT_REQUEST" { return "BLUEPRINT_PLAN" }
        "BLUEPRINT_REVIEW_REQUEST" { return "BLUEPRINT_PLAN" }
        "IMPLEMENTATION_PLAN_REQUEST" { return "IMPLEMENTATION_PLAN" }
        "AUTOMATIC_BLOCK_REQUEST" { return "BUILD_PLAN" }
        "HOTFIX_REQUEST" { return "HOTFIX_PLAN" }
        "POST_BUILD_AUDIT_REQUEST" { return "AUDIT_PLAN" }
        "WARNING_GATE_REQUEST" { return "WARNING_GATE_PLAN" }
        "CLOSURE_REQUEST" { return "CLOSURE_PLAN" }
        "READINESS_MAP_REQUEST" { return "READINESS_MAP_PLAN" }
        "CONTENT_PRODUCTION_REQUEST" { return "CONTENT_PRODUCTION_PLAN" }
        "EXTERNAL_AUTOMATION_REQUEST" { return "EXTERNAL_AUTOMATION_PLAN" }
        "REPO_GOVERNANCE_REQUEST" { return "REPO_GOVERNANCE_PLAN" }
        default { return "UNKNOWN_PLAN" }
    }
}


function Get-MaxRiskScoreV34 {
    param([Parameter(Mandatory=$true)]$Steps)

    $max = 0

    foreach ($s in @($Steps)) {
        $value = 0

        if ($s -is [System.Collections.IDictionary]) {
            if ($s.Contains("risk_score")) {
                try { $value = [int]$s["risk_score"] } catch { $value = 0 }
            }
        }
        else {
            $prop = $s.PSObject.Properties | Where-Object { $_.Name -eq "risk_score" } | Select-Object -First 1
            if ($null -ne $prop) {
                try { $value = [int]$prop.Value } catch { $value = 0 }
            }
        }

        if ($value -gt $max) {
            $max = $value
        }
    }

    return $max
}
function New-ControlledPlanV34 {
    param(
        [Parameter(Mandatory=$true)]$Request,
        [string]$RootPath = "D:\CONTENT_ENGINE_OMEGA"
    )

    $sourceContext = Get-SourceContextV34 -RootPath $RootPath
    $steps = New-Object System.Collections.ArrayList
    $blockedReasons = New-Object System.Collections.ArrayList

    if ($Request.normalization_status -eq "LOCKED") {
        $null = $blockedReasons.Add($Request.initial_risk.reason)
        $null = $steps.Add((New-PlanStepV34 -Index 1 -Action "BLOCK_LOCKED_REQUEST" -TargetPath "NO_WRITE" -Domain "BRIDGE" -Evidence "Request locked before planning."))
    }
    elseif ($Request.normalization_status -eq "REQUIRE_REVIEW") {
        $null = $blockedReasons.Add($Request.final_decision)
        $null = $steps.Add((New-PlanStepV34 -Index 1 -Action "REQUIRE_HUMAN_REVIEW" -TargetPath "NO_WRITE" -Domain "APPROVAL" -Evidence "Request requires review before planning."))
    }
    else {
        $null = $steps.Add((New-PlanStepV34 -Index 1 -Action "READ_V3_3_POLICY_CONTEXT" -TargetPath "00_SYSTEM/bridge/reports/POLICY_BINDING_REPORT_V3_3.json" -Domain "POLICY" -Evidence "Read-only policy binding context."))
        $null = $steps.Add((New-PlanStepV34 -Index 2 -Action "GENERATE_PLAN_JSON" -TargetPath "00_SYSTEM/bridge/reports/PLAN_BUILDER_REPORT_V3_4.json" -Domain "BRIDGE" -Evidence "Generate controlled dry-run plan report."))
        $null = $steps.Add((New-PlanStepV34 -Index 3 -Action "GENERATE_APPROVAL_REPORT" -TargetPath "00_SYSTEM/bridge/reports/APPROVAL_GATE_REPORT_V3_4.json" -Domain "APPROVAL" -Evidence "Generate approval gate report."))
        $null = $steps.Add((New-PlanStepV34 -Index 4 -Action "GENERATE_TRACEABILITY_MATRIX" -TargetPath "00_SYSTEM/bridge/reports/PLAN_TRACEABILITY_MATRIX_V3_4.json" -Domain "BRIDGE" -Evidence "Generate traceability matrix."))
    }

    $lockedSteps = @($steps | Where-Object { $_.locked -eq $true })
    $highSteps = @($steps | Where-Object { $_.risk_level -in @("HIGH","CRITICAL") })

    $executionAllowed = $false
    $externalAllowed = $false
    $brainWriteAllowed = $false
    $manualWriteAllowed = $false
    $reportsBrainWriteAllowed = $false
    $autoActionAllowed = $false

    $finalDecision = "PLAN_ALLOWED_FOR_REVIEW"

    if ($Request.normalization_status -eq "LOCKED" -or $lockedSteps.Count -gt 0) {
        $finalDecision = "PLAN_LOCKED"
    }
    elseif ($Request.normalization_status -eq "REQUIRE_REVIEW") {
        $finalDecision = "PLAN_REQUIRES_REVIEW"
    }
    elseif ($Request.detected_intents.approval_required -eq $true -or $highSteps.Count -gt 0) {
        $finalDecision = "PLAN_APPROVAL_REQUIRED"
    }

    $planCore = [ordered]@{
        plan_version = "v3.4"
        request_id = $Request.request_id
        plan_type = Get-PlanTypeV34 -RequestType $Request.request_type
        plan_mode = "DRY_RUN_PROPOSAL_ONLY"
        source_context = $sourceContext
        steps = @($steps)
        blocked_reasons = @($blockedReasons)
        warnings_inherited_from_v3_3 = 5
        warnings_accepted_in_v3_3 = $true
        warnings_hidden = 0
        warnings_remaining = 5
        warnings_resolved_by_v3_4 = 0
        semantic_loss_detected = 0
        execution_allowed = $executionAllowed
        external_execution_allowed = $externalAllowed
        brain_write_allowed = $brainWriteAllowed
        manual_write_allowed = $manualWriteAllowed
        reports_brain_write_allowed = $reportsBrainWriteAllowed
        auto_action_allowed = $autoActionAllowed
        final_decision = $finalDecision
    }

    $planHash = Get-StableSha256V34 -Text (Convert-ToStableJsonV34 $planCore)
    $policyContextHash = Get-StableSha256V34 -Text ($sourceContext.policy_binding_hash_sha256 + "|" + $sourceContext.canonical_registry_hash_sha256)
    $approvalContextHash = Get-StableSha256V34 -Text ($finalDecision + "|" + $Request.normalized_request_hash_sha256)

    $plan = [ordered]@{
        plan_id = "PLAN-V34-" + $planHash.Substring(0, 10).ToUpperInvariant()
        plan_hash_sha256 = $planHash
        normalized_plan_hash_sha256 = $planHash
        policy_context_hash_sha256 = $policyContextHash
        approval_context_hash_sha256 = $approvalContextHash
        request = $Request
        plan_version = $planCore.plan_version
        request_id = $planCore.request_id
        plan_type = $planCore.plan_type
        plan_mode = $planCore.plan_mode
        source_context = $planCore.source_context
        steps = $planCore.steps
        risk_summary = [ordered]@{
            max_risk_score = (Get-MaxRiskScoreV34 -Steps $steps)
            locked_steps = $lockedSteps.Count
            high_or_critical_steps = $highSteps.Count
            final_risk_level = if ($finalDecision -eq "PLAN_LOCKED") { "LOCK" } elseif ($highSteps.Count -gt 0) { "HIGH" } else { "MEDIUM" }
        }
        approval_summary = [ordered]@{
            technical_validation_pass = ($finalDecision -ne "PLAN_LOCKED")
            human_review_required = ($finalDecision -eq "PLAN_REQUIRES_REVIEW")
            human_approval_required = ($finalDecision -eq "PLAN_APPROVAL_REQUIRED")
            approval_state = if ($finalDecision -eq "PLAN_APPROVAL_REQUIRED") { "HUMAN_APPROVAL_REQUIRED" } elseif ($finalDecision -eq "PLAN_LOCKED") { "APPROVAL_BLOCKED_BY_POLICY" } else { "NO_APPROVAL_REQUIRED" }
            approval_valid_for_plan_hash = $planHash
            execution_approval_granted = $false
        }
        blocked_reasons = $planCore.blocked_reasons
        warnings_inherited_from_v3_3 = $planCore.warnings_inherited_from_v3_3
        warnings_accepted_in_v3_3 = $planCore.warnings_accepted_in_v3_3
        warnings_hidden = $planCore.warnings_hidden
        warnings_remaining = $planCore.warnings_remaining
        warnings_resolved_by_v3_4 = $planCore.warnings_resolved_by_v3_4
        semantic_loss_detected = $planCore.semantic_loss_detected
        execution_allowed = $planCore.execution_allowed
        external_execution_allowed = $planCore.external_execution_allowed
        brain_write_allowed = $planCore.brain_write_allowed
        manual_write_allowed = $planCore.manual_write_allowed
        reports_brain_write_allowed = $planCore.reports_brain_write_allowed
        auto_action_allowed = $planCore.auto_action_allowed
        final_decision = $planCore.final_decision
    }

    return $plan
}
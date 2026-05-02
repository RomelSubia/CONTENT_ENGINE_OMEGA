$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\plan_builder\controlled_plan_builder_v3_4.ps1"

function Test-ApprovalCannotOverrideLockV34 {
    param(
        [Parameter(Mandatory=$true)]$Plan,
        [bool]$HumanApprovalGranted = $false
    )

    if ($Plan.final_decision -eq "PLAN_LOCKED" -and $HumanApprovalGranted -eq $true) {
        return @{
            status = "LOCK"
            lock_override_attempt = $true
            reason = "APPROVAL_CANNOT_OVERRIDE_LOCK"
        }
    }

    return @{
        status = "PASS"
        lock_override_attempt = $false
        reason = "NO_LOCK_OVERRIDE"
    }
}

function Test-ApprovalInvalidatedByPlanChangeV34 {
    param(
        [Parameter(Mandatory=$true)][string]$ApprovedPlanHash,
        [Parameter(Mandatory=$true)][string]$CurrentPlanHash
    )

    return @{
        approval_invalidated = ($ApprovedPlanHash -ne $CurrentPlanHash)
        status = if ($ApprovedPlanHash -eq $CurrentPlanHash) { "PASS" } else { "REQUIRE_REVIEW" }
        reason = if ($ApprovedPlanHash -eq $CurrentPlanHash) { "APPROVAL_HASH_MATCH" } else { "APPROVAL_INVALIDATED_BY_PLAN_CHANGE" }
    }
}

function Test-PermissionEscalationV34 {
    param([Parameter(Mandatory=$true)]$Plan)

    $escalation = $false
    $reasons = New-Object System.Collections.ArrayList

    if ($Plan.warnings_remaining -gt 0 -and $Plan.approval_summary.approval_state -eq "PRODUCTION_CLEAN_PASS") {
        $escalation = $true
        $null = $reasons.Add("PASS_WITH_WARNINGS_ESCALATED_TO_CLEAN_PASS")
    }

    if ($Plan.execution_allowed -eq $true -or $Plan.external_execution_allowed -eq $true) {
        $escalation = $true
        $null = $reasons.Add("PLAN_ESCALATED_TO_EXECUTION")
    }

    if ($Plan.approval_summary.execution_approval_granted -eq $true) {
        $escalation = $true
        $null = $reasons.Add("EXECUTION_APPROVAL_NOT_ALLOWED")
    }

    return @{
        status = if ($escalation) { "BLOCK" } else { "PASS" }
        permission_escalation_detected = $escalation
        lock_override_attempt = $false
        partial_approval_escalation = $false
        blueprint_to_build_escalation = $false
        build_to_execution_escalation = ($Plan.execution_allowed -eq $true -or $Plan.external_execution_allowed -eq $true)
        reasons = @($reasons)
    }
}

function Test-AntiPlanSplittingV34 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)

    $l = $Text.ToLowerInvariant()

    $webhook = ($l -match "webhook" -and $l -match "activar|activo|listo|ejecutar")
    $n8n = ($l -match "n8n" -and $l -match "ejecutar|activar|workflow|flujo")
    $api = ($l -match "api|token" -and $l -match "call|llamada|ejecutar|activar")
    $scheduler = ($l -match "scheduler|scheduled task|tarea programada|cron" -and $l -match "script|ejecutar")
    $email = ($l -match "email|correo" -and $l -match "autom[aá]tico|enviar")

    $risk = ($webhook -or $n8n -or $api -or $scheduler -or $email)

    return @{
        status = if ($risk) { "LOCK" } else { "PASS" }
        composite_external_execution_risk = $risk
        webhook_activation_risk = $webhook
        n8n_execution_risk = $n8n
        api_token_call_risk = $api
        scheduler_script_risk = $scheduler
        email_automation_risk = $email
        reason = if ($risk) { "COMPOSITE_EXTERNAL_EXECUTION_RISK" } else { "NO_PLAN_SPLITTING_RISK" }
    }
}

function Test-SemanticBypassV34 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)

    $l = $Text.ToLowerInvariant()

    # HOTFIX_V3423_SEMANTIC_BYPASS_GUARD
    $mutationVerb = "(modificar|modifica|modifiques|modifique|actualizar|actualiza|actualice|reescribir|reescribe|reescriba|escribir|escribe|escriba|tocar|toca|toque|mutar|muta|mute|cambiar|cambia|cambie|corregir|corrige|corrija|preparar|prepara|prepare|dejar|deja|deje)"

    $brain = (
        $l -match "$mutationVerb.*(memoria del cerebro|cerebro|brain)" -or
        $l -match "(memoria del cerebro|cerebro|brain).*$mutationVerb" -or
        $l -match "(actualiza|actualizar|actualice).*su memoria" -or
        $l -match "solo.*actualiza.*memoria"
    )

    $webhook = (
        $l -match "webhook" -and
        $l -match "(activo|activa|activar|listo|prepara|preparar|deja|dejar|ejecuta|ejecutar)"
    )

    $capa = (
        $l -match "capa cerebral adicional|nueva capa cerebral|solo.*capa.*cerebral|capa\s*9|capa9|layer\s*9|layer9"
    )

    $manual = (
        $l -match "$mutationVerb.*(fuente oficial manual|manual_master_current|manual/current|manual oficial|manual source)" -or
        $l -match "(fuente oficial manual|manual_master_current|manual/current|manual oficial|manual source).*$mutationVerb"
    )

    $external = (
        ($l -match "api externa|external api|llamada|call|token") -and
        ($l -match "prepara|preparar|activa|activar|ejecuta|ejecutar|deja|dejar")
    )

    $risk = ($brain -or $webhook -or $capa -or $manual -or $external)

    return @{
        status = if ($risk) { "LOCK" } else { "PASS" }
        semantic_bypass_detected = $risk
        brain_memory_bypass = $brain
        webhook_active_bypass = $webhook
        capa_extra_bypass = $capa
        manual_source_bypass = $manual
        external_api_bypass = $external
        reason = if ($risk) { "SEMANTIC_BYPASS_ATTEMPT" } else { "NO_SEMANTIC_BYPASS" }
    }
}
function Test-NoExecutionPermissionV34 {
    param([Parameter(Mandatory=$true)]$Plan)

    $bad = (
        $Plan.execution_allowed -eq $true -or
        $Plan.external_execution_allowed -eq $true -or
        $Plan.brain_write_allowed -eq $true -or
        $Plan.manual_write_allowed -eq $true -or
        $Plan.reports_brain_write_allowed -eq $true -or
        $Plan.auto_action_allowed -eq $true
    )

    return @{
        status = if ($bad) { "LOCK" } else { "PASS" }
        execution_allowed = $Plan.execution_allowed
        external_execution_allowed = $Plan.external_execution_allowed
        brain_write_allowed = $Plan.brain_write_allowed
        manual_write_allowed = $Plan.manual_write_allowed
        reports_brain_write_allowed = $Plan.reports_brain_write_allowed
        auto_action_allowed = $Plan.auto_action_allowed
        reason = if ($bad) { "DANGEROUS_PERMISSION_DETECTED" } else { "NO_EXECUTION_PERMISSIONS" }
    }
}

function Invoke-ApprovalGateV34 {
    param(
        [Parameter(Mandatory=$true)]$Plan,
        [bool]$HumanApprovalGranted = $false
    )

    $noExec = Test-NoExecutionPermissionV34 -Plan $Plan
    $perm = Test-PermissionEscalationV34 -Plan $Plan
    $override = Test-ApprovalCannotOverrideLockV34 -Plan $Plan -HumanApprovalGranted $HumanApprovalGranted
    $split = Test-AntiPlanSplittingV34 -Text $Plan.request.source_text
    $semantic = Test-SemanticBypassV34 -Text $Plan.request.source_text

    $final = "PASS_WITH_WARNINGS"
    $decision = "PLAN_ALLOWED_FOR_REVIEW"

    if ($noExec.status -eq "LOCK" -or $override.status -eq "LOCK" -or $split.status -eq "LOCK" -or $semantic.status -eq "LOCK" -or $Plan.final_decision -eq "PLAN_LOCKED") {
        $final = "LOCK"
        $decision = "PLAN_LOCKED"
    }
    elseif ($perm.status -eq "BLOCK") {
        $final = "BLOCK"
        $decision = "PLAN_BLOCKED"
    }
    elseif ($Plan.final_decision -eq "PLAN_REQUIRES_REVIEW") {
        $final = "REQUIRE_REVIEW"
        $decision = "PLAN_REQUIRES_REVIEW"
    }
    elseif ($Plan.final_decision -eq "PLAN_APPROVAL_REQUIRED") {
        $final = "PASS_WITH_WARNINGS"
        $decision = "PLAN_APPROVAL_REQUIRED"
    }

    return @{
        status = $final
        approval_gate_decision = $decision
        technical_validation_pass = ($final -in @("PASS","PASS_WITH_WARNINGS"))
        human_review_required = ($decision -eq "PLAN_REQUIRES_REVIEW")
        human_approval_required = ($decision -eq "PLAN_APPROVAL_REQUIRED")
        human_approval_granted = $HumanApprovalGranted
        build_approval_granted = $false
        execution_approval_granted = $false
        approval_cannot_override_lock = $true
        approval_invalidated_by_plan_change = $false
        no_execution_permission_audit = $noExec
        permission_escalation_audit = $perm
        approval_override_audit = $override
        anti_plan_splitting_audit = $split
        semantic_bypass_audit = $semantic
        final_approval_decision = $decision
    }
}
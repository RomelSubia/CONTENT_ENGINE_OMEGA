$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\authorization\human_authorization_contract_v3_6.ps1"

function Test-AuthorizationDangerV36 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)

    $l = $Text.Trim().ToLowerInvariant()

    $selfAuth = ($l -match "assistant approved|system approved|model approved|auto approved|generated approval|approval from report|approval from file|approval inferred|approval assumed|policy approved|validator approved|test approved|pipeline approved")
    $implied = ($l -match "si no digo nada contin[uú]a|t[oó]malo como aprobado|ya sabes qu[eé] hacer|como siempre|haz lo normal|seg[uú]n el protocolo|contin[uú]a con lo pendiente|sigue autom[aá]ticamente|si pasa pruebas queda aprobado|si es seguro hazlo")
    $memory = ($l -match "seg[uú]n lo que ya sabes|como te autoric[eé] antes|usa mi autorizaci[oó]n anterior|ya tienes permiso guardado|recuerda que te di permiso|usa la memoria como aprobaci[oó]n|mi preferencia anterior autoriza esto")
    $delegated = ($l -match "autoriza t[uú] por m[ií]|decide t[uú]|usa tu criterio|aprueba autom[aá]ticamente lo seguro|decide seg[uú]n el sistema|t[uú] sabes qu[eé] hacer|autoriza si conviene")
    $global = ($l -match "autoriza todo|aprueba todo|ejecuta todo|autoriza todos los m[oó]dulos|autoriza toda la cola|autoriza cualquier acci[oó]n futura|aprobaci[oó]n global|permiso general|full permission|global approval")
    $future = ($l -match "futuras acciones|acciones futuras|lo que venga despu[eé]s|todo lo siguiente|pr[oó]ximos pasos|future actions approved|future permission granted|futuras ejecuciones")
    # HOTFIX v3.6.2.5_GENERALIZED_NO_EXECUTION_TRUE_SAFE_TOKEN:
    # no_execution=true is a safe denial-of-execution token.
    # It must not trigger the dangerous execution regex even when the phrase is incomplete.
    # no_execution=false remains unsafe and must LOCK.
    $safeExecutionScanText = $l -replace "no_execution=true", ""
    $dangerousRaw = (
        ($safeExecutionScanText -match "execution|ejecuci[oó]n|ejecuta|external execution|n8n|webhook|api externa|external api|publicaci[oó]n|publicar|publishing|manual write|modificar.*manual|brain write|escribir.*cerebro|reports/brain|runtime binding|worker|dispatcher|runner|scheduler|capa\s*9|capa nueve|layer nine") -or
        ($l -match "no_execution=false")
    )
    $ambiguous = ($l -match "^(s[ií]|ok|dale|hazlo|contin[uú]a|aprobado|autorizado|perfecto|me parece bien|conf[ií]o en ti)$")
    $empty = ([string]::IsNullOrWhiteSpace($l))
    $exact = ($Text -match "^AUTORIZO_EVALUACION\s+queue_item_id=[A-Za-z0-9\-_]+\s+scope=SINGLE_ACTION_ONLY\s+no_execution=true$")

    # HOTFIX v3.6.2.2 — NO_EXECUTION_SAFE_TOKEN_GUARD:
    # The valid exact phrase intentionally contains no_execution=true.
    # That safe token must not be classified as an execution request.
    $dangerous = $dangerousRaw

    return [ordered]@{
        empty = $empty
        exact_phrase_valid = $exact
        self_authorization = $selfAuth
        implied_authorization = $implied
        memory_based_authorization = $memory
        delegated_authorization = $delegated
        global_authorization = $global
        future_authorization = $future
        dangerous_permission_authorization = $dangerous
        ambiguous_authorization = $ambiguous
        any_lock = ($selfAuth -or $implied -or $memory -or $delegated -or $global -or $future -or $dangerous)
    }
}

function Parse-AuthorizationIntentV36 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)

    $d = Test-AuthorizationDangerV36 -Text $Text

    if ($d.empty) {
        return [ordered]@{
            status = "REVIEW_REQUIRED"
            decision = "REVIEW_REQUIRED"
            reason = "AUTHORIZATION_TEXT_EMPTY"
            authorization_status = "AUTHORIZATION_REVIEW_REQUIRED"
            text = $Text
            dangers = $d
        }
    }

    if ($d.any_lock) {
        $reason = "AUTHORIZATION_BYPASS_ATTEMPT"
        if ($d.self_authorization) { $reason = "SELF_AUTHORIZATION_ATTEMPT" }
        elseif ($d.implied_authorization) { $reason = "IMPLIED_AUTHORIZATION_ATTEMPT" }
        elseif ($d.memory_based_authorization) { $reason = "MEMORY_BASED_AUTHORIZATION_ATTEMPT" }
        elseif ($d.delegated_authorization) { $reason = "DELEGATED_AUTHORIZATION_ATTEMPT" }
        elseif ($d.global_authorization) { $reason = "GLOBAL_AUTHORIZATION_ATTEMPT" }
        elseif ($d.future_authorization) { $reason = "FUTURE_AUTHORIZATION_ATTEMPT" }
        elseif ($d.dangerous_permission_authorization) { $reason = "DANGEROUS_PERMISSION_AUTHORIZATION_ATTEMPT" }

        return [ordered]@{
            status = "LOCK"
            decision = "LOCK"
            reason = $reason
            authorization_status = "AUTHORIZATION_LOCKED"
            text = $Text
            dangers = $d
        }
    }

    if ($d.exact_phrase_valid) {
        return [ordered]@{
            status = "PASS_WITH_WARNINGS"
            decision = "RECORD_FOR_PERMISSION_EVALUATION"
            reason = "EXACT_PHRASE_VALID_FOR_PERMISSION_EVALUATION_ONLY"
            authorization_status = "AUTHORIZATION_CONFIRMATION_REQUIRED"
            text = $Text
            dangers = $d
        }
    }

    if ($d.ambiguous_authorization) {
        return [ordered]@{
            status = "REVIEW_REQUIRED"
            decision = "REVIEW_REQUIRED"
            reason = "AMBIGUOUS_AUTHORIZATION"
            authorization_status = "AUTHORIZATION_REVIEW_REQUIRED"
            text = $Text
            dangers = $d
        }
    }

    return [ordered]@{
        status = "REVIEW_REQUIRED"
        decision = "REVIEW_REQUIRED"
        reason = "EXACT_PHRASE_MISSING"
        authorization_status = "AUTHORIZATION_REVIEW_REQUIRED"
        text = $Text
        dangers = $d
    }
}

function New-AuthorizationGuardReportsV36 {
    param([AllowEmptyString()][string]$SampleText = "")

    $parsed = Parse-AuthorizationIntentV36 -Text $SampleText

    return [ordered]@{
        authorization_intent_parser = $parsed
        no_self_authorization = [ordered]@{
            status = if ($parsed.dangers.self_authorization) { "LOCK" } else { "PASS" }
            reason = if ($parsed.dangers.self_authorization) { "SELF_AUTHORIZATION_ATTEMPT" } else { "NO_SELF_AUTHORIZATION_PASS" }
        }
        no_implied_authorization = [ordered]@{
            status = if ($parsed.dangers.implied_authorization) { "LOCK" } else { "PASS" }
            reason = if ($parsed.dangers.implied_authorization) { "IMPLIED_AUTHORIZATION_ATTEMPT" } else { "NO_IMPLIED_AUTHORIZATION_PASS" }
        }
        no_memory_based_authorization = [ordered]@{
            status = if ($parsed.dangers.memory_based_authorization) { "LOCK" } else { "PASS" }
            reason = if ($parsed.dangers.memory_based_authorization) { "MEMORY_BASED_AUTHORIZATION_ATTEMPT" } else { "NO_MEMORY_BASED_AUTHORIZATION_PASS" }
        }
        no_delegated_authorization = [ordered]@{
            status = if ($parsed.dangers.delegated_authorization) { "LOCK" } else { "PASS" }
            reason = if ($parsed.dangers.delegated_authorization) { "DELEGATED_AUTHORIZATION_ATTEMPT" } else { "NO_DELEGATED_AUTHORIZATION_PASS" }
        }
        exact_phrase_contract = [ordered]@{
            status = "PASS"
            reason = "EXACT_PHRASE_CONTRACT_DEFINED"
            required_format = "AUTORIZO_EVALUACION queue_item_id=<ID> scope=SINGLE_ACTION_ONLY no_execution=true"
            valid_sample_detected = $parsed.dangers.exact_phrase_valid
        }
        anti_bypass = [ordered]@{
            status = if ($parsed.dangers.any_lock) { "LOCK" } else { "PASS" }
            reason = if ($parsed.dangers.any_lock) { "AUTHORIZATION_BYPASS_ATTEMPT" } else { "AUTHORIZATION_ANTI_BYPASS_PASS" }
        }
    }
}
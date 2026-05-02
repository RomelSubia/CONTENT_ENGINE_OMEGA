$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Get-StableSha256V35 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)

    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $hash = $sha.ComputeHash($bytes)

    return ([BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
}

function Get-FileSha256LowerV35 {
    param([Parameter(Mandatory=$true)][string]$Path)

    if (!(Test-Path -LiteralPath $Path)) {
        throw "Missing file for hash: $Path"
    }

    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Convert-ToStableJsonV35 {
    param([Parameter(Mandatory=$true)]$Object)
    return ($Object | ConvertTo-Json -Depth 100 -Compress)
}

function Read-JsonStrictV35 {
    param([Parameter(Mandatory=$true)][string]$Path)

    if (!(Test-Path -LiteralPath $Path)) {
        throw "JSON requerido no existe: $Path"
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        throw "JSON inválido: $Path :: $($_.Exception.Message)"
    }
}

function Normalize-ActionTextV35 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)

    $t = $Text.Trim().ToLowerInvariant()
    $t = $t -replace "\s+", " "
    $t = $t -replace "[^a-z0-9áéíóúñü_\-\/ ]", ""
    return $t.Trim()
}

function Get-RiskWeightV35 {
    param([Parameter(Mandatory=$true)][string]$RiskLevel)

    switch ($RiskLevel.ToUpperInvariant()) {
        "CRITICAL" { return 100 }
        "HIGH" { return 80 }
        "MEDIUM" { return 60 }
        "LOW" { return 40 }
        default { return 20 }
    }
}

function New-DeterministicIdV35 {
    param(
        [Parameter(Mandatory=$true)][string]$Prefix,
        [Parameter(Mandatory=$true)][AllowEmptyString()][string]$Seed
    )

    $hash = Get-StableSha256V35 -Text $Seed
    return ("{0}-{1}" -f $Prefix, $hash.Substring(0,16).ToUpperInvariant())
}

function Test-DangerousTextV35 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)

    $l = $Text.ToLowerInvariant()

    $runtime = ($l -match "worker|dispatcher|runner|executor|scheduler|daemon|listener|background job|background queue|job queue|poller|polling|queue polling|consumer|trigger|runtime binding|queue processor|active queue|live queue|running queue|task queue runner")
    $hiddenApproval = ($l -match "approved\s*=\s*true|approved_by_human\s*=\s*true|human approved|authorization granted|execution authorized|approval token|authorization token|approval_signature|approved by default|auto approved")
    $queueBypass = ($l -match "ponlo en cola y ejec[uú]talo|d[eé]jalo listo y corre|queue and run|handoff and execute|activa el webhook despu[eé]s|programa la tarea|publica cuando est[eé] listo|ejecuta cuando termine|corre autom[aá]ticamente luego|prepara y ejecuta luego")
    $external = ($l -match "n8n|webhook|api externa|external api|youtube publish|tiktok publish|instagram publish|email automation|scheduler|scheduled task|cron|bot runner|auto post|auto publish|publicar autom[aá]ticamente|subir a youtube|enviar a tiktok")
    $capa9 = ($l -match "capa\s*9|capa nueve|capa ix|layer nine|layer\s*9|nueva capa cerebral|capa cerebral adicional|extensi[oó]n del cerebro|otro nivel del cerebro|subcerebro|brain layer extra")
    $manualMutation = ($l -match "modifica.*manual|actualiza.*manual|cambia.*manual|manual_master_current|manual/current|fuente oficial manual")
    $brainMutation = ($l -match "modifica.*cerebro|actualiza.*cerebro|actualiza.*memoria|memoria del cerebro|brain mutation|brain write")
    $reportsBrainMutation = ($l -match "reports/brain|reports\\brain|00_system/reports/brain")
    $productionCleanFalse = ($l -match "production_clean_pass\s*=\s*true|production clean true|production-clean|sin warnings|warnings hidden|warnings_hidden\s*>\s*0|warnings_resolved.*>\s*0")

    return [ordered]@{
        runtime_binding_intent = $runtime
        hidden_approval_intent = $hiddenApproval
        queue_execution_bypass_intent = $queueBypass
        external_automation_intent = $external
        capa9_intent = $capa9
        manual_mutation_intent = $manualMutation
        brain_mutation_intent = $brainMutation
        reports_brain_mutation_intent = $reportsBrainMutation
        false_production_clean_claim = $productionCleanFalse
        dangerous = ($runtime -or $hiddenApproval -or $queueBypass -or $external -or $capa9 -or $manualMutation -or $brainMutation -or $reportsBrainMutation -or $productionCleanFalse)
    }
}

function Get-ActionTypeV35 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)

    $danger = Test-DangerousTextV35 -Text $Text
    $l = $Text.ToLowerInvariant()

    if ($danger.capa9_intent) { return "CAPA9_ACTION" }
    if ($danger.external_automation_intent) { return "EXTERNAL_ACTION" }
    if ($danger.manual_mutation_intent) { return "MANUAL_MUTATION_ACTION" }
    if ($danger.brain_mutation_intent) { return "BRAIN_MUTATION_ACTION" }
    if ($danger.reports_brain_mutation_intent) { return "REPORTS_BRAIN_MUTATION_ACTION" }
    if ($danger.runtime_binding_intent) { return "EXECUTION_ACTION" }
    if ($danger.hidden_approval_intent) { return "EXECUTION_ACTION" }
    if ($danger.queue_execution_bypass_intent) { return "EXECUTION_ACTION" }

    if ($l -match "unknown|desconocid|vague|ambigu") { return "UNKNOWN_ACTION" }    if ($l -match "document|summary|resumen|explicaci[oó]n") { return "DOCUMENTATION_ACTION" }
    if ($l -match "validar|validaci[oó]n|validacion|validation|validate|test|prueba|verificar") { return "VALIDATION_ACTION" }
    if ($l -match "review|revisar|auditar|audit") { return "REVIEW_ACTION" }
    if ($l -match "queue|cola|handoff") { return "QUEUE_REVIEW_ACTION" }
    if ($l -match "config|configuration|configuraci[oó]n") { return "CONFIG_REVIEW_ACTION" }
    if ($l -match "trace|trazabilidad|evidencia") { return "TRACEABILITY_ACTION" }

    return "UNKNOWN_ACTION"
}

function New-ActionItemV35 {
    param(
        [Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text,
        [Parameter(Mandatory=$true)][int]$Sequence,
        [Parameter(Mandatory=$true)][string]$SourceHash,
        [Parameter(Mandatory=$true)][string]$SourceCommit
    )

    $normalized = Normalize-ActionTextV35 -Text $Text
    $actionType = Get-ActionTypeV35 -Text $Text
    $danger = Test-DangerousTextV35 -Text $Text

    $dangerousTypes = @(
        "EXECUTION_ACTION",
        "EXTERNAL_ACTION",
        "MUTATION_ACTION",
        "MANUAL_MUTATION_ACTION",
        "BRAIN_MUTATION_ACTION",
        "REPORTS_BRAIN_MUTATION_ACTION",
        "PUBLICATION_ACTION",
        "DEPLOYMENT_ACTION",
        "SCHEDULED_ACTION",
        "WEBHOOK_ACTION",
        "N8N_ACTION",
        "CAPA9_ACTION"
    )

    if ($danger.dangerous -or $dangerousTypes -contains $actionType) {
        $status = "LOCKED"
        $decision = "LOCK"
        $risk = "CRITICAL"
        $blocked = $true
        $locked = $true
        $review = $false
        $reason = "DANGEROUS_ACTION_TYPE_OR_INTENT"
    }
    elseif ($actionType -eq "UNKNOWN_ACTION") {
        $status = "REVIEW_REQUIRED"
        $decision = "REVIEW_REQUIRED"
        $risk = "MEDIUM"
        $blocked = $false
        $locked = $false
        $review = $true
        $reason = "UNKNOWN_ACTION_REQUIRES_REVIEW"
    }
    else {
        $status = "QUEUED_FOR_HUMAN_REVIEW"
        $decision = "PASS_WITH_WARNINGS"
        $risk = "LOW"
        $blocked = $false
        $locked = $false
        $review = $true
        $reason = "SAFE_REVIEW_ACTION"
    }

    $riskWeight = Get-RiskWeightV35 -RiskLevel $risk
    $seed = "$SourceHash|$normalized|$Sequence|$actionType|$SourceCommit"
    $actionId = New-DeterministicIdV35 -Prefix "V35-ACTION" -Seed $seed

    return [ordered]@{
        action_id = $actionId
        source_sequence = $Sequence
        action_text = $Text
        normalized_action_text = $normalized
        normalized_action_hash = Get-StableSha256V35 -Text $normalized
        action_type = $actionType
        status = $status
        decision = $decision
        reason = $reason
        risk_level = $risk
        risk_level_weight = $riskWeight
        dependency_depth = 0
        requires_human_approval = $true
        approved_by_human = $false
        approval_processing_supported = $false
        execution_permission = $false
        blocked = $blocked
        locked = $locked
        review_required = $review
        dangerous_intents = $danger
        evidence_hash_sha256 = Get-StableSha256V35 -Text $seed
    }
}

function Get-SafeDecisionCountV35 {
    param(
        [Parameter(Mandatory=$false)]
        [AllowNull()]
        [object]$Items,

        [Parameter(Mandatory=$true)]
        [string]$Decision
    )

    $safeItems = New-Object System.Collections.ArrayList

    foreach ($item in @($Items)) {
        if ($null -eq $item) { continue }

        if (
            $item -is [System.Collections.IEnumerable] -and
            -not ($item -is [string]) -and
            -not ($item -is [System.Collections.IDictionary])
        ) {
            foreach ($nested in $item) {
                if ($null -eq $nested) { continue }

                try {
                    if ($nested["decision"] -eq $Decision) {
                        $null = $safeItems.Add($nested)
                        continue
                    }
                }
                catch {
                    $prop = $nested.PSObject.Properties | Where-Object { $_.Name -eq "decision" } | Select-Object -First 1
                    if ($null -ne $prop -and $prop.Value -eq $Decision) {
                        $null = $safeItems.Add($nested)
                    }
                }
            }

            continue
        }

        try {
            if ($item["decision"] -eq $Decision) {
                $null = $safeItems.Add($item)
                continue
            }
        }
        catch {
            $prop = $item.PSObject.Properties | Where-Object { $_.Name -eq "decision" } | Select-Object -First 1
            if ($null -ne $prop -and $prop.Value -eq $Decision) {
                $null = $safeItems.Add($item)
            }
        }
    }

    return [int]$safeItems.Count
}

function Get-GlobalDecisionV35 {
    param(
        [Parameter(Mandatory=$true)]
        [AllowNull()]
        [object]$Actions
    )

    $all = New-Object System.Collections.ArrayList

    foreach ($item in @($Actions)) {
        if ($null -eq $item) { continue }

        if (
            $item -is [System.Collections.IEnumerable] -and
            -not ($item -is [string]) -and
            -not ($item -is [System.Collections.IDictionary])
        ) {
            foreach ($nested in $item) {
                if ($null -ne $nested) {
                    $null = $all.Add($nested)
                }
            }
        }
        else {
            $null = $all.Add($item)
        }
    }

    if ($all.Count -eq 0) {
        return "REVIEW_REQUIRED"
    }

    if ((Get-SafeDecisionCountV35 -Items $all -Decision "LOCK") -gt 0) {
        return "LOCK"
    }

    if ((Get-SafeDecisionCountV35 -Items $all -Decision "BLOCK") -gt 0) {
        return "BLOCK"
    }

    if ((Get-SafeDecisionCountV35 -Items $all -Decision "REVIEW_REQUIRED") -gt 0) {
        return "REVIEW_REQUIRED"
    }

    return "PASS_WITH_WARNINGS"
}
function Get-V35SourceBundle {
    param([string]$RootPath = "D:\CONTENT_ENGINE_OMEGA")

    $sources = [ordered]@{
        plan_builder = "00_SYSTEM\bridge\reports\PLAN_BUILDER_REPORT_V3_4.json"
        approval_gate = "00_SYSTEM\bridge\reports\APPROVAL_GATE_REPORT_V3_4.json"
        build_readiness = "00_SYSTEM\bridge\reports\BRIDGE_BUILD_READINESS_REPORT_V3_4.json"
        no_execution = "00_SYSTEM\bridge\reports\NO_EXECUTION_PERMISSION_AUDIT_V3_4.json"
        post_build_audit = "00_SYSTEM\bridge\reports\POST_BUILD_AUDIT_REPORT_V3_4.json"
        warning_gate = "00_SYSTEM\bridge\reports\WARNING_ACCEPTANCE_GATE_REPORT_V3_4.json"
        gate_closure = "00_SYSTEM\bridge\reports\GATE_CLOSURE_REPORT_V3_4.json"
        next_layer_map = "00_SYSTEM\bridge\reports\NEXT_LAYER_READINESS_MAP_V3_4.json"
        manifest_v34 = "00_SYSTEM\bridge\manifests\BRIDGE_ARTIFACT_MANIFEST_V3_4.json"
        seal_v34 = "00_SYSTEM\bridge\manifests\BRIDGE_MANIFEST_SEAL_V3_4.json"
        closure_manifest_v34 = "00_SYSTEM\bridge\manifests\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_MANIFEST_V3_4.json"
        closure_seal_v34 = "00_SYSTEM\bridge\manifests\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_SEAL_V3_4.json"
    }

    $items = New-Object System.Collections.ArrayList

    foreach ($entry in $sources.GetEnumerator()) {
        $full = Join-Path $RootPath $entry.Value

        if (!(Test-Path -LiteralPath $full)) {
            throw "Missing authorized source: $($entry.Value)"
        }

        $null = $items.Add([ordered]@{
            role = $entry.Key
            relative_path = $entry.Value.Replace("\","/")
            hash_sha256 = Get-FileSha256LowerV35 -Path $full
            read_only = $true
        })
    }

    return [ordered]@{
        status = "PASS"
        source_authority = "V3_4_CLOSED_CHAIN"
        authorized_sources_count = $items.Count
        sources = @($items)
    }
}

function New-HandoffPacketV35 {
    param(
        [string]$RootPath = "D:\CONTENT_ENGINE_OMEGA",
        [AllowEmptyString()][string]$SourceText = "",
        [AllowEmptyString()][string]$SourceCommit = ""
    )

    if ([string]::IsNullOrWhiteSpace($SourceCommit)) {
        try { $SourceCommit = (git rev-parse --short HEAD).Trim() } catch { $SourceCommit = "UNKNOWN_HEAD" }
    }

    $bundle = Get-V35SourceBundle -RootPath $RootPath

    $planPath = Join-Path $RootPath "00_SYSTEM\bridge\reports\PLAN_BUILDER_REPORT_V3_4.json"
    $approvalPath = Join-Path $RootPath "00_SYSTEM\bridge\reports\APPROVAL_GATE_REPORT_V3_4.json"
    $warningPath = Join-Path $RootPath "00_SYSTEM\bridge\reports\WARNING_ACCEPTANCE_GATE_REPORT_V3_4.json"
    $closurePath = Join-Path $RootPath "00_SYSTEM\bridge\reports\GATE_CLOSURE_REPORT_V3_4.json"

    $planHash = Get-FileSha256LowerV35 -Path $planPath
    $approvalHash = Get-FileSha256LowerV35 -Path $approvalPath
    $warningHash = Get-FileSha256LowerV35 -Path $warningPath
    $closureHash = Get-FileSha256LowerV35 -Path $closurePath

    if ([string]::IsNullOrWhiteSpace($SourceText)) {
        $defaultActions = @(
            "Review v3.4 controlled plan output",
            "Validate v3.4 approval gate result",
            "Review inherited warnings before future authorization",
            "Create non executable handoff evidence",
            "Create non executable action review queue",
            "Validate no-execution permission matrix",
            "Audit traceability evidence for next layer"
        )
    }
    else {
        $defaultActions = @($SourceText)
    }

    $actions = New-Object System.Collections.ArrayList

    for ($i = 0; $i -lt $defaultActions.Count; $i++) {
        $item = New-ActionItemV35 -Text $defaultActions[$i] -Sequence ($i + 1) -SourceHash $planHash -SourceCommit $SourceCommit
        $null = $actions.Add($item)
    }

    $globalDecision = Get-GlobalDecisionV35 -Actions @($actions)

    if ($globalDecision -eq "LOCK") {
        $packetStatus = "LOCKED"
    }
    elseif ($globalDecision -eq "BLOCK") {
        $packetStatus = "BLOCKED"
    }
    elseif ($globalDecision -eq "REVIEW_REQUIRED") {
        $packetStatus = "REVIEW_REQUIRED"
    }
    else {
        $packetStatus = "QUEUED_FOR_HUMAN_REVIEW"
    }

    $packetSeed = "$planHash|$approvalHash|$warningHash|$closureHash|$SourceCommit|$globalDecision|$(@($actions | ForEach-Object { $_["action_id"] }) -join ',')"
    $packetId = New-DeterministicIdV35 -Prefix "V35-PACKET" -Seed $packetSeed
    $handoffId = New-DeterministicIdV35 -Prefix "V35-HANDOFF" -Seed "$packetId|HANDOFF"
    $queueId = New-DeterministicIdV35 -Prefix "V35-QUEUE" -Seed "$packetId|QUEUE"

    return [ordered]@{
        status = $packetStatus
        reason = "CONTROLLED_ACTION_HANDOFF_PACKET_CREATED"
        packet_id = $packetId
        handoff_id = $handoffId
        queue_id = $queueId
        packet_version = "v3.5"
        packet_type = "CONTROLLED_ACTION_HANDOFF_PACKET"
        source_layer = "v3.4_CONTROLLED_PLAN_BUILDER_APPROVAL_GATE"
        source_commit = $SourceCommit
        source_plan_hash_sha256 = $planHash
        source_approval_hash_sha256 = $approvalHash
        source_warning_gate_hash_sha256 = $warningHash
        source_closure_hash_sha256 = $closureHash
        global_decision = $globalDecision
        requires_human_approval = $true
        approval_processing_supported = $false
        approved_by_human = $false
        execution_permission = $false
        queue_type = "NON_EXECUTABLE_ACTION_REVIEW_QUEUE"
        queue_operational = $false
        queue_executable = $false
        queue_runtime_binding = $false
        queue_worker_attached = $false
        queue_dispatcher_attached = $false
        queue_listener_attached = $false
        queue_runner_attached = $false
        actions = @($actions)
        blocked_actions = @($actions | Where-Object { $_["decision"] -eq "BLOCK" })
        locked_actions = @($actions | Where-Object { $_["decision"] -eq "LOCK" })
        review_required_actions = @($actions | Where-Object { $_["review_required"] -eq $true })
        permission_matrix = [ordered]@{
            execution_allowed = $false
            external_execution_allowed = $false
            manual_write_allowed = $false
            brain_write_allowed = $false
            reports_brain_write_allowed = $false
            auto_action_allowed = $false
            webhook_activation_allowed = $false
            n8n_activation_allowed = $false
            publishing_allowed = $false
            capa9_creation_allowed = $false
            human_approval_required = $true
        }
        warning_state = [ordered]@{
            production_clean_pass = $false
            production_with_warnings = $true
            warnings_inherited_visible = 5
            warnings_hidden = 0
            warnings_resolved_by_v3_5 = 0
        }
        revocation_expiration = [ordered]@{
            revocable = $true
            revoked = $false
            expires_required = $true
            expiration_mode = "NEXT_LAYER_REVIEW_ONLY"
            expires_at = $null
            ttl_minutes = $null
            permanent_queue_allowed = $false
        }
        source_bundle = $bundle
    }
}
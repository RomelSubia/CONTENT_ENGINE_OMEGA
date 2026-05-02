$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\action_handoff\action_handoff_builder_v3_5.ps1"

function New-NonExecutableQueueV35 {
    param(
        [Parameter(Mandatory=$true)]$Packet,
        [string]$RootPath = "D:\CONTENT_ENGINE_OMEGA"
    )

    $items = New-Object System.Collections.ArrayList

    $sorted = @($Packet["actions"] | Sort-Object `
        @{ Expression = { [int]$_["risk_level_weight"] }; Descending = $true }, `
        @{ Expression = { [int]$_["dependency_depth"] }; Ascending = $true }, `
        @{ Expression = { [int]$_["source_sequence"] }; Ascending = $true }, `
        @{ Expression = { [string]$_["normalized_action_hash"] }; Ascending = $true }, `
        @{ Expression = { [string]$_["action_id"] }; Ascending = $true })

    $index = 0

    foreach ($action in $sorted) {
        $index++
        $seed = "$($Packet["queue_id"])|$($action["action_id"])|$index|NON_EXECUTABLE"
        $queueItemId = New-DeterministicIdV35 -Prefix "V35-QITEM" -Seed $seed

        $queueStatus = "QUEUED_FOR_HUMAN_REVIEW"

        if ($action["decision"] -eq "LOCK") {
            $queueStatus = "LOCKED"
        }
        elseif ($action["decision"] -eq "BLOCK") {
            $queueStatus = "BLOCKED"
        }
        elseif ($action["decision"] -eq "REVIEW_REQUIRED") {
            $queueStatus = "REVIEW_REQUIRED"
        }

        $null = $items.Add([ordered]@{
            queue_item_id = $queueItemId
            sequence = $index
            source_action_id = $action["action_id"]
            action_type = $action["action_type"]
            action_text = $action["action_text"]
            risk_level = $action["risk_level"]
            risk_level_weight = $action["risk_level_weight"]
            status = $queueStatus
            requires_human_approval = $true
            approved_by_human = $false
            approval_processing_supported = $false
            execution_permission = $false
            blocked = $action["blocked"]
            locked = $action["locked"]
            block_reason = if ($action["blocked"] -or $action["locked"]) { $action["reason"] } else { $null }
            dependencies = @()
            evidence_hash_sha256 = Get-StableSha256V35 -Text $seed
        })
    }

    return [ordered]@{
        status = if ($Packet["global_decision"] -eq "LOCK") { "LOCKED" } elseif ($Packet["global_decision"] -eq "BLOCK") { "BLOCKED" } elseif ($Packet["global_decision"] -eq "REVIEW_REQUIRED") { "REVIEW_REQUIRED" } else { "PASS_WITH_WARNINGS" }
        reason = "NON_EXECUTABLE_ACTION_REVIEW_QUEUE_CREATED"
        queue_id = $Packet["queue_id"]
        packet_id = $Packet["packet_id"]
        queue_type = "NON_EXECUTABLE_ACTION_REVIEW_QUEUE"
        queue_status = "QUEUED_FOR_HUMAN_REVIEW"
        queue_operational = $false
        queue_executable = $false
        queue_dispatcher_attached = $false
        queue_worker_attached = $false
        queue_runtime_binding = $false
        queue_listener_attached = $false
        queue_consumer_attached = $false
        queue_processor_attached = $false
        queue_scheduler_attached = $false
        queue_background_job_attached = $false
        items_count = $items.Count
        queue_items = @($items)
    }
}

function Test-PermissionMatrixV35 {
    param([Parameter(Mandatory=$true)]$Packet)

    $m = $Packet["permission_matrix"]

    $danger = (
        $m["execution_allowed"] -ne $false -or
        $m["external_execution_allowed"] -ne $false -or
        $m["manual_write_allowed"] -ne $false -or
        $m["brain_write_allowed"] -ne $false -or
        $m["reports_brain_write_allowed"] -ne $false -or
        $m["auto_action_allowed"] -ne $false -or
        $m["webhook_activation_allowed"] -ne $false -or
        $m["n8n_activation_allowed"] -ne $false -or
        $m["publishing_allowed"] -ne $false -or
        $m["capa9_creation_allowed"] -ne $false
    )

    return [ordered]@{
        status = if ($danger) { "LOCK" } else { "PASS" }
        reason = if ($danger) { "DANGEROUS_PERMISSION_TRUE" } else { "ALL_DANGEROUS_PERMISSIONS_FALSE" }
        execution_allowed = $m["execution_allowed"]
        external_execution_allowed = $m["external_execution_allowed"]
        manual_write_allowed = $m["manual_write_allowed"]
        brain_write_allowed = $m["brain_write_allowed"]
        reports_brain_write_allowed = $m["reports_brain_write_allowed"]
        auto_action_allowed = $m["auto_action_allowed"]
        webhook_activation_allowed = $m["webhook_activation_allowed"]
        n8n_activation_allowed = $m["n8n_activation_allowed"]
        publishing_allowed = $m["publishing_allowed"]
        capa9_creation_allowed = $m["capa9_creation_allowed"]
        human_approval_required = $m["human_approval_required"]
    }
}

function Test-ApprovalNullContractV35 {
    param([Parameter(Mandatory=$true)]$Packet)

    $bad = (
        $Packet["approved_by_human"] -ne $false -or
        $Packet["approval_processing_supported"] -ne $false -or
        $Packet["execution_permission"] -ne $false
    )

    return [ordered]@{
        status = if ($bad) { "LOCK" } else { "PASS" }
        reason = if ($bad) { "HIDDEN_APPROVAL_DETECTED" } else { "APPROVAL_NULL_CONTRACT_PASS" }
        requires_human_approval = $Packet["requires_human_approval"]
        approved_by_human = $Packet["approved_by_human"]
        approval_processing_supported = $Packet["approval_processing_supported"]
        human_authorization_token = $null
        authorization_source = $null
        authorization_scope = $null
        authorization_timestamp = $null
        authorization_signature = $null
        execution_authorized = $false
    }
}

function Test-QueueRuntimeBindingV35 {
    param(
        [Parameter(Mandatory=$true)]$Queue,
        [AllowEmptyString()][string]$Text = ""
    )

    $dangerText = Test-DangerousTextV35 -Text $Text

    $bad = (
        $Queue["queue_operational"] -ne $false -or
        $Queue["queue_executable"] -ne $false -or
        $Queue["queue_dispatcher_attached"] -ne $false -or
        $Queue["queue_worker_attached"] -ne $false -or
        $Queue["queue_runtime_binding"] -ne $false -or
        $Queue["queue_listener_attached"] -ne $false -or
        $Queue["queue_consumer_attached"] -ne $false -or
        $Queue["queue_processor_attached"] -ne $false -or
        $Queue["queue_scheduler_attached"] -ne $false -or
        $Queue["queue_background_job_attached"] -ne $false -or
        $dangerText.runtime_binding_intent
    )

    return [ordered]@{
        status = if ($bad) { "LOCK" } else { "PASS" }
        reason = if ($bad) { "QUEUE_RUNTIME_BINDING_ATTEMPT" } else { "NO_QUEUE_RUNTIME_BINDING" }
        queue_operational = $Queue["queue_operational"]
        queue_executable = $Queue["queue_executable"]
        queue_runtime_binding = $Queue["queue_runtime_binding"]
        queue_worker_attached = $Queue["queue_worker_attached"]
        queue_dispatcher_attached = $Queue["queue_dispatcher_attached"]
        queue_listener_attached = $Queue["queue_listener_attached"]
        queue_consumer_attached = $Queue["queue_consumer_attached"]
        queue_processor_attached = $Queue["queue_processor_attached"]
    }
}

function Test-QueueLifecycleV35 {
    param([Parameter(Mandatory=$true)]$Packet)

    $r = $Packet["revocation_expiration"]

    $bad = (
        $r["revocable"] -ne $true -or
        $r["expires_required"] -ne $true -or
        $r["permanent_queue_allowed"] -ne $false -or
        $r["revoked"] -ne $false
    )

    return [ordered]@{
        status = if ($bad) { "BLOCK" } else { "PASS" }
        reason = if ($bad) { "QUEUE_LIFECYCLE_CONTRACT_FAILED" } else { "QUEUE_LIFECYCLE_CONTRACT_PASS" }
        revocable = $r["revocable"]
        revoked = $r["revoked"]
        expires_required = $r["expires_required"]
        expiration_mode = $r["expiration_mode"]
        expires_at = $r["expires_at"]
        ttl_minutes = $r["ttl_minutes"]
        permanent_queue_allowed = $r["permanent_queue_allowed"]
    }
}

function Test-WarningIntegrityV35 {
    param([Parameter(Mandatory=$true)]$Packet)

    $w = $Packet["warning_state"]

    $bad = (
        $w["production_clean_pass"] -ne $false -or
        $w["production_with_warnings"] -ne $true -or
        [int]$w["warnings_inherited_visible"] -ne 5 -or
        [int]$w["warnings_hidden"] -ne 0 -or
        [int]$w["warnings_resolved_by_v3_5"] -ne 0
    )

    return [ordered]@{
        status = if ($bad) { "BLOCK" } else { "PASS" }
        reason = if ($bad) { "FALSE_PRODUCTION_CLEAN_CLAIM" } else { "WARNING_INTEGRITY_PASS" }
        production_clean_pass = $w["production_clean_pass"]
        production_with_warnings = $w["production_with_warnings"]
        warnings_inherited_visible = $w["warnings_inherited_visible"]
        warnings_hidden = $w["warnings_hidden"]
        warnings_resolved_by_v3_5 = $w["warnings_resolved_by_v3_5"]
    }
}

function Test-NoExecutionQueueAuditV35 {
    param(
        [Parameter(Mandatory=$true)]$Packet,
        [Parameter(Mandatory=$true)]$Queue
    )

    $bad = (
        $Packet["execution_permission"] -ne $false -or
        $Queue["queue_executable"] -ne $false -or
        $Queue["queue_operational"] -ne $false -or
        $Queue["queue_runtime_binding"] -ne $false
    )

    return [ordered]@{
        status = if ($bad) { "LOCK" } else { "PASS" }
        reason = if ($bad) { "EXECUTION_QUEUE_PERMISSION_DETECTED" } else { "NO_EXECUTION_QUEUE_AUDIT_PASS" }
        script_execution = $false
        external_api_call = $false
        n8n_activation = $false
        webhook_activation = $false
        content_publishing = $false
        scheduled_task = $false
        worker = $false
        dispatcher = $false
        runner = $false
        listener = $false
        daemon = $false
        manual_mutation = $false
        brain_mutation = $false
        reports_brain_mutation = $false
        capa9 = $false
    }
}

function Test-DriftGuardV35 {
    param(
        [Parameter(Mandatory=$true)]$Packet,
        [string]$RootPath = "D:\CONTENT_ENGINE_OMEGA"
    )

    $planPath = Join-Path $RootPath "00_SYSTEM\bridge\reports\PLAN_BUILDER_REPORT_V3_4.json"
    $approvalPath = Join-Path $RootPath "00_SYSTEM\bridge\reports\APPROVAL_GATE_REPORT_V3_4.json"
    $warningPath = Join-Path $RootPath "00_SYSTEM\bridge\reports\WARNING_ACCEPTANCE_GATE_REPORT_V3_4.json"
    $closurePath = Join-Path $RootPath "00_SYSTEM\bridge\reports\GATE_CLOSURE_REPORT_V3_4.json"

    $actualPlan = Get-FileSha256LowerV35 -Path $planPath
    $actualApproval = Get-FileSha256LowerV35 -Path $approvalPath
    $actualWarning = Get-FileSha256LowerV35 -Path $warningPath
    $actualClosure = Get-FileSha256LowerV35 -Path $closurePath

    $bad = (
        $actualPlan -ne $Packet["source_plan_hash_sha256"] -or
        $actualApproval -ne $Packet["source_approval_hash_sha256"] -or
        $actualWarning -ne $Packet["source_warning_gate_hash_sha256"] -or
        $actualClosure -ne $Packet["source_closure_hash_sha256"]
    )

    return [ordered]@{
        status = if ($bad) { "LOCK" } else { "PASS" }
        reason = if ($bad) { "DRIFT_DETECTED" } else { "DRIFT_GUARD_PASS" }
        source_plan_hash_sha256 = $Packet["source_plan_hash_sha256"]
        actual_plan_hash_sha256 = $actualPlan
        source_approval_hash_sha256 = $Packet["source_approval_hash_sha256"]
        actual_approval_hash_sha256 = $actualApproval
        source_warning_gate_hash_sha256 = $Packet["source_warning_gate_hash_sha256"]
        actual_warning_gate_hash_sha256 = $actualWarning
        source_closure_hash_sha256 = $Packet["source_closure_hash_sha256"]
        actual_closure_hash_sha256 = $actualClosure
    }
}
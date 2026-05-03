$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\authorization\human_authorization_contract_v3_6.ps1"
. "00_SYSTEM\bridge\authorization\authorization_intent_parser_v3_6.ps1"

function New-ExecutionPermissionModelV36 {
    param([Parameter(Mandatory=$true)]$Contract)

    return [ordered]@{
        status = "PASS"
        reason = "PERMISSION_EVALUATION_ONLY_MODEL_CREATED"
        authorized_operation = "PERMISSION_EVALUATION_ONLY"
        execution_authorization_requested = $false
        execution_authorization_accepted = $false
        execution_permission_evaluable = $true
        execution_permission_granted = $false
        execution_ready = $false
        execution_performed = $false
        permission_matrix = $Contract["permission_matrix"]
    }
}

function Test-PermissionMatrixV36 {
    param([Parameter(Mandatory=$true)]$Contract)

    $m = $Contract["permission_matrix"]

    $bad = (
        $m["authorization_record_permission"] -ne $false -or
        $m["execution_permission"] -ne $false -or
        $m["external_execution_permission"] -ne $false -or
        $m["manual_write_permission"] -ne $false -or
        $m["brain_write_permission"] -ne $false -or
        $m["reports_brain_write_permission"] -ne $false -or
        $m["queue_runtime_binding_permission"] -ne $false -or
        $m["n8n_permission"] -ne $false -or
        $m["webhook_permission"] -ne $false -or
        $m["publishing_permission"] -ne $false -or
        $m["capa9_permission"] -ne $false
    )

    return [ordered]@{
        status = if ($bad) { "LOCK" } else { "PASS" }
        reason = if ($bad) { "DANGEROUS_PERMISSION_TRUE" } else { "PERMISSION_MATRIX_PASS" }
        permission_matrix = $m
    }
}

function Test-ChallengeContractV36 {
    param([Parameter(Mandatory=$true)]$Contract)

    $bad = (
        $Contract["challenge_required"] -ne $true -or
        $Contract["challenge_phrase_required"] -ne $true -or
        $Contract["challenge_confirmed"] -ne $false -or
        $Contract["challenge_valid"] -ne $false -or
        [int]$Contract["challenge_attempts"] -ne 0 -or
        [int]$Contract["challenge_max_attempts"] -ne 1
    )

    return [ordered]@{
        status = if ($bad) { "BLOCK" } else { "PASS" }
        reason = if ($bad) { "MISSING_CHALLENGE_CONFIRMATION" } else { "CHALLENGE_CONFIRMATION_CONTRACT_PASS" }
        challenge_required = $Contract["challenge_required"]
        challenge_id = $Contract["challenge_id"]
        challenge_phrase_required = $Contract["challenge_phrase_required"]
        challenge_confirmed = $Contract["challenge_confirmed"]
        challenge_valid = $Contract["challenge_valid"]
        challenge_attempts = $Contract["challenge_attempts"]
        challenge_max_attempts = $Contract["challenge_max_attempts"]
    }
}

function Test-RevocationExpirationV36 {
    param([Parameter(Mandatory=$true)]$Contract)

    $r = $Contract["revocation_expiration"]

    $bad = (
        $r["revocable"] -ne $true -or
        $r["revoked"] -ne $false -or
        $r["expiration_required"] -ne $true -or
        $r["permanent_authorization_allowed"] -ne $false
    )

    return [ordered]@{
        status = if ($bad) { "BLOCK" } else { "PASS" }
        reason = if ($bad) { "AUTHORIZATION_REVOCATION_EXPIRATION_FAILED" } else { "AUTHORIZATION_REVOCATION_EXPIRATION_PASS" }
        revocable = $r["revocable"]
        revoked = $r["revoked"]
        expiration_required = $r["expiration_required"]
        expiration_mode = $r["expiration_mode"]
        permanent_authorization_allowed = $r["permanent_authorization_allowed"]
    }
}

function Test-EligibilityV36 {
    param(
        [AllowNull()][object]$QueueItem = $null,
        [AllowEmptyString()][string]$ActionType = "REVIEW_ACTION",
        [AllowEmptyString()][string]$ActionStatus = "QUEUED_FOR_HUMAN_REVIEW"
    )

    if ($null -eq $QueueItem) {
        return [ordered]@{
            status = "BLOCK"
            reason = "AUTHORIZATION_BINDING_INCOMPLETE"
            eligible = $false
        }
    }

    if ($ActionStatus -eq "LOCKED") {
        return [ordered]@{ status = "LOCK"; reason = "LOCKED_ACTION_AUTHORIZATION_ATTEMPT"; eligible = $false }
    }

    if ($ActionStatus -eq "BLOCKED") {
        return [ordered]@{ status = "LOCK"; reason = "BLOCKED_ACTION_AUTHORIZATION_ATTEMPT"; eligible = $false }
    }

    if ($ActionType -eq "UNKNOWN_ACTION") {
        return [ordered]@{ status = "BLOCK"; reason = "UNKNOWN_ACTION_AUTHORIZATION_ATTEMPT"; eligible = $false }
    }

    if ($ActionType -match "EXECUTION|EXTERNAL|MUTATION|WEBHOOK|N8N|CAPA9|PUBLICATION|DEPLOYMENT") {
        return [ordered]@{ status = "LOCK"; reason = "DANGEROUS_ACTION_AUTHORIZATION_ATTEMPT"; eligible = $false }
    }

    return [ordered]@{
        status = "PASS"
        reason = "AUTHORIZATION_ELIGIBILITY_PASS"
        eligible = $true
    }
}

function Test-ReplayGuardV36 {
    param([bool]$Reused = $false)

    return [ordered]@{
        status = if ($Reused) { "LOCK" } else { "PASS" }
        reason = if ($Reused) { "AUTHORIZATION_REPLAY_ATTEMPT" } else { "AUTHORIZATION_REPLAY_GUARD_PASS" }
        authorization_replay_allowed = $false
        authorization_reused = $Reused
        previous_authorization_id = $null
        replay_detected = $Reused
    }
}

function Test-StaleSourceGuardV36 {
    param(
        [Parameter(Mandatory=$true)][string]$SourceQueueHash,
        [Parameter(Mandatory=$true)][string]$CurrentQueueHash,
        [Parameter(Mandatory=$true)][string]$SourcePacketHash,
        [Parameter(Mandatory=$true)][string]$CurrentPacketHash
    )

    $stale = ($SourceQueueHash -ne $CurrentQueueHash -or $SourcePacketHash -ne $CurrentPacketHash)

    return [ordered]@{
        status = if ($stale) { "LOCK" } else { "PASS" }
        reason = if ($stale) { "STALE_AUTHORIZATION_SOURCE" } else { "AUTHORIZATION_STALE_SOURCE_GUARD_PASS" }
        source_queue_hash_at_authorization = $SourceQueueHash
        current_queue_hash = $CurrentQueueHash
        source_packet_hash_at_authorization = $SourcePacketHash
        current_packet_hash = $CurrentPacketHash
        authorization_stale = $stale
    }
}

function Test-IntegrityBindingV36 {
    param([Parameter(Mandatory=$true)]$Contract)

    $missing = (
        [string]::IsNullOrWhiteSpace([string]$Contract["source_queue_hash_sha256"]) -or
        [string]::IsNullOrWhiteSpace([string]$Contract["source_packet_hash_sha256"]) -or
        [string]::IsNullOrWhiteSpace([string]$Contract["source_closure_hash_sha256"]) -or
        [string]::IsNullOrWhiteSpace([string]$Contract["source_warning_gate_hash_sha256"]) -or
        [string]::IsNullOrWhiteSpace([string]$Contract["source_post_build_audit_hash_sha256"]) -or
        [string]::IsNullOrWhiteSpace([string]$Contract["source_manifest_hash_sha256"])
    )

    return [ordered]@{
        status = if ($missing) { "BLOCK" } else { "PASS" }
        reason = if ($missing) { "AUTHORIZATION_BINDING_INCOMPLETE" } else { "AUTHORIZATION_INTEGRITY_BINDING_PASS" }
        source_queue_hash_sha256 = $Contract["source_queue_hash_sha256"]
        source_packet_hash_sha256 = $Contract["source_packet_hash_sha256"]
        source_closure_hash_sha256 = $Contract["source_closure_hash_sha256"]
        source_warning_gate_hash_sha256 = $Contract["source_warning_gate_hash_sha256"]
        source_post_build_audit_hash_sha256 = $Contract["source_post_build_audit_hash_sha256"]
        source_manifest_hash_sha256 = $Contract["source_manifest_hash_sha256"]
    }
}

function Test-ConflictV36 {
    param([AllowEmptyString()][string]$Text = "")

    $l = $Text.ToLowerInvariant()
    $conflict = ($l -match "autorizo ejecuci[oó]n externa.*external_execution_allowed=false|autorizo escribir en manual.*manual_write_allowed=false|autorizo todo.*single_action_only|hash corresponde|action_id no coincide|challenge vencido")
    $escalation = ($l -match "eleva permisos|override policy|bypass policy|grant execution|concede ejecuci[oó]n")

    return [ordered]@{
        status = if ($escalation) { "LOCK" } elseif ($conflict) { "BLOCK" } else { "PASS" }
        reason = if ($escalation) { "AUTHORIZATION_PRIVILEGE_ESCALATION" } elseif ($conflict) { "AUTHORIZATION_CONFLICT" } else { "AUTHORIZATION_CONFLICT_DETECTOR_PASS" }
        conflict_detected = $conflict
        privilege_escalation_detected = $escalation
    }
}

function Test-NoExecutionPermissionAuditV36 {
    param([Parameter(Mandatory=$true)]$Contract)

    $m = $Contract["permission_matrix"]

    $bad = (
        $Contract["execution_permission_granted"] -ne $false -or
        $Contract["execution_ready"] -ne $false -or
        $Contract["execution_performed"] -ne $false -or
        $m["execution_permission"] -ne $false -or
        $m["external_execution_permission"] -ne $false -or
        $m["manual_write_permission"] -ne $false -or
        $m["brain_write_permission"] -ne $false -or
        $m["reports_brain_write_permission"] -ne $false -or
        $m["queue_runtime_binding_permission"] -ne $false -or
        $m["n8n_permission"] -ne $false -or
        $m["webhook_permission"] -ne $false -or
        $m["publishing_permission"] -ne $false -or
        $m["capa9_permission"] -ne $false
    )

    return [ordered]@{
        status = if ($bad) { "LOCK" } else { "PASS" }
        reason = if ($bad) { "EXECUTION_PERMISSION_DETECTED_IN_V3_6" } else { "NO_EXECUTION_PERMISSION_AUDIT_PASS" }
        execution_permission_granted = $Contract["execution_permission_granted"]
        execution_ready = $Contract["execution_ready"]
        execution_performed = $Contract["execution_performed"]
        external_execution_permission = $m["external_execution_permission"]
        manual_write_permission = $m["manual_write_permission"]
        brain_write_permission = $m["brain_write_permission"]
        reports_brain_write_permission = $m["reports_brain_write_permission"]
        n8n_permission = $m["n8n_permission"]
        webhook_permission = $m["webhook_permission"]
        publishing_permission = $m["publishing_permission"]
        capa9_permission = $m["capa9_permission"]
    }
}
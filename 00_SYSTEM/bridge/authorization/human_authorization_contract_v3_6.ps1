$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Get-StableSha256V36 {
    param([Parameter(Mandatory=$true)][AllowEmptyString()][string]$Text)

    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $hash = $sha.ComputeHash($bytes)

    return ([BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
}

function Get-FileSha256LowerV36 {
    param([Parameter(Mandatory=$true)][string]$Path)

    if (!(Test-Path -LiteralPath $Path)) {
        throw "Missing file for hash: $Path"
    }

    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function New-DeterministicIdV36 {
    param(
        [Parameter(Mandatory=$true)][string]$Prefix,
        [Parameter(Mandatory=$true)][AllowEmptyString()][string]$Seed
    )

    $hash = Get-StableSha256V36 -Text $Seed
    return ("{0}-{1}" -f $Prefix, $hash.Substring(0,16).ToUpperInvariant())
}

function Get-V36SourceBundle {
    param([string]$RootPath = "D:\CONTENT_ENGINE_OMEGA")

    $sources = [ordered]@{
        gate_closure = "00_SYSTEM\bridge\reports\GATE_CLOSURE_REPORT_V3_5.json"
        next_layer_map = "00_SYSTEM\bridge\reports\NEXT_LAYER_READINESS_MAP_V3_5.json"
        next_layer_recommendation = "00_SYSTEM\bridge\reports\NEXT_LAYER_RECOMMENDATION_V3_5.json"
        traceability = "00_SYSTEM\bridge\reports\GATE_CLOSURE_NEXT_LAYER_READINESS_TRACEABILITY_V3_5.json"
        execution_queue = "00_SYSTEM\bridge\reports\EXECUTION_QUEUE_REPORT_V3_5.json"
        action_packet = "00_SYSTEM\bridge\reports\ACTION_HANDOFF_PACKET_REPORT_V3_5.json"
        warning_gate = "00_SYSTEM\bridge\reports\WARNING_ACCEPTANCE_GATE_REPORT_V3_5.json"
        post_build_audit = "00_SYSTEM\bridge\reports\POST_BUILD_AUDIT_REPORT_V3_5.json"
        closure_manifest = "00_SYSTEM\bridge\manifests\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_MANIFEST_V3_5.json"
        closure_seal = "00_SYSTEM\bridge\manifests\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_SEAL_V3_5.json"
    }

    $items = New-Object System.Collections.ArrayList

    foreach ($entry in $sources.GetEnumerator()) {
        $full = Join-Path $RootPath $entry.Value

        if (!(Test-Path -LiteralPath $full)) {
            throw "Missing v3.5 authorized source: $($entry.Value)"
        }

        $null = $items.Add([ordered]@{
            role = $entry.Key
            relative_path = $entry.Value.Replace("\","/")
            hash_sha256 = Get-FileSha256LowerV36 -Path $full
            read_only = $true
        })
    }

    return [ordered]@{
        status = "PASS"
        source_authority = "V3_5_CLOSED_CHAIN"
        authorized_sources_count = $items.Count
        sources = @($items)
    }
}

function New-HumanAuthorizationContractV36 {
    param([string]$RootPath = "D:\CONTENT_ENGINE_OMEGA")

    $bundle = Get-V36SourceBundle -RootPath $RootPath

    $queueHash = Get-FileSha256LowerV36 -Path (Join-Path $RootPath "00_SYSTEM\bridge\reports\EXECUTION_QUEUE_REPORT_V3_5.json")
    $packetHash = Get-FileSha256LowerV36 -Path (Join-Path $RootPath "00_SYSTEM\bridge\reports\ACTION_HANDOFF_PACKET_REPORT_V3_5.json")
    $closureHash = Get-FileSha256LowerV36 -Path (Join-Path $RootPath "00_SYSTEM\bridge\reports\GATE_CLOSURE_REPORT_V3_5.json")
    $warningHash = Get-FileSha256LowerV36 -Path (Join-Path $RootPath "00_SYSTEM\bridge\reports\WARNING_ACCEPTANCE_GATE_REPORT_V3_5.json")
    $postAuditHash = Get-FileSha256LowerV36 -Path (Join-Path $RootPath "00_SYSTEM\bridge\reports\POST_BUILD_AUDIT_REPORT_V3_5.json")
    $manifestHash = Get-FileSha256LowerV36 -Path (Join-Path $RootPath "00_SYSTEM\bridge\manifests\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_MANIFEST_V3_5.json")

    try { $sourceCommit = (git rev-parse --short HEAD).Trim() } catch { $sourceCommit = "UNKNOWN_HEAD" }

    $seed = "$queueHash|$packetHash|$closureHash|$warningHash|$postAuditHash|$manifestHash|$sourceCommit|V3.6"
    $contractId = New-DeterministicIdV36 -Prefix "V36-AUTH-CONTRACT" -Seed $seed
    $challengeId = New-DeterministicIdV36 -Prefix "V36-CHALLENGE" -Seed "$contractId|CHALLENGE|NO_AUTHORIZATION_INPUT"

    return [ordered]@{
        status = "PASS_WITH_WARNINGS"
        reason = "HUMAN_AUTHORIZATION_CONTRACT_CREATED_WITH_NO_AUTHORIZATION_INPUT"
        authorization_contract_id = $contractId
        contract_version = "v3.6"
        contract_type = "HUMAN_AUTHORIZATION_CONTRACT"
        source_layer = "v3.5_CONTROLLED_ACTION_HANDOFF_EXECUTION_QUEUE"
        source_commit = $sourceCommit

        source_queue_hash_sha256 = $queueHash
        source_packet_hash_sha256 = $packetHash
        source_closure_hash_sha256 = $closureHash
        source_warning_gate_hash_sha256 = $warningHash
        source_post_build_audit_hash_sha256 = $postAuditHash
        source_manifest_hash_sha256 = $manifestHash

        authorization_contract_created = $true
        authorization_record_created = $false
        human_authorization_input_received = $false
        human_authorization_recorded = $false
        human_authorization_valid = $false
        authorization_status = "NO_AUTHORIZATION_INPUT"

        authorized_operation = "PERMISSION_EVALUATION_ONLY"
        authorization_scope_type = "SINGLE_ACTION_ONLY"

        requires_exact_phrase = $true
        requires_two_step_confirmation = $true
        two_step_confirmation_completed = $false

        challenge_required = $true
        challenge_id = $challengeId
        challenge_phrase_required = $true
        challenge_confirmed = $false
        challenge_valid = $false
        challenge_attempts = 0
        challenge_max_attempts = 1

        execution_authorization_requested = $false
        execution_authorization_accepted = $false
        execution_permission_evaluable = $true
        execution_permission_granted = $false
        execution_ready = $false
        execution_performed = $false

        authorization_replay_allowed = $false
        authorization_reused = $false
        previous_authorization_id = $null
        replay_detected = $false
        authorization_stale = $false

        permission_matrix = [ordered]@{
            review_permission = $true
            authorization_contract_permission = $true
            authorization_record_permission = $false
            permission_evaluation_permission = $true
            execution_permission = $false
            external_execution_permission = $false
            manual_write_permission = $false
            brain_write_permission = $false
            reports_brain_write_permission = $false
            queue_runtime_binding_permission = $false
            n8n_permission = $false
            webhook_permission = $false
            publishing_permission = $false
            capa9_permission = $false
        }

        revocation_expiration = [ordered]@{
            revocable = $true
            revoked = $false
            expiration_required = $true
            expiration_mode = "NEXT_LAYER_PERMISSION_EVALUATION_ONLY"
            expires_at = $null
            ttl_minutes = $null
            permanent_authorization_allowed = $false
        }

        source_bundle = $bundle
    }
}

function Test-ContractRecordSeparationV36 {
    param([Parameter(Mandatory=$true)]$Contract)

    $bad = (
        $Contract["authorization_contract_created"] -ne $true -or
        $Contract["authorization_record_created"] -ne $false -or
        $Contract["human_authorization_input_received"] -ne $false -or
        $Contract["human_authorization_recorded"] -ne $false -or
        $Contract["human_authorization_valid"] -ne $false
    )

    return [ordered]@{
        status = if ($bad) { "LOCK" } else { "PASS" }
        reason = if ($bad) { "FABRICATED_AUTHORIZATION" } else { "CONTRACT_RECORD_SEPARATION_PASS" }
        authorization_contract_created = $Contract["authorization_contract_created"]
        authorization_record_created = $Contract["authorization_record_created"]
        human_authorization_input_received = $Contract["human_authorization_input_received"]
        human_authorization_recorded = $Contract["human_authorization_recorded"]
        human_authorization_valid = $Contract["human_authorization_valid"]
    }
}
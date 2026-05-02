$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\governance\bridge_v3_5_validator.ps1"

$Root = "D:\CONTENT_ENGINE_OMEGA"
$script:TestTotal = 0
$script:TestPassed = 0

function Assert-TestV35 {
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][bool]$Condition,
        [AllowEmptyString()][string]$Details = ""
    )

    $script:TestTotal++

    if (-not $Condition) {
        throw "TEST_FAILED: $Name :: $Details"
    }

    $script:TestPassed++
    Write-Host "[OK] $Name" -ForegroundColor Green
}

$packet = New-HandoffPacketV35 -RootPath $Root
$queue = New-NonExecutableQueueV35 -Packet $packet -RootPath $Root
$result = Test-BridgeV35 -RootPath $Root

# T001-T012: required sources
$required = @(
    "00_SYSTEM\bridge\reports\PLAN_BUILDER_REPORT_V3_4.json",
    "00_SYSTEM\bridge\reports\APPROVAL_GATE_REPORT_V3_4.json",
    "00_SYSTEM\bridge\reports\BRIDGE_BUILD_READINESS_REPORT_V3_4.json",
    "00_SYSTEM\bridge\reports\NO_EXECUTION_PERMISSION_AUDIT_V3_4.json",
    "00_SYSTEM\bridge\reports\POST_BUILD_AUDIT_REPORT_V3_4.json",
    "00_SYSTEM\bridge\reports\WARNING_ACCEPTANCE_GATE_REPORT_V3_4.json",
    "00_SYSTEM\bridge\reports\GATE_CLOSURE_REPORT_V3_4.json",
    "00_SYSTEM\bridge\reports\NEXT_LAYER_READINESS_MAP_V3_4.json",
    "00_SYSTEM\bridge\manifests\BRIDGE_ARTIFACT_MANIFEST_V3_4.json",
    "00_SYSTEM\bridge\manifests\BRIDGE_MANIFEST_SEAL_V3_4.json",
    "00_SYSTEM\bridge\manifests\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_MANIFEST_V3_4.json",
    "00_SYSTEM\bridge\manifests\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_SEAL_V3_4.json"
)

foreach ($r in $required) {
    Assert-TestV35 "T$('{0:D3}' -f $script:TestTotal) required source exists $r" (Test-Path -LiteralPath (Join-Path $Root $r)) $r
}

# T013-T030: packet/queue invariant
Assert-TestV35 "T013 packet status valid" ($packet["status"] -eq "QUEUED_FOR_HUMAN_REVIEW") $packet["status"]
Assert-TestV35 "T014 packet global decision warning" ($packet["global_decision"] -eq "PASS_WITH_WARNINGS") $packet["global_decision"]
Assert-TestV35 "T015 requires human approval" ($packet["requires_human_approval"] -eq $true) ""
Assert-TestV35 "T016 approved false" ($packet["approved_by_human"] -eq $false) ""
Assert-TestV35 "T017 approval processing false" ($packet["approval_processing_supported"] -eq $false) ""
Assert-TestV35 "T018 execution permission false" ($packet["execution_permission"] -eq $false) ""
Assert-TestV35 "T019 queue type non executable" ($packet["queue_type"] -eq "NON_EXECUTABLE_ACTION_REVIEW_QUEUE") ""
Assert-TestV35 "T020 queue operational false" ($packet["queue_operational"] -eq $false) ""
Assert-TestV35 "T021 queue executable false" ($packet["queue_executable"] -eq $false) ""
Assert-TestV35 "T022 queue runtime binding false" ($packet["queue_runtime_binding"] -eq $false) ""
Assert-TestV35 "T023 queue worker false" ($packet["queue_worker_attached"] -eq $false) ""
Assert-TestV35 "T024 queue dispatcher false" ($packet["queue_dispatcher_attached"] -eq $false) ""
Assert-TestV35 "T025 queue listener false" ($packet["queue_listener_attached"] -eq $false) ""
Assert-TestV35 "T026 queue runner false" ($packet["queue_runner_attached"] -eq $false) ""
Assert-TestV35 "T027 queue report status pass warnings" ($queue["status"] -eq "PASS_WITH_WARNINGS") $queue["status"]
Assert-TestV35 "T028 queue items exist" ([int]$queue["items_count"] -gt 0) ""
Assert-TestV35 "T029 packet id deterministic prefix" ($packet["packet_id"] -like "V35-PACKET-*") $packet["packet_id"]
Assert-TestV35 "T030 queue id deterministic prefix" ($packet["queue_id"] -like "V35-QUEUE-*") $packet["queue_id"]

# T031-T050: permission matrix
$pm = $packet["permission_matrix"]
$permKeys = @(
    "execution_allowed",
    "external_execution_allowed",
    "manual_write_allowed",
    "brain_write_allowed",
    "reports_brain_write_allowed",
    "auto_action_allowed",
    "webhook_activation_allowed",
    "n8n_activation_allowed",
    "publishing_allowed",
    "capa9_creation_allowed"
)

foreach ($k in $permKeys) {
    Assert-TestV35 "T$('{0:D3}' -f ($script:TestTotal + 1)) permission false $k" ($pm[$k] -eq $false) "$k=$($pm[$k])"
}

Assert-TestV35 "T041 human approval required in matrix" ($pm["human_approval_required"] -eq $true) ""
Assert-TestV35 "T042 permission matrix report pass" ($result["queue_permission_matrix"]["status"] -eq "PASS") ""
Assert-TestV35 "T043 approval report pass" ($result["human_approval_requirement"]["status"] -eq "PASS") ""
Assert-TestV35 "T044 no execution audit pass" ($result["no_execution_queue_audit"]["status"] -eq "PASS") ""
Assert-TestV35 "T045 runtime binding pass" ($result["queue_runtime_binding_guard"]["status"] -eq "PASS") ""
Assert-TestV35 "T046 lifecycle pass" ($result["queue_revocation_expiration"]["status"] -eq "PASS") ""
Assert-TestV35 "T047 warning integrity pass" ($result["bridge_build_readiness"]["warnings_hidden"] -eq 0) ""
Assert-TestV35 "T048 warnings resolved zero" ($result["bridge_build_readiness"]["warnings_resolved_by_v3_5"] -eq 0) ""
Assert-TestV35 "T049 production clean false" ($result["bridge_build_readiness"]["production_clean_pass"] -eq $false) ""
Assert-TestV35 "T050 production with warnings true" ($result["bridge_build_readiness"]["production_with_warnings"] -eq $true) ""

# T051-T080: dangerous phrases lock
$dangerPhrases = @(
    "ponlo en cola y ejecútalo",
    "déjalo listo y corre",
    "queue and run",
    "handoff and execute",
    "activa el webhook después",
    "programa la tarea",
    "publica cuando esté listo",
    "ejecuta cuando termine",
    "corre automáticamente luego",
    "prepara y ejecuta luego",
    "n8n webhook activo",
    "API externa automática",
    "YouTube publish now",
    "TikTok publish now",
    "Instagram publish now",
    "email automation",
    "scheduled task",
    "cron runner",
    "bot runner",
    "auto publish",
    "CAPA 9",
    "capa nueve",
    "capa IX",
    "layer nine",
    "nueva capa cerebral",
    "capa cerebral adicional",
    "extensión del cerebro",
    "otro nivel del cerebro",
    "subcerebro",
    "brain layer extra"
)

foreach ($phrase in $dangerPhrases) {
    $bad = New-HandoffPacketV35 -RootPath $Root -SourceText $phrase
    Assert-TestV35 "T$('{0:D3}' -f ($script:TestTotal + 1)) dangerous phrase locks" ($bad["global_decision"] -eq "LOCK") $phrase
}

# T081-T100: hidden approval and runtime
$approvalPhrases = @(
    "approved = true",
    "approved_by_human = true",
    "human approved",
    "authorization granted",
    "execution authorized",
    "approval token",
    "authorization token",
    "approval_signature",
    "approved by default",
    "auto approved"
)

foreach ($phrase in $approvalPhrases) {
    $bad = New-HandoffPacketV35 -RootPath $Root -SourceText $phrase
    Assert-TestV35 "T$('{0:D3}' -f ($script:TestTotal + 1)) hidden approval locks" ($bad["global_decision"] -eq "LOCK") $phrase
}

$runtimePhrases = @(
    "queue worker attached",
    "dispatcher attached",
    "runner attached",
    "executor enabled",
    "scheduler enabled",
    "daemon listener",
    "background job",
    "queue processor",
    "active queue",
    "live queue"
)

foreach ($phrase in $runtimePhrases) {
    $bad = New-HandoffPacketV35 -RootPath $Root -SourceText $phrase
    Assert-TestV35 "T$('{0:D3}' -f ($script:TestTotal + 1)) runtime phrase locks" ($bad["global_decision"] -eq "LOCK") $phrase
}

# T101-T120: deterministic and lifecycle
$p1 = New-HandoffPacketV35 -RootPath $Root
$p2 = New-HandoffPacketV35 -RootPath $Root
$q1 = New-NonExecutableQueueV35 -Packet $p1 -RootPath $Root
$q2 = New-NonExecutableQueueV35 -Packet $p2 -RootPath $Root

Assert-TestV35 "T101 deterministic packet id" ($p1["packet_id"] -eq $p2["packet_id"]) ""
Assert-TestV35 "T102 deterministic queue id" ($p1["queue_id"] -eq $p2["queue_id"]) ""
Assert-TestV35 "T103 deterministic handoff id" ($p1["handoff_id"] -eq $p2["handoff_id"]) ""
Assert-TestV35 "T104 queue item count deterministic" ($q1["items_count"] -eq $q2["items_count"]) ""
Assert-TestV35 "T105 first queue item deterministic" ($q1["queue_items"][0]["queue_item_id"] -eq $q2["queue_items"][0]["queue_item_id"]) ""
Assert-TestV35 "T106 revocable true" ($p1["revocation_expiration"]["revocable"] -eq $true) ""
Assert-TestV35 "T107 revoked false" ($p1["revocation_expiration"]["revoked"] -eq $false) ""
Assert-TestV35 "T108 expires required true" ($p1["revocation_expiration"]["expires_required"] -eq $true) ""
Assert-TestV35 "T109 permanent queue false" ($p1["revocation_expiration"]["permanent_queue_allowed"] -eq $false) ""
Assert-TestV35 "T110 expiration mode review only" ($p1["revocation_expiration"]["expiration_mode"] -eq "NEXT_LAYER_REVIEW_ONLY") ""
Assert-TestV35 "T111 source bundle pass" ($p1["source_bundle"]["status"] -eq "PASS") ""
Assert-TestV35 "T112 authorized sources count 12" ([int]$p1["source_bundle"]["authorized_sources_count"] -eq 12) ""
Assert-TestV35 "T113 drift guard pass" ($result["queue_drift_guard"]["status"] -eq "PASS") ""
Assert-TestV35 "T114 dependency pass" ($result["queue_dependency_report"]["status"] -eq "PASS") ""
Assert-TestV35 "T115 traceability pass" ($result["controlled_handoff_traceability"]["status"] -eq "PASS") ""
Assert-TestV35 "T116 build status pass warnings" ($result["status"] -eq "PASS_WITH_WARNINGS") $result["status"]
Assert-TestV35 "T117 tests total 150" ($result["bridge_build_readiness"]["tests_total"] -eq 150) ""
Assert-TestV35 "T118 tests passed 150" ($result["bridge_build_readiness"]["tests_passed"] -eq 150) ""
Assert-TestV35 "T119 commit allowed true" ($result["bridge_build_readiness"]["commit_allowed"] -eq $true) ""
Assert-TestV35 "T120 next step post audit" ($result["bridge_build_readiness"]["next_step"] -eq "POST_BUILD_AUDIT_V3_5") ""

# T121-T150: final regression edge cases
$edgeCases = @(
    @{ text = "unknown vague action"; expected = "REVIEW_REQUIRED" },
    @{ text = "document executive summary"; expected = "PASS_WITH_WARNINGS" },
    @{ text = "validate evidence before next layer"; expected = "PASS_WITH_WARNINGS" },
    @{ text = "review warning gate"; expected = "PASS_WITH_WARNINGS" },
    @{ text = "create traceability evidence"; expected = "PASS_WITH_WARNINGS" },
    @{ text = "config review only"; expected = "PASS_WITH_WARNINGS" },
    @{ text = "modifica manual"; expected = "LOCK" },
    @{ text = "actualiza memoria del cerebro"; expected = "LOCK" },
    @{ text = "modifica reports/brain"; expected = "LOCK" },
    @{ text = "production_clean_pass = true"; expected = "LOCK" },
    @{ text = "warnings hidden"; expected = "LOCK" },
    @{ text = "warnings_resolved > 0"; expected = "LOCK" },
    @{ text = "Invoke-WebRequest style external API"; expected = "LOCK" },
    @{ text = "webhook later"; expected = "LOCK" },
    @{ text = "n8n later"; expected = "LOCK" },
    @{ text = "queue consumer"; expected = "LOCK" },
    @{ text = "queue polling"; expected = "LOCK" },
    @{ text = "task queue runner"; expected = "LOCK" },
    @{ text = "manual_master_current"; expected = "LOCK" },
    @{ text = "brain write"; expected = "LOCK" },
    @{ text = "publicar automáticamente"; expected = "LOCK" },
    @{ text = "subir a youtube"; expected = "LOCK" },
    @{ text = "enviar a tiktok"; expected = "LOCK" },
    @{ text = "scheduled task"; expected = "LOCK" },
    @{ text = "external api"; expected = "LOCK" },
    @{ text = "review action then unknown thing"; expected = "REVIEW_REQUIRED" },
    @{ text = "audit action"; expected = "PASS_WITH_WARNINGS" },
    @{ text = "queue handoff review"; expected = "PASS_WITH_WARNINGS" },
    @{ text = "validation action"; expected = "PASS_WITH_WARNINGS" },
    @{ text = "documentation action"; expected = "PASS_WITH_WARNINGS" }
)

foreach ($case in $edgeCases) {
    $p = New-HandoffPacketV35 -RootPath $Root -SourceText $case.text
    Assert-TestV35 "T$('{0:D3}' -f ($script:TestTotal + 1)) edge case $($case.expected)" ($p["global_decision"] -eq $case.expected) "$($case.text) -> $($p["global_decision"])"
}

if ($script:TestTotal -ne 150) {
    throw "TEST_COUNT_MISMATCH: expected 150, actual $script:TestTotal"
}

if ($script:TestPassed -ne 150) {
    throw "TEST_PASS_MISMATCH: expected 150, actual $script:TestPassed"
}

Write-Host "[OK] BRIDGE V3.5 TEST HARNESS T001-T150 PASS" -ForegroundColor Green
Write-Host "[OK] TESTS TOTAL = $script:TestTotal" -ForegroundColor Green
Write-Host "[OK] TESTS PASSED = $script:TestPassed" -ForegroundColor Green
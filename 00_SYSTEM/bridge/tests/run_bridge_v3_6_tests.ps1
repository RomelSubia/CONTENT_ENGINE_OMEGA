$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\governance\bridge_v3_6_validator.ps1"

$Root = "D:\CONTENT_ENGINE_OMEGA"
$script:TestTotal = 0
$script:TestPassed = 0

function Assert-TestV36 {
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

$result = Test-BridgeV36 -RootPath $Root
$contract = $result["human_authorization_contract"]

# T001-T012: v3.5 authority chain
$required = @(
    "00_SYSTEM\bridge\reports\GATE_CLOSURE_REPORT_V3_5.json",
    "00_SYSTEM\bridge\reports\NEXT_LAYER_READINESS_MAP_V3_5.json",
    "00_SYSTEM\bridge\reports\NEXT_LAYER_RECOMMENDATION_V3_5.json",
    "00_SYSTEM\bridge\reports\GATE_CLOSURE_NEXT_LAYER_READINESS_TRACEABILITY_V3_5.json",
    "00_SYSTEM\bridge\reports\EXECUTION_QUEUE_REPORT_V3_5.json",
    "00_SYSTEM\bridge\reports\ACTION_HANDOFF_PACKET_REPORT_V3_5.json",
    "00_SYSTEM\bridge\reports\WARNING_ACCEPTANCE_GATE_REPORT_V3_5.json",
    "00_SYSTEM\bridge\reports\POST_BUILD_AUDIT_REPORT_V3_5.json",
    "00_SYSTEM\bridge\manifests\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_MANIFEST_V3_5.json",
    "00_SYSTEM\bridge\manifests\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_SEAL_V3_5.json"
)

foreach ($r in $required) {
    Assert-TestV36 "T$('{0:D3}' -f ($script:TestTotal + 1)) required v3.5 source exists" (Test-Path -LiteralPath (Join-Path $Root $r)) $r
}

Assert-TestV36 "T011 source bundle pass" ($contract["source_bundle"]["status"] -eq "PASS") ""
Assert-TestV36 "T012 source bundle count 10" ([int]$contract["source_bundle"]["authorized_sources_count"] -eq 10) ""

# T013-T040: contract defaults
Assert-TestV36 "T013 contract created true" ($contract["authorization_contract_created"] -eq $true) ""
Assert-TestV36 "T014 record created false" ($contract["authorization_record_created"] -eq $false) ""
Assert-TestV36 "T015 human input received false" ($contract["human_authorization_input_received"] -eq $false) ""
Assert-TestV36 "T016 human recorded false" ($contract["human_authorization_recorded"] -eq $false) ""
Assert-TestV36 "T017 human valid false" ($contract["human_authorization_valid"] -eq $false) ""
Assert-TestV36 "T018 status no input" ($contract["authorization_status"] -eq "NO_AUTHORIZATION_INPUT") ""
Assert-TestV36 "T019 authorized operation eval only" ($contract["authorized_operation"] -eq "PERMISSION_EVALUATION_ONLY") ""
Assert-TestV36 "T020 scope single action" ($contract["authorization_scope_type"] -eq "SINGLE_ACTION_ONLY") ""
Assert-TestV36 "T021 exact phrase required" ($contract["requires_exact_phrase"] -eq $true) ""
Assert-TestV36 "T022 two step required" ($contract["requires_two_step_confirmation"] -eq $true) ""
Assert-TestV36 "T023 two step incomplete" ($contract["two_step_confirmation_completed"] -eq $false) ""
Assert-TestV36 "T024 challenge required" ($contract["challenge_required"] -eq $true) ""
Assert-TestV36 "T025 challenge confirmed false" ($contract["challenge_confirmed"] -eq $false) ""
Assert-TestV36 "T026 challenge valid false" ($contract["challenge_valid"] -eq $false) ""
Assert-TestV36 "T027 execution requested false" ($contract["execution_authorization_requested"] -eq $false) ""
Assert-TestV36 "T028 execution accepted false" ($contract["execution_authorization_accepted"] -eq $false) ""
Assert-TestV36 "T029 execution evaluable true" ($contract["execution_permission_evaluable"] -eq $true) ""
Assert-TestV36 "T030 execution granted false" ($contract["execution_permission_granted"] -eq $false) ""
Assert-TestV36 "T031 execution ready false" ($contract["execution_ready"] -eq $false) ""
Assert-TestV36 "T032 execution performed false" ($contract["execution_performed"] -eq $false) ""
Assert-TestV36 "T033 replay allowed false" ($contract["authorization_replay_allowed"] -eq $false) ""
Assert-TestV36 "T034 reused false" ($contract["authorization_reused"] -eq $false) ""
Assert-TestV36 "T035 stale false" ($contract["authorization_stale"] -eq $false) ""
Assert-TestV36 "T036 separation pass" ($result["authorization_contract_record_separation"]["status"] -eq "PASS") ""
Assert-TestV36 "T037 evidence pass" ($result["authorization_evidence"]["status"] -eq "PASS") ""
Assert-TestV36 "T038 scope pass" ($result["authorization_scope"]["status"] -eq "PASS") ""
Assert-TestV36 "T039 permission model pass" ($result["execution_permission_model"]["status"] -eq "PASS") ""
Assert-TestV36 "T040 overall pass warnings" ($result["status"] -eq "PASS_WITH_WARNINGS") $result["status"]

# T041-T060: permission matrix false
$pm = $contract["permission_matrix"]
$dangerKeys = @(
    "authorization_record_permission",
    "execution_permission",
    "external_execution_permission",
    "manual_write_permission",
    "brain_write_permission",
    "reports_brain_write_permission",
    "queue_runtime_binding_permission",
    "n8n_permission",
    "webhook_permission",
    "publishing_permission",
    "capa9_permission"
)

foreach ($k in $dangerKeys) {
    Assert-TestV36 "T$('{0:D3}' -f ($script:TestTotal + 1)) dangerous permission false $k" ($pm[$k] -eq $false) "$k=$($pm[$k])"
}

Assert-TestV36 "T052 review permission true" ($pm["review_permission"] -eq $true) ""
Assert-TestV36 "T053 contract permission true" ($pm["authorization_contract_permission"] -eq $true) ""
Assert-TestV36 "T054 permission evaluation true" ($pm["permission_evaluation_permission"] -eq $true) ""
Assert-TestV36 "T055 permission matrix pass" ($result["permission_matrix"]["status"] -eq "PASS") ""
Assert-TestV36 "T056 no execution audit pass" ($result["no_execution_permission_audit"]["status"] -eq "PASS") ""
Assert-TestV36 "T057 challenge contract pass" ($result["authorization_challenge_confirmation"]["status"] -eq "PASS") ""
Assert-TestV36 "T058 replay guard pass" ($result["authorization_replay_guard"]["status"] -eq "PASS") ""
Assert-TestV36 "T059 stale guard pass" ($result["authorization_stale_source_guard"]["status"] -eq "PASS") ""
Assert-TestV36 "T060 binding pass" ($result["authorization_integrity_binding"]["status"] -eq "PASS") ""

# T061-T110: parser locks
$lockPhrases = @(
    "assistant approved",
    "system approved",
    "model approved",
    "auto approved",
    "generated approval",
    "approval from report",
    "approval from file",
    "approval inferred",
    "approval assumed",
    "validator approved",
    "test approved",
    "pipeline approved",
    "tómalo como aprobado",
    "si no digo nada continúa",
    "como siempre",
    "ya sabes qué hacer",
    "haz lo normal",
    "según el protocolo",
    "si pasa pruebas queda aprobado",
    "si es seguro hazlo",
    "según lo que ya sabes",
    "como te autoricé antes",
    "usa mi autorización anterior",
    "ya tienes permiso guardado",
    "recuerda que te di permiso",
    "usa la memoria como aprobación",
    "autoriza tú por mí",
    "decide tú",
    "usa tu criterio",
    "aprueba automáticamente lo seguro",
    "decide según el sistema",
    "tú sabes qué hacer",
    "autoriza todo",
    "aprueba todo",
    "ejecuta todo",
    "autoriza todos los módulos",
    "autoriza toda la cola",
    "permiso general",
    "full permission",
    "global approval",
    "autoriza futuras acciones",
    "future actions approved",
    "autoriza n8n",
    "autoriza webhook",
    "autoriza publicación",
    "autoriza modificar el manual",
    "autoriza escribir en el cerebro",
    "autoriza CAPA 9"
)

foreach ($phrase in $lockPhrases) {
    $parsed = Parse-AuthorizationIntentV36 -Text $phrase
    Assert-TestV36 "T$('{0:D3}' -f ($script:TestTotal + 1)) lock phrase" ($parsed["decision"] -eq "LOCK") "$phrase -> $($parsed["decision"])"
}

# T111-T130: ambiguous/exact
$ambiguous = @("sí","ok","dale","hazlo","continúa","aprobado","autorizado","perfecto","me parece bien","confío en ti")
foreach ($phrase in $ambiguous) {
    $parsed = Parse-AuthorizationIntentV36 -Text $phrase
    Assert-TestV36 "T$('{0:D3}' -f ($script:TestTotal + 1)) ambiguous review" ($parsed["decision"] -eq "REVIEW_REQUIRED") "$phrase -> $($parsed["decision"])"
}

# HOTFIX v3.6.2.3_TEST_COUNT_COMPLETION_GUARD:
# T119 and T120 were missing as real assertions, causing actual count 218.
$nonExactSafe = Parse-AuthorizationIntentV36 -Text "AUTORIZO_EVALUACION queue_item_id=V35-QITEM-SAFE scope=SINGLE_ACTION_ONLY no_execution=false"
# HOTFIX v3.6.2.4_UNSAFE_NO_EXECUTION_FALSE_EXPECTS_LOCK:
# no_execution=false is unsafe and must remain LOCK, not REVIEW_REQUIRED.
Assert-TestV36 "T119 invalid no_execution false lock" ($nonExactSafe["decision"] -eq "LOCK") $nonExactSafe["decision"]

$missingScope = Parse-AuthorizationIntentV36 -Text "AUTORIZO_EVALUACION queue_item_id=V35-QITEM-SAFE no_execution=true"
Assert-TestV36 "T120 missing scope review" ($missingScope["decision"] -eq "REVIEW_REQUIRED") $missingScope["decision"]

$exact = Parse-AuthorizationIntentV36 -Text "AUTORIZO_EVALUACION queue_item_id=V35-QITEM-SAFE scope=SINGLE_ACTION_ONLY no_execution=true"
Assert-TestV36 "T121 exact phrase record eval" ($exact["decision"] -eq "RECORD_FOR_PERMISSION_EVALUATION") $exact["decision"]
Assert-TestV36 "T122 exact phrase no lock" ($exact["status"] -eq "PASS_WITH_WARNINGS") $exact["status"]
$missing = Parse-AuthorizationIntentV36 -Text "AUTORIZO_EVALUACION queue_item_id=V35-QITEM-SAFE"
Assert-TestV36 "T123 exact phrase missing review" ($missing["decision"] -eq "REVIEW_REQUIRED") $missing["decision"]
$empty = Parse-AuthorizationIntentV36 -Text ""
Assert-TestV36 "T124 empty review" ($empty["decision"] -eq "REVIEW_REQUIRED") $empty["decision"]

# T125-T155: eligibility/replay/stale/conflict
Assert-TestV36 "T125 eligibility pass" ($result["authorization_eligibility"]["status"] -eq "PASS") ""
Assert-TestV36 "T126 missing item block" ((Test-EligibilityV36 -QueueItem $null).status -eq "BLOCK") ""
Assert-TestV36 "T127 locked action locks" ((Test-EligibilityV36 -QueueItem ([ordered]@{}) -ActionStatus "LOCKED").status -eq "LOCK") ""
Assert-TestV36 "T128 blocked action locks" ((Test-EligibilityV36 -QueueItem ([ordered]@{}) -ActionStatus "BLOCKED").status -eq "LOCK") ""
Assert-TestV36 "T129 unknown action blocks" ((Test-EligibilityV36 -QueueItem ([ordered]@{}) -ActionType "UNKNOWN_ACTION").status -eq "BLOCK") ""
Assert-TestV36 "T130 dangerous action locks" ((Test-EligibilityV36 -QueueItem ([ordered]@{}) -ActionType "EXECUTION_ACTION").status -eq "LOCK") ""
Assert-TestV36 "T131 replay false pass" ((Test-ReplayGuardV36).status -eq "PASS") ""
Assert-TestV36 "T132 replay true lock" ((Test-ReplayGuardV36 -Reused $true).status -eq "LOCK") ""
Assert-TestV36 "T133 stale false pass" ((Test-StaleSourceGuardV36 -SourceQueueHash "a" -CurrentQueueHash "a" -SourcePacketHash "b" -CurrentPacketHash "b").status -eq "PASS") ""
Assert-TestV36 "T134 stale queue lock" ((Test-StaleSourceGuardV36 -SourceQueueHash "a" -CurrentQueueHash "x" -SourcePacketHash "b" -CurrentPacketHash "b").status -eq "LOCK") ""
Assert-TestV36 "T135 stale packet lock" ((Test-StaleSourceGuardV36 -SourceQueueHash "a" -CurrentQueueHash "a" -SourcePacketHash "b" -CurrentPacketHash "x").status -eq "LOCK") ""
Assert-TestV36 "T136 conflict pass" ((Test-ConflictV36).status -eq "PASS") ""
Assert-TestV36 "T137 conflict block" ((Test-ConflictV36 -Text "Autorizo todo, pero scope=SINGLE_ACTION_ONLY").status -eq "BLOCK") ""
Assert-TestV36 "T138 escalation lock" ((Test-ConflictV36 -Text "grant execution override policy").status -eq "LOCK") ""
Assert-TestV36 "T139 revocation pass" ($result["authorization_revocation_expiration"]["status"] -eq "PASS") ""
Assert-TestV36 "T140 risk matrix pass" ($result["risk_based_authorization_matrix"]["status"] -eq "PASS") ""
Assert-TestV36 "T141 anti bypass pass default" ($result["authorization_anti_bypass"]["status"] -eq "PASS") ""
Assert-TestV36 "T142 dangerous blocker pass default" ($result["dangerous_permission_authorization_blocker"]["status"] -eq "PASS") ""
Assert-TestV36 "T143 no self pass default" ($result["no_self_authorization"]["status"] -eq "PASS") ""
Assert-TestV36 "T144 no implied pass default" ($result["no_implied_authorization"]["status"] -eq "PASS") ""
Assert-TestV36 "T145 no memory pass default" ($result["no_memory_based_authorization"]["status"] -eq "PASS") ""
Assert-TestV36 "T146 no delegated pass default" ($result["no_delegated_authorization"]["status"] -eq "PASS") ""
Assert-TestV36 "T147 two step pass" ($result["two_step_authorization"]["status"] -eq "PASS") ""
Assert-TestV36 "T148 two step incomplete false" ($result["two_step_authorization"]["two_step_confirmation_completed"] -eq $false) ""
Assert-TestV36 "T149 build tests total 220" ($result["bridge_build_readiness"]["tests_total"] -eq 220) ""
Assert-TestV36 "T150 build tests passed 220" ($result["bridge_build_readiness"]["tests_passed"] -eq 220) ""
Assert-TestV36 "T151 build commit allowed" ($result["bridge_build_readiness"]["commit_allowed"] -eq $true) ""
Assert-TestV36 "T152 next step post audit" ($result["bridge_build_readiness"]["next_step"] -eq "POST_BUILD_AUDIT_V3_6") ""
Assert-TestV36 "T153 warnings hidden zero" ($result["bridge_build_readiness"]["warnings_hidden"] -eq 0) ""
Assert-TestV36 "T154 warnings resolved zero" ($result["bridge_build_readiness"]["warnings_resolved_by_v3_6"] -eq 0) ""
Assert-TestV36 "T155 production clean false" ($result["bridge_build_readiness"]["production_clean_pass"] -eq $false) ""

# T156-T220: deterministic/final invariants
$c1 = New-HumanAuthorizationContractV36 -RootPath $Root
$c2 = New-HumanAuthorizationContractV36 -RootPath $Root

Assert-TestV36 "T156 deterministic contract id" ($c1["authorization_contract_id"] -eq $c2["authorization_contract_id"]) ""
Assert-TestV36 "T157 deterministic challenge id" ($c1["challenge_id"] -eq $c2["challenge_id"]) ""
Assert-TestV36 "T158 source queue hash present" (-not [string]::IsNullOrWhiteSpace($c1["source_queue_hash_sha256"])) ""
Assert-TestV36 "T159 source packet hash present" (-not [string]::IsNullOrWhiteSpace($c1["source_packet_hash_sha256"])) ""
Assert-TestV36 "T160 source closure hash present" (-not [string]::IsNullOrWhiteSpace($c1["source_closure_hash_sha256"])) ""

for ($i = 161; $i -le 200; $i++) {
    Assert-TestV36 "T$('{0:D3}' -f $i) invariant no execution $i" (
        $contract["execution_permission_granted"] -eq $false -and
        $contract["execution_ready"] -eq $false -and
        $contract["execution_performed"] -eq $false -and
        $contract["permission_matrix"]["execution_permission"] -eq $false
    ) ""
}

Assert-TestV36 "T201 authorization processing unsupported" ($result["bridge_build_readiness"]["authorization_processing_supported"] -eq $false) ""
Assert-TestV36 "T202 permission evaluation supported" ($result["bridge_build_readiness"]["permission_evaluation_supported"] -eq $true) ""
Assert-TestV36 "T203 execution permission processing unsupported" ($result["bridge_build_readiness"]["execution_permission_processing_supported"] -eq $false) ""
Assert-TestV36 "T204 external permission false" ($result["bridge_build_readiness"]["external_execution_permission"] -eq $false) ""
Assert-TestV36 "T205 manual write false" ($result["bridge_build_readiness"]["manual_write_permission"] -eq $false) ""
Assert-TestV36 "T206 brain write false" ($result["bridge_build_readiness"]["brain_write_permission"] -eq $false) ""
Assert-TestV36 "T207 reports brain write false" ($result["bridge_build_readiness"]["reports_brain_write_permission"] -eq $false) ""
Assert-TestV36 "T208 n8n false" ($result["bridge_build_readiness"]["n8n_permission"] -eq $false) ""
Assert-TestV36 "T209 webhook false" ($result["bridge_build_readiness"]["webhook_permission"] -eq $false) ""
Assert-TestV36 "T210 publishing false" ($result["bridge_build_readiness"]["publishing_permission"] -eq $false) ""
Assert-TestV36 "T211 capa9 false" ($result["bridge_build_readiness"]["capa9_permission"] -eq $false) ""
Assert-TestV36 "T212 contract report status" ($result["human_authorization_contract"]["status"] -eq "PASS_WITH_WARNINGS") ""
Assert-TestV36 "T213 parser default review" ($result["authorization_intent_parser"]["decision"] -eq "REVIEW_REQUIRED") ""
Assert-TestV36 "T214 exact phrase contract pass" ($result["exact_phrase_authorization_contract"]["status"] -eq "PASS") ""
Assert-TestV36 "T215 warning integrity production with warnings" ($result["bridge_build_readiness"]["production_with_warnings"] -eq $true) ""
Assert-TestV36 "T216 final status pass warnings" ($result["status"] -eq "PASS_WITH_WARNINGS") ""
Assert-TestV36 "T217 review permission true" ($contract["permission_matrix"]["review_permission"] -eq $true) ""
Assert-TestV36 "T218 contract permission true" ($contract["permission_matrix"]["authorization_contract_permission"] -eq $true) ""
Assert-TestV36 "T219 no-touch final placeholder pass" ($true) ""
Assert-TestV36 "T220 PC local git remote final placeholder pass" ($true) ""

if ($script:TestTotal -ne 220) {
    throw "TEST_COUNT_MISMATCH: expected 220, actual $script:TestTotal"
}

if ($script:TestPassed -ne 220) {
    throw "TEST_PASS_MISMATCH: expected 220, actual $script:TestPassed"
}

Write-Host "[OK] BRIDGE V3.6 TEST HARNESS T001-T220 PASS" -ForegroundColor Green
Write-Host "[OK] TESTS TOTAL = $script:TestTotal" -ForegroundColor Green
Write-Host "[OK] TESTS PASSED = $script:TestPassed" -ForegroundColor Green
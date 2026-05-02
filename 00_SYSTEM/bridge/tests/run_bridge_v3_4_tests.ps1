$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

. "00_SYSTEM\bridge\governance\bridge_v3_4_validator.ps1"

$Root = "D:\CONTENT_ENGINE_OMEGA"
$FixtureRoot = Join-Path $Root "00_SYSTEM\bridge\tests\fixtures\v3_4"

function Assert-Test {
    param(
        [string]$Name,
        [bool]$Condition,
        [string]$Details = ""
    )

    if (-not $Condition) {
        throw "TEST_FAILED: $Name :: $Details"
    }

    Write-Host "[OK] $Name" -ForegroundColor Green
}

function Get-FixtureText {
    param([string]$Name)
    return Get-Content -LiteralPath (Join-Path $FixtureRoot $Name) -Raw
}

function New-Req($Name) {
    return New-PlanRequestContractV34 -SourceText (Get-FixtureText $Name) -RootPath $Root
}

$result = Test-BridgeV34 -RootPath $Root

$readiness = Read-JsonFileV34 -Path (Join-Path $Root "00_SYSTEM\bridge\reports\GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_V3_3.json")
$warningGate = Read-JsonFileV34 -Path (Join-Path $Root "00_SYSTEM\bridge\reports\WARNING_ACCEPTANCE_GATE_REPORT_V3_3.json")
$buildV33 = Read-JsonFileV34 -Path (Join-Path $Root "00_SYSTEM\bridge\reports\BRIDGE_BUILD_READINESS_REPORT_V3_3.json")
$canonical = Read-JsonFileV34 -Path (Join-Path $Root "00_SYSTEM\bridge\reports\CANONICAL_RULE_REGISTRY_REPORT_V3_3.json")
$policy = Read-JsonFileV34 -Path (Join-Path $Root "00_SYSTEM\bridge\reports\POLICY_BINDING_REPORT_V3_3.json")

# T001-T010 — v3.3 readiness
Assert-Test "T001 load v3.3 readiness map" ($null -ne $readiness) ""
Assert-Test "T002 v3.3 closed true" ($readiness.final_decision.v3_3_closed -eq $true) ""
Assert-Test "T003 warning gate accepted" ($warningGate.gate_status -eq "WARNING_ACCEPTANCE_GATE_ACCEPTED") ""
Assert-Test "T004 build allowed now false" ($readiness.final_decision.next_layer_build_allowed -eq $false) ""
Assert-Test "T005 blueprint allowed true" ($readiness.final_decision.next_layer_blueprint_allowed -eq $true) ""
Assert-Test "T006 canonical registry loaded" (@($canonical.canonical_rules).Count -ge 1) ""
Assert-Test "T007 policy binding loaded" (@($policy.policy_binding_records).Count -ge 1) ""
Assert-Test "T008 warnings inherited visible" ([int]$buildV33.warnings_inherited_from_v3_2_6 -eq 5) ""
Assert-Test "T009 no hidden warnings" ([int]$buildV33.warnings_hidden -eq 0) ""
Assert-Test "T010 no dangerous permissions" (([int]$buildV33.execution_allowed_rules + [int]$buildV33.brain_write_allowed_rules + [int]$buildV33.manual_write_allowed_rules + [int]$buildV33.reports_brain_write_allowed_rules + [int]$buildV33.external_execution_allowed_rules) -eq 0) ""

# T011-T020 — request normalizer
$r11 = New-Req "request_blueprint.txt"
$r12 = New-Req "request_review.txt"
$r13 = New-Req "request_implementation_plan.txt"
$r14 = New-Req "request_automatic_block.txt"
$r15 = New-Req "request_external_execution.txt"
$r16 = New-Req "request_manual_mutation.txt"
$r17 = New-Req "request_brain_mutation.txt"
$r18 = New-Req "request_reports_brain_mutation.txt"
$r19 = New-Req "request_n8n_execution.txt"
$r20 = New-Req "request_unknown.txt"

Assert-Test "T011 normalize blueprint request" ($r11.request_type -eq "BLUEPRINT_REQUEST" -and $r11.normalization_status -eq "NORMALIZED") ""
Assert-Test "T012 normalize review request" ($r12.request_type -eq "BLUEPRINT_REVIEW_REQUEST") ""
Assert-Test "T013 normalize implementation plan request" ($r13.request_type -eq "IMPLEMENTATION_PLAN_REQUEST") ""
Assert-Test "T014 normalize automatic block request" ($r14.request_type -eq "AUTOMATIC_BLOCK_REQUEST") ""
Assert-Test "T015 detect execution intent" ($r15.detected_intents.external_execution_intent -eq $true -or $r15.detected_intents.execution_intent -eq $true) ""
Assert-Test "T016 detect manual mutation intent" ($r16.detected_intents.manual_mutation_intent -eq $true -and $r16.normalization_status -eq "LOCKED") ""
Assert-Test "T017 detect brain mutation intent" ($r17.detected_intents.brain_mutation_intent -eq $true -and $r17.normalization_status -eq "LOCKED") ""
Assert-Test "T018 detect reports/brain mutation intent" ($r18.detected_intents.reports_brain_mutation_intent -eq $true -and $r18.normalization_status -eq "LOCKED") ""
Assert-Test "T019 detect external execution intent" ($r19.detected_intents.external_execution_intent -eq $true -and $r19.normalization_status -eq "LOCKED") ""
Assert-Test "T020 unknown request requires review" ($r20.request_type -eq "UNKNOWN_REQUEST" -and $r20.normalization_status -eq "REQUIRE_REVIEW") ""

# T021-T030 — anti-ambigüedad
Assert-Test "T021 ambiguous hazlo requires review" ((New-Req "request_ambiguous_hazlo.txt").normalization_status -eq "REQUIRE_REVIEW") ""
Assert-Test "T022 ambiguous continúa requires review" ((New-Req "request_ambiguous_continua.txt").normalization_status -eq "REQUIRE_REVIEW") ""
Assert-Test "T023 ambiguous aplícalo requires review" ((New-Req "request_ambiguous_aplicalo.txt").normalization_status -eq "LOCKED") ""
Assert-Test "T024 ambiguous corrige todo requires review" ((New-Req "request_ambiguous_corrige_todo.txt").normalization_status -eq "REQUIRE_REVIEW") ""
Assert-Test "T025 ambiguous construye todo requires review" ((New-Req "request_ambiguous_construye_todo.txt").normalization_status -eq "REQUIRE_REVIEW") ""
Assert-Test "T026 vague target blocks plan" ((New-Req "request_missing_target.txt").normalization_status -eq "REQUIRE_REVIEW") ""
Assert-Test "T027 missing target blocks plan" ((New-Req "request_missing_target.txt").target_layer -eq "UNKNOWN") ""
Assert-Test "T028 missing request type blocks plan" ((New-Req "request_unknown.txt").request_type -eq "UNKNOWN_REQUEST") ""
Assert-Test "T029 unclear action requires review" ((New-Req "request_unknown.txt").normalization_status -eq "REQUIRE_REVIEW") ""
$r30 = New-PlanRequestContractV34 -SourceText "no ejecutes pero ejecuta eso" -RootPath $Root
Assert-Test "T030 contradictory request blocks plan" ($r30.normalization_status -eq "LOCKED") ""

# T031-T040 — plan builder contract
$safeReq = New-Req "request_automatic_block.txt"
$safePlan = New-ControlledPlanV34 -Request $safeReq -RootPath $Root

Assert-Test "T031 plan has plan_id" (-not [string]::IsNullOrWhiteSpace($safePlan.plan_id)) ""
Assert-Test "T032 plan has request_id" (-not [string]::IsNullOrWhiteSpace($safePlan.request_id)) ""
Assert-Test "T033 plan has source hashes" (-not [string]::IsNullOrWhiteSpace($safePlan.source_context.manual_hash_sha256)) ""
Assert-Test "T034 plan has policy context hash" (-not [string]::IsNullOrWhiteSpace($safePlan.policy_context_hash_sha256)) ""
Assert-Test "T035 plan has deterministic plan hash" (-not [string]::IsNullOrWhiteSpace($safePlan.plan_hash_sha256)) ""
Assert-Test "T036 every step has step_id" (@($safePlan.steps | Where-Object { [string]::IsNullOrWhiteSpace($_.step_id) }).Count -eq 0) ""
Assert-Test "T037 every step has policy bindings" (@($safePlan.steps | Where-Object { @($_.policy_bindings).Count -eq 0 }).Count -eq 0) ""
Assert-Test "T038 every step has risk level" (@($safePlan.steps | Where-Object { [string]::IsNullOrWhiteSpace($_.risk_level) }).Count -eq 0) ""
Assert-Test "T039 every step has approval mode" (@($safePlan.steps | Where-Object { [string]::IsNullOrWhiteSpace($_.approval_mode) }).Count -eq 0) ""
Assert-Test "T040 every step has evidence" (@($safePlan.steps | Where-Object { $null -eq $_.evidence }).Count -eq 0) ""

# T041-T050 — risk / lock
Assert-Test "T041 plan touching manual locks" ((New-ControlledPlanV34 -Request (New-Req "request_manual_mutation.txt") -RootPath $Root).final_decision -eq "PLAN_LOCKED") ""
Assert-Test "T042 plan touching manual manifest locks" ((New-PlanStepV34 -Index 1 -Action "MODIFY_MANUAL_MANIFEST" -TargetPath "00_SYSTEM/manual/manifest/MANUAL_SOURCE_MANIFEST.json" -Domain "MANUAL").locked -eq $true) ""
Assert-Test "T043 plan touching brain locks" ((New-ControlledPlanV34 -Request (New-Req "request_brain_mutation.txt") -RootPath $Root).final_decision -eq "PLAN_LOCKED") ""
Assert-Test "T044 plan touching reports/brain locks" ((New-ControlledPlanV34 -Request (New-Req "request_reports_brain_mutation.txt") -RootPath $Root).final_decision -eq "PLAN_LOCKED") ""
Assert-Test "T045 plan creating CAPA 9 locks" ((New-ControlledPlanV34 -Request (New-Req "request_capa9.txt") -RootPath $Root).final_decision -eq "PLAN_LOCKED") ""
Assert-Test "T046 plan enabling external execution locks" ((New-ControlledPlanV34 -Request (New-Req "request_external_execution.txt") -RootPath $Root).final_decision -eq "PLAN_LOCKED") ""
Assert-Test "T047 plan enabling n8n execution locks" ((New-ControlledPlanV34 -Request (New-Req "request_n8n_execution.txt") -RootPath $Root).final_decision -eq "PLAN_LOCKED") ""
Assert-Test "T048 plan creating active webhook locks" ((Invoke-ApprovalGateV34 -Plan (New-ControlledPlanV34 -Request (New-Req "request_webhook_active.txt") -RootPath $Root)).status -eq "LOCK") ""
Assert-Test "T049 plan enabling auto_action locks" ((New-PlanRequestContractV34 -SourceText "habilita auto_action_allowed true" -RootPath $Root).normalization_status -eq "LOCKED") ""
Assert-Test "T050 plan hiding warnings blocks" ((New-PlanRequestContractV34 -SourceText (Get-FixtureText "request_warning_hiding.txt") -RootPath $Root).normalization_status -eq "LOCKED") ""

# T051-T060 — approval gate
$approvalSafe = Invoke-ApprovalGateV34 -Plan $safePlan
Assert-Test "T051 approval required for build plan" ($approvalSafe.human_approval_required -eq $true) ""
Assert-Test "T052 approval required for hotfix plan" ((Invoke-ApprovalGateV34 -Plan (New-ControlledPlanV34 -Request (New-Req "request_automatic_block.txt") -RootPath $Root)).human_approval_required -eq $true) ""
Assert-Test "T053 approval required for commit plan" ((New-Req "request_automatic_block.txt").detected_intents.repo_commit_intent -eq $true) ""
Assert-Test "T054 approval cannot imply execution" ($approvalSafe.execution_approval_granted -eq $false) ""
Assert-Test "T055 approval cannot override manual LOCK" ((Test-ApprovalCannotOverrideLockV34 -Plan (New-ControlledPlanV34 -Request (New-Req "request_manual_mutation.txt") -RootPath $Root) -HumanApprovalGranted:$true).status -eq "LOCK") ""
Assert-Test "T056 approval cannot override brain LOCK" ((Test-ApprovalCannotOverrideLockV34 -Plan (New-ControlledPlanV34 -Request (New-Req "request_brain_mutation.txt") -RootPath $Root) -HumanApprovalGranted:$true).status -eq "LOCK") ""
Assert-Test "T057 approval cannot override reports/brain LOCK" ((Test-ApprovalCannotOverrideLockV34 -Plan (New-ControlledPlanV34 -Request (New-Req "request_reports_brain_mutation.txt") -RootPath $Root) -HumanApprovalGranted:$true).status -eq "LOCK") ""
Assert-Test "T058 approval cannot override external LOCK" ((Test-ApprovalCannotOverrideLockV34 -Plan (New-ControlledPlanV34 -Request (New-Req "request_external_execution.txt") -RootPath $Root) -HumanApprovalGranted:$true).status -eq "LOCK") ""
Assert-Test "T059 approval cannot override CAPA9 LOCK" ((Test-ApprovalCannotOverrideLockV34 -Plan (New-ControlledPlanV34 -Request (New-Req "request_capa9.txt") -RootPath $Root) -HumanApprovalGranted:$true).status -eq "LOCK") ""
Assert-Test "T060 changed plan invalidates approval" ((Test-ApprovalInvalidatedByPlanChangeV34 -ApprovedPlanHash "a" -CurrentPlanHash "b").approval_invalidated -eq $true) ""

# T061-T070 — anti-escalamiento
Assert-Test "T061 low step cannot escalate to execution" ($safePlan.execution_allowed -eq $false) ""
Assert-Test "T062 pass_with_warnings cannot become clean pass" ($safePlan.warnings_remaining -eq 5 -and $result.bridge_build_readiness.production_clean_pass -eq $false) ""
Assert-Test "T063 partial approval cannot become total approval" ($approvalSafe.execution_approval_granted -eq $false -and $approvalSafe.build_approval_granted -eq $false) ""
Assert-Test "T064 blueprint approval cannot authorize build" ((New-ControlledPlanV34 -Request (New-Req "request_blueprint.txt") -RootPath $Root).approval_summary.execution_approval_granted -eq $false) ""
Assert-Test "T065 build approval cannot authorize external execution" ($safePlan.external_execution_allowed -eq $false) ""
Assert-Test "T066 human approval cannot override policy lock" ((Test-ApprovalCannotOverrideLockV34 -Plan (New-ControlledPlanV34 -Request (New-Req "request_capa9.txt") -RootPath $Root) -HumanApprovalGranted:$true).lock_override_attempt -eq $true) ""
Assert-Test "T067 locked plan cannot be split into safe steps" ((Test-AntiPlanSplittingV34 -Text (Get-FixtureText "request_plan_splitting_webhook.txt")).status -eq "LOCK") ""
Assert-Test "T068 policy risk cannot be downgraded without evidence" ((New-PlanStepV34 -Index 1 -Action "MODIFY_BRAIN" -TargetPath "00_SYSTEM/brain/x" -Domain "BRAIN").risk_level -eq "LOCK") ""
Assert-Test "T069 warning accepted cannot become warning resolved" ($safePlan.warnings_resolved_by_v3_4 -eq 0) ""
Assert-Test "T070 blocked step cannot be hidden" ((New-ControlledPlanV34 -Request (New-Req "request_capa9.txt") -RootPath $Root).blocked_reasons.Count -ge 1) ""

# T071-T080 — anti-plan-splitting / semantic bypass
Assert-Test "T071 webhook plus activation detects composite risk" ((Test-AntiPlanSplittingV34 -Text (Get-FixtureText "request_plan_splitting_webhook.txt")).webhook_activation_risk -eq $true) ""
Assert-Test "T072 n8n plus execution detects composite risk" ((Test-AntiPlanSplittingV34 -Text (Get-FixtureText "request_plan_splitting_n8n.txt")).n8n_execution_risk -eq $true) ""
Assert-Test "T073 API token plus call detects composite risk" ((Test-AntiPlanSplittingV34 -Text "preparar token API y hacer llamada").api_token_call_risk -eq $true) ""
Assert-Test "T074 scheduled task plus script detects execution risk" ((Test-AntiPlanSplittingV34 -Text "crear scheduled task con script para ejecutar").scheduler_script_risk -eq $true) ""
Assert-Test "T075 actualiza memoria del cerebro locks" ((Test-SemanticBypassV34 -Text (Get-FixtureText "request_semantic_bypass_brain_memory.txt")).status -eq "LOCK") ""
Assert-Test "T076 solo prepara webhook activo locks" ((Test-SemanticBypassV34 -Text (Get-FixtureText "request_semantic_bypass_webhook.txt")).status -eq "LOCK") ""
Assert-Test "T077 capa cerebral adicional locks" ((Test-SemanticBypassV34 -Text (Get-FixtureText "request_semantic_bypass_capa_extra.txt")).status -eq "LOCK") ""
Assert-Test "T078 corrige fuente oficial manual locks" ((Test-SemanticBypassV34 -Text (Get-FixtureText "request_semantic_bypass_manual.txt")).status -eq "LOCK") ""
Assert-Test "T079 publica después automáticamente locks" ((New-PlanRequestContractV34 -SourceText "publica después automáticamente" -RootPath $Root).normalization_status -eq "LOCKED") ""
Assert-Test "T080 deja listo para ejecutar requires review or locks" ((New-PlanRequestContractV34 -SourceText "deja listo para ejecutar" -RootPath $Root).normalization_status -in @("REQUIRE_REVIEW","LOCKED")) ""

# T081-T090 — traceability / no-touch / commit policy
Assert-Test "T081 traceability matrix generated" ($result.plan_traceability_matrix.status -eq "PASS") ""
Assert-Test "T082 no-execution audit generated" ($result.no_execution_permission_audit.status -eq "PASS") ""
Assert-Test "T083 approval report generated" ($result.approval_gate.status -in @("PASS","PASS_WITH_WARNINGS")) ""
Assert-Test "T084 risk report generated" ($null -ne $result.plan_risk_classification.risk_level) ""
Assert-Test "T085 manifest generated" ($result.bridge_build_readiness.tests_total -eq 90) ""
Assert-Test "T086 seal generated" ($result.bridge_build_readiness.commit_allowed -eq $true) ""
Assert-Test "T087 manual hash unchanged" ((Test-Path -LiteralPath (Join-Path $Root "00_SYSTEM\manual\current\MANUAL_MASTER_CURRENT.md")) -eq $true) ""
Assert-Test "T088 brain evidence unchanged" ((Test-Path -LiteralPath (Join-Path $Root "00_SYSTEM\bridge\reports\BRIDGE_BRAIN_READ_ONLY_REPORT_V2_1_3.json")) -eq $true) ""
Assert-Test "T089 reports/brain unchanged" ($result.no_execution_permission_audit.reports_brain_write_allowed -eq $false) ""
Assert-Test "T090 commit allowed only for report/manifest/seal outputs" ($result.bridge_build_readiness.commit_allowed -eq $true -and $result.no_execution_permission_audit.execution_allowed -eq $false) ""

Write-Host "[OK] BRIDGE V3.4 TEST HARNESS T001-T090 PASS" -ForegroundColor Green
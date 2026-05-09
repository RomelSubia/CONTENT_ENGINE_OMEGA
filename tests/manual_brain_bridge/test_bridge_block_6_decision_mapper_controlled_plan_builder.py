
from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = ROOT / "04_SCRIPTS" / "python" / "manual_brain_bridge"
sys.path.insert(0, str(MODULE_DIR))

import bridge_block_6_decision_mapper_controlled_plan_builder as b6


GOOD_HASH = "a" * 64
OTHER_HASH = "b" * 64


def safe_step(step_id="s1", order=1):
    return b6.PlanStepContract(
        step_id=step_id,
        step_order=order,
        step_type="MAP_DECISION",
        description="Map decision requirement for the future gate",
        evidence_required=["e1"],
        risk_level="LOW",
        rollback_required=True,
    )


def safe_evidence(tmp_path):
    artifact = tmp_path / "artifact.json"
    artifact.write_text('{"status":"CLOSED_VALIDATED"}\n', encoding="utf-8")
    return b6.EvidenceDependency(
        evidence_id="e1",
        artifact_path=artifact.relative_to(Path.cwd()).as_posix() if artifact.is_relative_to(Path.cwd()) else artifact.as_posix(),
        sha256=b6.sha256_bytes(artifact.read_bytes()),
        source_block="BLOQUE_5",
        source_status="CLOSED_VALIDATED",
        source_authority="SEALED",
    )


def safe_auth():
    return b6.AuthorizationRequirement(
        authorization_required=True,
        authorization_type="HUMAN_APPROVAL",
    )


def safe_rollback():
    return b6.RollbackRequirement(rollback_required=True)


def safe_plan(tmp_path):
    return b6.build_controlled_plan(
        plan_type="BUILD_PLAN",
        steps=[safe_step()],
        required_evidence=[safe_evidence(tmp_path)],
        required_authorizations=[safe_auth()],
        rollback_requirements=[safe_rollback()],
        risk_classification="LOW",
    )


def safe_decision():
    return b6.map_decision(
        source_inputs=["BLOQUE_5"],
        evidence_refs=["evidence://block5/gate_closure"],
        hash_refs=[GOOD_HASH],
        decision_candidates=[b6.PASS],
        source_authorities=["SEALED"],
        reason="All preconditions satisfied",
        allowed_next_step="BLOQUE_6_POST_BUILD_AUDIT",
    )


@pytest.mark.parametrize(
    "decisions,expected",
    [
        ([b6.PASS, b6.BLOCK], b6.BLOCK),
        ([b6.PASS, b6.LOCK], b6.LOCK),
        ([b6.REQUIRE_REVIEW, b6.PASS_WITH_WARNINGS], b6.REQUIRE_REVIEW),
        (["BAD"], b6.LOCK),
        ([], b6.LOCK),
    ],
)
def test_choose_worst_decision(decisions, expected):
    assert b6.choose_worst_decision(decisions) == expected


@pytest.mark.parametrize(
    "text",
    [
        "run powershell",
        "use pwsh",
        "open cmd",
        "bash script",
        "python build.py",
        "pytest tests",
        "git commit -m x",
        "git push",
        "git reset --hard",
        "git clean -fd",
        "subprocess call",
        "Start-Process app",
        "Invoke-WebRequest url",
        "curl url",
        "wget url",
        "n8n run workflow",
        "call webhook",
        "publish content",
        "write file",
        "delete file",
        "move file",
        "copy file",
        "open('x', 'w')",
        "Path.write_text",
        "Path.write_bytes",
    ],
)
def test_executable_plan_content_scanner_locks(text):
    assert b6.validate_executable_content(text)["status"] == b6.LOCK


@pytest.mark.parametrize(
    "text",
    [
        "describe future gate",
        "map evidence requirement",
        "propose review",
        "summarize risk",
        "declare future authorization requirement",
    ],
)
def test_executable_plan_content_scanner_allows_safe_text(text):
    assert b6.validate_executable_content(text)["status"] == b6.PASS


@pytest.mark.parametrize(
    "step_type",
    [
        "VALIDATE_NOW",
        "GENERATE_REPORT_NOW",
        "RUN_TESTS_NOW",
        "WRITE_REPORT_NOW",
        "EXECUTE",
        "WRITE_MANUAL",
        "WRITE_BRAIN",
        "WRITE_REPORTS_BRAIN",
        "PUBLISH",
        "WEBHOOK",
        "N8N_RUN",
        "CAPA9_RUN",
    ],
)
def test_forbidden_step_types_lock(step_type):
    assert b6.validate_step_type(step_type)["status"] == b6.LOCK


@pytest.mark.parametrize(
    "step_type",
    [
        "DESCRIBE_VALIDATION",
        "DESCRIBE_REPORT",
        "PROPOSE_REVIEW",
        "MAP_DECISION",
        "MAP_EVIDENCE",
        "MAP_RISK",
        "MAP_AUTHORIZATION_REQUIREMENT",
        "MAP_ROLLBACK_REQUIREMENT",
        "MAP_NEXT_GATE",
    ],
)
def test_allowed_step_types_pass(step_type):
    assert b6.validate_step_type(step_type)["status"] == b6.PASS


@pytest.mark.parametrize(
    "field",
    [
        "authorization_input_present",
        "authorization_validated",
        "authorization_granted",
        "authorization_consumed",
        "execution_permission_granted",
    ],
)
def test_authorization_non_consumption_guard_locks_forbidden_true(field):
    payload = {
        "authorization_required": True,
        "authorization_type": "HUMAN_APPROVAL",
        "authorization_status": "NOT_REQUESTED",
        "authorization_input_present": False,
        "authorization_validated": False,
        "authorization_granted": False,
        "authorization_consumed": False,
        "execution_permission_granted": False,
    }
    payload[field] = True
    assert b6.validate_authorization_requirement(payload)["status"] == b6.LOCK


def test_authorization_non_consumption_guard_passes_safe_auth():
    assert b6.validate_authorization_requirement(safe_auth())["status"] == b6.PASS


@pytest.mark.parametrize(
    "field,value,expected",
    [
        ("evidence_id", "", b6.BLOCK),
        ("artifact_path", "", b6.BLOCK),
        ("sha256", "", b6.BLOCK),
        ("sha256", "bad", b6.BLOCK),
        ("source_status", "BAD", b6.LOCK),
        ("source_authority", "UNKNOWN", b6.LOCK),
    ],
)
def test_evidence_dependency_policy_fail_closed(tmp_path, field, value, expected):
    artifact = tmp_path / "artifact.json"
    artifact.write_text("{}", encoding="utf-8")
    dep = {
        "evidence_id": "e1",
        "artifact_path": artifact.as_posix(),
        "sha256": b6.sha256_bytes(artifact.read_bytes()),
        "source_block": "BLOQUE_5",
        "source_status": "CLOSED_VALIDATED",
        "source_authority": "SEALED",
        "required": True,
    }
    dep[field] = value
    assert b6.verify_evidence_dependency(dep, root=Path("/"))["status"] == expected


def test_evidence_dependency_policy_detects_hash_mismatch(tmp_path):
    artifact = tmp_path / "artifact.json"
    artifact.write_text("{}", encoding="utf-8")
    dep = {
        "evidence_id": "e1",
        "artifact_path": artifact.as_posix(),
        "sha256": OTHER_HASH,
        "source_block": "BLOQUE_5",
        "source_status": "CLOSED_VALIDATED",
        "source_authority": "SEALED",
        "required": True,
    }
    assert b6.verify_evidence_dependency(dep, root=Path("/"))["status"] == b6.LOCK


def test_evidence_dependency_policy_passes_valid_dependency(tmp_path):
    artifact = tmp_path / "artifact.json"
    artifact.write_text("{}", encoding="utf-8")
    dep = {
        "evidence_id": "e1",
        "artifact_path": artifact.as_posix(),
        "sha256": b6.sha256_bytes(artifact.read_bytes()),
        "source_block": "BLOQUE_5",
        "source_status": "CLOSED_VALIDATED",
        "source_authority": "SEALED",
        "required": True,
    }
    assert b6.verify_evidence_dependency(dep, root=Path("/"))["status"] == b6.PASS


@pytest.mark.parametrize(
    "text",
    [
        "git commit the result",
        "run pytest now",
        "write file to disk",
        "publish the content",
        "call webhook",
        "Path.write_text",
    ],
)
def test_non_actionable_output_guard_locks_actionable_text(text):
    assert b6.validate_non_actionable_output(text)["status"] == b6.LOCK


def test_non_actionable_output_guard_passes_future_gate_description():
    assert b6.validate_non_actionable_output("Describe future gate requirements only")["status"] == b6.PASS


@pytest.mark.parametrize(
    "field",
    [
        "rollback_executor_created",
        "rollback_executed",
        "recovery_writer_created",
        "quarantine_writer_created",
    ],
)
def test_rollback_declaration_only_guard_locks_executors(field):
    payload = {
        "rollback_required": True,
        "rollback_type": "DECLARED_REQUIREMENT_ONLY",
        "rollback_strategy_described": True,
        "rollback_executor_created": False,
        "rollback_executed": False,
        "recovery_writer_created": False,
        "quarantine_writer_created": False,
    }
    payload[field] = True
    assert b6.validate_rollback_requirement(payload)["status"] == b6.LOCK


def test_rollback_declaration_only_guard_blocks_missing_rollback():
    assert b6.validate_rollback_requirement({"rollback_required": False})["status"] == b6.BLOCK


def test_rollback_declaration_only_guard_passes_safe_declaration():
    assert b6.validate_rollback_requirement(safe_rollback())["status"] == b6.PASS


@pytest.mark.parametrize(
    "token",
    [
        "global traceability engine",
        "full reporting layer",
        "cross-block report consolidator",
        "historical report reconciler",
        "manifest registry engine",
        "global evidence dashboard",
        "bridge-wide reporting orchestrator",
        "GlobalTraceabilityEngine",
        "ReportConsolidator",
        "ManifestRegistryEngine",
    ],
)
def test_block7_boundary_denylist_locks(token):
    assert b6.validate_block7_boundary({"component": token})["status"] == b6.LOCK


def test_block7_boundary_allows_minimal_traceability():
    assert b6.validate_block7_boundary({"component": "minimal traceability"})["status"] == b6.PASS


@pytest.mark.parametrize(
    "token",
    [
        "AtomicWriter",
        "LockManager",
        "QuarantineWriter",
        "RecoveryExecutor",
        "RollbackExecutor",
        "WriteTransaction",
        "PendingWriteSet",
        "MutationQueue",
        "FilesystemMutationPlan",
        "AtomicCommitPlan",
        "PatchApplier",
        "ManualWriter",
        "BrainWriter",
        "ReportsBrainWriter",
    ],
)
def test_block8_writer_boundary_denylist_locks(token):
    assert b6.validate_block8_boundary({"component": token})["status"] == b6.LOCK


def test_block8_boundary_allows_rollback_requirement_only():
    assert b6.validate_block8_boundary({"rollback_type": "DECLARED_REQUIREMENT_ONLY"})["status"] == b6.PASS


@pytest.mark.parametrize(
    "field,value,expected",
    [
        ("plan_status", "APPROVED", b6.LOCK),
        ("approval_status", "APPROVED", b6.LOCK),
        ("execution_status", "EXECUTED", b6.LOCK),
        ("next_gate_required", False, b6.BLOCK),
        ("approval_gate_required", False, b6.BLOCK),
        ("build_gate_required", False, b6.BLOCK),
    ],
)
def test_approval_by_plan_guard_fail_closed(tmp_path, field, value, expected):
    plan = b6.asdict(safe_plan(tmp_path)) if hasattr(b6, "asdict") else safe_plan(tmp_path).__dict__
    plan[field] = value
    assert b6.validate_approval_by_plan(plan)["status"] == expected


def test_approval_by_plan_guard_passes_safe_plan(tmp_path):
    assert b6.validate_approval_by_plan(safe_plan(tmp_path))["status"] == b6.PASS


@pytest.mark.parametrize(
    "mutator,expected",
    [
        (lambda p: {**p, "steps": [{"description": "x", "step_type": "MAP_DECISION"}] * 26}, b6.BLOCK),
        (lambda p: {**p, "required_evidence": [{}] * 51}, b6.BLOCK),
        (lambda p: {**p, "required_authorizations": [{}] * 11}, b6.BLOCK),
        (lambda p: {**p, "steps": [{"description": "x" * 501, "step_type": "MAP_DECISION"}]}, b6.BLOCK),
        (lambda p: {**p, "extra": {"a": {"b": {"c": {"d": {"e": "too deep"}}}}}}, b6.BLOCK),
    ],
)
def test_plan_size_complexity_bounds_fail_closed(tmp_path, mutator, expected):
    plan = safe_plan(tmp_path).__dict__
    assert b6.validate_plan_bounds(mutator(plan))["status"] == expected


def test_plan_size_complexity_bounds_pass_safe_plan(tmp_path):
    assert b6.validate_plan_bounds(safe_plan(tmp_path))["status"] == b6.PASS


def test_sort_decisions_prioritizes_highest_rank():
    d1 = {"decision_id": "b", "decision_type": b6.PASS, "decision_precedence_rank": 1, "source_authority_rank": 1}
    d2 = {"decision_id": "a", "decision_type": b6.LOCK, "decision_precedence_rank": 5, "source_authority_rank": 5}
    assert b6.sort_decisions([d1, d2])[0]["decision_type"] == b6.LOCK


def test_hash_stability_passes_for_same_plan(tmp_path):
    plan = safe_plan(tmp_path).__dict__
    assert b6.validate_hash_stability(plan)["status"] == b6.PASS


@pytest.mark.parametrize("field", ["timestamp", "created_at", "updated_at", "random_id", "uuid"])
def test_hash_stability_locks_volatile_fields(tmp_path, field):
    plan = safe_plan(tmp_path).__dict__
    plan[field] = "volatile"
    assert b6.validate_hash_stability(plan)["status"] == b6.LOCK


@pytest.mark.parametrize(
    "payload,expected",
    [
        ({}, b6.BLOCK),
        ({"decision_reason": "x", "evidence_refs": [], "hash_refs": ["a" * 64]}, b6.BLOCK),
        ({"decision_reason": "x", "evidence_refs": ["e"], "hash_refs": []}, b6.BLOCK),
        ({"decision_reason": "x", "evidence_refs": ["e"], "hash_refs": ["a" * 64], "raw_source_dump_allowed": True}, b6.LOCK),
        ({"decision_reason": "x", "evidence_refs": ["e"], "hash_refs": ["a" * 64], "full_artifact_dump_allowed": True}, b6.LOCK),
        ({"decision_reason": "x", "evidence_refs": ["e"], "hash_refs": ["a" * 64]}, b6.PASS),
    ],
)
def test_explainability_without_leakage_policy(payload, expected):
    assert b6.validate_explainability(payload)["status"] == expected


@pytest.mark.parametrize(
    "payload,expected",
    [
        ({"recursive_plan_generation_allowed": True}, b6.LOCK),
        ({"self_referential_plan_allowed": True}, b6.BLOCK),
        ({"plan_generates_plan_allowed": True}, b6.LOCK),
        ({"decision_plan_cycles": 2}, b6.LOCK),
        ({"decision_plan_cycles": 1}, b6.PASS),
    ],
)
def test_anti_loop_guard(payload, expected):
    assert b6.validate_anti_loop(payload)["status"] == expected


@pytest.mark.parametrize(
    "payload",
    [
        {"intent": "manual_write"},
        {"intent": "brain_write"},
        {"intent": "reports_brain_write"},
        {"path": "00_SYSTEM/brain/file.json"},
        {"path": "00_SYSTEM/reports/brain/file.json"},
        {"path": "manual/current/file.md"},
    ],
)
def test_protected_write_intent_locks(payload):
    assert b6.validate_protected_write_intent(payload)["status"] == b6.LOCK


def test_protected_write_intent_passes_safe_payload():
    assert b6.validate_protected_write_intent({"intent": "describe future gate"})["status"] == b6.PASS


def test_decision_mapper_creates_safe_decision():
    decision = safe_decision()
    assert decision.decision_type == b6.PASS
    assert decision.execution_allowed is False
    assert decision.manual_write_allowed is False
    assert b6.validate_decision_envelope(decision)["status"] == b6.PASS


@pytest.mark.parametrize(
    "field,value,expected",
    [
        ("decision_reason", "", b6.BLOCK),
        ("evidence_refs", [], b6.BLOCK),
        ("hash_refs", [], b6.BLOCK),
        ("authorization_consumed", True, b6.LOCK),
        ("execution_permission_granted", True, b6.LOCK),
        ("manual_write_allowed", True, b6.LOCK),
        ("brain_write_allowed", True, b6.LOCK),
        ("reports_brain_write_allowed", True, b6.LOCK),
    ],
)
def test_decision_envelope_fail_closed(field, value, expected):
    payload = safe_decision().__dict__
    payload[field] = value
    assert b6.validate_decision_envelope(payload)["status"] == expected


def test_controlled_plan_builder_creates_safe_plan(tmp_path):
    plan = safe_plan(tmp_path)
    assert plan.plan_status == "PROPOSED_ONLY"
    assert plan.approval_status == "NOT_APPROVED"
    assert plan.execution_status == "NOT_EXECUTED"
    assert b6.validate_controlled_plan(plan)["status"] == b6.PASS


@pytest.mark.parametrize(
    "field,value,expected",
    [
        ("plan_status", "APPROVED", b6.LOCK),
        ("approval_status", "APPROVED", b6.LOCK),
        ("execution_status", "EXECUTED", b6.LOCK),
        ("next_gate_required", False, b6.BLOCK),
        ("execution_allowed", True, b6.LOCK),
        ("manual_write_allowed", True, b6.LOCK),
        ("brain_write_allowed", True, b6.LOCK),
        ("reports_brain_write_allowed", True, b6.LOCK),
        ("external_io_allowed", True, b6.LOCK),
    ],
)
def test_controlled_plan_envelope_fail_closed(tmp_path, field, value, expected):
    payload = safe_plan(tmp_path).__dict__
    payload[field] = value
    assert b6.validate_controlled_plan(payload)["status"] == expected


def test_controlled_plan_locks_step_execution_true(tmp_path):
    payload = safe_plan(tmp_path).__dict__
    payload["steps"] = [{"step_id": "s", "step_order": 1, "step_type": "MAP_DECISION", "description": "safe", "execution_allowed": True}]
    assert b6.validate_controlled_plan(payload)["status"] == b6.LOCK


def test_controlled_plan_blocks_ambiguous_step_type(tmp_path):
    payload = safe_plan(tmp_path).__dict__
    payload["steps"] = [{"step_id": "s", "step_order": 1, "step_type": "VALIDATE", "description": "safe"}]
    assert b6.validate_controlled_plan(payload)["status"] == b6.BLOCK


def test_controlled_plan_locks_executable_text(tmp_path):
    payload = safe_plan(tmp_path).__dict__
    payload["steps"] = [{"step_id": "s", "step_order": 1, "step_type": "MAP_DECISION", "description": "git commit now"}]
    assert b6.validate_controlled_plan(payload)["status"] == b6.LOCK


def test_controlled_plan_locks_block7_boundary(tmp_path):
    payload = safe_plan(tmp_path).__dict__
    payload["component"] = "GlobalTraceabilityEngine"
    assert b6.validate_controlled_plan(payload)["status"] == b6.LOCK


def test_controlled_plan_locks_block8_boundary(tmp_path):
    payload = safe_plan(tmp_path).__dict__
    payload["component"] = "AtomicWriter"
    assert b6.validate_controlled_plan(payload)["status"] == b6.LOCK


def test_report_payloads_are_built_pending_post_audit():
    reports = b6.build_block6_report_payloads()
    assert len(reports) == 6
    for payload in reports.values():
        assert payload["status"] == "BUILT_PENDING_POST_AUDIT"


def test_report_payloads_block_runtime_permissions():
    reports = b6.build_block6_report_payloads()
    readiness = reports["BRIDGE_BLOCK_6_NEXT_LAYER_READINESS_MAP.json"]
    assert readiness["post_build_audit_allowed_next"] is True
    assert readiness["bloque_7_blueprint_allowed_now"] is False
    permissions = readiness["permissions"]
    assert permissions["execution_allowed_now"] is False
    assert permissions["manual_write_allowed_now"] is False
    assert permissions["brain_write_allowed_now"] is False
    assert permissions["reports_brain_write_allowed_now"] is False
    assert permissions["n8n_allowed_now"] is False
    assert permissions["webhook_allowed_now"] is False
    assert permissions["publishing_allowed_now"] is False
    assert permissions["capa9_allowed_now"] is False

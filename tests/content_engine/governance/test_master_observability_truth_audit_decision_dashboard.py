from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "04_SCRIPTS" / "python"
sys.path.insert(0, str(SRC))


from content_engine.governance.master_observability_truth_audit_decision_dashboard import (
    build_operational_truth_record,
    classify_phase_action,
    closed_component_truth,
    phase_permission_matrix,
    sync_lock_state,
)


def test_closed_component_requires_seal_manifest_report():
    record = closed_component_truth(
        "SAMPLE_COMPONENT",
        {"seal": True, "manifest": True, "report": True, "repo_stable": True, "conflict": False},
    )

    assert record["truth_state"] == "VALIDATED_TRUE"
    assert record["confidence_status"] == "VALIDATED_TRUE"
    assert record["confidence_score"] >= 90
    assert record["validated_closed"] is True
    assert record["missing_required_evidence"] == []


def test_partial_evidence_does_not_become_complete_truth():
    record = closed_component_truth(
        "PARTIAL_COMPONENT",
        {"seal": True, "manifest": False, "report": False, "repo_stable": True, "conflict": False},
    )

    assert record["truth_state"] != "VALIDATED_TRUE"
    assert record["validated_closed"] is False
    assert "manifest" in record["missing_required_evidence"]
    assert "report" in record["missing_required_evidence"]


def test_automatic_block_build_allows_allowlisted_source_and_test_writes():
    decision = classify_phase_action(
        "AUTOMATIC_BLOCK_BUILD",
        source_files_written=True,
        test_files_written=True,
        allowlisted_scope=True,
    )

    assert decision["allowed"] is True
    assert decision["classification"] == "EXPECTED_WITH_CONDITIONS"
    assert decision["violations"] == []


def test_post_build_audit_blocks_source_and_test_writes():
    decision = classify_phase_action(
        "POST_BUILD_AUDIT",
        source_files_written=True,
        test_files_written=True,
        allowlisted_scope=True,
    )

    assert decision["allowed"] is False
    assert decision["classification"] == "POLICY_VIOLATION"
    assert "source_write" in decision["violations"]
    assert "test_write" in decision["violations"]


def test_sync_lock_blocks_dirty_worktree():
    state = sync_lock_state(head="abc", upstream="abc", dirty_paths=["04_SCRIPTS/python/example.py"])

    assert state["sync_status"] == "BLOCKED_SYNC"
    assert state["dirty_count"] == 1


def test_sync_lock_validated_when_clean_and_synced():
    state = sync_lock_state(head="abc", upstream="abc", dirty_paths=[])

    assert state["sync_status"] == "VALIDATED_SYNC"
    assert state["dirty_count"] == 0


def test_decision_advisor_allows_only_validated_truth_and_validated_sync():
    record = build_operational_truth_record(
        component="SAMPLE_COMPONENT",
        evidence={"seal": True, "manifest": True, "report": True, "repo_stable": True, "conflict": False},
        head="abc",
        upstream="abc",
        dirty_paths=[],
    )

    assert record["confidence_status"] == "VALIDATED_TRUE"
    assert record["sync_status"] == "VALIDATED_SYNC"
    assert record["decision_advisor"]["decision"] == "ALLOW_NEXT_GOVERNED_STEP"


def test_phase_permission_matrix_exposes_required_phases():
    matrix = phase_permission_matrix()

    assert matrix["AUTOMATIC_BLOCK_BUILD"]["source_write"] is True
    assert matrix["POST_BUILD_AUDIT"]["source_write"] is False
    assert matrix["GATE_CLOSE_VALIDATION"]["test_write"] is False

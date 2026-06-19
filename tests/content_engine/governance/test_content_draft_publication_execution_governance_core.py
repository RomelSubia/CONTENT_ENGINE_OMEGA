from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = ROOT / "04_SCRIPTS" / "python"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from content_engine.governance.content_draft_publication_execution_governance_core import (
    BLOCKED_DECISION,
    PLAN_ONLY_DECISION,
    ContentDraftPublicationExecutionGovernanceCore,
    PublicationExecutionGovernanceInput,
    evaluate_publication_execution_governance,
)


PRODUCTIVE_PERMISSION_FLAGS = (
    "publication_execution_allowed_now",
    "publishing_allowed_now",
    "posting_allowed_now",
    "publication_scheduling_allowed_now",
    "publication_channel_mutation_allowed_now",
    "runtime_execution_allowed_now",
    "queue_write_allowed_now",
    "queue_item_creation_allowed_now",
    "queue_item_update_allowed_now",
    "automation_allowed_now",
    "n8n_allowed_now",
    "webhook_allowed_now",
    "capa9_allowed_now",
)

PRODUCTIVE_ACTION_FLAGS = (
    "source_files_written",
    "test_files_written",
    "publication_execution_started",
    "publishing_started",
    "posting_started",
    "publication_scheduling_started",
    "publication_channel_mutation_started",
    "automation_started",
    "queue_write_performed",
    "queue_item_created",
    "queue_item_updated",
)


def assert_all_productive_flags_false(result):
    payload = result.to_dict()
    for key in PRODUCTIVE_PERMISSION_FLAGS + PRODUCTIVE_ACTION_FLAGS:
        assert payload[key] is False, key


def test_default_result_is_fail_closed():
    result = ContentDraftPublicationExecutionGovernanceCore().evaluate(None)

    assert result.status == "BLOCKED_FAIL_CLOSED"
    assert result.decision == BLOCKED_DECISION
    assert_all_productive_flags_false(result)
    assert any("missing_required_evidence" in reason for reason in result.reasons)


def test_complete_evidence_is_plan_only_and_still_blocks_execution():
    request = PublicationExecutionGovernanceInput(
        request_id="REQ-001",
        draft_id="DRAFT-001",
        queue_item_id="QUEUE-001",
        publication_governance_seal={"sealed_status": "CONTENT_DRAFT_PUBLICATION_GOVERNANCE_CORE_GATE_CLOSED_VALIDATED"},
        operator_authorization_status="approved_for_plan_only",
        channel_policy_status="validated_for_plan_only",
        dry_run_required=True,
        channel_candidate="dry-run-channel",
    )

    result = evaluate_publication_execution_governance(request)

    assert result.status == "VALIDATED_PLAN_ONLY_EXECUTION_BLOCKED"
    assert result.decision == PLAN_ONLY_DECISION
    assert_all_productive_flags_false(result)
    assert "productive_execution_requires_future_gate" in result.reasons


def test_mapping_input_is_supported_and_json_serializable():
    result = evaluate_publication_execution_governance(
        {
            "request_id": "REQ-002",
            "draft_id": "DRAFT-002",
            "queue_item_id": "QUEUE-002",
            "publication_governance_seal": {"sealed_status": "OK"},
            "operator_authorization_status": "approved_for_plan_only",
            "channel_policy_status": "validated_for_plan_only",
            "dry_run_required": True,
        }
    )

    payload = result.to_dict()

    assert payload["component"] == "CONTENT_DRAFT_PUBLICATION_EXECUTION_GOVERNANCE_CORE"
    assert payload["publishing_allowed_now"] is False
    assert payload["automation_allowed_now"] is False
    json.dumps(payload, sort_keys=True)


def test_dry_run_false_blocks_fail_closed():
    result = evaluate_publication_execution_governance(
        {
            "request_id": "REQ-003",
            "draft_id": "DRAFT-003",
            "queue_item_id": "QUEUE-003",
            "publication_governance_seal": {"sealed_status": "OK"},
            "operator_authorization_status": "approved_for_plan_only",
            "channel_policy_status": "validated_for_plan_only",
            "dry_run_required": False,
        }
    )

    assert result.status == "BLOCKED_FAIL_CLOSED"
    assert result.decision == BLOCKED_DECISION
    assert_all_productive_flags_false(result)
    assert "dry_run_required_must_remain_true" in result.reasons


def test_unapproved_operator_or_channel_blocks_fail_closed():
    result = evaluate_publication_execution_governance(
        {
            "request_id": "REQ-004",
            "draft_id": "DRAFT-004",
            "queue_item_id": "QUEUE-004",
            "publication_governance_seal": {"sealed_status": "OK"},
            "operator_authorization_status": "approved_for_execution",
            "channel_policy_status": "validated_for_execution",
            "dry_run_required": True,
        }
    )

    assert result.status == "BLOCKED_FAIL_CLOSED"
    assert_all_productive_flags_false(result)
    assert "operator_authorization_not_approved_for_plan_only" in result.reasons
    assert "channel_policy_not_validated_for_plan_only" in result.reasons

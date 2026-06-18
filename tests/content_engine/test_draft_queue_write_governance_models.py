from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.content_draft_queue_write_governance.models import (
    REQUIRED_UPSTREAM_STATUS,
    QueueWriteGovernanceEvidence,
    QueueWriteGovernanceRequest,
)


VALID_HASH = "a" * 64


def valid_evidence() -> QueueWriteGovernanceEvidence:
    return QueueWriteGovernanceEvidence(
        queue_governance_reference="reports/queue-governance.json",
        queue_governance_sha256=VALID_HASH,
        queue_governance_status=REQUIRED_UPSTREAM_STATUS,
        queue_governance_manifest_reference="manifests/queue-governance.json",
        source_draft_reference="drafts/source.json",
        source_draft_sha256=VALID_HASH,
        finalization_reference="finalization/final.json",
        finalization_sha256=VALID_HASH,
    )


def valid_request(**overrides) -> QueueWriteGovernanceRequest:
    data = {
        "request_id": "REQ-001",
        "operator_identity": "test-operator",
        "policy_version": "v1",
        "timestamp": "2026-06-18T00:00:00Z",
        "target_queue": "draft_queue",
        "write_intent": "prepare_plan_only_queue_write",
        "idempotency_key": "idem-001",
        "decision": "AUTHORIZE_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY",
        "evidence": valid_evidence(),
    }
    data.update(overrides)
    return QueueWriteGovernanceRequest(**data)

from dataclasses import FrozenInstanceError

from content_engine.content_draft_queue_write_governance.models import (
    FORBIDDEN_DECISIONS,
    QueueWriteIntent,
    is_valid_sha256,
)


def test_sha256_validation():
    assert is_valid_sha256("a" * 64)
    assert not is_valid_sha256("z" * 64)
    assert not is_valid_sha256("short")


def test_intent_is_plan_only_and_no_side_effects():
    intent = QueueWriteIntent(
        target_queue="draft_queue",
        write_intent="prepare",
        idempotency_key="idem",
    )
    assert intent.result_is_plan_only is True
    assert intent.queue_write_performed is False
    assert intent.queue_item_created is False
    assert intent.queue_item_updated is False
    assert intent.target_queue_mutated is False


def test_dataclass_is_immutable():
    evidence = valid_evidence()
    try:
        evidence.queue_governance_reference = "mutated"
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("evidence must be immutable")


def test_forbidden_decisions_include_queue_mutations():
    assert "WRITE_QUEUE_NOW" in FORBIDDEN_DECISIONS
    assert "CREATE_QUEUE_ITEM_NOW" in FORBIDDEN_DECISIONS
    assert "UPDATE_QUEUE_ITEM_NOW" in FORBIDDEN_DECISIONS

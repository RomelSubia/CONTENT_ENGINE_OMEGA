from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd() / "04_SCRIPTS" / "python"))

from content_engine.content_draft_finalization_governance.models import (
    FinalizationDecision,
    FinalizationEvidence,
    FinalizationRequest,
)
from content_engine.content_draft_finalization_governance.finalization_record import build_finalization_record

VALID_HASH = "a" * 64

def valid_evidence():
    return FinalizationEvidence(
        human_review_reference="human-review://ok",
        human_review_sha256=VALID_HASH,
        human_review_manifest_reference="manifest://human-review",
        safe_preview_reference="safe-preview://ok",
        safe_preview_sha256=VALID_HASH,
        safe_preview_manifest_reference="manifest://safe-preview",
        draft_reference="draft://ok",
        draft_sha256=VALID_HASH,
        draft_manifest_reference="manifest://draft",
    )

def valid_request(decision=FinalizationDecision.FINALIZE_FOR_QUEUE_GOVERNANCE_PLAN_ONLY):
    return FinalizationRequest(
        request_id="fin-001",
        operator_identity="tester",
        policy_version="v1",
        timestamp="2026-06-17T00:00:00",
        intent="plan-only finalization governance",
        decision=decision,
        evidence=valid_evidence(),
    )

import pytest

from content_engine.content_draft_finalization_governance.models import FinalizationEvidence, FinalizationRequest

def test_missing_human_review_reference_fails_closed():
    evidence = FinalizationEvidence(
        human_review_reference="",
        human_review_sha256=VALID_HASH,
        human_review_manifest_reference="manifest://human-review",
        safe_preview_reference="safe-preview://ok",
        safe_preview_sha256=VALID_HASH,
        safe_preview_manifest_reference="manifest://safe-preview",
        draft_reference="draft://ok",
        draft_sha256=VALID_HASH,
        draft_manifest_reference="manifest://draft",
    )
    request = FinalizationRequest(
        request_id="fin-001",
        operator_identity="tester",
        policy_version="v1",
        timestamp="2026-06-17T00:00:00",
        intent="plan-only",
        decision=FinalizationDecision.FINALIZE_FOR_QUEUE_GOVERNANCE_PLAN_ONLY,
        evidence=evidence,
    )
    with pytest.raises(ValueError):
        build_finalization_record(request)

def test_forbidden_queue_write_decision_fails_closed():
    request = FinalizationRequest(
        request_id="fin-001",
        operator_identity="tester",
        policy_version="v1",
        timestamp="2026-06-17T00:00:00",
        intent="plan-only",
        decision="QUEUE_WRITE_NOW",
        evidence=valid_evidence(),
    )
    with pytest.raises(ValueError):
        build_finalization_record(request)

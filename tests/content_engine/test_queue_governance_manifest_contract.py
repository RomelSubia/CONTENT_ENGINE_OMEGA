from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine import queue_governance as qg


def safe_item():
    return {
        "schema_version": "QUEUE_ITEM_SCHEMA_V1",
        "queue_item_id": "QG-20260516-231455-A13F09BC",
        "created_at_utc": "2026-05-16T23:14:55Z",
        "source_type": "MANUAL_IDEA",
        "channel_id": "CHANNEL_D_AI_TECH_PERSONAL_BRAND",
        "content_intent": "education",
        "idea_title": "Automatización con IA para productividad",
        "idea_summary": "Idea conceptual para revisión humana sin publicación",
        "pillar_id": "PILLAR_AI_AUTOMATION",
        "audience_profile_id": "AUDIENCE_TECH_BUILDERS",
        "lifecycle_state": "DRAFT_INTAKE",
        "priority_score": 0,
        "priority_band": "LOW",
        "readiness_score": 0,
        "readiness_status": "NOT_READY",
        "risk_level": "LOW_REVIEW_BLOCK",
        "evidence_required": True,
        "evidence_status": "PARTIAL",
        "generation_allowed": False,
        "publishing_allowed": False,
        "queue_write_allowed": False,
        "blocked_reason": None,
        "traceability": {
            "construction_core_ref": "CLOSED_VALIDATED",
            "strategy_foundation_ref": "CLOSED_VALIDATED",
            "prompt_governance_ref": "CLOSED_VALIDATED",
            "queue_governance_ref": "QUEUE_GOVERNANCE_CORE",
        },
    }


def test_manifest_contract_passes():
    manifest = qg.build_queue_manifest_payload(["a"], {"a": "hash"})
    assert qg.validate_queue_manifest_payload(manifest)["status"] == "PASS"


def test_manifest_next_safe_step_required():
    manifest = qg.build_queue_manifest_payload(["a"], {"a": "hash"})
    manifest["next_safe_step"] = "BAD"
    assert qg.validate_queue_manifest_payload(manifest)["status"] == "BLOCK"


def test_seal_contract_passes():
    seal = {
        "sealed_status": "CONTENT_ENGINE_QUEUE_GOVERNANCE_CORE_BUILT_PENDING_POST_AUDIT",
        "next_safe_step": "CONTENT_ENGINE_QUEUE_GOVERNANCE_POST_BUILD_AUDIT",
        "queue_write_allowed_now": False,
    }
    assert qg.validate_queue_seal_payload(seal)["status"] == "PASS"


def test_seal_queue_write_false_required():
    seal = {
        "sealed_status": "CONTENT_ENGINE_QUEUE_GOVERNANCE_CORE_BUILT_PENDING_POST_AUDIT",
        "next_safe_step": "CONTENT_ENGINE_QUEUE_GOVERNANCE_POST_BUILD_AUDIT",
        "queue_write_allowed_now": True,
    }
    assert qg.validate_queue_seal_payload(seal)["status"] == "BLOCK"


def test_seal_status_required():
    seal = {
        "sealed_status": "BAD",
        "next_safe_step": "CONTENT_ENGINE_QUEUE_GOVERNANCE_POST_BUILD_AUDIT",
        "queue_write_allowed_now": False,
    }
    assert qg.validate_queue_seal_payload(seal)["status"] == "BLOCK"

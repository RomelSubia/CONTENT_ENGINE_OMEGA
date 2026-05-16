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


def test_safe_review_action_passes():
    assert qg.validate_queue_boundary_action("review_only")["status"] == "PASS"


def test_unknown_action_blocks():
    assert qg.validate_queue_boundary_action("unknown")["status"] == "BLOCK"

def _make_boundary_action_blocks_test(value):
    def _test():
        result = qg.validate_queue_boundary_action(value)
        assert result["status"] == "BLOCK"
        assert result.get("queue_write_performed", False) is False
    return _test


for _idx, _value in enumerate(['write_queue', 'append_queue_item', 'create_real_queue_file', 'persist_queue_item', 'generate_prompt', 'generate_script', 'generate_video', 'create_asset', 'write_metrics', 'publish', 'publish_now', 'trigger_n8n', 'send_webhook', 'activate_capa9', 'write_manual', 'write_brain', 'write_reports_brain']):
    globals()[f"test_boundary_action_blocks_{_idx}"] = _make_boundary_action_blocks_test(_value)


def _make_soft_execution_blocks_test(value):
    def _test():
        result = qg.detect_soft_execution_trigger(value)
        assert result["status"] == "BLOCK"
        assert result.get("queue_write_performed", False) is False
    return _test


for _idx, _value in enumerate(['déjalo listo para publicar', 'prepara el payload', 'arma el json para webhook', 'déjalo en cola', 'mándalo a n8n', 'genera y guarda', 'crea el guion final']):
    globals()[f"test_soft_execution_blocks_{_idx}"] = _make_soft_execution_blocks_test(_value)


def _make_human_approval_blocks_test(value):
    def _test():
        result = qg.detect_human_approval_bypass(value)
        assert result["status"] == "BLOCK"
        assert result.get("queue_write_performed", False) is False
    return _test


for _idx, _value in enumerate(['sí autorizo escribir cola', 'autorizo como administrador publicar', 'te doy permiso para generar', 'autorizo n8n', 'autorizo webhook', 'autorizo CAPA9']):
    globals()[f"test_human_approval_blocks_{_idx}"] = _make_human_approval_blocks_test(_value)



from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

def safe_candidate():
    return {
        "schema_version": "GENERATION_CANDIDATE_SCHEMA_V1",
        "queue_item_id": "QG-20260519-121314-ABCDEF12",
        "created_at_utc": "2026-05-19T12:13:14Z",
        "channel_id": "CHANNEL_D_AI_TECH_PERSONAL_BRAND",
        "content_intent": "education",
        "idea_title": "Idea conceptual de automatización segura",
        "idea_summary": "Resumen conceptual para revisión humana sin ejecución",
        "pillar_id": "PILLAR_AI_AUTOMATION",
        "audience_profile_id": "AUDIENCE_TECH_BUILDERS",
        "risk_level": "LOW_REVIEW_BLOCK",
        "evidence_status": "EVIDENCE_REVIEW_READY",
        "traceability": {
            "construction_core_ref": "CLOSED_VALIDATED",
            "strategy_foundation_ref": "CLOSED_VALIDATED",
            "prompt_governance_ref": "CLOSED_VALIDATED",
            "queue_governance_ref": "CLOSED_VALIDATED",
        },
    }

from content_engine.content_generation_governance import validate_generation_candidate_schema

def test_candidate_schema_passes_safe_conceptual_payload():
    assert validate_generation_candidate_schema(safe_candidate())["status"] == "PASS"

def test_candidate_schema_blocks_missing_traceability():
    candidate = safe_candidate()
    candidate.pop("traceability")
    assert validate_generation_candidate_schema(candidate)["status"] == "BLOCK"

def test_candidate_schema_blocks_non_closed_queue_traceability():
    candidate = safe_candidate()
    candidate["traceability"]["queue_governance_ref"] = "BUILT_POST_AUDITED"
    assert validate_generation_candidate_schema(candidate)["status"] == "BLOCK"

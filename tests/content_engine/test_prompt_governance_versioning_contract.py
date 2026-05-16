from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_prompt_version


def valid_version():
    return {
        "prompt_id": "PG-001",
        "prompt_version": "v1",
        "channel_id": "CHANNEL_A_MONEY_MINDSET_CONVERSION",
        "prompt_type": "IDEA_PROMPT_TEMPLATE_CONCEPTUAL",
        "classification": "CONCEPTUAL_ONLY",
        "status": "CONCEPTUAL_DRAFT",
        "created_by_layer": "CONTENT_ENGINE_PROMPT_GOVERNANCE_CORE",
        "previous_version": "NONE",
        "change_reason": "initial",
        "content_hash": "abc123",
        "evidence_reference": "report.json",
        "created_at_layer_step": "BUILD",
    }


def test_version_passes():
    assert validate_prompt_version(valid_version())["status"] == "PASS"


def test_missing_hash_blocks_negative():
    payload = valid_version()
    payload["content_hash"] = ""
    assert validate_prompt_version(payload)["status"] == "BLOCK"


def test_missing_evidence_blocks_negative():
    payload = valid_version()
    payload["evidence_reference"] = ""
    assert validate_prompt_version(payload)["status"] == "BLOCK"


def test_production_ready_blocks_negative():
    payload = valid_version()
    payload["status"] = "PRODUCTION_READY"
    assert validate_prompt_version(payload)["status"] == "BLOCK"


def test_ready_to_publish_blocks_negative():
    payload = valid_version()
    payload["status"] = "READY_TO_PUBLISH"
    assert validate_prompt_version(payload)["status"] == "BLOCK"

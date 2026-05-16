from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_channel_id, validate_channel_prompt_binding


VALID_PAYLOAD = {
        "prompt_id": "PG_CONCEPTUAL_001",
        "prompt_type": "IDEA_PROMPT_TEMPLATE_CONCEPTUAL",
        "channel_id": "CHANNEL_A_MONEY_MINDSET_CONVERSION",
        "prompt_intent": "DEFINE_STRUCTURE",
        "allowed_tone": ["directo"],
        "blocked_tone": ["venta_agresiva"],
        "allowed_output_shape": ["structure_schema"],
        "blocked_output_shape": ["final_script"],
        "pillar_reference": "A_MENTALIDAD_FINANCIERA",
        "audience_reference": "AUD_A_DISCIPLINA_ECONOMICA",
        "quality_rules": ["channel_alignment"],
        "safety_rules": ["no_generation_trigger"],
    }


def test_channel_binding_passes():
    assert validate_channel_prompt_binding(VALID_PAYLOAD)["status"] == "PASS"


def test_unknown_channel_blocks_negative():
    assert validate_channel_id("UNKNOWN")["status"] == "BLOCK"


def test_ambiguous_channel_alias_blocks_negative():
    assert validate_channel_id("money")["status"] == "BLOCK"


def test_prompt_without_channel_blocks_negative():
    payload = dict(VALID_PAYLOAD)
    payload["channel_id"] = ""
    assert validate_channel_prompt_binding(payload)["status"] == "BLOCK"


def test_missing_required_field_blocks_negative():
    payload = dict(VALID_PAYLOAD)
    payload["quality_rules"] = []
    assert validate_channel_prompt_binding(payload)["status"] == "BLOCK"

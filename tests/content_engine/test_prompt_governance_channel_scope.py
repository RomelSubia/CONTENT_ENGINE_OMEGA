from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_prompt_channel_scope


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


def test_channel_scope_passes():
    assert validate_prompt_channel_scope(VALID_PAYLOAD)["status"] == "PASS"


def test_universal_prompt_blocks_negative():
    payload = dict(VALID_PAYLOAD, universal_prompt=True)
    assert validate_prompt_channel_scope(payload)["status"] == "BLOCK"


def test_multi_channel_without_bridge_blocks_negative():
    payload = dict(VALID_PAYLOAD, channel_ids=["CHANNEL_A_MONEY_MINDSET_CONVERSION", "CHANNEL_B_CURIOSITIES_MASS_TRAFFIC"])
    assert validate_prompt_channel_scope(payload)["status"] == "BLOCK"


def test_multi_channel_with_bridge_passes():
    payload = dict(VALID_PAYLOAD, channel_ids=["CHANNEL_A_MONEY_MINDSET_CONVERSION", "CHANNEL_C_MOTIVATION_DISCIPLINE_RETENTION"], bridge_rule="discipline")
    assert validate_prompt_channel_scope(payload)["status"] == "PASS"


def test_cross_channel_contamination_blocks_negative():
    payload = dict(VALID_PAYLOAD, mixes_channel_tones=True)
    assert validate_prompt_channel_scope(payload)["status"] == "BLOCK"

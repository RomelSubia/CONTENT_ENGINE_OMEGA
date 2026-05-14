from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.strategy_foundation.content_lifecycle_contract import (
    build_lifecycle_contract,
    validate_lifecycle_state,
    validate_transition,
)


def test_lifecycle_contract_passes():
    assert build_lifecycle_contract()["status"] == "PASS"


def test_conceptual_state_passes():
    assert validate_lifecycle_state("IDEA")["status"] == "PASS"


def test_execution_state_blocks_negative():
    assert validate_lifecycle_state("PUBLISH_REAL")["status"] == "BLOCK"


def test_n8n_trigger_state_blocks_negative():
    assert validate_lifecycle_state("N8N_TRIGGER_REAL")["status"] == "BLOCK"


def test_unknown_lifecycle_blocks_negative():
    assert validate_lifecycle_state("RANDOM")["status"] == "BLOCK"


def test_conceptual_transition_passes():
    assert validate_transition("IDEA", "SELECTED")["status"] == "PASS"


def test_transition_to_execution_blocks_negative():
    assert validate_transition("IDEA", "QUEUE_WRITE_REAL")["status"] == "BLOCK"

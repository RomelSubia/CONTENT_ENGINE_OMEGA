from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.construction_core.project_state_reader import (
    build_project_state_read_contract,
    validate_bridge_status,
    validate_final_closure_subject,
)


def test_project_reader_is_read_only():
    contract = build_project_state_read_contract()
    assert contract["read_only"] is True
    assert contract["write_allowed"] is False


def test_final_closure_subject_passes():
    assert validate_final_closure_subject("Close MANUAL-CEREBRO bridge final closure")["status"] == "PASS"


def test_final_closure_subject_blocks_wrong_subject_negative():
    assert validate_final_closure_subject("Wrong subject")["status"] == "BLOCK"


def test_bridge_status_blocks_wrong_value_negative():
    assert validate_bridge_status("NOT_CLOSED")["status"] == "BLOCK"

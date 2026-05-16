from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_prompt_governance_idempotency


def test_none_status_passes():
    assert validate_prompt_governance_idempotency(None)["status"] == "PASS"


def test_built_pending_blocks_negative():
    assert validate_prompt_governance_idempotency("BUILT_PENDING_POST_AUDIT")["status"] == "BLOCK"


def test_built_post_audited_blocks_negative():
    assert validate_prompt_governance_idempotency("BUILT_POST_AUDITED")["status"] == "BLOCK"


def test_validated_post_audited_blocks_negative():
    assert validate_prompt_governance_idempotency("VALIDATED_POST_AUDITED")["status"] == "BLOCK"


def test_closed_validated_blocks_negative():
    assert validate_prompt_governance_idempotency("CLOSED_VALIDATED")["status"] == "BLOCK"

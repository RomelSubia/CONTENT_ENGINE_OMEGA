from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_policy_override


def test_safe_policy_reference_passes():
    assert validate_policy_override("respect_governance")["status"] == "PASS"


def test_bypass_governance_blocks_negative():
    assert validate_policy_override("bypass_governance")["status"] == "BLOCK"


def test_skip_evidence_blocks_negative():
    assert validate_policy_override("skip_evidence")["status"] == "BLOCK"


def test_force_commit_blocks_negative():
    assert validate_policy_override("force_commit")["status"] == "BLOCK"


def test_force_push_blocks_negative():
    assert validate_policy_override("force_push")["status"] == "BLOCK"

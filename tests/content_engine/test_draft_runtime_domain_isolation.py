from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY_ROOT = ROOT / "04_SCRIPTS" / "python"
if str(PY_ROOT) not in sys.path:
    sys.path.insert(0, str(PY_ROOT))


from content_engine.content_draft_runtime_governance.runtime_domain_isolation import validate_domain_isolation

def test_domain_passes():
    assert validate_domain_isolation("digital_a")["status"] == "PASS"

def test_unknown_domain_blocks():
    assert validate_domain_isolation("unknown")["status"] == "FAILED_BLOCKED"

def test_expected_mismatch_blocks():
    assert validate_domain_isolation("digital_a", "digital_b")["status"] == "FAILED_BLOCKED"

def test_expected_match_passes():
    assert validate_domain_isolation("bravi", "bravi")["status"] == "PASS"

def test_context_must_match_true():
    assert validate_domain_isolation("cacao")["domain_context_must_match"] is True

def test_cross_domain_false():
    assert validate_domain_isolation("cacao")["cross_domain_contamination_allowed"] is False

def test_brand_voice_false():
    pass

    assert validate_domain_isolation("cacao")["brand_voice_mixing_allowed"] is False

def test_campaign_context_false():
    assert validate_domain_isolation("cacao")["campaign_context_mixing_allowed"] is False

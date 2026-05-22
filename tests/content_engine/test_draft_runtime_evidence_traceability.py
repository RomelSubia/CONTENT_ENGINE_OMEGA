from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY_ROOT = ROOT / "04_SCRIPTS" / "python"
if str(PY_ROOT) not in sys.path:
    sys.path.insert(0, str(PY_ROOT))


from content_engine.content_draft_runtime_governance.runtime_evidence_contract import validate_evidence_refs
from content_engine.content_draft_runtime_governance.runtime_traceability_contract import validate_traceability_refs

def test_evidence_refs_pass():
    assert validate_evidence_refs(["ev"])["status"] == "PASS"

def test_empty_evidence_blocks():
    assert validate_evidence_refs([])["status"] == "FAILED_BLOCKED"

def test_traceability_refs_pass():
    assert validate_traceability_refs(["tr"])["status"] == "PASS"

def test_empty_traceability_blocks():
    assert validate_traceability_refs([])["status"] == "FAILED_BLOCKED"

def test_evidence_requires_canonical_json():
    assert validate_evidence_refs(["ev"])["canonical_json_required"] is True

def test_evidence_requires_manifest():
    assert validate_evidence_refs(["ev"])["manifest_required"] is True

def test_evidence_requires_seal():
    assert validate_evidence_refs(["ev"])["seal_required"] is True

def test_traceability_required_flag():
    assert validate_traceability_refs(["tr"])["traceability_required"] is True

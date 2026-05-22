from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY_ROOT = ROOT / "04_SCRIPTS" / "python"
if str(PY_ROOT) not in sys.path:
    sys.path.insert(0, str(PY_ROOT))


from content_engine.content_draft_runtime_governance.runtime_argos_boundary import argos_boundary_status

def test_argos_status_passes():
    assert argos_boundary_status()["status"] == "PASS"

def test_argos_metadata_only():
    assert argos_boundary_status()["argos_mode"] == "METADATA_ONLY"

def test_no_argos_dependency():
    assert argos_boundary_status()["argos_dependency"] is False

def test_argos_does_not_control_ce():
    assert argos_boundary_status()["argos_controls_content_engine"] is False

def test_ce_does_not_require_argos():
    assert argos_boundary_status()["content_engine_requires_argos"] is False

def test_cross_imports_false():
    assert argos_boundary_status()["cross_imports_allowed"] is False

def test_bridge_build_false():
    assert argos_boundary_status()["argos_bridge_build_allowed_now"] is False

def test_cascade_prevention_true():
    assert argos_boundary_status()["cascade_failure_prevention"] is True

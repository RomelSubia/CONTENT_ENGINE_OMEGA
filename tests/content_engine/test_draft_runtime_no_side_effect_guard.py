from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY_ROOT = ROOT / "04_SCRIPTS" / "python"
if str(PY_ROOT) not in sys.path:
    sys.path.insert(0, str(PY_ROOT))


from content_engine.content_draft_runtime_governance.runtime_no_side_effect_guard import assert_no_side_effects

def test_no_surface_passes():
    assert assert_no_side_effects()["status"] == "PASS"

def test_mutation_surface_blocks():
    assert assert_no_side_effects(["x"])["status"] == "FAILED_BLOCKED"

def test_external_calls_false():
    assert assert_no_side_effects()["external_calls_performed"] is False

def test_filesystem_writes_false():
    assert assert_no_side_effects()["filesystem_writes_performed"] is False

def test_queue_mutation_false():
    assert assert_no_side_effects()["queue_mutation_performed"] is False

def test_publication_mutation_false():
    assert assert_no_side_effects()["publication_mutation_performed"] is False

def test_asset_generation_false():
    assert assert_no_side_effects()["asset_generation_performed"] is False

def test_automation_false():
    assert assert_no_side_effects()["automation_triggered"] is False

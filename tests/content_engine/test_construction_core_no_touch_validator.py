from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.construction_core.no_touch_validator import compare_fingerprints, fingerprint_tree


def test_compare_fingerprints_passes_same():
    before = {"a": "1"}
    after = {"a": "1"}
    assert compare_fingerprints(before, after)["status"] == "PASS"


def test_compare_fingerprints_blocks_change_negative():
    before = {"a": "1"}
    after = {"a": "2"}
    assert compare_fingerprints(before, after)["status"] == "BLOCK"


def test_fingerprint_missing_path(tmp_path):
    missing = tmp_path / "missing"
    assert fingerprint_tree(missing) == "MISSING"


def test_fingerprint_empty_path(tmp_path):
    assert fingerprint_tree(tmp_path) == "EMPTY"

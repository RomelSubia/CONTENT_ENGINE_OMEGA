from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import json

from content_engine.prompt_governance import build_prompt_evidence_contract, canonical_json, sha256_text, validate_manifest_completeness


def test_evidence_contract_passes():
    assert build_prompt_evidence_contract()["status"] == "PASS"


def test_canonical_json_sorted():
    text = canonical_json({"b": 1, "a": 2})
    assert text.index('"a"') < text.index('"b"')
    assert json.loads(text)["a"] == 2


def test_sha256_len():
    assert len(sha256_text("abc")) == 64


def test_manifest_complete_passes():
    assert validate_manifest_completeness(["a"], ["a"])["status"] == "PASS"


def test_manifest_missing_blocks_negative():
    assert validate_manifest_completeness(["a"], ["a", "b"])["status"] == "BLOCK"

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.construction_core.domain_registry import DOMAINS, build_domain_registry, validate_domain_registry


def test_domain_registry_passes():
    registry = build_domain_registry()
    assert validate_domain_registry(registry)["status"] == "PASS"


def test_domain_registry_contains_required_domains():
    registry = build_domain_registry()
    ids = [item["id"] for item in registry["domains"]]
    assert "governance" in ids
    assert "publishing_preparation" in ids
    assert "monetization" in ids


def test_domain_registry_blocks_missing_domain_negative():
    registry = build_domain_registry()
    registry["domains"] = registry["domains"][:-1]
    assert validate_domain_registry(registry)["status"] == "BLOCK"


def test_domain_registry_blocks_execution_true_negative():
    registry = build_domain_registry()
    registry["domains"][0]["execution_allowed_now"] = True
    assert validate_domain_registry(registry)["status"] == "BLOCK"

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.strategy_foundation.strategy_identity_contract import REQUIRED_FIELDS, build_identity_contracts, validate_identity_contracts


def test_identity_contract_passes():
    assert validate_identity_contracts(build_identity_contracts())["status"] == "PASS"


def test_identity_contract_has_required_fields():
    contracts = build_identity_contracts()
    first = next(iter(contracts.values()))
    assert all(field in first for field in REQUIRED_FIELDS)


def test_identity_blocks_missing_field_negative():
    contracts = build_identity_contracts()
    first_key = next(iter(contracts))
    del contracts[first_key]["core_purpose"]
    assert validate_identity_contracts(contracts)["status"] == "BLOCK"


def test_identity_blocks_empty_allowed_tone_negative():
    contracts = build_identity_contracts()
    first_key = next(iter(contracts))
    contracts[first_key]["allowed_tone"] = []
    assert validate_identity_contracts(contracts)["status"] == "BLOCK"


def test_identity_monetization_is_future_only():
    assert all("futura" in payload["monetization_future"] for payload in build_identity_contracts().values())


def test_identity_has_separation_rules():
    assert all(payload["separation_rules"] for payload in build_identity_contracts().values())

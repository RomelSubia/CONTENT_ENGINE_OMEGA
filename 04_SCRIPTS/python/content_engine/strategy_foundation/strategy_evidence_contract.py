from __future__ import annotations

import hashlib
import json
from typing import Any

EXPECTED_REPORT_KINDS = [
    "core",
    "state",
    "identity",
    "channel_registry",
    "channel_separation",
    "pillar_registry",
    "audience_registry",
    "lifecycle",
    "rule_engine",
    "boundary",
    "quality",
    "learning_placeholder",
    "evidence_contract",
    "failure_policy",
    "no_touch",
    "output_scope",
    "next_layer_readiness",
]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_evidence_contract() -> dict[str, Any]:
    return {"status": "PASS", "canonical_json_required": True, "sha256_required": True, "manifest_required": True, "seal_required": True, "expected_report_kinds": list(EXPECTED_REPORT_KINDS)}


def validate_manifest_completeness(produced: list[str], expected: list[str]) -> dict[str, Any]:
    missing = sorted(set(expected) - set(produced))
    extra = sorted(set(produced) - set(expected))
    return {"status": "PASS" if not missing and not extra else "BLOCK", "missing": missing, "extra": extra}

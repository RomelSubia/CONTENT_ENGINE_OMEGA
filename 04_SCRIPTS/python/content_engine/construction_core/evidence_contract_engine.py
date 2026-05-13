from __future__ import annotations

import hashlib
import json
from typing import Any

EXPECTED_REPORTS = [
    "CONTENT_ENGINE_CONSTRUCTION_CORE_REPORT.json",
    "CONTENT_ENGINE_CONSTRUCTION_STATE_REPORT.json",
    "CONTENT_ENGINE_CONSTRUCTION_PERMISSION_MATRIX.json",
    "CONTENT_ENGINE_CONSTRUCTION_DOMAIN_REGISTRY_REPORT.json",
    "CONTENT_ENGINE_CONSTRUCTION_BOUNDARY_REPORT.json",
    "CONTENT_ENGINE_CONSTRUCTION_EVIDENCE_CONTRACT_REPORT.json",
    "CONTENT_ENGINE_CONSTRUCTION_PLAN_KERNEL_REPORT.json",
    "CONTENT_ENGINE_CONSTRUCTION_NO_TOUCH_REPORT.json",
    "CONTENT_ENGINE_CONSTRUCTION_FAILURE_POLICY_REPORT.json",
    "CONTENT_ENGINE_CONSTRUCTION_OUTPUT_SCOPE_REPORT.json",
    "CONTENT_ENGINE_CONSTRUCTION_NEXT_LAYER_READINESS_MAP.json",
]

EXPECTED_MANIFESTS = [
    "CONTENT_ENGINE_CONSTRUCTION_CORE_MANIFEST.json",
    "CONTENT_ENGINE_CONSTRUCTION_CORE_SEAL.json",
]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_evidence_contract() -> dict[str, Any]:
    return {
        "status": "PASS",
        "canonical_json_required": True,
        "sha256_required": True,
        "manifest_completeness_required": True,
        "seal_manifest_hash_required": True,
        "expected_reports": list(EXPECTED_REPORTS),
        "expected_manifests": list(EXPECTED_MANIFESTS),
    }


def validate_manifest_completeness(produced: list[str], expected: list[str]) -> dict[str, Any]:
    missing = sorted(set(expected) - set(produced))
    extra = sorted(set(produced) - set(expected))
    return {"status": "PASS" if not missing and not extra else "BLOCK", "missing": missing, "extra": extra}

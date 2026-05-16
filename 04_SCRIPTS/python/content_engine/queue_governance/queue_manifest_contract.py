from __future__ import annotations

from .queue_failure_policy import PASS, BLOCK

EXPECTED_SEALED_STATUS = "CONTENT_ENGINE_QUEUE_GOVERNANCE_CORE_BUILT_PENDING_POST_AUDIT"
EXPECTED_NEXT_SAFE_STEP = "CONTENT_ENGINE_QUEUE_GOVERNANCE_POST_BUILD_AUDIT"


def build_queue_manifest_payload(produced_artifacts: list[str], hashed_artifacts: dict[str, str]) -> dict:
    return {
        "project": "CONTENT_ENGINE_OMEGA",
        "component": "CONTENT_ENGINE_QUEUE_GOVERNANCE_CORE",
        "status": "BUILT_PENDING_POST_AUDIT",
        "result": PASS,
        "manifest_type": "CONTENT_ENGINE_QUEUE_GOVERNANCE_CORE_MANIFEST",
        "produced_artifacts": sorted(produced_artifacts),
        "hashed_artifacts": dict(sorted(hashed_artifacts.items())),
        "canonical_json": True,
        "hash_algorithm": "sha256",
        "manifest_completeness": PASS,
        "next_safe_step": EXPECTED_NEXT_SAFE_STEP,
    }


def validate_queue_manifest_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {"status": BLOCK, "reason": "QUEUE_MANIFEST_SEAL_MISMATCH"}
    if payload.get("manifest_type") != "CONTENT_ENGINE_QUEUE_GOVERNANCE_CORE_MANIFEST":
        return {"status": BLOCK, "reason": "QUEUE_MANIFEST_SEAL_MISMATCH"}
    if payload.get("manifest_completeness") != PASS:
        return {"status": BLOCK, "reason": "QUEUE_MANIFEST_SEAL_MISMATCH"}
    if payload.get("next_safe_step") != EXPECTED_NEXT_SAFE_STEP:
        return {"status": BLOCK, "reason": "QUEUE_MANIFEST_SEAL_MISMATCH"}
    return {"status": PASS, "reason": "QUEUE_MANIFEST_VALIDATED"}


def validate_queue_seal_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {"status": BLOCK, "reason": "QUEUE_MANIFEST_SEAL_MISMATCH"}
    if payload.get("sealed_status") != EXPECTED_SEALED_STATUS:
        return {"status": BLOCK, "reason": "QUEUE_MANIFEST_SEAL_MISMATCH"}
    if payload.get("next_safe_step") != EXPECTED_NEXT_SAFE_STEP:
        return {"status": BLOCK, "reason": "QUEUE_MANIFEST_SEAL_MISMATCH"}
    if payload.get("queue_write_allowed_now") is not False:
        return {"status": BLOCK, "reason": "QUEUE_MANIFEST_SEAL_MISMATCH"}
    return {"status": PASS, "reason": "QUEUE_SEAL_VALIDATED"}

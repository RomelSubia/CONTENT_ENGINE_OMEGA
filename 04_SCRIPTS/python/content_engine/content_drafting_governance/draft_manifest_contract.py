from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_manifest(payload: dict[str, object]) -> dict[str, object]:
    manifest = {
        "component": "CONTENT_DRAFTING_GOVERNANCE_CORE",
        "status": "BUILT_PENDING_POST_AUDIT",
        "payload": payload,
        "draft_creation_allowed": False,
        "content_generation_allowed": False,
        "queue_write_allowed": False,
        "publishing_allowed": False,
        "automation_allowed": False,
        "canonical_json": True,
    }
    manifest["self_sha256"] = sha256_text(canonical_json(manifest))
    return manifest

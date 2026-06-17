from __future__ import annotations

from typing import Mapping

from .contracts import SafePreviewResult


def build_audit_bundle(result: SafePreviewResult) -> dict[str, object]:
    data = result.as_dict()
    data["audit_status"] = "SAFE_PREVIEW_AUDIT_BUNDLE_CREATED"
    data["productive_operations_blocked"] = all(
        value is False for value in result.blocked_productive_flags.values()
    )
    return data


def assert_no_productive_flags(flags: Mapping[str, bool]) -> bool:
    return all(value is False for value in flags.values())

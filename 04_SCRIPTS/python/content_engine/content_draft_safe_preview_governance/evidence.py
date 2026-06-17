from __future__ import annotations

from collections.abc import Sequence

from .contracts import SafePreviewError


def require_non_empty_refs(refs: Sequence[str], field_name: str) -> tuple[str, ...]:
    normalized = tuple(str(ref).strip() for ref in refs if str(ref).strip())
    if not normalized:
        raise SafePreviewError(f"{field_name}_required")
    return normalized


def require_text(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise SafePreviewError(f"{field_name}_required")
    return normalized

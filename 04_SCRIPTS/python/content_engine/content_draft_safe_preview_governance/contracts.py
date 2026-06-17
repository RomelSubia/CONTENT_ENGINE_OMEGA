from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence


class SafePreviewError(ValueError):
    """Raised when a safe preview request violates fail-closed governance."""


@dataclass(frozen=True)
class SafePreviewRequest:
    request_id: str
    candidate_id: str
    domain_id: str
    preview_text: str
    classification: str
    evidence_refs: tuple[str, ...]
    traceability_refs: tuple[str, ...]
    human_review_required: bool = True
    metadata: Mapping[str, object] = field(default_factory=dict)

    @classmethod
    def from_values(
        cls,
        *,
        request_id: str,
        candidate_id: str,
        domain_id: str,
        preview_text: str,
        classification: str,
        evidence_refs: Sequence[str],
        traceability_refs: Sequence[str],
        human_review_required: bool = True,
        metadata: Mapping[str, object] | None = None,
    ) -> "SafePreviewRequest":
        return cls(
            request_id=request_id,
            candidate_id=candidate_id,
            domain_id=domain_id,
            preview_text=preview_text,
            classification=classification,
            evidence_refs=tuple(evidence_refs),
            traceability_refs=tuple(traceability_refs),
            human_review_required=human_review_required,
            metadata=dict(metadata or {}),
        )


@dataclass(frozen=True)
class SafePreviewResult:
    request_id: str
    candidate_id: str
    domain_id: str
    preview_text: str
    classification: str
    preview_label: str
    human_review_required: bool
    evidence_refs: tuple[str, ...]
    traceability_refs: tuple[str, ...]
    blocked_productive_flags: Mapping[str, bool]

    def as_dict(self) -> dict[str, object]:
        return {
            "request_id": self.request_id,
            "candidate_id": self.candidate_id,
            "domain_id": self.domain_id,
            "preview_text": self.preview_text,
            "classification": self.classification,
            "preview_label": self.preview_label,
            "human_review_required": self.human_review_required,
            "evidence_refs": list(self.evidence_refs),
            "traceability_refs": list(self.traceability_refs),
            "blocked_productive_flags": dict(self.blocked_productive_flags),
        }

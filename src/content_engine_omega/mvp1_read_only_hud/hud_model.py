"""Data model for the MVP1 read-only HUD."""

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class HudState:
    """Immutable HUD state for display only."""

    system_identity: str
    blueprint_status: str
    guard_status: str
    evidence_status: str
    main_risk: str
    reality_level: str
    next_safe_step: str
    required_authorization: str
    communication_mode: str
    audit_status: str

    @classmethod
    def fail_closed(cls, reason: str) -> "HudState":
        """Return a safe fallback state without guessing."""
        return cls(
            system_identity="CONTENT_ENGINE_OMEGA",
            blueprint_status="UNKNOWN_REVIEW_REQUIRED",
            guard_status="UNKNOWN_REVIEW_REQUIRED",
            evidence_status="UNKNOWN_REVIEW_REQUIRED",
            main_risk=reason,
            reality_level="NO_RUNTIME_NO_ARGOS_NO_PRODUCTIVE_ACTIONS",
            next_safe_step="MANUAL_REVIEW_REQUIRED",
            required_authorization="EXPLICIT_USER_AUTHORIZATION_REQUIRED",
            communication_mode="READ_ONLY_STATUS",
            audit_status="FAIL_CLOSED",
        )

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "HudState":
        """Build state from a mapping using safe defaults."""
        return cls(
            system_identity=str(data.get("system_identity", "CONTENT_ENGINE_OMEGA")),
            blueprint_status=str(data.get("blueprint_status", "UNKNOWN_REVIEW_REQUIRED")),
            guard_status=str(data.get("guard_status", "UNKNOWN_REVIEW_REQUIRED")),
            evidence_status=str(data.get("evidence_status", "UNKNOWN_REVIEW_REQUIRED")),
            main_risk=str(data.get("main_risk", "NONE_DECLARED")),
            reality_level=str(data.get("reality_level", "READ_ONLY")),
            next_safe_step=str(data.get("next_safe_step", "MANUAL_REVIEW_REQUIRED")),
            required_authorization=str(
                data.get("required_authorization", "EXPLICIT_USER_AUTHORIZATION_REQUIRED")
            ),
            communication_mode=str(data.get("communication_mode", "READ_ONLY_STATUS")),
            audit_status=str(data.get("audit_status", "UNVERIFIED")),
        )

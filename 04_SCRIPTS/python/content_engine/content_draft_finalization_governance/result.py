from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FinalizationResult:
    request_id: str
    finalization_status: str
    finalized_artifact_reference: str
    finalized_artifact_sha256: str
    queue_governance_readiness_reference: str
    next_allowed_step_for_queue_governance_only: bool
    blocked_operation_flags: dict[str, bool]

    def assert_no_productive_side_effects(self) -> None:
        opened = [key for key, value in self.blocked_operation_flags.items() if value is not False]
        if opened:
            raise ValueError(f"PRODUCTIVE_SIDE_EFFECT_FLAGS_OPENED: {opened}")

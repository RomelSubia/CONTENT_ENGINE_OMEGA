from __future__ import annotations

from dataclasses import dataclass

from .models import QueueGovernanceStatus


@dataclass(frozen=True)
class QueueGovernanceResult:
    request_id: str
    queue_governance_status: QueueGovernanceStatus
    queue_governance_record_reference: str
    queue_governance_record_sha256: str
    queue_write_readiness_reference: str
    next_allowed_step_for_queue_write_governance_only: bool
    blocked_operation_flags: dict[str, bool]

    def assert_no_productive_side_effects(self) -> None:
        opened = [
            name
            for name, value in self.blocked_operation_flags.items()
            if value is not False
        ]
        if opened:
            raise AssertionError(f"PRODUCTIVE_SIDE_EFFECT_FLAG_OPEN: {opened}")

        if self.next_allowed_step_for_queue_write_governance_only is not True:
            raise AssertionError("QUEUE_WRITE_GOVERNANCE_NEXT_STEP_NOT_MARKED_PLAN_ONLY")

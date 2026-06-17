from __future__ import annotations

from enum import StrEnum


class HumanReviewState(StrEnum):
    REVIEW_NOT_STARTED = "REVIEW_NOT_STARTED"
    REVIEW_PENDING = "REVIEW_PENDING"
    REVIEW_IN_PROGRESS = "REVIEW_IN_PROGRESS"
    REVIEW_APPROVED = "REVIEW_APPROVED"
    REVIEW_REJECTED = "REVIEW_REJECTED"
    REVISION_REQUIRED = "REVISION_REQUIRED"
    REVIEW_EXPIRED = "REVIEW_EXPIRED"
    FAILED_CLOSED = "FAILED_CLOSED"


ALLOWED_TRANSITIONS: dict[HumanReviewState, set[HumanReviewState]] = {
    HumanReviewState.REVIEW_NOT_STARTED: {
        HumanReviewState.REVIEW_PENDING,
        HumanReviewState.FAILED_CLOSED,
    },
    HumanReviewState.REVIEW_PENDING: {
        HumanReviewState.REVIEW_IN_PROGRESS,
        HumanReviewState.REVIEW_EXPIRED,
        HumanReviewState.FAILED_CLOSED,
    },
    HumanReviewState.REVIEW_IN_PROGRESS: {
        HumanReviewState.REVIEW_APPROVED,
        HumanReviewState.REVIEW_REJECTED,
        HumanReviewState.REVISION_REQUIRED,
        HumanReviewState.FAILED_CLOSED,
    },
    HumanReviewState.REVIEW_APPROVED: set(),
    HumanReviewState.REVIEW_REJECTED: set(),
    HumanReviewState.REVISION_REQUIRED: set(),
    HumanReviewState.REVIEW_EXPIRED: set(),
    HumanReviewState.FAILED_CLOSED: set(),
}


def transition_state(current: HumanReviewState, target: HumanReviewState) -> HumanReviewState:
    if target not in ALLOWED_TRANSITIONS[current]:
        return HumanReviewState.FAILED_CLOSED
    return target


def state_for_decision(decision: str) -> HumanReviewState:
    if decision == "APPROVE_FOR_FINALIZATION_PLAN_ONLY":
        return HumanReviewState.REVIEW_APPROVED
    if decision == "REQUEST_REVISION":
        return HumanReviewState.REVISION_REQUIRED
    if decision == "REJECT":
        return HumanReviewState.REVIEW_REJECTED
    if decision in {"HOLD", "ESCALATE"}:
        return HumanReviewState.REVIEW_PENDING
    return HumanReviewState.FAILED_CLOSED

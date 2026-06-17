"""Content Draft Finalization Governance Core.

This package is governance-only. It prepares finalization-ready records and
explicitly blocks queue write, publishing, automation, runtime side effects,
manual-current mutation, brain writes, and ARGOS bridge escalation.
"""

from .models import (
    FinalizationDecision,
    FinalizationEvidence,
    FinalizationRequest,
    FinalizationStatus,
)
from .policy import FinalizationPolicy, FinalizationPolicyError
from .result import FinalizationResult
from .validator import validate_finalization_request
from .finalization_record import build_finalization_record

__all__ = [
    "FinalizationDecision",
    "FinalizationEvidence",
    "FinalizationRequest",
    "FinalizationStatus",
    "FinalizationPolicy",
    "FinalizationPolicyError",
    "FinalizationResult",
    "validate_finalization_request",
    "build_finalization_record",
]

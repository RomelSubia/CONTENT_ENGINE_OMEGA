from __future__ import annotations

from typing import Dict


def pending_output(reason: str) -> Dict:
    return {
        "phase": "G",
        "subphase": "G-E",
        "status": "PENDING_HUMAN_APPROVAL",
        "authorized_items": [],
        "pending_items": [],
        "blocked_items": [],
        "approval_summary": {"reason": reason},
        "decision": "PENDING_HUMAN_APPROVAL",
        "deterministic": True,
    }


def blocked_output(reason: str) -> Dict:
    return {
        "phase": "G",
        "subphase": "G-E",
        "status": "BLOCKED",
        "authorized_items": [],
        "pending_items": [],
        "blocked_items": [],
        "approval_summary": {"reason": reason},
        "decision": "BLOCK",
        "deterministic": True,
    }

from __future__ import annotations

from typing import Dict, Tuple

from .constants import RUNNER_TARGET


def validate_runner_lock(runner_target: str) -> Tuple[bool, str]:
    if runner_target != RUNNER_TARGET:
        return False, "INVALID_RUNNER_TARGET"

    return True, "RUNNER_LOCK_OK"

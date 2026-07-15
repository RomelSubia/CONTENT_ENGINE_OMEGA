"""Read-only state reader for the MVP1 HUD.

This module reads approved local JSON status documents only.
It does not write files, start processes, activate ARGOS,
or mutate local project data.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from .hud_model import HudState


class ReadOnlyStateReader:
    """Read approved local status files and return a fail-closed HUD state."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.blueprint_status_path = (
            repo_root
            / "00_MANUAL"
            / "content_engine"
            / "blueprints"
            / "CURRENT_BLUEPRINT_STATUS.json"
        )
        self.guard_status_path = (
            repo_root
            / "00_MANUAL"
            / "content_engine"
            / "build_transition"
            / "CURRENT_PRE_BUILD_TRANSITION_GUARD_STATUS.json"
        )
        self.mvp1_status_path = (
            repo_root
            / "00_MANUAL"
            / "content_engine"
            / "mvp1_read_only_hud"
            / "CURRENT_MVP1_READ_ONLY_HUD_TECHNICAL_PLAN_STATUS.json"
        )

    def read(self) -> HudState:
        """Read known status files and return HUD state.

        Missing or malformed files return a fail-closed state.
        """
        try:
            blueprint = self._read_json(self.blueprint_status_path)
            guard = self._read_json(self.guard_status_path)
            mvp1 = self._read_json(self.mvp1_status_path)
        except (OSError, ValueError, TypeError) as exc:
            return HudState.fail_closed(f"STATUS_READ_FAILED: {exc.__class__.__name__}")

        data = {
            "system_identity": "CONTENT_ENGINE_OMEGA",
            "blueprint_status": self._safe_nested(
                blueprint, ["current_blueprint", "status"], "UNKNOWN_REVIEW_REQUIRED"
            ),
            "guard_status": self._safe_nested(
                guard, ["pre_build_guard", "next_recommended_scope"], "UNKNOWN_REVIEW_REQUIRED"
            ),
            "evidence_status": "TECHNICAL_PLAN_EVIDENCE_PRESENT",
            "main_risk": "PATCH_PREVIEW_NOT_APPLIED",
            "reality_level": "READ_ONLY_NO_RUNTIME_NO_ARGOS",
            "next_safe_step": str(mvp1.get("next_safe_step", "MANUAL_REVIEW_REQUIRED")),
            "required_authorization": "EXPLICIT_USER_AUTHORIZATION_REQUIRED_FOR_ANY_MUTATION",
            "communication_mode": "STATUS_VISIBILITY_ONLY",
            "audit_status": str(mvp1.get("status", "UNVERIFIED")),
        }

        return HudState.from_mapping(data)

    def _read_json(self, path: Path) -> Dict[str, Any]:
        """Read JSON file from an approved local path."""
        with path.open("r", encoding="utf-8") as file_handle:
            value = json.load(file_handle)

        if not isinstance(value, dict):
            raise ValueError("status JSON must be an object")

        return value

    def _safe_nested(self, data: Dict[str, Any], path: List[str], default: str) -> str:
        """Read a nested string safely."""
        current = data

        for key in path:
            if not isinstance(current, dict):
                return default
            current = current.get(key)

        if current is None:
            return default

        return str(current)

from __future__ import annotations

from typing import Any

FUTURE_METRICS = ["retention_future", "watch_time_future", "conversion_signal_future", "quality_signal_future"]
BLOCKED_ACTIONS = {"read_real_metrics", "connect_api", "scrape_platform", "activate_dashboard", "modify_decisions_by_external_data"}


def build_learning_placeholder() -> dict[str, Any]:
    return {"status": "PASS", "future_metrics": list(FUTURE_METRICS), "real_metrics_ingestion_allowed": False, "blocked_actions": sorted(BLOCKED_ACTIONS)}


def validate_learning_action(action: str) -> dict[str, Any]:
    if action in BLOCKED_ACTIONS:
        return {"status": "BLOCK", "reason": "REAL_LEARNING_ACTION_BLOCKED", "action": action}
    return {"status": "PASS", "action": action}

from __future__ import annotations

from typing import Any, Dict, List


def _semantic_key(record: Dict[str, Any]) -> str:
    data = record.get("data", {})
    for key in ("event", "status", "decision", "validation", "error", "outcome"):
        if key in data:
            return f"{record['type']}:{key}:{data[key]}"
    return f"{record['type']}:generic"


def detect_patterns(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counts = {}

    for record in records:
        key = _semantic_key(record)
        counts[key] = counts.get(key, 0) + 1

    patterns = []
    for key in sorted(counts.keys()):
        count = counts[key]
        if count >= 2:
            category = key.split(":", 1)[0]
            pattern_type = "REPEATED_EVENT"

            if "error" in key.lower() or "failure" in key.lower() or "fail" in key.lower():
                pattern_type = "REPEATED_ERROR"
            elif "ok" in key.lower() or "pass" in key.lower() or "success" in key.lower():
                pattern_type = "REPEATED_SUCCESS"
            elif category == "decisions":
                pattern_type = "REPEATED_DECISION"
            elif category == "metrics":
                pattern_type = "PERFORMANCE_SIGNAL"
            elif category == "outcomes":
                pattern_type = "OUTCOME_TREND"

            patterns.append(
                {
                    "pattern_key": key,
                    "pattern_type": pattern_type,
                    "count": count,
                    "category": category,
                }
            )

    return patterns

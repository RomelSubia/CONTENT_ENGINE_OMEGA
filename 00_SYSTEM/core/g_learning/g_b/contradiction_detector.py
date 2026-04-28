from __future__ import annotations

from typing import Dict, List


def detect_contradictions(patterns: List[Dict], records: List[Dict]) -> List[Dict]:
    has_success = False
    has_failure = False

    for record in records:
        data_text = str(record.get("data", {})).lower()
        if "ok" in data_text or "success" in data_text or "pass" in data_text:
            has_success = True
        if "fail" in data_text or "failure" in data_text or "error" in data_text:
            has_failure = True

    contradictions = []

    if has_success and has_failure:
        contradictions.append(
            {
                "type": "SUCCESS_FAILURE_CONFLICT",
                "reason": "success and failure signals coexist",
            }
        )

    for pattern in patterns:
        if pattern["pattern_type"] == "REPEATED_SUCCESS" and has_failure:
            contradictions.append(
                {
                    "type": "PATTERN_OUTCOME_CONFLICT",
                    "pattern": pattern,
                }
            )

    return contradictions

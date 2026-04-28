from __future__ import annotations

from typing import Any, Dict, List


def register_evidence(evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
    registry: List[Dict[str, Any]] = []

    for evidence_type in sorted(evidence.keys()):
        values = evidence[evidence_type]
        for index, item in enumerate(values):
            registry.append(
                {
                    "type": evidence_type,
                    "index": index,
                    "data": item,
                }
            )

    return registry

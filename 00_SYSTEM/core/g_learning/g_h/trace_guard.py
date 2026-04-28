from __future__ import annotations

from typing import Dict, Tuple


def validate_trace_chain(trace_chain: Dict) -> Tuple[bool, str]:
    if not isinstance(trace_chain, dict):
        return False, "TRACE_CHAIN_NOT_DICT"

    required = ("trace_id", "g_e", "g_f", "g_g")
    missing = [key for key in required if key not in trace_chain]
    if missing:
        return False, "MISSING_TRACE_KEYS:" + ",".join(missing)

    return True, "TRACE_CHAIN_OK"

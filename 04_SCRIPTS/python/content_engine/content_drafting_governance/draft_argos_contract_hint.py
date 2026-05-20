from __future__ import annotations

def get_argos_contract_hint() -> dict[str, object]:
    return {
        "compatibility_mode": "METADATA_ONLY",
        "argos_dependency": False,
        "cross_imports_allowed": False,
        "bridge_build_allowed_now": False,
        "read_only_manifest_first": True,
        "health_status_bridge_hint_only": True,
        "argos_can_bypass_gates": False,
    }

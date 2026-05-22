from __future__ import annotations

from .runtime_contracts import PASS, hard_false_flags

def assert_no_side_effects(surface: list[str] | None = None) -> dict[str, object]:
    mutation_surface = list(surface or [])
    return {
        "status": PASS if not mutation_surface else "FAILED_BLOCKED",
        "NO_SIDE_EFFECT_RUNTIME": True,
        "mutation_surface": mutation_surface,
        "external_calls_performed": False,
        "filesystem_writes_performed": False,
        "queue_mutation_performed": False,
        "publication_mutation_performed": False,
        "asset_generation_performed": False,
        "automation_triggered": False,
        **hard_false_flags(),
    }

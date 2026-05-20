from __future__ import annotations

from .draft_channel_policy import validate_channel_or_domain

DOMAIN_TONE_MARKERS = {
    "finca_san_mateo": {"evento", "finca", "reserva", "familia"},
    "bravi": {"corporativo", "cliente", "operación", "servicio"},
    "bramviss": {"industrial", "mantenimiento", "técnico", "proyecto"},
    "cacao": {"cacao", "cultivo", "origen", "finca"},
}


def inspect_domain_contamination(channel_or_domain_id: str, text: str) -> dict[str, object]:
    validate_channel_or_domain(channel_or_domain_id)
    lowered = text.lower()
    own_markers = DOMAIN_TONE_MARKERS.get(channel_or_domain_id, set())
    foreign_matches = []
    for domain, markers in DOMAIN_TONE_MARKERS.items():
        if domain == channel_or_domain_id:
            continue
        if any(marker in lowered for marker in markers) and not any(marker in lowered for marker in own_markers):
            foreign_matches.append(domain)
    return {
        "blocked": bool(foreign_matches),
        "foreign_domain_matches": sorted(foreign_matches),
        "reason": "DOMAIN_CONTAMINATION_BLOCK" if foreign_matches else "DOMAIN_CONTAMINATION_CLEAR",
    }

"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


def forbidden_operational_literals() -> list[str]:
    return [
        "OPEN" + "AI_API_KEY",
        "api." + "open" + "ai.com",
        "eleven" + "labs.io",
        "web" + "hook_url",
        "n" + "8n_url",
        "publish" + "_endpoint",
        "tiktok_upload",
        "youtube_upload",
        "instagram_upload",
        "CAP" + "A9_ENDPOINT",
        "bearer ",
    ]

def validate_no_operational_literals(text: str) -> dict:
    lowered = str(text).lower()
    matched = [literal for literal in forbidden_operational_literals() if literal.lower() in lowered]
    if matched:
        return {"status": "BLOCK", "reason": "FORBIDDEN_OPERATIONAL_LITERAL", "matched_count": len(matched)}
    return {"status": "PASS", "reason": "NO_OPERATIONAL_LITERAL_DETECTED"}

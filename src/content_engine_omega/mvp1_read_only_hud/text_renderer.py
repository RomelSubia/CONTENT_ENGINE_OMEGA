"""Text renderer for MVP1 read-only HUD state."""

from .hud_model import HudState


class TextHudRenderer:
    """Render HUD state as plain text without side effects."""

    def render(self, state: HudState) -> str:
        """Return a deterministic text representation."""
        lines = [
            "CONTENT ENGINE OMEGA - MVP1 READ-ONLY HUD",
            "",
            f"System identity: {state.system_identity}",
            f"Blueprint status: {state.blueprint_status}",
            f"Guard status: {state.guard_status}",
            f"Evidence status: {state.evidence_status}",
            f"Main risk: {state.main_risk}",
            f"Reality level: {state.reality_level}",
            f"Next safe step: {state.next_safe_step}",
            f"Required authorization: {state.required_authorization}",
            f"Communication mode: {state.communication_mode}",
            f"Audit status: {state.audit_status}",
            "",
            "Hard limits:",
            "- No runtime execution.",
            "- No ARGOS activation.",
            "- No productive actions.",
            "- No credential access.",
            "- No external API calls.",
            "- No file mutation from renderer.",
        ]

        return "\n".join(lines)

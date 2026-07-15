from src.content_engine_omega.mvp1_read_only_hud.hud_model import HudState
from src.content_engine_omega.mvp1_read_only_hud.text_renderer import TextHudRenderer


def test_renderer_includes_hard_limits() -> None:
    state = HudState.fail_closed("review")
    rendered = TextHudRenderer().render(state)

    assert "CONTENT ENGINE OMEGA" in rendered
    assert "No runtime execution" in rendered
    assert "No ARGOS activation" in rendered
    assert "No productive actions" in rendered
    assert "No credential access" in rendered
    assert "No external API calls" in rendered

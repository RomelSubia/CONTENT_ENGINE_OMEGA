from pathlib import Path

from src.content_engine_omega.mvp1_read_only_hud.hud_model import HudState
from src.content_engine_omega.mvp1_read_only_hud.state_reader import ReadOnlyStateReader


def test_hud_state_fail_closed() -> None:
    state = HudState.fail_closed("missing")

    assert state.system_identity == "CONTENT_ENGINE_OMEGA"
    assert state.next_safe_step == "MANUAL_REVIEW_REQUIRED"
    assert state.audit_status == "FAIL_CLOSED"


def test_reader_fail_closed_when_files_missing(tmp_path: Path) -> None:
    reader = ReadOnlyStateReader(tmp_path)
    state = reader.read()

    assert state.system_identity == "CONTENT_ENGINE_OMEGA"
    assert state.audit_status == "FAIL_CLOSED"
    assert "STATUS_READ_FAILED" in state.main_risk

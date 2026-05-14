from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.strategy_foundation.learning_placeholder_contract import build_learning_placeholder, validate_learning_action


def test_learning_placeholder_passes():
    assert build_learning_placeholder()["status"] == "PASS"


def test_real_metrics_ingestion_false():
    assert build_learning_placeholder()["real_metrics_ingestion_allowed"] is False


def test_connect_api_blocks_negative():
    assert validate_learning_action("connect_api")["status"] == "BLOCK"


def test_scrape_platform_blocks_negative():
    assert validate_learning_action("scrape_platform")["status"] == "BLOCK"


def test_define_future_metric_passes():
    assert validate_learning_action("define_future_metric")["status"] == "PASS"

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.construction_core.permission_matrix import (
    build_permission_matrix,
    dangerous_permissions_are_false,
    validate_permission_matrix,
)


def test_permission_matrix_passes():
    matrix = build_permission_matrix()
    assert validate_permission_matrix(matrix)["status"] == "PASS"


def test_permission_matrix_all_dangerous_false():
    assert dangerous_permissions_are_false() is True


def test_permission_matrix_allows_only_post_build_audit_next():
    matrix = build_permission_matrix()
    assert matrix["content_engine_construction_post_build_audit_allowed_next"] is True


def test_permission_matrix_blocks_n8n_negative():
    matrix = build_permission_matrix()
    matrix["n8n_allowed_now"] = True
    assert validate_permission_matrix(matrix)["status"] == "BLOCK"


def test_permission_matrix_blocks_publishing_negative():
    matrix = build_permission_matrix()
    matrix["publishing_allowed_now"] = True
    assert validate_permission_matrix(matrix)["status"] == "BLOCK"

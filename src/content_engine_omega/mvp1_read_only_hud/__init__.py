"""Content Engine Omega MVP1 Read-Only HUD.

This package is a proposed passive visibility layer.
It only describes a local read-only status interface.
It must not start processes, mutate project files, activate external systems,
or perform operational workflows of any kind.
"""

from .hud_model import HudState
from .state_reader import ReadOnlyStateReader
from .text_renderer import TextHudRenderer

__all__ = [
    "HudState",
    "ReadOnlyStateReader",
    "TextHudRenderer",
]

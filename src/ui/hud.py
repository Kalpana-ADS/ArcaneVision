"""
ArcaneVision – HUD Overlay
============================
Draws FPS, active spell, hand count, gesture label on the frame.
"""

from __future__ import annotations
import cv2
import numpy as np
import math

from src.core.types import FrameStats, SpellType
from src.core.config import (
    SPELL_NAMES, SPELL_COLORS,
    HUD_FONT_SIZE_LARGE, HUD_FONT_SIZE_MEDIUM, HUD_PADDING, HUD_BG_ALPHA,
)


class HUD:
    """
    Renders all HUD elements directly onto the OpenCV BGR frame in-place.
    """

    FONT       = cv2.FONT_HERSHEY_SIMPLEX
    FONT_BOLD  = cv2.FONT_HERSHEY_DUPLEX

    def __init__(self, width: int, height: int) -> None:
        self._w = width
        self._h = height
        self._spell_flash_timer: float = 0.0
        self._last_spell: SpellType = SpellType.NONE

    def render(self, frame: np.ndarray, stats: FrameStats, dt: float) -> None:
        """Draw all HUD elements onto `frame` in-place."""
        self._update_flash(stats, dt)
        self._draw_top_bar(frame, stats)
        self._draw_spell_panel(frame, stats)
        self._draw_hand_indicator(frame, stats)
        self._draw_controls_hint(frame)

    # ------------------------------------------------------------------
    # Internal draw helpers
    # ------------------------------------------------------------------

    def _draw_top_bar(self, frame: np.ndarray, stats: FrameStats) -> None:
        """FPS + frame info strip at top-left with HD scaling."""
        pad = HUD_PADDING
        lines = [
            f"FPS: {stats.fps:.0f}",
            f"Hands: {stats.hand_count}",
            f"Gesture: {stats.active_gesture.value}",
        ]
        box_h = len(lines) * 30 + pad
        box_w = 260
        # Semi-transparent background
        self._draw_rounded_rect(frame, pad, pad, box_w, box_h, (20, 20, 30), HUD_BG_ALPHA)
        for i, line in enumerate(lines):
            y = pad + 24 + i * 30
            cv2.putText(frame, line, (pad + 12, y),
                        self.FONT, 0.75, (200, 220, 255), 1, cv2.LINE_AA)

    def _draw_spell_panel(self, frame: np.ndarray, stats: FrameStats) -> None:
        """Active spell name + colour strip in the bottom-centre with HD scaling."""
        spell  = stats.active_spell
        name   = SPELL_NAMES.get(spell, "Unknown")
        c_pri, c_sec = SPELL_COLORS.get(spell, ((200, 200, 200), (150, 150, 150)))
        # BGR
        bgr_pri = (c_pri[2], c_pri[1], c_pri[0])
        bgr_sec = (c_sec[2], c_sec[1], c_sec[0])

        # Flash on new spell
        flash_alpha = max(0.0, min(1.0, self._spell_flash_timer / 0.5))

        box_w = 500
        box_h = 80
        bx    = (self._w - box_w) // 2
        by    = self._h - box_h - HUD_PADDING

        self._draw_rounded_rect(frame, bx, by, box_w, box_h, (10, 10, 20), HUD_BG_ALPHA)

        # Colour bar
        bar_h = 6
        ov    = frame.copy()
        cv2.rectangle(ov, (bx + 6, by + box_h - bar_h - 3),
                      (bx + box_w - 6, by + box_h - 3), bgr_pri, -1)
        cv2.addWeighted(ov, 0.9, frame, 0.1, 0, frame)

        # Spell name
        scale    = 1.1 if len(name) < 20 else 0.9
        text_x   = bx + 18
        text_y   = by + 48
        # Shadow
        cv2.putText(frame, name, (text_x + 2, text_y + 2),
                    self.FONT_BOLD, scale, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(frame, name, (text_x, text_y),
                    self.FONT_BOLD, scale, bgr_pri, 3, cv2.LINE_AA)

        # Flash glow on activation
        if flash_alpha > 0:
            ov2 = frame.copy()
            cv2.rectangle(ov2, (bx, by), (bx + box_w, by + box_h), bgr_pri, -1)
            cv2.addWeighted(ov2, flash_alpha * 0.35, frame, 1 - flash_alpha * 0.35, 0, frame)

    def _draw_hand_indicator(self, frame: np.ndarray, stats: FrameStats) -> None:
        """Hand-count icon at top-right with HD scaling."""
        pad  = HUD_PADDING
        box_w = 140
        box_h = 55
        bx   = self._w - box_w - pad
        by   = pad
        self._draw_rounded_rect(frame, bx, by, box_w, box_h, (20, 20, 30), HUD_BG_ALPHA)
        label = f"Hands: {stats.hand_count}"
        cv2.putText(frame, label, (bx + 12, by + 35),
                    self.FONT, 0.7, (160, 255, 200), 1, cv2.LINE_AA)

    def _draw_controls_hint(self, frame: np.ndarray) -> None:
        """Control cheatsheet at bottom-right with HD scaling."""
        hints = ["1-0: Spell  Q: Quit  D: Debug"]
        pad   = HUD_PADDING
        by    = self._h - 35 - pad
        bx    = self._w - 380 - pad
        self._draw_rounded_rect(frame, bx, by - 6, 380, 35, (10, 10, 20), 120)
        for i, h in enumerate(hints):
            cv2.putText(frame, h, (bx + 10, by + 22 + i * 24),
                        self.FONT, 0.6, (140, 160, 180), 1, cv2.LINE_AA)

    def _draw_rounded_rect(
        self,
        frame: np.ndarray,
        x: int, y: int,
        w: int, h: int,
        color,
        alpha: int,
    ) -> None:
        """Draw a semi-transparent rectangle."""
        ov = frame.copy()
        cv2.rectangle(ov, (x, y), (x + w, y + h), color, -1)
        a = alpha / 255.0
        cv2.addWeighted(ov, a, frame, 1 - a, 0, frame)

    def _update_flash(self, stats: FrameStats, dt: float) -> None:
        if stats.active_spell != self._last_spell:
            self._last_spell        = stats.active_spell
            self._spell_flash_timer = 0.5
        elif self._spell_flash_timer > 0:
            self._spell_flash_timer = max(0.0, self._spell_flash_timer - dt)

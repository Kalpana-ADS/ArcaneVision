"""
ArcaneVision – Base Spell
==========================
Abstract base that every spell inherits from.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import numpy as np

from src.core.types import SpellState, RenderContext, Particle


class BaseSpell(ABC):
    """
    Each spell owns its particle list and implements:
      - activate()    → called once when spell fires
      - update(dt)    → called every frame while active
      - render(frame) → draws onto OpenCV BGR frame in-place
    """

    def __init__(self) -> None:
        self.particles: List[Particle] = []
        self.active: bool = False
        self.state: SpellState = SpellState()

    # ------------------------------------------------------------------
    # Life-cycle
    # ------------------------------------------------------------------

    def activate(self, ctx: RenderContext) -> None:
        """Trigger the spell. Override to set state & emit particles."""
        self.active = True
        self.state.reset(ctx.hands[0].palm_center_pixel if ctx.hands else (ctx.width // 2, ctx.height // 2))
        self._on_activate(ctx)

    def update(self, dt: float, ctx: RenderContext) -> None:
        """Called every frame. Updates particles + state."""
        self.state.update(dt)
        self._update_particles(dt, ctx)
        self._on_update(dt, ctx)
        if self.state.is_expired():
            self.active = False

    def render(self, frame: np.ndarray, ctx: RenderContext) -> None:
        """Draw spell effects onto the frame in-place."""
        if not self.active:
            return
        self._on_render(frame, ctx)

    def deactivate(self) -> None:
        self.active = False
        self.particles.clear()

    # ------------------------------------------------------------------
    # To implement
    # ------------------------------------------------------------------

    @abstractmethod
    def _on_activate(self, ctx: RenderContext) -> None: ...

    @abstractmethod
    def _on_update(self, dt: float, ctx: RenderContext) -> None: ...

    @abstractmethod
    def _on_render(self, frame: np.ndarray, ctx: RenderContext) -> None: ...

    # ------------------------------------------------------------------
    # Shared particle utilities
    # ------------------------------------------------------------------

    def _update_particles(self, dt: float, ctx: RenderContext) -> None:
        alive: List[Particle] = []
        for p in self.particles:
            p.x  += p.vx * dt * 60
            p.y  += (p.vy + p.gravity) * dt * 60
            p.vy += p.gravity * dt * 60
            p.life -= p.decay * dt * 60
            p.rotation += p.rot_speed * dt * 60
            p.alpha = max(0.0, p.life)
            if p.life > 0:
                alive.append(p)
        self.particles = alive

    def _draw_particles(self, frame: np.ndarray) -> None:
        """Draw all particles with enhanced HD glowing effects for AR visuals."""
        import cv2
        h, w = frame.shape[:2]
        for p in self.particles:
            if p.alpha <= 0:
                continue
            px, py = int(p.x), int(p.y)
            if not (0 <= px < w and 0 <= py < h):
                continue
            r, g, b = p.color
            alpha   = p.alpha
            size    = max(1, int(p.size * alpha * 1.5))

            if p.glow:
                for i, gsize in enumerate([size * 4, size * 3, size * 2, size]):
                    a_factor = alpha * (0.08 if i == 0 else 0.15 if i == 1 else 0.35 if i == 2 else 1.0)
                    color = (
                        int(min(255, b * a_factor + (255 - b) * 0.3 * a_factor)),
                        int(min(255, g * a_factor + (255 - g) * 0.3 * a_factor)),
                        int(min(255, r * a_factor + (255 - r) * 0.3 * a_factor))
                    )
                    cv2.circle(frame, (px, py), max(1, gsize), color, -1, cv2.LINE_AA)
            else:
                color = (
                    int(min(255, b * alpha + (255 - b) * 0.2 * alpha)),
                    int(min(255, g * alpha + (255 - g) * 0.2 * alpha)),
                    int(min(255, r * alpha + (255 - r) * 0.2 * alpha))
                )
                cv2.circle(frame, (px, py), size, color, -1, cv2.LINE_AA)

"""
ArcaneVision – Lightning Spell
================================
Electric arcs between fingertips + jagged bolts.
"""

from __future__ import annotations
import random
import math
import numpy as np
import cv2

from src.spells.base_spell import BaseSpell
from src.core.types import Particle, RenderContext
from src.core.config import MAX_PARTICLES


def _lightning_arc(
    frame: np.ndarray,
    start,
    end,
    color=(180, 140, 255),
    segments: int = 12,
    deviation: int = 30,
    thickness: int = 2,
) -> None:
    """Draw a jagged lightning arc from start to end."""
    sx, sy = start
    ex, ey = end
    pts = [(sx, sy)]
    for i in range(1, segments):
        t = i / segments
        bx = int(sx + (ex - sx) * t + random.randint(-deviation, deviation))
        by = int(sy + (ey - sy) * t + random.randint(-deviation, deviation))
        pts.append((bx, by))
    pts.append((ex, ey))

    for i in range(len(pts) - 1):
        # Glow pass
        cv2.line(frame, pts[i], pts[i + 1],
                 (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50)),
                 thickness + 4, cv2.LINE_AA)
        # Core
        cv2.line(frame, pts[i], pts[i + 1], color, thickness, cv2.LINE_AA)
        # Bright core
        cv2.line(frame, pts[i], pts[i + 1], (255, 255, 255), max(1, thickness - 1), cv2.LINE_AA)


class LightningSpell(BaseSpell):

    def __init__(self) -> None:
        super().__init__()
        self._bolt_timer: float = 0.0
        self._bolt_interval: float = 0.05  # seconds

    def _on_activate(self, ctx: RenderContext) -> None:
        ox, oy = self.state.origin
        # Initial spark burst
        for _ in range(min(100, MAX_PARTICLES)):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1, 5)
            c = random.choice([(180, 140, 255), (255, 255, 100), (220, 200, 255)])
            self.particles.append(Particle(
                x=ox, y=oy,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0, decay=random.uniform(0.04, 0.09),
                size=random.uniform(1, 4), color=c, glow=True,
            ))
        self._bolt_timer = 0.0

    def _on_update(self, dt: float, ctx: RenderContext) -> None:
        self._bolt_timer += dt
        # Periodic spark emission from index+middle tips
        if ctx.hands and self._bolt_timer >= self._bolt_interval:
            self._bolt_timer = 0.0
            ix, iy = ctx.hands[0].index_tip_pixel
            mx, my = ctx.hands[0].middle_tip_pixel
            if len(self.particles) < MAX_PARTICLES:
                for ox, oy in [(ix, iy), (mx, my)]:
                    for _ in range(6):
                        angle = random.uniform(0, math.tau)
                        speed = random.uniform(0.5, 3.0)
                        c = random.choice([(180, 140, 255), (255, 255, 100)])
                        self.particles.append(Particle(
                            x=ox, y=oy,
                            vx=math.cos(angle) * speed,
                            vy=math.sin(angle) * speed,
                            life=1.0, decay=random.uniform(0.05, 0.12),
                            size=random.uniform(1.5, 4), color=c, glow=True,
                        ))

    def _on_render(self, frame: np.ndarray, ctx: RenderContext) -> None:
        self._draw_particles(frame)

        if not ctx.hands:
            return

        ix, iy = ctx.hands[0].index_tip_pixel
        mx, my = ctx.hands[0].middle_tip_pixel

        # Arc between fingers
        _lightning_arc(frame, (ix, iy), (mx, my),
                       color=(180, 140, 255), segments=8, deviation=15, thickness=2)

        # Random bolts to edge
        if random.random() < 0.4:
            h, w = frame.shape[:2]
            target = (random.choice([0, w]), random.randint(0, h))
            src    = random.choice([(ix, iy), (mx, my)])
            _lightning_arc(frame, src, target,
                           color=(255, 255, 100), segments=16, deviation=40, thickness=1)

        # Halo at fingertips
        t = self.state.progress
        for tip in [(ix, iy), (mx, my)]:
            r = int(20 + 10 * abs(math.sin(t * math.pi * 8)))
            ov = frame.copy()
            cv2.circle(ov, tip, r, (140, 100, 255), -1, cv2.LINE_AA)
            cv2.addWeighted(ov, 0.5 * self.state.intensity, frame, 1 - 0.5 * self.state.intensity, 0, frame)

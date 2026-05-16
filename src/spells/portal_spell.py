"""
ArcaneVision – Portal Spell
=============================
Doctor Strange-style rotating vortex portal.
"""

from __future__ import annotations
import random
import math
import numpy as np
import cv2

from src.spells.base_spell import BaseSpell
from src.core.types import Particle, RenderContext
from src.core.config import MAX_PARTICLES


class PortalSpell(BaseSpell):

    def __init__(self) -> None:
        super().__init__()
        self._angle: float = 0.0
        self._radius: float = 0.0

    def _on_activate(self, ctx: RenderContext) -> None:
        self._angle  = 0.0
        self._radius = 20.0
        self._spawn_ring(ctx)

    def _spawn_ring(self, ctx: RenderContext) -> None:
        ox, oy = self.state.origin
        n = min(60, MAX_PARTICLES - len(self.particles))
        r = self._radius
        for i in range(n):
            a = (i / n) * math.tau + self._angle
            speed_r = random.uniform(0.1, 0.8)
            tang_v  = random.uniform(2.0, 5.0)
            c = random.choice([(60, 180, 255), (180, 60, 255), (0, 220, 255), (200, 100, 255)])
            self.particles.append(Particle(
                x=ox + math.cos(a) * r,
                y=oy + math.sin(a) * r,
                vx=-math.sin(a) * tang_v + math.cos(a) * speed_r,
                vy= math.cos(a) * tang_v + math.sin(a) * speed_r,
                life=1.0, decay=random.uniform(0.005, 0.012),
                size=random.uniform(2, 6), color=c, glow=True,
            ))

    def _on_update(self, dt: float, ctx: RenderContext) -> None:
        self._angle += 3.5 * dt
        if self._radius < 160:
            self._radius += 60 * dt

        # Spawn continuously
        if len(self.particles) < MAX_PARTICLES and ctx.hands:
            ox, oy = ctx.hands[0].palm_center_pixel
            self.state.origin = (ox, oy)
            n = 12
            r = self._radius
            for i in range(n):
                a = (i / n) * math.tau + self._angle
                tang = random.uniform(2.5, 6.0)
                c = random.choice([(60, 180, 255), (180, 60, 255), (0, 220, 255)])
                self.particles.append(Particle(
                    x=ox + math.cos(a) * r + random.uniform(-8, 8),
                    y=oy + math.sin(a) * r + random.uniform(-8, 8),
                    vx=-math.sin(a) * tang,
                    vy= math.cos(a) * tang,
                    life=1.0, decay=random.uniform(0.006, 0.014),
                    size=random.uniform(2, 5), color=c, glow=True,
                ))

    def _on_render(self, frame: np.ndarray, ctx: RenderContext) -> None:
        ox, oy = self.state.origin
        r = int(self._radius)
        intensity = self.state.intensity

        # Dark portal interior
        if r > 10:
            ov = frame.copy()
            cv2.ellipse(ov, (ox, oy), (r, int(r * 0.7)), int(math.degrees(self._angle)),
                        0, 360, (0, 0, 0), -1, cv2.LINE_AA)
            cv2.addWeighted(ov, 0.7 * intensity, frame, 1 - 0.7 * intensity, 0, frame)

        # Glowing rings
        for ring_r, ring_a, ring_c in [
            (r,      3, (255, 120, 60)),
            (r - 6,  2, (255, 60,  180)),
            (r + 4,  2, (60,  180, 255)),
        ]:
            if ring_r > 0:
                cv2.ellipse(frame, (ox, oy), (ring_r, int(ring_r * 0.7)),
                            int(math.degrees(self._angle)), 0, 360,
                            ring_c, ring_a, cv2.LINE_AA)

        self._draw_particles(frame)

        # Spinning orange sparks
        for i in range(6):
            a = self._angle * 3 + i * math.tau / 6
            sx = int(ox + math.cos(a) * r)
            sy = int(oy + math.sin(a) * int(r * 0.7))
            cv2.circle(frame, (sx, sy), 5, (50, 180, 255), -1, cv2.LINE_AA)

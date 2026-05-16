"""
ArcaneVision – Fireball Spell
================================
Fire projectile with explosion particles.
"""

from __future__ import annotations
import random
import math
import numpy as np
import cv2

from src.spells.base_spell import BaseSpell
from src.core.types import Particle, RenderContext
from src.core.config import MAX_PARTICLES


class FireSpell(BaseSpell):

    def __init__(self) -> None:
        super().__init__()
        self._ball_x: float = 0.0
        self._ball_y: float = 0.0
        self._ball_vx: float = 0.0
        self._ball_vy: float = 0.0
        self._exploded: bool = False
        self._ball_radius: float = 28.0

    def _on_activate(self, ctx: RenderContext) -> None:
        ox, oy = self.state.origin
        self._ball_x = float(ox)
        self._ball_y = float(oy)
        self._ball_vx = random.uniform(4.0, 8.0) * (1 if random.random() > 0.5 else -1)
        self._ball_vy = random.uniform(-6.0, -3.0)
        self._exploded = False
        self._ball_radius = 28.0

    def _on_update(self, dt: float, ctx: RenderContext) -> None:
        if self._exploded:
            return

        self._ball_x += self._ball_vx * dt * 60
        self._ball_y += self._ball_vy * dt * 60
        self._ball_vy += 0.15 * dt * 60   # gravity

        # Emit fire trail
        if len(self.particles) < MAX_PARTICLES:
            for _ in range(12):
                angle = random.uniform(0, math.tau)
                speed = random.uniform(0.3, 1.8)
                c = random.choice([(255, 60, 0), (255, 160, 0), (255, 220, 0), (200, 40, 0)])
                self.particles.append(Particle(
                    x=self._ball_x + random.uniform(-5, 5),
                    y=self._ball_y + random.uniform(-5, 5),
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                    life=1.0, decay=random.uniform(0.04, 0.09),
                    size=random.uniform(3, 9),
                    color=c, gravity=0.02, glow=True,
                ))

        # Out of frame → explode
        if (self._ball_x < 0 or self._ball_x > ctx.width or
                self._ball_y < 0 or self._ball_y > ctx.height or
                self.state.progress > 0.6):
            self._explode(ctx)

    def _explode(self, ctx: RenderContext) -> None:
        self._exploded = True
        ex, ey = int(self._ball_x), int(self._ball_y)
        for _ in range(min(250, MAX_PARTICLES - len(self.particles))):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1.0, 9.0)
            c = random.choice([(255, 50, 0), (255, 150, 0), (255, 230, 50), (255, 255, 200)])
            self.particles.append(Particle(
                x=ex, y=ey,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0, decay=random.uniform(0.02, 0.05),
                size=random.uniform(4, 14), color=c, gravity=0.04, glow=True,
            ))

    def _on_render(self, frame: np.ndarray, ctx: RenderContext) -> None:
        self._draw_particles(frame)

        if not self._exploded:
            bx, by = int(self._ball_x), int(self._ball_y)
            r = int(self._ball_radius)
            # Glow layers
            for gr, ga in [(r * 3, 0.08), (r * 2, 0.18), (r, 0.5)]:
                overlay = frame.copy()
                cv2.circle(overlay, (bx, by), gr, (0, 80, 255), -1, cv2.LINE_AA)
                cv2.addWeighted(overlay, ga, frame, 1 - ga, 0, frame)
            cv2.circle(frame, (bx, by), r, (50, 200, 255), -1, cv2.LINE_AA)
            cv2.circle(frame, (bx, by), r // 2, (200, 230, 255), -1, cv2.LINE_AA)

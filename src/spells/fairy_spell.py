"""
ArcaneVision – Fairy Dust Spell
=================================
Sparkly golden/pink particle burst from palm.
"""

from __future__ import annotations
import random
import math
import numpy as np
import cv2

from src.spells.base_spell import BaseSpell
from src.core.types import Particle, RenderContext
from src.core.config import MAX_PARTICLES


class FairySpell(BaseSpell):

    def _on_activate(self, ctx: RenderContext) -> None:
        ox, oy = self.state.origin
        colors = [
            (255, 220, 80),
            (255, 180, 230),
            (255, 255, 160),
            (200, 255, 200),
            (255, 140, 200),
        ]
        n = min(200, MAX_PARTICLES - len(self.particles))
        for _ in range(n):
            angle  = random.uniform(0, math.tau)
            speed  = random.uniform(0.5, 4.0)
            self.particles.append(Particle(
                x=ox + random.uniform(-20, 20),
                y=oy + random.uniform(-20, 20),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - random.uniform(0.5, 2.0),
                life=1.0,
                decay=random.uniform(0.008, 0.018),
                size=random.uniform(2, 6),
                color=random.choice(colors),
                gravity=-0.02,
                rot_speed=random.uniform(-5, 5),
                glow=True,
            ))

    def _on_update(self, dt: float, ctx: RenderContext) -> None:
        # Continuously emit while active and a hand is present
        if ctx.hands and len(self.particles) < MAX_PARTICLES:
            ox, oy = ctx.hands[0].palm_center_pixel
            colors = [(255, 220, 80), (255, 180, 230), (255, 255, 200)]
            for _ in range(8):
                angle = random.uniform(0, math.tau)
                speed = random.uniform(0.3, 2.5)
                self.particles.append(Particle(
                    x=ox + random.uniform(-10, 10),
                    y=oy + random.uniform(-10, 10),
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed - 1.0,
                    life=1.0,
                    decay=random.uniform(0.01, 0.02),
                    size=random.uniform(1.5, 5),
                    color=random.choice(colors),
                    gravity=-0.015,
                    glow=True,
                ))

    def _on_render(self, frame: np.ndarray, ctx: RenderContext) -> None:
        self._draw_particles(frame)

        # Soft golden glow at palm
        if ctx.hands:
            ox, oy = ctx.hands[0].palm_center_pixel
            t = self.state.progress
            radius = int(60 + 30 * math.sin(t * math.pi * 4))
            alpha  = max(0.0, self.state.intensity * 0.35)
            overlay = frame.copy()
            cv2.circle(overlay, (ox, oy), radius, (80, 220, 255), -1, cv2.LINE_AA)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

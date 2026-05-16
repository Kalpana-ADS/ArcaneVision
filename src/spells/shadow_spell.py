"""
ArcaneVision – Shadow Magic Spell
====================================
Expanding dark smoke tendrils from the hand.
"""

from __future__ import annotations
import random
import math
import numpy as np
import cv2

from src.spells.base_spell import BaseSpell
from src.core.types import Particle, RenderContext
from src.core.config import MAX_PARTICLES


class ShadowSpell(BaseSpell):

    def _on_activate(self, ctx: RenderContext) -> None:
        ox, oy = self.state.origin
        for _ in range(min(160, MAX_PARTICLES)):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(0.2, 3.5)
            c = random.choice([(80, 0, 120), (40, 0, 60), (120, 20, 160), (60, 0, 90)])
            self.particles.append(Particle(
                x=ox + random.uniform(-10, 10),
                y=oy + random.uniform(-10, 10),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 0.5,
                life=1.0, decay=random.uniform(0.003, 0.01),
                size=random.uniform(8, 22), color=c, glow=False,
            ))

    def _on_update(self, dt: float, ctx: RenderContext) -> None:
        if ctx.hands and len(self.particles) < MAX_PARTICLES:
            ox, oy = ctx.hands[0].palm_center_pixel
            for _ in range(10):
                angle = random.uniform(0, math.tau)
                speed = random.uniform(0.2, 2.5)
                c = random.choice([(80, 0, 120), (40, 0, 60), (120, 20, 160)])
                self.particles.append(Particle(
                    x=ox + random.uniform(-5, 5),
                    y=oy + random.uniform(-5, 5),
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed - 0.3,
                    life=1.0, decay=random.uniform(0.004, 0.012),
                    size=random.uniform(6, 20), color=c,
                    gravity=-0.005, glow=False,
                ))

    def _on_render(self, frame: np.ndarray, ctx: RenderContext) -> None:
        # Dark vignette
        h, w = frame.shape[:2]
        dark = np.zeros_like(frame)
        intensity = self.state.intensity * 0.55
        cv2.addWeighted(dark, intensity, frame, 1 - intensity, 0, frame)

        # Draw smoke particles (additive blend would darken here)
        for p in self.particles:
            if p.alpha <= 0:
                continue
            px, py = int(p.x), int(p.y)
            if not (0 <= px < w and 0 <= py < h):
                continue
            r, g, b = p.color
            size    = max(1, int(p.size * p.alpha))
            alpha   = p.alpha * 0.4
            ov      = frame.copy()
            cv2.circle(ov, (px, py), size,
                       (int(b), int(g), int(r)), -1, cv2.LINE_AA)
            cv2.addWeighted(ov, alpha, frame, 1 - alpha, 0, frame)

        # Purple glow at palm
        if ctx.hands:
            ox, oy = ctx.hands[0].palm_center_pixel
            t = self.state.progress
            radius = int(50 + 30 * math.sin(t * math.pi * 3))
            ov = frame.copy()
            cv2.circle(ov, (ox, oy), radius, (120, 0, 80), -1, cv2.LINE_AA)
            cv2.addWeighted(ov, 0.4 * self.state.intensity, frame, 1 - 0.4 * self.state.intensity, 0, frame)

"""
ArcaneVision – Levitation Spell
==================================
Floating orbs + upward wind lines from open palm.
"""

from __future__ import annotations
import random
import math
import numpy as np
import cv2

from src.spells.base_spell import BaseSpell
from src.core.types import Particle, RenderContext
from src.core.config import MAX_PARTICLES


class LevitationSpell(BaseSpell):

    def __init__(self) -> None:
        super().__init__()
        self._orbs: list = []  # [(x,y,phase,size,color)]

    def _on_activate(self, ctx: RenderContext) -> None:
        ox, oy = self.state.origin
        self._orbs = []
        for i in range(7):
            angle = (i / 7) * math.tau
            r = random.uniform(60, 130)
            c = random.choice([(100, 255, 200), (200, 255, 100), (150, 255, 240)])
            self._orbs.append([
                ox + math.cos(angle) * r,
                oy + math.sin(angle) * r,
                random.uniform(0, math.tau),
                random.uniform(10, 22),
                c,
            ])
        # Wind particles
        for _ in range(min(80, MAX_PARTICLES)):
            self.particles.append(Particle(
                x=random.uniform(ox - 100, ox + 100),
                y=oy + random.uniform(-20, 20),
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(-3.0, -1.0),
                life=1.0, decay=random.uniform(0.01, 0.02),
                size=random.uniform(1, 3),
                color=random.choice([(100, 255, 200), (200, 255, 150)]),
                glow=True,
            ))

    def _on_update(self, dt: float, ctx: RenderContext) -> None:
        # Float orbs around palm
        if ctx.hands:
            ox, oy = ctx.hands[0].palm_center_pixel
        else:
            ox, oy = self.state.origin
        t = self.state.progress

        for orb in self._orbs:
            orb[2] += dt * 1.5
            orb[0] += math.cos(orb[2]) * 0.5
            orb[1] += -0.3 + math.sin(orb[2] * 2) * 0.3

        # Wind streams
        if len(self.particles) < MAX_PARTICLES:
            for _ in range(5):
                self.particles.append(Particle(
                    x=ox + random.uniform(-80, 80),
                    y=oy + random.uniform(0, 30),
                    vx=random.uniform(-0.3, 0.3),
                    vy=random.uniform(-2.5, -0.8),
                    life=1.0, decay=random.uniform(0.012, 0.025),
                    size=random.uniform(1, 2.5),
                    color=(100, 255, 200), glow=True,
                ))

    def _on_render(self, frame: np.ndarray, ctx: RenderContext) -> None:
        self._draw_particles(frame)

        # Draw glowing orbs
        for orb in self._orbs:
            ox2, oy2, _, size, color = orb
            px, py = int(ox2), int(oy2)
            s = int(size)
            r, g, b = color
            # Outer glow
            ov = frame.copy()
            cv2.circle(ov, (px, py), s * 3, (int(b * 0.3), int(g * 0.3), int(r * 0.3)), -1, cv2.LINE_AA)
            cv2.addWeighted(ov, 0.3 * self.state.intensity, frame, 1 - 0.3 * self.state.intensity, 0, frame)
            # Core
            cv2.circle(frame, (px, py), s, (int(b), int(g), int(r)), -1, cv2.LINE_AA)
            cv2.circle(frame, (px, py), max(1, s // 2), (255, 255, 255), -1, cv2.LINE_AA)

        # Aura at palm
        if ctx.hands:
            px, py = ctx.hands[0].palm_center_pixel
            t = self.state.progress
            r = int(40 + 20 * math.sin(t * math.pi * 5))
            ov = frame.copy()
            cv2.circle(ov, (px, py), r, (100, 255, 180), -1, cv2.LINE_AA)
            cv2.addWeighted(ov, 0.35 * self.state.intensity, frame, 1 - 0.35 * self.state.intensity, 0, frame)

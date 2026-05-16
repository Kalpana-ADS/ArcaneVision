"""
ArcaneVision – Healing Aura Spell
====================================
Pulsing green glow + rising healing orbs.
"""

from __future__ import annotations
import random
import math
import numpy as np
import cv2

from src.spells.base_spell import BaseSpell
from src.core.types import Particle, RenderContext
from src.core.config import MAX_PARTICLES


class HealingSpell(BaseSpell):

    def _on_activate(self, ctx: RenderContext) -> None:
        ox, oy = self.state.origin
        for _ in range(min(120, MAX_PARTICLES)):
            angle = random.uniform(0, math.tau)
            r     = random.uniform(20, 80)
            speed = random.uniform(0.1, 1.0)
            self.particles.append(Particle(
                x=ox + math.cos(angle) * r,
                y=oy + math.sin(angle) * r,
                vx=math.cos(angle) * speed * 0.3,
                vy=random.uniform(-1.5, -0.5),
                life=1.0, decay=random.uniform(0.005, 0.012),
                size=random.uniform(3, 9),
                color=random.choice([(40, 255, 120), (150, 255, 180), (200, 255, 200)]),
                gravity=-0.01, glow=True,
            ))

    def _on_update(self, dt: float, ctx: RenderContext) -> None:
        if ctx.hands and len(self.particles) < MAX_PARTICLES:
            ox, oy = ctx.hands[0].palm_center_pixel
            for _ in range(6):
                angle = random.uniform(0, math.tau)
                r = random.uniform(10, 60)
                self.particles.append(Particle(
                    x=ox + math.cos(angle) * r,
                    y=oy + math.sin(angle) * r,
                    vx=math.cos(angle) * 0.2,
                    vy=random.uniform(-1.2, -0.4),
                    life=1.0, decay=random.uniform(0.007, 0.015),
                    size=random.uniform(2, 7),
                    color=random.choice([(40, 255, 120), (100, 255, 160)]),
                    gravity=-0.008, glow=True,
                ))

    def _on_render(self, frame: np.ndarray, ctx: RenderContext) -> None:
        # Pulsing green screen overlay
        t = self.state.progress
        pulse = 0.5 + 0.5 * math.sin(t * math.pi * 6)
        intensity = self.state.intensity * 0.25 * pulse
        glow = np.full_like(frame, (80, 255, 80), dtype=np.uint8)
        cv2.addWeighted(glow, intensity, frame, 1 - intensity, 0, frame)

        # Aura rings at palm
        if ctx.hands:
            ox, oy = ctx.hands[0].palm_center_pixel
            for i in range(3):
                phase   = (t * 4 + i * 0.33) % 1.0
                ring_r  = int(30 + 120 * phase)
                ring_a  = max(0.0, self.state.intensity * (1.0 - phase))
                ov = frame.copy()
                cv2.circle(ov, (ox, oy), ring_r, (80, 255, 100), 3, cv2.LINE_AA)
                cv2.addWeighted(ov, ring_a * 0.5, frame, 1 - ring_a * 0.5, 0, frame)

        self._draw_particles(frame)

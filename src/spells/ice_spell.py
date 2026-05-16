"""
ArcaneVision – Ice Freeze Spell
=================================
Crystalline frost overlay + ice shards from fingertip.
"""

from __future__ import annotations
import random
import math
import numpy as np
import cv2

from src.spells.base_spell import BaseSpell
from src.core.types import Particle, RenderContext
from src.core.config import MAX_PARTICLES


class IceSpell(BaseSpell):

    def _on_activate(self, ctx: RenderContext) -> None:
        ox, oy = self.state.origin
        # Burst of ice shards
        for _ in range(min(150, MAX_PARTICLES)):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1.0, 6.0)
            c = random.choice([(180, 230, 255), (140, 200, 255), (220, 245, 255), (100, 180, 255)])
            self.particles.append(Particle(
                x=ox, y=oy,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0, decay=random.uniform(0.005, 0.015),
                size=random.uniform(2, 7), color=c,
                gravity=0.03, rot_speed=random.uniform(-8, 8), glow=True,
            ))

    def _on_update(self, dt: float, ctx: RenderContext) -> None:
        # Emit ice crystals from index tip
        if ctx.hands and len(self.particles) < MAX_PARTICLES:
            ix, iy = ctx.hands[0].index_tip_pixel
            c = random.choice([(180, 230, 255), (140, 200, 255), (255, 255, 255)])
            for _ in range(5):
                angle = random.uniform(0, math.tau)
                self.particles.append(Particle(
                    x=ix + random.uniform(-5, 5),
                    y=iy + random.uniform(-5, 5),
                    vx=math.cos(angle) * random.uniform(0.5, 3.0),
                    vy=math.sin(angle) * random.uniform(0.5, 3.0),
                    life=1.0, decay=random.uniform(0.01, 0.025),
                    size=random.uniform(1.5, 5), color=c,
                    gravity=0.01, glow=True,
                ))

    def _on_render(self, frame: np.ndarray, ctx: RenderContext) -> None:
        # Full-screen frost overlay
        intensity = self.state.intensity * 0.45
        frost = np.full_like(frame, (255, 245, 220), dtype=np.uint8)  # BGR ice-blue
        cv2.addWeighted(frost, intensity, frame, 1 - intensity, 0, frame)

        # Vignette frost edges
        h, w = frame.shape[:2]
        mask = np.zeros((h, w), dtype=np.float32)
        cx, cy = w // 2, h // 2
        for y in range(0, h, 2):
            for x in range(0, w, 2):
                dist = math.sqrt(((x - cx) / w) ** 2 + ((y - cy) / h) ** 2)
                mask[y, x] = min(1.0, dist * 1.8)
        mask = cv2.blur(mask, (61, 61))
        frost_edge = (mask[..., None] * np.array([255, 245, 220]) * self.state.intensity * 0.6).astype(np.uint8)
        cv2.addWeighted(frost_edge, 1, frame, 1, 0, frame)

        self._draw_particles(frame)

        # Blue aura at fingertip
        if ctx.hands:
            ix, iy = ctx.hands[0].index_tip_pixel
            radius = int(30 + 10 * math.sin(self.state.progress * math.pi * 6))
            ov = frame.copy()
            cv2.circle(ov, (ix, iy), radius, (255, 220, 140), -1, cv2.LINE_AA)
            cv2.addWeighted(ov, 0.4 * self.state.intensity, frame, 1 - 0.4 * self.state.intensity, 0, frame)

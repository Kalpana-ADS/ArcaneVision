"""
ArcaneVision – Time Freeze Spell
====================================
Blue desaturated screen freeze effect + clock-ring visuals.
"""

from __future__ import annotations
import random
import math
import numpy as np
import cv2

from src.spells.base_spell import BaseSpell
from src.core.types import Particle, RenderContext
from src.core.config import MAX_PARTICLES


class TimeSpell(BaseSpell):

    def __init__(self) -> None:
        super().__init__()
        self._frozen_frame: np.ndarray | None = None
        self._ring_angle: float = 0.0

    def _on_activate(self, ctx: RenderContext) -> None:
        self._ring_angle = 0.0
        self._frozen_frame = None

        ox, oy = self.state.origin
        # Burst of clock-like particles radiating outward
        for _ in range(min(120, MAX_PARTICLES)):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1.0, 5.0)
            c = random.choice([(180, 220, 255), (100, 160, 220), (220, 240, 255)])
            self.particles.append(Particle(
                x=ox, y=oy,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0, decay=random.uniform(0.01, 0.02),
                size=random.uniform(2, 6), color=c, glow=True,
            ))

    def _on_update(self, dt: float, ctx: RenderContext) -> None:
        self._ring_angle += dt * 2.0
        # Slow drip of particles
        if ctx.hands and len(self.particles) < MAX_PARTICLES:
            ox, oy = ctx.hands[0].palm_center_pixel
            for _ in range(3):
                angle = random.uniform(0, math.tau)
                self.particles.append(Particle(
                    x=ox, y=oy,
                    vx=math.cos(angle) * random.uniform(0.3, 2),
                    vy=math.sin(angle) * random.uniform(0.3, 2),
                    life=1.0, decay=random.uniform(0.008, 0.018),
                    size=random.uniform(2, 5),
                    color=(180, 220, 255), glow=True,
                ))

    def _on_render(self, frame: np.ndarray, ctx: RenderContext) -> None:
        # Desaturate the frame (time-frozen look)
        intensity = self.state.intensity * 0.6
        grey      = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        grey_bgr  = cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)
        # Tint blue
        blue_tint = grey_bgr.copy()
        blue_tint[:, :, 2] = np.clip(blue_tint[:, :, 2].astype(np.int32) - 20, 0, 255).astype(np.uint8)
        blue_tint[:, :, 0] = np.clip(blue_tint[:, :, 0].astype(np.int32) + 30, 0, 255).astype(np.uint8)
        cv2.addWeighted(blue_tint, intensity, frame, 1 - intensity, 0, frame)

        self._draw_particles(frame)

        # Clock rings
        if ctx.hands:
            ox, oy = ctx.hands[0].palm_center_pixel
        else:
            ox, oy = self.state.origin

        for ring_i in range(3):
            r = 50 + ring_i * 35
            angle_off = self._ring_angle * (1.0 - ring_i * 0.3)
            cv2.ellipse(frame, (ox, oy), (r, r),
                        math.degrees(angle_off), 0, 270,
                        (180, 220, 255), 2, cv2.LINE_AA)
            # Tick marks
            for tick in range(12):
                ta = angle_off + (tick / 12) * math.tau
                t_outer = (int(ox + math.cos(ta) * r), int(oy + math.sin(ta) * r))
                t_inner = (int(ox + math.cos(ta) * (r - 8)), int(oy + math.sin(ta) * (r - 8)))
                cv2.line(frame, t_inner, t_outer, (100, 160, 255), 1, cv2.LINE_AA)

        # Central glow
        ov = frame.copy()
        cv2.circle(ov, (ox, oy), 25, (180, 220, 255), -1, cv2.LINE_AA)
        cv2.addWeighted(ov, 0.4 * self.state.intensity, frame, 1 - 0.4 * self.state.intensity, 0, frame)

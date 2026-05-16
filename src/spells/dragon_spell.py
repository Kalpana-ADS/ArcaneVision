"""
ArcaneVision – Summon Dragon Spell
=====================================
Animated fire-dragon drawn procedurally with bezier curves + fire particles.
"""

from __future__ import annotations
import random
import math
import numpy as np
import cv2

from src.spells.base_spell import BaseSpell
from src.core.types import Particle, RenderContext
from src.core.config import MAX_PARTICLES


def _bezier(p0, p1, p2, t):
    """Quadratic bezier point."""
    return (
        int((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]),
        int((1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]),
    )


class DragonSpell(BaseSpell):

    def __init__(self) -> None:
        super().__init__()
        self._phase: float = 0.0
        self._wing_angle: float = 0.0
        self._body_offset: float = 0.0

    def _on_activate(self, ctx: RenderContext) -> None:
        self._phase       = 0.0
        self._wing_angle  = 0.0
        self._body_offset = 0.0
        ox, oy = self.state.origin
        # Initial fire burst
        for _ in range(min(200, MAX_PARTICLES)):
            angle = random.uniform(-math.pi / 3, math.pi / 3) - math.pi / 2
            speed = random.uniform(1, 8)
            c = random.choice([(255, 50, 0), (255, 140, 0), (255, 220, 0)])
            self.particles.append(Particle(
                x=ox, y=oy,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0, decay=random.uniform(0.02, 0.05),
                size=random.uniform(4, 12), color=c, glow=True, gravity=-0.02,
            ))

    def _on_update(self, dt: float, ctx: RenderContext) -> None:
        self._phase       += dt * 3.0
        self._wing_angle  += dt * 4.0
        self._body_offset  = math.sin(self._phase) * 30.0

        # Continuous fire breath
        if ctx.hands and len(self.particles) < MAX_PARTICLES:
            ox, oy = ctx.hands[0].palm_center_pixel
            for _ in range(15):
                angle = random.uniform(-math.pi / 4, math.pi / 4) - math.pi / 2
                speed = random.uniform(2, 9)
                c = random.choice([(255, 50, 0), (255, 140, 0), (255, 220, 50), (200, 40, 0)])
                self.particles.append(Particle(
                    x=ox + random.uniform(-20, 20),
                    y=oy + random.uniform(-10, 10),
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                    life=1.0, decay=random.uniform(0.025, 0.06),
                    size=random.uniform(3, 11), color=c, glow=True, gravity=-0.015,
                ))

    def _on_render(self, frame: np.ndarray, ctx: RenderContext) -> None:
        self._draw_particles(frame)

        if ctx.hands:
            ox, oy = ctx.hands[0].palm_center_pixel
        else:
            ox, oy = self.state.origin

        cx = ox
        cy = oy + int(self._body_offset) - 80

        # --- Body (serpentine) ---
        body_pts = []
        for i in range(20):
            t = i / 19
            bx = cx + int(math.sin(self._phase + t * math.pi * 2) * 40 * t)
            by = cy + int(t * 140)
            body_pts.append((bx, by))

        for i in range(len(body_pts) - 1):
            thick = max(2, int(16 * (1 - i / len(body_pts)) * self.state.intensity))
            # Glow
            cv2.line(frame, body_pts[i], body_pts[i + 1], (0, 80, 200), thick + 6, cv2.LINE_AA)
            cv2.line(frame, body_pts[i], body_pts[i + 1], (0, 140, 255), thick + 2, cv2.LINE_AA)
            cv2.line(frame, body_pts[i], body_pts[i + 1], (50, 200, 255), thick, cv2.LINE_AA)

        # --- Head ---
        hx, hy = body_pts[0] if body_pts else (cx, cy)
        head_r = int(22 * self.state.intensity)
        if head_r > 0:
            cv2.circle(frame, (hx, hy), head_r + 8, (0, 80, 200), -1, cv2.LINE_AA)
            cv2.circle(frame, (hx, hy), head_r, (0, 160, 255), -1, cv2.LINE_AA)
            # Eyes (glowing red)
            eye_off = max(1, head_r // 3)
            cv2.circle(frame, (hx - eye_off, hy - 4), 5, (0, 0, 255), -1, cv2.LINE_AA)
            cv2.circle(frame, (hx + eye_off, hy - 4), 5, (0, 0, 255), -1, cv2.LINE_AA)
            cv2.circle(frame, (hx - eye_off, hy - 4), 2, (0, 100, 255), -1, cv2.LINE_AA)
            cv2.circle(frame, (hx + eye_off, hy - 4), 2, (0, 100, 255), -1, cv2.LINE_AA)

        # --- Wings ---
        wa = self._wing_angle
        wing_span = int(90 * self.state.intensity)
        for side in [-1, 1]:
            ctrl = (hx + side * wing_span, hy - int(60 + 20 * math.sin(wa)))
            tip  = (hx + side * int(wing_span * 1.4), hy + 20)
            bezier_pts = [_bezier((hx, hy), ctrl, tip, t / 20) for t in range(21)]
            for i in range(len(bezier_pts) - 1):
                cv2.line(frame, bezier_pts[i], bezier_pts[i + 1], (0, 100, 200), 2, cv2.LINE_AA)
            # Wing membrane fill
            tri = np.array([(hx, hy), ctrl, tip], dtype=np.int32)
            ov  = frame.copy()
            cv2.fillPoly(ov, [tri], (20, 60, 120))
            cv2.addWeighted(ov, 0.3 * self.state.intensity, frame, 1 - 0.3 * self.state.intensity, 0, frame)

        # Roar glow
        ov = frame.copy()
        cv2.circle(ov, (hx, hy), head_r + 20, (0, 100, 255), -1, cv2.LINE_AA)
        cv2.addWeighted(ov, 0.25 * self.state.intensity, frame, 1 - 0.25 * self.state.intensity, 0, frame)

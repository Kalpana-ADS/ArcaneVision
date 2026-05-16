"""
ArcaneVision – Particle System
================================
Central particle engine (not used directly by spells—each spell owns its own list).
This module provides factory helpers for complex burst patterns.
"""

from __future__ import annotations
import random
import math
from typing import List
from src.core.types import Particle


class ParticleFactory:
    """Static helpers for generating common particle patterns with HD quality."""

    @staticmethod
    def radial_burst(
        origin_x: float,
        origin_y: float,
        count: int,
        speed_min: float,
        speed_max: float,
        colors: List,
        size_min: float = 3.0,
        size_max: float = 10.0,
        decay_min: float = 0.008,
        decay_max: float = 0.02,
        gravity: float = 0.0,
        glow: bool = True,
    ) -> List[Particle]:
        particles = []
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(speed_min, speed_max)
            particles.append(Particle(
                x=origin_x + random.uniform(-8, 8),
                y=origin_y + random.uniform(-8, 8),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0,
                decay=random.uniform(decay_min, decay_max),
                size=random.uniform(size_min, size_max),
                color=random.choice(colors),
                gravity=gravity,
                glow=glow,
            ))
        return particles

    @staticmethod
    def fountain(
        origin_x: float,
        origin_y: float,
        count: int,
        spread_angle: float,     # half-angle in radians
        direction: float,        # base angle (up = -pi/2)
        speed_min: float,
        speed_max: float,
        colors: List,
        gravity: float = 0.05,
        glow: bool = True,
    ) -> List[Particle]:
        particles = []
        for _ in range(count):
            angle = direction + random.uniform(-spread_angle, spread_angle)
            speed = random.uniform(speed_min, speed_max)
            particles.append(Particle(
                x=origin_x,
                y=origin_y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0,
                decay=random.uniform(0.006, 0.018),
                size=random.uniform(3, 10),
                color=random.choice(colors),
                gravity=gravity,
                glow=glow,
            ))
        return particles

    @staticmethod
    def ring(
        cx: float,
        cy: float,
        radius: float,
        count: int,
        tangent_speed: float,
        colors: List,
        angle_offset: float = 0.0,
        glow: bool = True,
    ) -> List[Particle]:
        particles = []
        for i in range(count):
            a = (i / count) * math.tau + angle_offset
            tang_vx = -math.sin(a) * tangent_speed
            tang_vy =  math.cos(a) * tangent_speed
            particles.append(Particle(
                x=cx + math.cos(a) * radius,
                y=cy + math.sin(a) * radius,
                vx=tang_vx + random.uniform(-0.8, 0.8),
                vy=tang_vy + random.uniform(-0.8, 0.8),
                life=1.0,
                decay=random.uniform(0.005, 0.012),
                size=random.uniform(3, 8),
                color=random.choice(colors),
                glow=glow,
            ))
        return particles

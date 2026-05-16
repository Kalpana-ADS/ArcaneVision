"""
ArcaneVision – Shared Data Types
================================
CRITICAL: All modules import from here to prevent circular imports.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, List, Tuple
import time


# ---------------------------------------------------------------------------
# Spell Enum
# ---------------------------------------------------------------------------

class SpellType(Enum):
    NONE        = auto()
    FAIRY_DUST  = auto()
    FIREBALL    = auto()
    ICE_FREEZE  = auto()
    LIGHTNING   = auto()
    PORTAL      = auto()
    LEVITATION  = auto()
    HEALING     = auto()
    SHADOW      = auto()
    TIME_FREEZE = auto()
    DRAGON      = auto()


# ---------------------------------------------------------------------------
# Gesture Enum
# ---------------------------------------------------------------------------

class GestureType(Enum):
    NONE          = "none"
    OPEN_PALM     = "open_palm"
    CLOSED_FIST   = "closed_fist"
    POINTING      = "pointing"
    PEACE         = "peace"
    THUMBS_UP     = "thumbs_up"
    PINCH         = "pinch"
    SPREAD        = "spread"
    OK_SIGN       = "ok_sign"
    VULCAN        = "vulcan"
    HORNS         = "horns"


# ---------------------------------------------------------------------------
# Landmark / Hand data
# ---------------------------------------------------------------------------

@dataclass
class HandLandmark:
    x: float  # normalized [0, 1]
    y: float
    z: float

    def to_pixel(self, width: int, height: int) -> Tuple[int, int]:
        return int(self.x * width), int(self.y * height)


@dataclass
class HandData:
    landmarks: List[HandLandmark]
    handedness: str          # "Left" or "Right"
    confidence: float
    gesture: GestureType = GestureType.NONE
    wrist_pixel: Tuple[int, int] = (0, 0)
    palm_center_pixel: Tuple[int, int] = (0, 0)
    index_tip_pixel: Tuple[int, int] = (0, 0)
    middle_tip_pixel: Tuple[int, int] = (0, 0)


# ---------------------------------------------------------------------------
# Frame stats (passed around engine → HUD etc.)
# ---------------------------------------------------------------------------

@dataclass
class FrameStats:
    fps: float = 0.0
    frame_time: float = 0.0
    hand_count: int = 0
    active_spell: SpellType = SpellType.NONE
    active_gesture: GestureType = GestureType.NONE
    frame_number: int = 0
    timestamp: float = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# Spell state
# ---------------------------------------------------------------------------

@dataclass
class SpellState:
    spell_type: SpellType = SpellType.NONE
    active: bool = False
    intensity: float = 0.0       # 0.0 – 1.0
    progress: float = 0.0        # lifecycle 0.0 – 1.0
    origin: Tuple[int, int] = (0, 0)
    target: Optional[Tuple[int, int]] = None
    start_time: float = field(default_factory=time.time)
    duration: float = 3.0        # seconds
    color_primary: Tuple[int, int, int] = (255, 255, 255)
    color_secondary: Tuple[int, int, int] = (200, 200, 200)

    def update(self, dt: float) -> None:
        if self.active:
            elapsed = time.time() - self.start_time
            self.progress = min(elapsed / max(self.duration, 0.001), 1.0)
            self.intensity = 1.0 - self.progress

    def is_expired(self) -> bool:
        return self.progress >= 1.0

    def reset(self, origin: Tuple[int, int] = (0, 0)) -> None:
        self.active = True
        self.progress = 0.0
        self.intensity = 1.0
        self.origin = origin
        self.start_time = time.time()


# ---------------------------------------------------------------------------
# Particle
# ---------------------------------------------------------------------------

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float          # remaining life [0, 1]
    decay: float         # per-frame life reduction
    size: float
    color: Tuple[int, int, int]
    alpha: float = 1.0
    gravity: float = 0.0
    rotation: float = 0.0
    rot_speed: float = 0.0
    glow: bool = False


# ---------------------------------------------------------------------------
# Engine config snapshot passed to renderers
# ---------------------------------------------------------------------------

@dataclass
class RenderContext:
    width: int
    height: int
    dt: float
    stats: FrameStats
    spell_state: SpellState
    hands: List[HandData] = field(default_factory=list)
    time_frozen: bool = False

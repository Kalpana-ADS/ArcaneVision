"""
ArcaneVision – Central Configuration
=====================================
All magic numbers live here. No hardcoding in other modules.
"""

from __future__ import annotations
from typing import Dict, Tuple
from src.core.types import SpellType, GestureType


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

WINDOW_TITLE   = "ArcaneVision – HD AR Magical Hand Gesture System"
WINDOW_WIDTH   = 1920
WINDOW_HEIGHT  = 1080
TARGET_FPS     = 60
WEBCAM_INDEX   = 0          # change if your webcam isn't device 0
FLIP_FRAME     = True       # mirror webcam (selfie mode)


# ---------------------------------------------------------------------------
# MediaPipe
# ---------------------------------------------------------------------------

MP_MAX_HANDS           = 2
MP_DETECTION_CONF      = 0.65
MP_TRACKING_CONF       = 0.55
MP_MODEL_COMPLEXITY    = 1


# ---------------------------------------------------------------------------
# Gesture thresholds
# ---------------------------------------------------------------------------

FINGER_BENT_RATIO      = 0.6    # ratio for detecting bent finger
PINCH_DISTANCE_THRESH  = 0.07   # normalised distance for pinch
SPREAD_DISTANCE_THRESH = 0.22   # spread / open palm


# ---------------------------------------------------------------------------
# Gesture → Spell mapping
# ---------------------------------------------------------------------------

GESTURE_SPELL_MAP: Dict[GestureType, SpellType] = {
    GestureType.OPEN_PALM:   SpellType.FAIRY_DUST,
    GestureType.CLOSED_FIST: SpellType.FIREBALL,
    GestureType.PEACE:       SpellType.LIGHTNING,
    GestureType.POINTING:    SpellType.ICE_FREEZE,
    GestureType.PINCH:       SpellType.PORTAL,
    GestureType.SPREAD:      SpellType.LEVITATION,
    GestureType.THUMBS_UP:   SpellType.HEALING,
    GestureType.OK_SIGN:     SpellType.SHADOW,
    GestureType.VULCAN:      SpellType.TIME_FREEZE,
    GestureType.HORNS:       SpellType.DRAGON,
}

# Manual keyboard override: 1-0 keys
KEY_SPELL_MAP: Dict[int, SpellType] = {
    ord('1'): SpellType.FAIRY_DUST,
    ord('2'): SpellType.FIREBALL,
    ord('3'): SpellType.ICE_FREEZE,
    ord('4'): SpellType.LIGHTNING,
    ord('5'): SpellType.PORTAL,
    ord('6'): SpellType.LEVITATION,
    ord('7'): SpellType.HEALING,
    ord('8'): SpellType.SHADOW,
    ord('9'): SpellType.TIME_FREEZE,
    ord('0'): SpellType.DRAGON,
}


# ---------------------------------------------------------------------------
# Spell colours
# ---------------------------------------------------------------------------

SPELL_COLORS: Dict[SpellType, Tuple[Tuple[int,int,int], Tuple[int,int,int]]] = {
    SpellType.FAIRY_DUST:  ((255, 220, 80),  (255, 180, 230)),
    SpellType.FIREBALL:    ((255, 80,  20),  (255, 200, 0)),
    SpellType.ICE_FREEZE:  ((100, 200, 255), (220, 240, 255)),
    SpellType.LIGHTNING:   ((180, 140, 255), (255, 255, 100)),
    SpellType.PORTAL:      ((60,  180, 255), (180, 60,  255)),
    SpellType.LEVITATION:  ((100, 255, 200), (200, 255, 100)),
    SpellType.HEALING:     ((40,  255, 120), (200, 255, 180)),
    SpellType.SHADOW:      ((80,  0,   120), (40,  0,   60)),
    SpellType.TIME_FREEZE: ((180, 220, 255), (100, 160, 220)),
    SpellType.DRAGON:      ((255, 60,  0),   (255, 160, 0)),
    SpellType.NONE:        ((200, 200, 200), (150, 150, 150)),
}

SPELL_NAMES: Dict[SpellType, str] = {
    SpellType.NONE:        "No Spell",
    SpellType.FAIRY_DUST:  "✨ Fairy Dust",
    SpellType.FIREBALL:    "🔥 Fireball",
    SpellType.ICE_FREEZE:  "❄️  Ice Freeze",
    SpellType.LIGHTNING:   "⚡ Lightning",
    SpellType.PORTAL:      "🌀 Portal",
    SpellType.LEVITATION:  "🌬️  Levitation",
    SpellType.HEALING:     "💚 Healing Aura",
    SpellType.SHADOW:      "🌑 Shadow Magic",
    SpellType.TIME_FREEZE: "⏸️  Time Freeze",
    SpellType.DRAGON:      "🐉 Summon Dragon",
}

SPELL_DURATIONS: Dict[SpellType, float] = {
    SpellType.FAIRY_DUST:  4.0,
    SpellType.FIREBALL:    3.0,
    SpellType.ICE_FREEZE:  5.0,
    SpellType.LIGHTNING:   2.5,
    SpellType.PORTAL:      6.0,
    SpellType.LEVITATION:  4.0,
    SpellType.HEALING:     5.0,
    SpellType.SHADOW:      4.0,
    SpellType.TIME_FREEZE: 5.0,
    SpellType.DRAGON:      6.0,
}


# ---------------------------------------------------------------------------
# Particle limits
# ---------------------------------------------------------------------------

MAX_PARTICLES = 5000


# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------

HUD_FONT_SIZE_LARGE  = 40
HUD_FONT_SIZE_MEDIUM = 28
HUD_FONT_SIZE_SMALL  = 20
HUD_PADDING          = 20
HUD_CORNER_RADIUS    = 15
HUD_BG_ALPHA         = 180     # 0-255


# ---------------------------------------------------------------------------
# Sound
# ---------------------------------------------------------------------------

SOUND_ENABLED    = True
SOUND_VOLUME     = 0.6
MUSIC_VOLUME     = 0.25

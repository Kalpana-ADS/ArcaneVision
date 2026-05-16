"""
ArcaneVision – Gesture Recognizer
===================================
Rule-based gesture classification over HandData landmarks.
ML-ready: swap classify() with a model call if desired.
"""

from __future__ import annotations
from typing import List
import math

from src.core.types import HandData, HandLandmark, GestureType
from src.core.config import PINCH_DISTANCE_THRESH, SPREAD_DISTANCE_THRESH
from src.utils.logger import get_logger

log = get_logger(__name__)


# Landmark indices (same as MediaPipe Hands)
WRIST        = 0
THUMB_CMC    = 1
THUMB_MCP    = 2
THUMB_IP     = 3
THUMB_TIP    = 4
INDEX_MCP    = 5
INDEX_PIP    = 6
INDEX_DIP    = 7
INDEX_TIP    = 8
MIDDLE_MCP   = 9
MIDDLE_PIP   = 10
MIDDLE_DIP   = 11
MIDDLE_TIP   = 12
RING_MCP     = 13
RING_PIP     = 14
RING_DIP     = 15
RING_TIP     = 16
PINKY_MCP    = 17
PINKY_PIP    = 18
PINKY_DIP    = 19
PINKY_TIP    = 20


def _dist(a: HandLandmark, b: HandLandmark) -> float:
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


def _finger_extended(lms: List[HandLandmark], tip: int, pip: int, dip: int, mcp: int) -> bool:
    """
    Reliable finger extension detection: tip is further from wrist than both pip and mcp.
    Also checks the y-position hierarchy (tip should be above pip).
    """
    wrist = lms[WRIST]
    tip_lm = lms[tip]
    pip_lm = lms[pip]
    mcp_lm = lms[mcp]
    
    dist_tip_wrist = _dist(tip_lm, wrist)
    dist_pip_wrist = _dist(pip_lm, wrist)
    dist_mcp_wrist = _dist(mcp_lm, wrist)
    
    # For all fingers except thumb: check y position (tip should be higher than pip)
    if tip != THUMB_TIP:
        tip_above_pip = tip_lm.y < pip_lm.y
        tip_further = dist_tip_wrist > dist_pip_wrist
        return tip_above_pip or tip_further
    else:
        # Thumb: check if it's extended from the palm
        return dist_tip_wrist > dist_pip_wrist


def _thumb_extended(lms: List[HandLandmark]) -> bool:
    """Simple thumb extension check using distance from wrist."""
    return _finger_extended(lms, THUMB_TIP, THUMB_IP, THUMB_MCP, THUMB_CMC)


class GestureRecognizer:
    """
    Classifies each HandData's gesture field in-place.
    Returns the most confident gesture across all hands.
    """

    def recognize(self, hands: List[HandData]) -> GestureType:
        """Classify all hands; return dominant gesture."""
        dominant = GestureType.NONE
        for hand in hands:
            g = self._classify(hand)
            hand.gesture = g
            if dominant == GestureType.NONE:
                dominant = g
        return dominant

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def _classify(self, hand: HandData) -> GestureType:
        lms = hand.landmarks
        if len(lms) < 21:
            return GestureType.NONE

        # Finger extension flags (use reliable detection)
        index_ext  = _finger_extended(lms, INDEX_TIP, INDEX_PIP, INDEX_DIP, INDEX_MCP)
        middle_ext = _finger_extended(lms, MIDDLE_TIP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_MCP)
        ring_ext   = _finger_extended(lms, RING_TIP, RING_PIP, RING_DIP, RING_MCP)
        pinky_ext  = _finger_extended(lms, PINKY_TIP, PINKY_PIP, PINKY_DIP, PINKY_MCP)
        thumb_ext  = _thumb_extended(lms)

        ext_count = sum([index_ext, middle_ext, ring_ext, pinky_ext, thumb_ext])

        # Calculate pinch distance first
        pinch_d = _dist(lms[THUMB_TIP], lms[INDEX_TIP])

        # -- Closed fist (0 or 1 fingers extended - very inclusive)
        if ext_count <= 1 and not (index_ext and ext_count == 1):
            return GestureType.CLOSED_FIST

        # -- OK sign (pinch between thumb and index, others extended)
        if pinch_d < PINCH_DISTANCE_THRESH and middle_ext and ring_ext and pinky_ext:
            return GestureType.OK_SIGN

        # -- Pinch (thumb + index close, others don't matter)
        if pinch_d < PINCH_DISTANCE_THRESH:
            return GestureType.PINCH

        # -- Open palm (all extended)
        if ext_count >= 5:
            return GestureType.OPEN_PALM

        # -- Pointing (only index extended - make this very reliable)
        if index_ext and not middle_ext and not ring_ext and not pinky_ext:
            return GestureType.POINTING

        # -- Peace / Victory (index + middle extended, others closed)
        if index_ext and middle_ext and not ring_ext and not pinky_ext:
            return GestureType.PEACE

        # -- Horns / Rock (index + pinky extended)
        if index_ext and not middle_ext and not ring_ext and pinky_ext:
            return GestureType.HORNS

        # -- Spread / Spider-Man (index + pinky + thumb extended)
        if index_ext and pinky_ext and thumb_ext and not middle_ext and not ring_ext:
            if _dist(lms[INDEX_TIP], lms[PINKY_TIP]) > SPREAD_DISTANCE_THRESH:
                return GestureType.SPREAD

        # -- Vulcan salute (index+middle split from ring+pinky)
        if index_ext and middle_ext and ring_ext and pinky_ext and not thumb_ext:
            gap = _dist(lms[MIDDLE_TIP], lms[RING_TIP])
            if gap > 0.07:
                return GestureType.VULCAN

        # -- Thumbs up (only thumb extended, fist otherwise)
        if thumb_ext and not index_ext and not middle_ext and not ring_ext and not pinky_ext:
            return GestureType.THUMBS_UP

        # Default
        return GestureType.NONE

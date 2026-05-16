"""
ArcaneVision – Hand Tracker
============================
Wraps MediaPipe Hands. Returns List[HandData].
"""

from __future__ import annotations
from typing import List, Optional, Tuple
import numpy as np
import mediapipe as mp
import cv2

from src.core.types import HandData, HandLandmark, GestureType
from src.core.config import (
    MP_MAX_HANDS, MP_DETECTION_CONF, MP_TRACKING_CONF, MP_MODEL_COMPLEXITY
)
from src.utils.logger import get_logger

log = get_logger(__name__)


class HandTracker:
    """
    Wraps mediapipe.solutions.hands.Hands.
    Call process(frame_rgb) → List[HandData].
    """

    # MediaPipe landmark indices (reference)
    WRIST        = 0
    THUMB_TIP    = 4
    INDEX_MCP    = 5
    INDEX_PIP    = 6
    INDEX_TIP    = 8
    MIDDLE_MCP   = 9
    MIDDLE_PIP   = 10
    MIDDLE_TIP   = 12
    RING_PIP     = 14
    RING_TIP     = 16
    PINKY_PIP    = 18
    PINKY_TIP    = 20
    THUMB_IP     = 3
    THUMB_MCP    = 2
    THUMB_CMC    = 1

    def __init__(self) -> None:
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MP_MAX_HANDS,
            model_complexity=MP_MODEL_COMPLEXITY,
            min_detection_confidence=MP_DETECTION_CONF,
            min_tracking_confidence=MP_TRACKING_CONF,
        )
        self._mp_drawing = mp.solutions.drawing_utils
        self._mp_drawing_styles = mp.solutions.drawing_styles
        log.info("HandTracker initialised (max_hands=%d)", MP_MAX_HANDS)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(
        self,
        frame_rgb: np.ndarray,
        frame_width: int,
        frame_height: int,
    ) -> List[HandData]:
        """
        Run MediaPipe on an RGB frame.
        Returns a list of HandData (0..max_hands).
        """
        results = self._hands.process(frame_rgb)
        hands: List[HandData] = []

        if not results.multi_hand_landmarks:
            return hands

        handedness_list = results.multi_handedness or []

        for idx, hand_lms in enumerate(results.multi_hand_landmarks):
            # Handedness
            if idx < len(handedness_list):
                label = handedness_list[idx].classification[0].label
                score = handedness_list[idx].classification[0].score
            else:
                label = "Right"
                score = 1.0

            lm_list: List[HandLandmark] = [
                HandLandmark(lm.x, lm.y, lm.z)
                for lm in hand_lms.landmark
            ]

            wrist_px   = lm_list[self.WRIST].to_pixel(frame_width, frame_height)
            index_px   = lm_list[self.INDEX_TIP].to_pixel(frame_width, frame_height)
            middle_px  = lm_list[self.MIDDLE_TIP].to_pixel(frame_width, frame_height)
            palm_px    = self._palm_center(lm_list, frame_width, frame_height)

            hand = HandData(
                landmarks=lm_list,
                handedness=label,
                confidence=score,
                gesture=GestureType.NONE,
                wrist_pixel=wrist_px,
                palm_center_pixel=palm_px,
                index_tip_pixel=index_px,
                middle_tip_pixel=middle_px,
            )
            hands.append(hand)

        return hands

    def draw_landmarks(self, frame_bgr: np.ndarray, hands: List[HandData]) -> np.ndarray:
        """
        Draw mediapipe skeleton on the BGR frame (for debug overlay).
        This rebuilds a lightweight version without re-running inference.
        """
        overlay = frame_bgr.copy()
        h, w = frame_bgr.shape[:2]

        for hand in hands:
            # Draw connections
            connections = self._mp_hands.HAND_CONNECTIONS
            lms = hand.landmarks
            for conn in connections:
                start = lms[conn[0]].to_pixel(w, h)
                end   = lms[conn[1]].to_pixel(w, h)
                cv2.line(overlay, start, end, (80, 200, 120), 1, cv2.LINE_AA)

            # Draw joints
            for lm in lms:
                px = lm.to_pixel(w, h)
                cv2.circle(overlay, px, 3, (255, 255, 255), -1, cv2.LINE_AA)

        return overlay

    def close(self) -> None:
        self._hands.close()
        log.info("HandTracker closed")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _palm_center(
        self,
        lms: List[HandLandmark],
        w: int,
        h: int,
    ) -> Tuple[int, int]:
        """Average of WRIST + 4 MCP joints → approximate palm centre."""
        palm_ids = [0, 5, 9, 13, 17]
        xs = [lms[i].x for i in palm_ids]
        ys = [lms[i].y for i in palm_ids]
        return int(np.mean(xs) * w), int(np.mean(ys) * h)

"""
ArcaneVision – Renderer
=========================
Composites webcam + spell overlays onto Pygame surface.
"""

from __future__ import annotations
import numpy as np
import pygame
import cv2

from src.core.types import RenderContext


class Renderer:
    """
    Converts an OpenCV BGR numpy frame to a Pygame surface and blits it.
    Also provides utility for additive / alpha overlays.
    """

    def __init__(self, surface: pygame.Surface) -> None:
        self._surface = surface
        self._w, self._h = surface.get_size()

    def blit_cv_frame(self, frame: np.ndarray) -> None:
        """Convert BGR frame → RGB Pygame surface with HD interpolation and blit to display."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Resize to display dimensions with high-quality interpolation
        if frame_rgb.shape[1] != self._w or frame_rgb.shape[0] != self._h:
            frame_rgb = cv2.resize(frame_rgb, (self._w, self._h), interpolation=cv2.INTER_LANCZOS4)
        pg_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        self._surface.blit(pg_surface, (0, 0))

    def draw_hand_skeleton(
        self,
        frame: np.ndarray,
        hand_data_list: list,
    ) -> np.ndarray:
        """Thin wrapper kept here for possible future GPU texture work."""
        return frame

    @property
    def surface(self) -> pygame.Surface:
        return self._surface

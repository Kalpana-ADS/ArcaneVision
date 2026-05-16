"""
ArcaneVision – Engine
======================
Central game loop: webcam → tracking → gesture → spell → render → HUD.
"""

from __future__ import annotations
import time
import sys
from collections import deque
from typing import Dict, Optional

import cv2
import numpy as np
import pygame

from src.core.types import (
    FrameStats, SpellState, SpellType, RenderContext, GestureType,
)
from src.core.config import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, TARGET_FPS,
    WEBCAM_INDEX, FLIP_FRAME,
    KEY_SPELL_MAP, GESTURE_SPELL_MAP,
    SPELL_COLORS, SPELL_DURATIONS,
    SOUND_ENABLED, SOUND_VOLUME,
)
from src.gestures.hand_tracker       import HandTracker
from src.gestures.gesture_recognizer import GestureRecognizer
from src.effects.renderer            import Renderer
from src.ui.hud                      import HUD
from src.utils.logger                import get_logger

# Spell imports
from src.spells.fairy_spell      import FairySpell
from src.spells.fire_spell       import FireSpell
from src.spells.ice_spell        import IceSpell
from src.spells.lightning_spell  import LightningSpell
from src.spells.portal_spell     import PortalSpell
from src.spells.levitation_spell import LevitationSpell
from src.spells.healing_spell    import HealingSpell
from src.spells.shadow_spell     import ShadowSpell
from src.spells.time_spell       import TimeSpell
from src.spells.dragon_spell     import DragonSpell

log = get_logger(__name__)


class Engine:
    """
    Orchestrates the entire ArcaneVision application.
    Owns the main loop, webcam, Pygame window, and all subsystems.
    """

    def __init__(self) -> None:
        log.info("Initialising ArcaneVision Engine …")

        # --- Pygame ---
        pygame.init()
        self._screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE
        )
        pygame.display.set_caption(WINDOW_TITLE)
        self._clock  = pygame.time.Clock()

        # --- Sound ---
        if SOUND_ENABLED:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self._sound_enabled = True
            except Exception as e:
                log.warning("pygame.mixer failed: %s – sound disabled", e)
                self._sound_enabled = False
        else:
            self._sound_enabled = False

        # --- Webcam ---
        self._cap = cv2.VideoCapture(WEBCAM_INDEX)
        if not self._cap.isOpened():
            log.error("Cannot open webcam index %d", WEBCAM_INDEX)
            raise RuntimeError(f"Webcam {WEBCAM_INDEX} not available.")
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH,  WINDOW_WIDTH)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)
        self._cap.set(cv2.CAP_PROP_FPS,          TARGET_FPS)
        log.info("Webcam opened")

        # --- Sub-systems ---
        self._tracker    = HandTracker()
        self._recognizer = GestureRecognizer()
        self._renderer   = Renderer(self._screen)
        self._hud        = HUD(WINDOW_WIDTH, WINDOW_HEIGHT)

        # --- Spells registry ---
        self._spells: Dict[SpellType, object] = {
            SpellType.FAIRY_DUST:  FairySpell(),
            SpellType.FIREBALL:    FireSpell(),
            SpellType.ICE_FREEZE:  IceSpell(),
            SpellType.LIGHTNING:   LightningSpell(),
            SpellType.PORTAL:      PortalSpell(),
            SpellType.LEVITATION:  LevitationSpell(),
            SpellType.HEALING:     HealingSpell(),
            SpellType.SHADOW:      ShadowSpell(),
            SpellType.TIME_FREEZE: TimeSpell(),
            SpellType.DRAGON:      DragonSpell(),
        }
        self._active_spell: Optional[SpellType] = None

        # --- Frame stats ---
        self._stats      = FrameStats()
        self._fps_buf    = deque(maxlen=30)
        self._prev_time  = time.perf_counter()
        self._frame_num  = 0
        self._debug_mode = False

        # --- Gesture hold timer (gesture must hold 0.5s to fire) ---
        self._gesture_hold: Dict[GestureType, float] = {}
        self._hold_threshold = 0.4   # seconds

        log.info("Engine ready.")

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        log.info("Starting main loop …")
        running = True

        while running:
            # Δt
            now = time.perf_counter()
            dt  = now - self._prev_time
            self._prev_time = now
            dt  = min(dt, 0.05)   # clamp to 50 ms to avoid physics explosions

            # --- Events ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_d:
                        self._debug_mode = not self._debug_mode
                        log.info("Debug mode: %s", self._debug_mode)
                    else:
                        k = event.key
                        if k in KEY_SPELL_MAP:
                            self._trigger_spell(KEY_SPELL_MAP[k], None)

            # --- Webcam ---
            ret, frame_bgr = self._cap.read()
            if not ret:
                log.warning("Webcam frame read failed – skipping")
                continue

            if FLIP_FRAME:
                frame_bgr = cv2.flip(frame_bgr, 1)

            h, w = frame_bgr.shape[:2]
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

            # --- Hand tracking ---
            hands = self._tracker.process(frame_rgb, w, h)

            # --- Gesture recognition + auto-spell fire ---
            gesture = self._recognizer.recognize(hands)
            self._process_gesture(gesture, hands, dt)

            # --- Build render context ---
            ctx = RenderContext(
                width=w, height=h, dt=dt,
                stats=self._stats,
                spell_state=SpellState(
                    spell_type=self._active_spell or SpellType.NONE,
                    active=self._active_spell is not None,
                ),
                hands=hands,
                time_frozen=self._active_spell == SpellType.TIME_FREEZE,
            )

            # --- Update & render active spell ---
            if self._active_spell is not None:
                spell_obj = self._spells[self._active_spell]
                spell_obj.update(dt, ctx)
                spell_obj.render(frame_bgr, ctx)
                if not spell_obj.active:
                    log.debug("Spell %s expired", self._active_spell)
                    self._active_spell = None

            # --- Debug skeleton overlay ---
            if self._debug_mode:
                frame_bgr = self._tracker.draw_landmarks(frame_bgr, hands)

            # --- HUD ---
            self._update_stats(hands, gesture, dt)
            self._hud.render(frame_bgr, self._stats, dt)

            # --- Blit to screen ---
            self._renderer.blit_cv_frame(frame_bgr)
            pygame.display.flip()
            self._clock.tick(TARGET_FPS)
            self._frame_num += 1

        self._shutdown()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _process_gesture(self, gesture: GestureType, hands, dt: float) -> None:
        """Hold-fire: gesture must be held for _hold_threshold seconds."""
        if gesture == GestureType.NONE or gesture not in GESTURE_SPELL_MAP:
            self._gesture_hold.clear()
            return

        held = self._gesture_hold.get(gesture, 0.0) + dt
        self._gesture_hold[gesture] = held

        # Clear other gestures
        for g in list(self._gesture_hold.keys()):
            if g != gesture:
                del self._gesture_hold[g]

        if held >= self._hold_threshold and self._active_spell is None:
            origin = hands[0].palm_center_pixel if hands else (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            self._trigger_spell(GESTURE_SPELL_MAP[gesture], origin)
            self._gesture_hold.clear()

    def _trigger_spell(self, spell_type: SpellType, origin) -> None:
        """Fire a spell, deactivating any current one first."""
        # Deactivate previous
        if self._active_spell and self._active_spell in self._spells:
            self._spells[self._active_spell].deactivate()

        self._active_spell = spell_type
        spell_obj = self._spells[spell_type]
        c_pri, c_sec = SPELL_COLORS.get(spell_type, ((255, 255, 255), (200, 200, 200)))
        spell_obj.state.spell_type     = spell_type
        spell_obj.state.duration       = SPELL_DURATIONS.get(spell_type, 4.0)
        spell_obj.state.color_primary  = c_pri
        spell_obj.state.color_secondary = c_sec

        dummy_ctx = RenderContext(
            width=WINDOW_WIDTH, height=WINDOW_HEIGHT, dt=0,
            stats=self._stats,
            spell_state=spell_obj.state,
            hands=[],
        )
        if origin:
            spell_obj.state.origin = origin
        spell_obj.activate(dummy_ctx)
        log.info("Spell triggered: %s", spell_type)

    def _update_stats(self, hands, gesture, dt: float) -> None:
        self._fps_buf.append(1.0 / max(dt, 1e-6))
        self._stats.fps           = sum(self._fps_buf) / len(self._fps_buf)
        self._stats.frame_time    = dt * 1000
        self._stats.hand_count    = len(hands)
        self._stats.active_spell  = self._active_spell or SpellType.NONE
        self._stats.active_gesture = gesture
        self._stats.frame_number  = self._frame_num

    def _shutdown(self) -> None:
        log.info("Shutting down …")
        self._tracker.close()
        self._cap.release()
        if self._sound_enabled:
            pygame.mixer.quit()
        pygame.quit()
        log.info("Goodbye!")

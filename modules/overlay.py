"""OpenCV HUD overlay drawing for GesturePilot (Tasks API — no mp.solutions)."""

from typing import List, Optional

import cv2
import numpy as np

from config import SHOW_FPS, SHOW_LANDMARKS
from modules.hand_detector import (
    HAND_CONNECTIONS,
    INDEX_TIP,
    THUMB_TIP,
    MIDDLE_TIP,
)


class Overlay:
    """Draws landmarks, gesture indicators, and HUD panels onto OpenCV frames."""

    def draw(
        self,
        frame: np.ndarray,
        landmarks: Optional[List],
        gesture_name: str,
        left_pinch_dist: float,
        right_pinch_dist: float,
        left_pinch_active: bool,
        right_pinch_active: bool,
        fps: float,
        frame_w: int,
        frame_h: int,
    ) -> np.ndarray:
        """Composite all HUD elements onto the frame in-place.

        Args:
            frame: BGR OpenCV frame.
            landmarks: List of 21 NormalizedLandmark objects, or None.
            gesture_name: Human-readable gesture label for the HUD.
            left_pinch_dist: Pixel distance between index and thumb tips.
            right_pinch_dist: Pixel distance between middle and thumb tips.
            left_pinch_active: Whether left pinch is currently active.
            right_pinch_active: Whether right pinch is currently active.
            fps: Current frames per second.
            frame_w: Frame width.
            frame_h: Frame height.

        Returns:
            The annotated BGR frame (same object, modified in-place).
        """
        try:
            if landmarks is not None:
                if SHOW_LANDMARKS:
                    self._draw_skeleton(frame, landmarks, frame_w, frame_h)
                self._draw_fingertip_circles(
                    frame, landmarks, frame_w, frame_h,
                    left_pinch_active, right_pinch_active,
                )
            self._draw_hud_panel(frame, gesture_name, left_pinch_dist, right_pinch_dist)
            if SHOW_FPS:
                self._draw_fps(frame, fps, frame_w)
            self._draw_bottom_bar(frame, frame_h)
        except Exception:
            pass
        return frame

    def _draw_skeleton(
        self,
        frame: np.ndarray,
        landmarks: List,
        frame_w: int,
        frame_h: int,
    ) -> None:
        """Render skeleton connections and landmark dots manually."""
        pts = [
            (int(lm.x * frame_w), int(lm.y * frame_h))
            for lm in landmarks
        ]
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, pts[a], pts[b], (173, 216, 230), 1, cv2.LINE_AA)
        for pt in pts:
            cv2.circle(frame, pt, 4, (255, 255, 255), -1)
            cv2.circle(frame, pt, 4, (0, 0, 255), 1)

    def _draw_fingertip_circles(
        self,
        frame: np.ndarray,
        landmarks: List,
        frame_w: int,
        frame_h: int,
        left_pinch_active: bool,
        right_pinch_active: bool,
    ) -> None:
        """Draw colored circles and pinch line indicators on fingertips."""
        def lm_px(idx):
            lm = landmarks[idx]
            return int(lm.x * frame_w), int(lm.y * frame_h)

        idx_pt = lm_px(INDEX_TIP)
        thumb_pt = lm_px(THUMB_TIP)
        mid_pt = lm_px(MIDDLE_TIP)

        if left_pinch_active:
            cv2.line(frame, idx_pt, thumb_pt, (0, 255, 0), 2)
            cv2.circle(frame, idx_pt, 10, (0, 255, 0), -1)
            cv2.circle(frame, thumb_pt, 10, (0, 255, 0), -1)
        else:
            cv2.circle(frame, idx_pt, 10, (255, 0, 0), -1)
            cv2.circle(frame, idx_pt, 10, (0, 0, 255), 2)
            cv2.circle(frame, thumb_pt, 10, (0, 255, 255), -1)
            cv2.circle(frame, thumb_pt, 10, (0, 0, 255), 2)

        if right_pinch_active:
            cv2.line(frame, mid_pt, thumb_pt, (0, 165, 255), 2)
            cv2.circle(frame, mid_pt, 8, (0, 165, 255), -1)

    def _draw_hud_panel(
        self,
        frame: np.ndarray,
        gesture_name: str,
        left_dist: float,
        right_dist: float,
    ) -> None:
        """Draw a semi-transparent dark panel in the top-left corner."""
        panel = frame.copy()
        cv2.rectangle(panel, (5, 5), (280, 75), (20, 20, 20), -1)
        cv2.addWeighted(panel, 0.6, frame, 0.4, 0, frame)

        cv2.putText(
            frame, gesture_name,
            (12, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
            (255, 255, 255), 2, cv2.LINE_AA,
        )
        dist_text = f"L: {int(left_dist)}px  R: {int(right_dist)}px"
        cv2.putText(
            frame, dist_text,
            (12, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
            (180, 180, 180), 1, cv2.LINE_AA,
        )

    def _draw_fps(self, frame: np.ndarray, fps: float, frame_w: int) -> None:
        """Render FPS counter in the top-right corner."""
        text = f"FPS: {int(fps)}"
        (tw, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.putText(
            frame, text,
            (frame_w - tw - 10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
            (255, 255, 255), 1, cv2.LINE_AA,
        )

    def _draw_bottom_bar(self, frame: np.ndarray, frame_h: int) -> None:
        """Draw instruction text along the bottom of the frame."""
        cv2.putText(
            frame,
            "Q = quit  |  Move index finger = cursor  |  Pinch = click",
            (8, frame_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
            (160, 160, 160), 1, cv2.LINE_AA,
        )

"""Gesture detection logic: pinch, scroll, cursor mapping."""

import math
from typing import List, Optional, Tuple

import numpy as np

from config import (
    PINCH_THRESHOLD,
    PINCH_RELEASE_THRESHOLD,
    SCROLL_DEADZONE,
)
from modules.hand_detector import (
    INDEX_TIP,
    MIDDLE_TIP,
    RING_TIP,
    PINKY_TIP,
    INDEX_MCP,
    MIDDLE_MCP,
    RING_MCP,
    PINKY_MCP,
)


class GestureRecognizer:
    """Stateless gesture recognition helper — all methods are pure functions."""

    def get_cursor_position(
        self,
        landmarks: List,
        frame_w: int,
        frame_h: int,
        screen_w: int,
        screen_h: int,
    ) -> Tuple[int, int]:
        """Map index fingertip normalized coords to screen pixel coordinates.

        X is mirrored so the cursor moves in the natural direction.

        Args:
            landmarks: List of 21 NormalizedLandmark objects.
            frame_w: Camera frame width in pixels.
            frame_h: Camera frame height in pixels.
            screen_w: Display width in pixels.
            screen_h: Display height in pixels.

        Returns:
            (screen_x, screen_y) as integers clamped to screen bounds.
        """
        lm = landmarks[INDEX_TIP]
        mapped_x = int(lm.x * screen_w)
        mapped_y = int(lm.y * screen_h)
        mapped_x = max(0, min(screen_w - 1, mapped_x))
        mapped_y = max(0, min(screen_h - 1, mapped_y))
        return mapped_x, mapped_y

    def _tip_distance_px(
        self,
        landmarks: List,
        frame_w: int,
        frame_h: int,
        tip_a: int,
        tip_b: int,
    ) -> float:
        """Calculate Euclidean distance between two landmark tips in pixel space."""
        lm_a = landmarks[tip_a]
        lm_b = landmarks[tip_b]
        dx = (lm_a.x - lm_b.x) * frame_w
        dy = (lm_a.y - lm_b.y) * frame_h
        return math.hypot(dx, dy)

    def is_pinching(
        self,
        landmarks: List,
        frame_w: int,
        frame_h: int,
        tip_a: int,
        tip_b: int,
    ) -> bool:
        """Return True when the distance between two tips is below PINCH_THRESHOLD.

        Args:
            landmarks: List of 21 NormalizedLandmark objects.
            frame_w: Camera frame width.
            frame_h: Camera frame height.
            tip_a: Landmark index of the first fingertip.
            tip_b: Landmark index of the second fingertip.
        """
        return self._tip_distance_px(landmarks, frame_w, frame_h, tip_a, tip_b) < PINCH_THRESHOLD

    def is_releasing(
        self,
        landmarks: List,
        frame_w: int,
        frame_h: int,
        tip_a: int,
        tip_b: int,
    ) -> bool:
        """Return True when the distance between two tips exceeds PINCH_RELEASE_THRESHOLD.

        Hysteresis prevents rapid on/off flapping near the threshold boundary.

        Args:
            landmarks: List of 21 NormalizedLandmark objects.
            frame_w: Camera frame width.
            frame_h: Camera frame height.
            tip_a: Landmark index of the first fingertip.
            tip_b: Landmark index of the second fingertip.
        """
        return self._tip_distance_px(landmarks, frame_w, frame_h, tip_a, tip_b) > PINCH_RELEASE_THRESHOLD

    def get_pinch_distance(
        self,
        landmarks: List,
        frame_w: int,
        frame_h: int,
        tip_a: int,
        tip_b: int,
    ) -> float:
        """Return the raw pixel distance between two tips (for HUD display)."""
        return self._tip_distance_px(landmarks, frame_w, frame_h, tip_a, tip_b)

    def is_scroll_mode(self, landmarks: List, frame_h: int) -> bool:
        """Return True when all four fingers are fully extended.

        A finger is considered extended when its tip y-coordinate is above
        (smaller than) its MCP (knuckle) y-coordinate in the frame.

        Args:
            landmarks: List of 21 NormalizedLandmark objects.
            frame_h: Camera frame height (unused but kept for API consistency).
        """
        fingers = [
            (INDEX_TIP, INDEX_MCP),
            (MIDDLE_TIP, MIDDLE_MCP),
            (RING_TIP, RING_MCP),
            (PINKY_TIP, PINKY_MCP),
        ]
        return all(landmarks[tip].y < landmarks[mcp].y for tip, mcp in fingers)

    def get_scroll_direction(
        self, current_wrist_y: float, previous_wrist_y: float
    ) -> int:
        """Determine scroll direction from wrist y-delta.

        Args:
            current_wrist_y: Current wrist y in normalized coords scaled to px.
            previous_wrist_y: Previous wrist y value.

        Returns:
            1 for scroll up, -1 for scroll down, 0 for no scroll.
        """
        diff = current_wrist_y - previous_wrist_y
        if diff > SCROLL_DEADZONE:
            return -1
        if diff < -SCROLL_DEADZONE:
            return 1
        return 0

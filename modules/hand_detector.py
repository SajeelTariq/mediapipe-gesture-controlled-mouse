"""MediaPipe hand detection wrapper — uses the Tasks API (mediapipe >= 0.10)."""

import time
from typing import List, Optional

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import numpy as np


# Landmark index constants (same 21-point model)
WRIST = 0
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20
INDEX_MCP = 5
MIDDLE_MCP = 9
RING_MCP = 13
PINKY_MCP = 17

# Hand skeleton connections for manual drawing
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),          # index
    (5, 9), (9, 10), (10, 11), (11, 12),     # middle
    (9, 13), (13, 14), (14, 15), (15, 16),   # ring
    (13, 17), (17, 18), (18, 19), (19, 20),  # pinky
    (0, 17),                                  # palm base
]


class HandDetector:
    """Wraps the MediaPipe Tasks HandLandmarker in VIDEO mode for real-time tracking."""

    def __init__(self, model_path: str = "hand_landmarker.task") -> None:
        """Initialize the HandLandmarker in VIDEO running mode.

        VIDEO mode uses inter-frame temporal context, giving significantly
        better tracking than single-IMAGE mode for live webcam feeds.

        Args:
            model_path: Path to the hand_landmarker.task model asset.
        """
        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._detector = mp_vision.HandLandmarker.create_from_options(options)
        self._start_time_ms: int = int(time.time() * 1000)

    def detect(self, frame: np.ndarray) -> Optional[List]:
        """Detect hand landmarks in an RGB frame using the video timestamp.

        Args:
            frame: RGB image as a NumPy uint8 array.

        Returns:
            List of 21 NormalizedLandmark objects if a hand is found, else None.
        """
        timestamp_ms = int(time.time() * 1000) - self._start_time_ms
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = self._detector.detect_for_video(mp_image, timestamp_ms)
        if result.hand_landmarks:
            return result.hand_landmarks[0]
        return None

    def close(self) -> None:
        """Release detector resources."""
        self._detector.close()

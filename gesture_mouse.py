"""GesturePilot — main entry point."""

import os
import time
import urllib.request
from typing import Optional

import cv2
import pyautogui

_MODEL_PATH = "hand_landmarker.task"
_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)


def _ensure_model() -> None:
    """Download the MediaPipe hand landmark model if not already present."""
    if not os.path.exists(_MODEL_PATH):
        print(f"Downloading hand landmark model to '{_MODEL_PATH}'...")
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
        print("Model downloaded.")

from config import (
    CAMERA_INDEX,
    COUNTDOWN_SECONDS,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    HOLD_DURATION,
)
from modules.gesture_recognizer import GestureRecognizer
from modules.hand_detector import HandDetector, THUMB_TIP, INDEX_TIP, MIDDLE_TIP, WRIST
from modules.mouse_controller import MouseController
from modules.overlay import Overlay

_BANNER = r"""
  ____           _                    ____  _ _       _
 / ___| ___  ___| |_ _   _ _ __ ___  |  _ \(_) | ___ | |_
| |  _ / _ \/ __| __| | | | '__/ _ \ | |_) | | |/ _ \| __|
| |_| |  __/\__ \ |_| |_| | | |  __/ |  __/| | | (_) | |_
 \____|\___||___/\__|\__,_|_|  \___| |_|   |_|_|\___/ \__|

  Gesture Controlled Mouse  v1.0
"""


def _countdown(seconds: int) -> None:
    """Print a blocking countdown to the terminal."""
    for i in range(seconds, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)


def main() -> None:
    """Run the GesturePilot gesture-controlled mouse application."""
    print(_BANNER)
    _ensure_model()
    print("Initializing camera...")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("ERROR: Could not open camera. Check CAMERA_INDEX in config.py.")
        return

    _countdown(COUNTDOWN_SECONDS)

    hand_detector = HandDetector(model_path=_MODEL_PATH)
    gesture_recognizer = GestureRecognizer()
    mouse_controller = MouseController()
    overlay = Overlay()

    screen_w, screen_h = pyautogui.size()

    # State tracking
    left_pinch_state: bool = False
    left_hold_active: bool = False
    left_pinch_start_time: Optional[float] = None

    right_pinch_state: bool = False
    right_hold_active: bool = False
    right_pinch_start_time: Optional[float] = None

    prev_wrist_y: float = 0.0
    gesture_name: str = "NO HAND"

    fps: float = 0.0
    prev_tick: float = time.time()

    print("GesturePilot running. Press Q in the camera window to quit.\n")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("WARNING: Failed to read frame.")
                continue

            frame = cv2.flip(frame, 1)
            frame_h, frame_w = frame.shape[:2]

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            landmarks = hand_detector.detect(rgb_frame)

            left_dist: float = 0.0
            right_dist: float = 0.0

            if landmarks is not None:
                # --- Cursor movement ---
                cx, cy = gesture_recognizer.get_cursor_position(
                    landmarks, frame_w, frame_h, screen_w, screen_h
                )
                mouse_controller.move(cx, cy)
                gesture_name = "MOVING"

                # --- Pinch distances for HUD ---
                left_dist = gesture_recognizer.get_pinch_distance(
                    landmarks, frame_w, frame_h, INDEX_TIP, THUMB_TIP
                )
                right_dist = gesture_recognizer.get_pinch_distance(
                    landmarks, frame_w, frame_h, MIDDLE_TIP, THUMB_TIP
                )

                # --- Left pinch (index + thumb) ---
                now = time.time()
                pinching_left = gesture_recognizer.is_pinching(
                    landmarks, frame_w, frame_h, INDEX_TIP, THUMB_TIP
                )
                releasing_left = gesture_recognizer.is_releasing(
                    landmarks, frame_w, frame_h, INDEX_TIP, THUMB_TIP
                )

                if pinching_left:
                    if not left_pinch_state:
                        # Newly entered pinch
                        left_pinch_state = True
                        left_pinch_start_time = now
                    else:
                        elapsed = now - (left_pinch_start_time or now)
                        if elapsed >= HOLD_DURATION and not left_hold_active:
                            left_hold_active = True
                            mouse_controller.mouse_down()
                            gesture_name = "LEFT HOLD"
                        elif left_hold_active:
                            gesture_name = "LEFT HOLD"
                        else:
                            gesture_name = "LEFT CLICK"
                elif releasing_left and left_pinch_state:
                    if left_hold_active:
                        mouse_controller.mouse_up()
                        left_hold_active = False
                    else:
                        mouse_controller.left_click()
                        gesture_name = "LEFT CLICK"
                    left_pinch_state = False
                    left_pinch_start_time = None

                # --- Right pinch (middle + thumb) ---
                pinching_right = gesture_recognizer.is_pinching(
                    landmarks, frame_w, frame_h, MIDDLE_TIP, THUMB_TIP
                )
                releasing_right = gesture_recognizer.is_releasing(
                    landmarks, frame_w, frame_h, MIDDLE_TIP, THUMB_TIP
                )

                if pinching_right:
                    if not right_pinch_state:
                        right_pinch_state = True
                        right_pinch_start_time = now
                    else:
                        elapsed = now - (right_pinch_start_time or now)
                        if elapsed >= HOLD_DURATION and not right_hold_active:
                            right_hold_active = True
                            gesture_name = "RIGHT HOLD"
                        elif right_hold_active:
                            gesture_name = "RIGHT HOLD"
                        else:
                            gesture_name = "RIGHT CLICK"
                elif releasing_right and right_pinch_state:
                    if right_hold_active:
                        right_hold_active = False
                    else:
                        mouse_controller.right_click()
                        gesture_name = "RIGHT CLICK"
                    right_pinch_state = False
                    right_pinch_start_time = None

                # --- Scroll mode (all four fingers extended) ---
                if gesture_recognizer.is_scroll_mode(landmarks, frame_h):
                    wrist_y = landmarks[WRIST].y * frame_h
                    direction = gesture_recognizer.get_scroll_direction(wrist_y, prev_wrist_y)
                    mouse_controller.scroll(direction)
                    prev_wrist_y = wrist_y
                    gesture_name = "SCROLLING"
                else:
                    prev_wrist_y = landmarks[WRIST].y * frame_h

            else:
                gesture_name = "NO HAND"
                # Release any held button if hand disappears
                if left_hold_active:
                    mouse_controller.mouse_up()
                    left_hold_active = False
                left_pinch_state = False
                right_pinch_state = False
                right_hold_active = False

            # --- FPS calculation ---
            now_tick = time.time()
            elapsed_tick = now_tick - prev_tick
            fps = 1.0 / elapsed_tick if elapsed_tick > 0 else fps
            prev_tick = now_tick

            # --- Overlay ---
            frame = overlay.draw(
                frame,
                landmarks,
                gesture_name,
                left_dist,
                right_dist,
                left_pinch_state,
                right_pinch_state,
                fps,
                frame_w,
                frame_h,
            )

            cv2.imshow("GesturePilot — Press Q to quit", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        pass
    finally:
        if left_hold_active:
            mouse_controller.mouse_up()
        cap.release()
        cv2.destroyAllWindows()
        hand_detector.close()
        print("GesturePilot closed.")


if __name__ == "__main__":
    main()

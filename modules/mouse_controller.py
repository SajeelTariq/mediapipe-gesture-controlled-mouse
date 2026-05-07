"""PyAutoGUI wrapper with smoothing and click cooldown enforcement."""

import time
from collections import deque
from typing import Deque

import numpy as np
import pyautogui

from config import CLICK_COOLDOWN, SCROLL_SPEED, SMOOTHING_BUFFER


class MouseController:
    """Controls the system mouse with position smoothing and click rate limiting."""

    def __init__(self) -> None:
        """Initialize buffers, cooldown state, and PyAutoGUI settings."""
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0

        self._buf_x: Deque[float] = deque(maxlen=SMOOTHING_BUFFER)
        self._buf_y: Deque[float] = deque(maxlen=SMOOTHING_BUFFER)
        self._last_click_time: float = 0.0

    def smooth(self, x: int, y: int) -> tuple:
        """Append new position to buffers and return the rolling mean.

        Args:
            x: Raw screen x coordinate.
            y: Raw screen y coordinate.

        Returns:
            (smoothed_x, smoothed_y) as integers.
        """
        self._buf_x.append(x)
        self._buf_y.append(y)
        return int(np.mean(self._buf_x)), int(np.mean(self._buf_y))

    def move(self, x: int, y: int) -> None:
        """Smooth the position then move the cursor instantly.

        Args:
            x: Target screen x coordinate.
            y: Target screen y coordinate.
        """
        sx, sy = self.smooth(x, y)
        pyautogui.moveTo(sx, sy, duration=0)

    def _cooldown_ok(self) -> bool:
        """Return True if enough time has elapsed since the last click."""
        return (time.time() - self._last_click_time) >= CLICK_COOLDOWN

    def _record_click(self) -> None:
        self._last_click_time = time.time()

    def left_click(self) -> None:
        """Fire a left click if the cooldown period has elapsed."""
        if self._cooldown_ok():
            pyautogui.click()
            self._record_click()

    def right_click(self) -> None:
        """Fire a right click if the cooldown period has elapsed."""
        if self._cooldown_ok():
            pyautogui.rightClick()
            self._record_click()

    def mouse_down(self) -> None:
        """Press and hold the left mouse button."""
        pyautogui.mouseDown()

    def mouse_up(self) -> None:
        """Release the left mouse button."""
        pyautogui.mouseUp()

    def scroll(self, direction: int) -> None:
        """Scroll the mouse wheel.

        Args:
            direction: 1 for up, -1 for down, 0 for no-op.
        """
        if direction != 0:
            pyautogui.scroll(direction * SCROLL_SPEED)

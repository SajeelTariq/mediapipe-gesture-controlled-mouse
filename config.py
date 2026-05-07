# Pinch detection
PINCH_THRESHOLD = 10          # px — distance to trigger pinch (fingertips must touch)
PINCH_RELEASE_THRESHOLD = 35  # px — hysteresis to prevent flapping

# Cursor sensitivity
# 1.0 = hand must move full frame width to cross full screen
# 1.5 = default — small movements cover more screen real estate
# 2.0 = very sensitive, tiny hand movements move cursor far
CURSOR_SENSITIVITY = 5

# Smoothing
SMOOTHING_BUFFER = 5          # number of frames to average cursor position

# Timing
CLICK_COOLDOWN = 0.8          # seconds between single clicks
HOLD_DURATION = 0.8           # seconds of pinch before triggering hold/drag

# Scroll
SCROLL_SPEED = 3              # pyautogui scroll units per frame
SCROLL_DEADZONE = 10          # px vertical movement needed to trigger scroll

# Camera
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# UI
SHOW_LANDMARKS = True
SHOW_FPS = True
COUNTDOWN_SECONDS = 3

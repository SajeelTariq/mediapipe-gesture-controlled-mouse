# Pinch detection
PINCH_THRESHOLD = 40          # px — distance to trigger pinch
PINCH_RELEASE_THRESHOLD = 55  # px — hysteresis to prevent flapping

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

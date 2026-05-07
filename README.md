# GesturePilot — Gesture Controlled Mouse

Control your computer mouse using only hand gestures captured through your webcam — no physical mouse required.

## Demo

> Add GIF or screenshot here

## Features

- Real-time cursor movement via index fingertip
- Left click, right click, click-and-hold, drag support
- Scroll up/down with open palm gesture
- Smooth cursor movement with jitter reduction
- Live HUD overlay showing active gesture and pinch distances
- Zero-config startup — just run and go

## Gesture Reference

| Gesture | Action |
|---|---|
| Move index fingertip | Move cursor |
| Index + thumb pinch (quick) | Left click |
| Index + thumb pinch (hold >0.8s) | Left click hold / drag |
| Middle + thumb pinch (quick) | Right click |
| Middle + thumb pinch (hold >0.8s) | Right click hold |
| All 4 fingers up + hand moves up/down | Scroll up / down |

## Project Structure

```
mediapipe-gesture-controlled-mouse/
│
├── gesture_mouse.py          # Main entry point
├── config.py                 # All tunable constants
├── modules/
│   ├── __init__.py
│   ├── hand_detector.py      # MediaPipe hand detection wrapper
│   ├── gesture_recognizer.py # Pinch, hold, scroll logic
│   ├── mouse_controller.py   # PyAutoGUI wrapper + smoothing
│   └── overlay.py            # OpenCV HUD overlay
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.8 or higher
- Webcam
- Good lighting (works best in well-lit environments)
- Keep hand 30–60 cm from camera

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/mediapipe-gesture-controlled-mouse.git
   cd mediapipe-gesture-controlled-mouse
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate it:
   - **Linux / macOS:** `source venv/bin/activate`
   - **Windows:** `venv\Scripts\activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run:
   ```bash
   python gesture_mouse.py
   ```

## Platform Notes

- **Windows:** works out of the box.
- **macOS:** grant Terminal accessibility permissions in *System Preferences > Privacy & Security > Accessibility*.
- **Linux:** may need `sudo apt install python3-tk python3-dev`.

## Configuration

All settings live in `config.py`. Key values to tune:

| Setting | Default | Effect |
|---|---|---|
| `PINCH_THRESHOLD` | 40 px | Increase if clicks trigger too easily |
| `SMOOTHING_BUFFER` | 5 frames | Increase for smoother cursor, decrease for faster response |
| `HOLD_DURATION` | 0.8 s | Time before a pinch becomes a hold/drag |
| `CLICK_COOLDOWN` | 0.8 s | Minimum time between clicks |
| `SCROLL_SPEED` | 3 | Scroll units per frame |

## How It Works

```
Webcam → OpenCV frame → MediaPipe 21 landmarks → Gesture logic → PyAutoGUI mouse control → OpenCV HUD overlay
```

1. Each frame is captured via OpenCV and flipped horizontally.
2. MediaPipe Hands detects 21 landmarks on the hand.
3. `GestureRecognizer` maps the index fingertip to screen coordinates and evaluates pinch distances and scroll state.
4. `MouseController` smooths the cursor position over a rolling buffer and dispatches PyAutoGUI commands.
5. `Overlay` renders a live HUD showing the active gesture, pinch distances, and FPS.

## Known Limitations

- Works with one hand only.
- Performance degrades in low light.
- Very fast hand movements may cause cursor jumps — increase `SMOOTHING_BUFFER`.
- On some systems PyAutoGUI may require elevated permissions.

## Tech Stack

| Library | Role |
|---|---|
| MediaPipe | Hand landmark detection |
| OpenCV | Webcam capture and overlay |
| PyAutoGUI | Mouse and keyboard control |
| NumPy | Coordinate smoothing math |

## License

MIT

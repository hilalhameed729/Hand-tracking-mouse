# Hand Tracking Mouse Cursor

Control your mouse cursor with your hand using a laptop webcam.

Beginner-friendly Python project using OpenCV + MediaPipe + PyAutoGUI.

> Status: not yet run/tested on this machine.

## Project Overview

This program watches your hand through the webcam, finds your fingertips, and moves the real mouse cursor to follow your index finger. Pinch your thumb and index finger together to left-click.

Perfect as a first computer-vision project — single file (`main.py`), lots of comments, no complex setup.

## Features

- Move mouse cursor with index fingertip (landmark 8)
- Left-click with thumb-index pinch gesture
- Cursor smoothing to reduce shaking
- Live webcam preview with hand landmarks drawn
- Webcam error handling with helpful messages
- Works with both MediaPipe APIs:
  - Classic `mp.solutions.hands` if available
  - New `mp.tasks.vision.HandLandmarker` fallback (auto-downloads model once)
- Adjustable settings at top of `main.py` (smoothing, click distance, camera index)

## Windows Setup Instructions

You need:

1. Python 3.9 - 3.12 from https://www.python.org/downloads/
   - IMPORTANT: tick `Add python.exe to PATH` during install
2. A working webcam + good room lighting
3. Check Python installed:

```cmd
python --version
pip --version
```

If `python` is not found, reinstall Python with PATH enabled or try `py --version`.

## Installation Commands

Run in Command Prompt (`cmd`) or PowerShell:

```cmd
cd path\to\hand-tracking-mouse
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

What this does (simple explanation):

- `python -m venv venv` — creates an isolated `venv/` folder for packages
- `venv\Scripts\activate` — switches to that isolated environment
- `pip install -r requirements.txt` — installs `opencv-python`, `mediapipe`, `pyautogui`

You should see `(venv)` at the start of your terminal line when activated.

## Usage Instructions

1. Activate venv if not already active:
   ```cmd
   venv\Scripts\activate
   ```
2. Start program:
   ```cmd
   python main.py
   ```
3. A window named `Hand Tracking Mouse` opens.
4. Show **one hand**, about 30-60 cm from camera.
5. Point with index finger to move cursor.
6. Touch thumb tip to index tip and hold briefly to left-click.
7. Quit when done (see below).

Settings to try in `main.py`:

- `SMOOTHING = 5` — higher = smoother but slower (try 3-8)
- `CLICK_DISTANCE_PX = 40` — smaller = harder pinch needed (try 30-50)
- `CLICK_COOLDOWN = 0.8` — wait time between clicks
- `CAMERA_INDEX = 0` — change to `1` if webcam won't open

## Keyboard Controls

| Key | Action |
|-----|--------|
| `Q` | Quit program (webcam window must be focused/clicked first) |

No other keys needed. Mouse control is 100% by hand gestures:

- Move = index fingertip
- Click = thumb + index pinch
- Quit = `Q` key

## File Structure

```text
hand-tracking-mouse/
  main.py           - main program (webcam + tracking + mouse)
  requirements.txt  - opencv-python, mediapipe, pyautogui
  .gitignore        - ignores venv/, __pycache__/, *.pyc, OS/editor files
  README.md         - this file
```

Do NOT commit these if they appear later:

- `venv/` — your local virtual environment
- `__pycache__/` / `*.pyc` — auto-generated Python cache
- `hand_landmarker.task` — auto-downloaded model (~8 MB, only if Tasks API used)

## Troubleshooting

- Webcam black / error:
  - Close Zoom, Teams, Camera app
  - Try `CAMERA_INDEX = 1` in `main.py`
  - Windows Settings > Privacy & security > Camera > allow desktop apps
- `No module named cv2 / mediapipe / pyautogui`:
  - Make sure `(venv)` is active, rerun `pip install -r requirements.txt`
- `has no attribute 'solutions'`:
  - Program auto-switches to Tasks API and downloads `hand_landmarker.task` once
- Cursor jittery:
  - Increase `SMOOTHING`, improve lighting, keep background plain
- Too many clicks:
  - Increase `CLICK_COOLDOWN` or lower `CLICK_DISTANCE_PX`

## Safety Note

This moves your real cursor. Keep keyboard nearby to press `Q`. `pyautogui.FAILSAFE = False` is set so corners won't crash the demo — set to `True` if you want moving to a corner to emergency-stop.

"""
Hand Tracking Mouse Cursor - Beginner Project
---------------------------------------------
Move mouse with your index fingertip.
Left-click by pinching thumb tip + index tip together.

Gestures:
  - Move cursor : Show one hand, point with index finger
  - Left click  : Touch thumb tip to index tip (pinch)
  - Quit        : Press 'Q' on the keyboard while webcam window is focused

Compatible with both MediaPipe APIs:
  1. Classic Solutions API  (mp.solutions.hands) - preferred, no extra files
  2. New Tasks API (mp.tasks.vision.HandLandmarker) - used automatically
     only if Solutions API is not available in your installed version.
"""

import math
import time
import sys

import cv2
import mediapipe as mp
import pyautogui

# ---------------- Settings (tweak these) ----------------
SMOOTHING = 5            # Higher = smoother but slower. Try 3-8.
CLICK_DISTANCE_PX = 40   # Thumb-index distance (pixels) below this = click. Try 30-50.
CLICK_COOLDOWN = 0.8     # Seconds between clicks to avoid double-clicks.
CAMERA_INDEX = 0         # 0 = default laptop webcam. Try 1 if you have USB camera.
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
# ---------------------------------------------------------

# Safety: moving mouse to a corner aborts PyAutoGUI by default.
# We turn it off for this demo so the cursor doesn't crash,
# but you can set it to True if you want that safety feature.
pyautogui.FAILSAFE = False


def get_screen_size():
    """Get screen size, with error handling."""
    try:
        width, height = pyautogui.size()
        print(f"Screen size: {width} x {height}")
        return width, height
    except Exception as e:
        print(f"Error getting screen size: {e}")
        sys.exit(1)


def finger_distance(x1, y1, x2, y2):
    """Simple pixel distance between two points."""
    return math.hypot(x2 - x1, y2 - y1)


def has_solutions_api():
    """Check if installed MediaPipe still has the classic Solutions API."""
    try:
        _ = mp.solutions.hands
        _ = mp.solutions.drawing_utils
        return True
    except AttributeError:
        return False


def run_with_solutions_api(screen_w, screen_h):
    """Main loop using classic MediaPipe Solutions API (beginner-friendly)."""
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    # Open webcam with error handling
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"ERROR: Could not open webcam (index {CAMERA_INDEX}).")
        print("Tips:")
        print("  - Close other apps using the camera (Zoom, Teams, etc.)")
        print("  - Try CAMERA_INDEX = 1 at the top of main.py")
        print("  - Check Windows camera privacy permissions")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    # Smoothing variables
    prev_x, prev_y = 0, 0
    last_click_time = 0

    # One hand only, to keep it simple and fast
    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    ) as hands:
        print("Webcam started. Show one hand. Press 'Q' to quit.")
        while True:
            success, frame = cap.read()
            if not success or frame is None:
                print("WARNING: Failed to read frame from webcam. Exiting...")
                break

            # Mirror image so movement feels natural
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            # MediaPipe needs RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb_frame)

            if result.multi_hand_landmarks:
                hand_landmarks = result.multi_hand_landmarks[0]
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

                # Landmark 8 = index fingertip, 4 = thumb tip
                index_tip = hand_landmarks.landmark[8]
                thumb_tip = hand_landmarks.landmark[4]

                # Convert normalized 0-1 coords to pixels on webcam frame
                index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)

                # Map webcam position to full screen position
                target_x = index_tip.x * screen_w
                target_y = index_tip.y * screen_h

                # --- Cursor smoothing ---
                # Move part-way toward target each frame instead of jumping.
                curr_x = prev_x + (target_x - prev_x) / SMOOTHING
                curr_y = prev_y + (target_y - prev_y) / SMOOTHING
                prev_x, prev_y = curr_x, curr_y

                try:
                    pyautogui.moveTo(curr_x, curr_y)
                except Exception as e:
                    print(f"Mouse move failed: {e}")

                # Draw circles on index + thumb so you can see them
                cv2.circle(frame, (index_x, index_y), 10, (255, 0, 255), -1)
                cv2.circle(frame, (thumb_x, thumb_y), 10, (0, 255, 0), -1)
                cv2.line(frame, (index_x, index_y), (thumb_x, thumb_y), (255, 255, 0), 2)

                # --- Pinch to left-click ---
                pinch_dist = finger_distance(index_x, index_y, thumb_x, thumb_y)
                cv2.putText(frame, f"Pinch: {int(pinch_dist)}px",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 255, 0), 2)

                now = time.time()
                if pinch_dist < CLICK_DISTANCE_PX and (now - last_click_time) > CLICK_COOLDOWN:
                    try:
                        pyautogui.click()
                        print("Left click!")
                    except Exception as e:
                        print(f"Click failed: {e}")
                    last_click_time = now
                    # Visual feedback
                    cv2.putText(frame, "CLICK!", (index_x, index_y - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "Show one hand to control mouse",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 0, 255), 2)

            cv2.putText(frame, "Press 'Q' to quit", (10, h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.imshow("Hand Tracking Mouse", frame)

            # Press Q to quit (window must be focused)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Q pressed. Exiting...")
                break

    cap.release()
    cv2.destroyAllWindows()


def run_with_tasks_api(screen_w, screen_h):
    """
    Fallback loop using new MediaPipe Tasks API.
    Only used if mp.solutions.hands is missing.
    Requires 'hand_landmarker.task' model file (auto-downloaded).
    """
    import os
    import urllib.request

    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    MODEL_PATH = "hand_landmarker.task"
    MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/"
                 "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task")

    if not os.path.exists(MODEL_PATH):
        print(f"Downloading hand tracking model to {MODEL_PATH}...")
        print("This happens once (about 8 MB).")
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("Download complete.")
        except Exception as e:
            print(f"ERROR: Could not download model file: {e}")
            print(f"Manually download from:\n{MODEL_URL}")
            print(f"and save as {MODEL_PATH} in this folder.")
            return

    base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"ERROR: Could not open webcam (index {CAMERA_INDEX}).")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    prev_x, prev_y = 0, 0
    last_click_time = 0

    with vision.HandLandmarker.create_from_options(options) as landmarker:
        print("Webcam started (Tasks API). Show one hand. Press 'Q' to quit.")
        while True:
            success, frame = cap.read()
            if not success or frame is None:
                print("WARNING: Failed to read frame from webcam. Exiting...")
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            timestamp_ms = int(time.time() * 1000)
            result = landmarker.detect_for_video(mp_image, timestamp_ms)

            if result.hand_landmarks:
                lm = result.hand_landmarks[0]
                index_tip = lm[8]
                thumb_tip = lm[4]

                index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
                thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)

                target_x = index_tip.x * screen_w
                target_y = index_tip.y * screen_h

                curr_x = prev_x + (target_x - prev_x) / SMOOTHING
                curr_y = prev_y + (target_y - prev_y) / SMOOTHING
                prev_x, prev_y = curr_x, curr_y

                try:
                    pyautogui.moveTo(curr_x, curr_y)
                except Exception as e:
                    print(f"Mouse move failed: {e}")

                cv2.circle(frame, (index_x, index_y), 10, (255, 0, 255), -1)
                cv2.circle(frame, (thumb_x, thumb_y), 10, (0, 255, 0), -1)

                pinch_dist = finger_distance(index_x, index_y, thumb_x, thumb_y)
                cv2.putText(frame, f"Pinch: {int(pinch_dist)}px",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 255, 0), 2)

                now = time.time()
                if pinch_dist < CLICK_DISTANCE_PX and (now - last_click_time) > CLICK_COOLDOWN:
                    try:
                        pyautogui.click()
                        print("Left click!")
                    except Exception as e:
                        print(f"Click failed: {e}")
                    last_click_time = now
            else:
                cv2.putText(frame, "Show one hand to control mouse",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 0, 255), 2)

            cv2.putText(frame, "Press 'Q' to quit", (10, h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.imshow("Hand Tracking Mouse", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Q pressed. Exiting...")
                break

    cap.release()
    cv2.destroyAllWindows()


def main():
    print("MediaPipe version check...")
    print("mediapipe imported OK")

    screen_w, screen_h = get_screen_size()

    if has_solutions_api():
        print("Using MediaPipe Solutions API (mp.solutions.hands)")
        run_with_solutions_api(screen_w, screen_h)
    else:
        print("Solutions API not found. Using MediaPipe Tasks API fallback.")
        run_with_tasks_api(screen_w, screen_h)


if __name__ == "__main__":
    main()

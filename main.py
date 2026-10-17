
import cv2
import mediapipe as mp
import numpy as np
import random
import math
import time
import os

# =========================================================
# AIRSCRIPT PRO | HAND-TRACKING DIGITAL PAINT
# =========================================================

WINDOW = "AirScript Pro"
CAMERA_INDEX = 0

COLORS = {
    "Green":   (60, 255, 90),
    "Cyan":    (255, 230, 0),
    "Blue":    (255, 100, 40),
    "Purple":  (220, 50, 255),
    "Pink":    (180, 70, 255),
    "Orange":  (0, 140, 255),
    "White":   (240, 255, 240),
    "Yellow":  (0, 255, 255),
}

COLOR_KEYS = {
    ord("1"): "Green",
    ord("2"): "Cyan",
    ord("3"): "Blue",
    ord("4"): "Purple",
    ord("5"): "Pink",
    ord("6"): "Orange",
    ord("7"): "White",
    ord("8"): "Yellow",
}

# ---------- Camera and MediaPipe ----------

cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    raise SystemExit(
        "Cannot open webcam. Close other camera apps "
        "or change CAMERA_INDEX to 1."
    )

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

tracker = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# ---------- Application state ----------

canvas = None
previous_point = None
particles = []

selected_color = "Green"
brush_size = 8
eraser_size = 35
eraser_mode = False
rainbow_mode = False

frame_number = 0
last_particle_time = 0.0


# =========================================================
# GESTURE RECOGNITION
# =========================================================

def is_up(points, tip, pip):
    """Approximate finger extension from landmark positions."""
    return points[tip].y < points[pip].y


def get_gesture(points):
    """
    Return DRAW, PALM, ERASE, BURST, or IDLE.

    These are simple landmark heuristics, not a trained
    gesture classifier.
    """
    index = is_up(points, 8, 6)
    middle = is_up(points, 12, 10)
    ring = is_up(points, 16, 14)
    pinky = is_up(points, 20, 18)

    if index and middle and ring and pinky:
        return "PALM"

    if index and not middle and not ring and not pinky:
        return "DRAW"

    if not index and not middle and not ring and not pinky:
        return "ERASE"

    if index and middle and not ring and not pinky:
        return "BURST"

    return "IDLE"


# =========================================================
# PARTICLE EFFECTS
# =========================================================

def create_particles(x, y, amount=8):
    for _ in range(amount):
        particles.append({
            "x": float(x + random.randint(-25, 25)),
            "y": float(y + random.randint(-20, 20)),
            "vx": random.uniform(-2.5, 2.5),
            "vy": random.uniform(-3.5, 1.0),
            "life": random.randint(20, 45),
            "color": random.choice(list(COLORS.values())),
            "size": random.randint(2, 5),
            "char": random.choice("01ABCDEF"),
        })


def update_particles(frame):
    alive = []

    for p in particles:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.08
        p["life"] -= 1

        if p["life"] > 0:
            x, y = int(p["x"]), int(p["y"])
            color = p["color"]

            cv2.putText(
                frame, p["char"], (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45, color, 1, cv2.LINE_AA
            )

            alive.append(p)

    # Limit particle count to maintain performance.
    particles[:] = alive[-500:]


# =========================================================
# DRAWING AND UI HELPERS
# =========================================================




def draw_stroke(canvas, p1, p2, color, thickness):
    p1 = tuple(map(int, p1))
    p2 = tuple(map(int, p2))
    thickness = max(1, int(thickness))

    # Thick black outline.
    cv2.line(
        canvas, p1, p2, (0, 0, 0),
        thickness + 6, cv2.LINE_AA
    )

    # Selected color on top.
    cv2.line(
        canvas, p1, p2, tuple(map(int, color)),
        thickness, cv2.LINE_AA
    )


def draw_hud(frame, gesture, width, height):
    """Draw a clean dark HUD with color and mode information."""
    panel_color = (20, 35, 25)
    accent = COLORS[selected_color]

    cv2.rectangle(
        frame, (12, 12), (width - 12, 112),
        panel_color, -1
    )

    cv2.rectangle(
        frame, (12, 12), (width - 12, 112),
        accent, 1
    )

    cv2.putText(
        frame, "A I R S C R I P T   /   P R O",
        (26, 39), cv2.FONT_HERSHEY_SIMPLEX,
        0.72, accent, 2, cv2.LINE_AA
    )

    mode = "ERASER" if eraser_mode else (
        "RAINBOW" if rainbow_mode else "PAINT"
    )

    cv2.putText(
        frame,
        f"MODE: {mode}   |   GESTURE: {gesture}",
        (26, 67), cv2.FONT_HERSHEY_SIMPLEX,
        0.48, (225, 240, 225), 1, cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"COLOR: {selected_color.upper()}   |   SIZE: {brush_size}",
        (26, 92), cv2.FONT_HERSHEY_SIMPLEX,
        0.48, accent, 1, cv2.LINE_AA
    )

    # Color swatches.
    x_start = 24
    y = height - 66

    cv2.rectangle(
        frame, (12, height - 94), (width - 12, height - 12),
        panel_color, -1
    )

    cv2.putText(
        frame, "COLOR PALETTE  (1-8)",
        (x_start, y - 9), cv2.FONT_HERSHEY_SIMPLEX,
        0.42, (220, 230, 220), 1, cv2.LINE_AA
    )

    for i, (name, color) in enumerate(COLORS.items()):
        x = x_start + i * 43
        cv2.rectangle(frame, (x, y), (x + 27, y + 18), color, -1)

        if name == selected_color:
            cv2.rectangle(
                frame, (x - 2, y - 2), (x + 29, y + 20),
                (255, 255, 255), 1
            )

    cv2.putText(
        frame,
        "E: ERASER  R: RAINBOW  +/-: SIZE  C: CLEAR  S: SAVE  Q: QUIT",
        (24, height - 22), cv2.FONT_HERSHEY_SIMPLEX,
        0.40, (210, 235, 210), 1, cv2.LINE_AA
    )



def composite_canvas(frame):
    """Show strokes with a dark outline so they remain visible."""
    if canvas is None:
        return frame.copy()

    # Detect pixels where artwork exists.
    mask = np.any(canvas > 0, axis=2)

    # Make a copy of the camera frame.
    output = frame.copy()

    # Draw artwork only where strokes exist.
    output[mask] = canvas[mask]

    return output

# =========================================================
# MAIN LOOP
# =========================================================

try:
    while True:
        ok, frame = cap.read()

        if not ok:
            print("Failed to read webcam.")
            break

        frame = cv2.flip(frame, 1)
        height, width = frame.shape[:2]

        if canvas is None:
            canvas = np.zeros_like(frame)

        frame_number += 1

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = tracker.process(rgb)

        gesture = "NO HAND"
        drawing = False

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            points = hand.landmark

            gesture = get_gesture(points)

            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(
                    color=COLORS["Green"],
                    thickness=2,
                    circle_radius=2,
                ),
                mp_draw.DrawingSpec(
                    color=(40, 130, 50),
                    thickness=2,
                ),
            )

            tip = points[8]
            x = int(tip.x * width)
            y = int(tip.y * height)
            point = (x, y)

            # Palm center for particle effects.
            palm_x = int((points[0].x + points[9].x) * width / 2)
            palm_y = int((points[0].y + points[9].y) * height / 2)

            # ----- OPEN PALM: DIGITAL PARTICLES -----
            if gesture == "PALM":
                now = time.time()

                if now - last_particle_time > 0.12:
                    create_particles(palm_x, palm_y, 8)
                    last_particle_time = now

                previous_point = None

            # ----- TWO FINGERS: PARTICLE BURST -----
            elif gesture == "BURST":
                now = time.time()

                if now - last_particle_time > 0.20:
                    create_particles(palm_x, palm_y, 18)
                    last_particle_time = now

                previous_point = None

            # ----- FIST: LOCAL ERASE -----
            elif gesture == "ERASE":
                cx = int(points[9].x * width)
                cy = int(points[9].y * height)

                cv2.circle(
                    canvas, (cx, cy),
                    eraser_size, (0, 0, 0), -1,
                    cv2.LINE_AA
                )

                cv2.circle(
                    frame, (cx, cy),
                    eraser_size, (0, 220, 255), 2,
                    cv2.LINE_AA
                )

                previous_point = None

            # ----- INDEX FINGER: PAINT OR ERASE -----
            elif gesture == "DRAW":
                drawing = True

                if eraser_mode:
                    cv2.circle(
                        canvas, point, eraser_size,
                        (0, 0, 0), -1, cv2.LINE_AA
                    )

                    cv2.circle(
                        frame, point, eraser_size,
                        (0, 220, 255), 2, cv2.LINE_AA
                    )

                else:
                    if rainbow_mode:
                        hue = (frame_number * 2) % 180
                        hsv = np.uint8([[[hue, 255, 255]]])
                        color = tuple(
                            int(v) for v in cv2.cvtColor(
                                hsv, cv2.COLOR_HSV2BGR
                            )[0, 0]
                        )
                    else:
                        color = COLORS[selected_color]

                    if previous_point is not None:
                        draw_stroke(
                            canvas,
                            previous_point, point,
                            color, brush_size
                        )

                    cv2.circle(
                        frame, point, max(4, brush_size),
                        color, -1, cv2.LINE_AA
                    )

                previous_point = point

            else:
                previous_point = None

        else:
            previous_point = None

        # Animate particles on top of the camera image.
        update_particles(frame)

        # Combine persistent artwork with the live camera.
        output = composite_canvas(frame)

        draw_hud(output, gesture, width, height)

        cv2.imshow(WINDOW, output)

        key = cv2.waitKey(1) & 0xFF

        # ----- KEYBOARD CONTROLS -----

        if key == ord("q"):
            break

        elif key == ord("c"):
            canvas = np.zeros_like(frame)
            previous_point = None

        elif key == ord("s"):
            filename = f"airscript_{int(time.time())}.png"

            if cv2.imwrite(filename, canvas):
                print(f"Saved artwork: {os.path.abspath(filename)}")

        elif key in COLOR_KEYS:
            selected_color = COLOR_KEYS[key]
            rainbow_mode = False
            eraser_mode = False

        elif key == ord("e"):
            eraser_mode = not eraser_mode
            rainbow_mode = False
            previous_point = None

        elif key == ord("r"):
            rainbow_mode = not rainbow_mode
            eraser_mode = False
            previous_point = None

        elif key in (ord("+"), ord("=")):
            brush_size = min(30, brush_size + 2)

        elif key in (ord("-"), ord("_")):
            brush_size = max(2, brush_size - 2)

finally:
    tracker.close()
    cap.release()
    cv2.destroyAllWindows()

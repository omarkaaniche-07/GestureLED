import cv2
import mediapipe as mp
import time
import serial

SERIAL_PORT = "COM3"
BAUD_RATE = 9600

arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


def distance(a, b):
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5


TIP_IDS = [8, 12, 16, 20]
PIP_IDS = [6, 10, 14, 18]


def fingers_up(hand_lm):
    wrist = hand_lm[0]
    result = []
    for tip_id, pip_id in zip(TIP_IDS, PIP_IDS):
        tip_dist = distance(hand_lm[tip_id], wrist)
        pip_dist = distance(hand_lm[pip_id], wrist)
        result.append(tip_dist > pip_dist)
    return result


def detect_number(hand_lm):
    if hand_lm is None:
        return None
    f = fingers_up(hand_lm)
    return sum(f)


cap = cv2.VideoCapture(0)
active_gesture = None
gesture_start_time = None
DISPLAY_SECONDS = 3
already_sent = False

print("Camera started! Show 1-5 fingers to the camera.")
print("Hold the same number steady for 3 seconds to confirm it.")
print("Press Q to quit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    hand_results = hands.process(rgb)

    detected_number = None

    if hand_results.multi_hand_landmarks:
        hand_landmarks = hand_results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style()
        )
        lm_list = hand_landmarks.landmark
        detected_number = detect_number(lm_list)

    if detected_number is not None:
        if detected_number == active_gesture:
            elapsed = time.time() - gesture_start_time
            if elapsed >= DISPLAY_SECONDS:
                cv2.putText(frame, f"Confirmed: {active_gesture}", (30, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                if not already_sent:
                    arduino.write(f"{active_gesture}\n".encode())
                    print(f"Sent to Arduino: {active_gesture}")
                    already_sent = True
            else:
                cv2.putText(frame, f"Holding {active_gesture}: {elapsed:.1f}s", (30, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        else:
            active_gesture = detected_number
            gesture_start_time = time.time()
            already_sent = False
            cv2.putText(frame, f"Holding {active_gesture}: 0.0s", (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    else:
        active_gesture = None
        gesture_start_time = None
        already_sent = False

    cv2.imshow("Gesture Detection", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
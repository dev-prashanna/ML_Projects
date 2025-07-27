import cv2
import mediapipe as mp
import time
import requests
import os

# Hide TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

ESP32_URL = "http://192.168.1.80/morse"   # ESP32 IP

MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
    '...--': '3', '....-': '4', '.....': '5', '-....': '6',
    '--...': '7', '---..': '8', '----.': '9'
}

LETTER_GAP = 3.0  # 3 sec gap for new letter

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

def count_fingers(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    fingers = []
    fingers.append(1 if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[tips[0] - 1].x else 0)
    for tip in tips[1:]:
        fingers.append(1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y else 0)
    return fingers.count(1)

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

current_signal = ""
sentence = ""
last_seen_time = time.time()
hand_detected = False

with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        finger_count = -1
        if results.multi_hand_landmarks:
            hand_detected = True
            last_seen_time = time.time()
            for lm in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
                finger_count = count_fingers(lm)

            # Closed fist (0 fingers) = DOT
            if finger_count == 0:
                current_signal += "."
                try:
                    requests.get(f"{ESP32_URL}?signal=dot", timeout=0.3)
                except:
                    print("⚠ ESP32 not reachable")
                time.sleep(0.5)  # debounce

            # Open hand (5 fingers) = DASH
            elif finger_count == 5:
                current_signal += "-"
                try:
                    requests.get(f"{ESP32_URL}?signal=dash", timeout=0.3)
                except:
                    print("⚠ ESP32 not reachable")
                time.sleep(0.5)  # debounce

        else:
            # No hand detected
            if hand_detected and (time.time() - last_seen_time > LETTER_GAP):
                # Gap detected: finalize letter
                if current_signal:
                    sentence += MORSE_CODE_DICT.get(current_signal, "?")
                    current_signal = ""
                hand_detected = False

        # Display on screen
        cv2.putText(frame, f"Morse: {current_signal}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Sentence: {sentence}", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        cv2.imshow("Morse Code Hand Input", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

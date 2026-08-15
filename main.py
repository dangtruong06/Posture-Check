import cv2
import mediapipe as mp
from config import CALIBRATION_FRAMES
from posture import compute_metrics, average_samples, check_posture
from posture_state import PostureState
from notifier import send_alert

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

# SET UP CAMERA CAPTURE
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print('Cannot open camera')
    exit()

frame_count = 0
baseline = None
calibrating = False
calibration_samples = []    #list of dictionaries, each metric is a dictionary {"dist": 0.18, "shoulder_tilt": 0.004, "nose_y": 0.32}

# CREATE STATE OBJECT 
posture_state = PostureState(3)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = pose.process(frame_rgb)

    if result.pose_landmarks:
        mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        landmarks = result.pose_landmarks.landmark
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]

        frame_count += 1   

        # current posture reading
        metrics = compute_metrics(left_shoulder=left_shoulder, right_shoulder=right_shoulder, nose=nose)

        if calibrating:
            calibration_samples.append(metrics)

            if len(calibration_samples) >= CALIBRATION_FRAMES:
                # average metric over 30 frames
                baseline = average_samples(calibration_samples)
                calibrating = False
                print(f"Baseline set: {baseline}")

        elif baseline and frame_count % 30 == 0:

            #check current posture with baseline average
            flags = check_posture(metrics, baseline)

            should_alert = posture_state.update(flags)
            if should_alert:
                send_alert(
                    title="Caution",
                    message="🚨 You've been slouching for over a minute — sit up straight!"
                )

    cv2.imshow('Live Posture Check', frame)

    # PRESS Q TO QUIT PROGRAM
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

    # SIT WITH GOOD POSTURE, THEN PRESS C TO SET BASE VALUES
    if key == ord('c'):
        calibrating = True
        calibration_samples = []
        print("Calibrating, sit still..")

cap.release()
cv2.destroyAllWindows()
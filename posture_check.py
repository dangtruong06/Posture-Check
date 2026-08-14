import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print('Cannot open camera')
    exit()

frame_count = 0
baseline = {}

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

        # SIDE LEAN CHECK
        shoulder_mid_x = (right_shoulder.x + left_shoulder.x) / 2

        # SLOUCHING CHECK
        shoulder_mid_y = (right_shoulder.y + left_shoulder.y) / 2
        distance_to_nose = shoulder_mid_y - nose.y

        # CHECK EVERY 30 FRAMES
        if frame_count % 30 == 0:     
            if baseline:
                if distance_to_nose < (baseline['dist'] * .9):
                    print(f"Slouching (distance): {distance_to_nose}")
                if nose.y > (baseline['nose_y'] * 1.1):
                    print(f"Slouching (nose height): {nose.y}")
                # if shoulder_mid_y > (baseline['shoulder_diff'] * 3):
                #     print(f"Shoulder tilting: {shoulder_mid_y}")
            

    cv2.imshow('Live Posture Check', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('c') or key == ord('C'):
        baseline = {
            "dist": distance_to_nose,
            "shoulder_diff": abs(left_shoulder.y - right_shoulder.y),
            "nose_y": nose.y
        }
        print("Base line is ", baseline)


cap.release()
cv2.destroyAllWindows()
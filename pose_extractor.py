import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose

KEYPOINTS = [
    mp_pose.PoseLandmark.LEFT_SHOULDER,
    mp_pose.PoseLandmark.RIGHT_SHOULDER,
    mp_pose.PoseLandmark.LEFT_HIP,
    mp_pose.PoseLandmark.RIGHT_HIP,
    mp_pose.PoseLandmark.LEFT_ELBOW,
    mp_pose.PoseLandmark.RIGHT_ELBOW,
    mp_pose.PoseLandmark.LEFT_WRIST,
    mp_pose.PoseLandmark.RIGHT_WRIST,
    mp_pose.PoseLandmark.LEFT_KNEE,
    mp_pose.PoseLandmark.RIGHT_KNEE,
    mp_pose.PoseLandmark.NOSE,
]

def extract_pose_keypoints(frames):
    output = {}
    with mp_pose.Pose(min_detection_confidence=0.5,
                      min_tracking_confidence=0.5) as pose:

        for idx, frame in frames:
            h, w, _ = frame.shape
            rgb = frame[:, :, ::-1]
            res = pose.process(rgb)

            pts = {}
            if res.pose_landmarks:
                for lm in KEYPOINTS:
                    l = res.pose_landmarks.landmark[lm]
                    pts[lm.name] = (l.x * w, l.y * h, l.visibility)

            output[idx] = {"pose": pts}

    return output

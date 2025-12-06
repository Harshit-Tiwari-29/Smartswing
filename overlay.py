# swing_analyzer/overlay.py
import cv2
import numpy as np

# List of keypoints to draw
KP_PAIRS = [
    ("LEFT_SHOULDER", "RIGHT_SHOULDER"),
    ("LEFT_HIP", "RIGHT_HIP"),
    ("LEFT_ELBOW", "LEFT_SHOULDER"),
    ("RIGHT_ELBOW", "RIGHT_SHOULDER"),
    ("LEFT_WRIST", "LEFT_ELBOW"),
    ("RIGHT_WRIST", "RIGHT_ELBOW"),
]

COLOR_KP = (0, 255, 0)      # green
COLOR_LINE = (0, 200, 200)  # yellow
COLOR_PHASE = (0, 0, 255)   # red


def draw_pose(frame, pose):
    """Draw skeleton on a single frame."""
    for kp1, kp2 in KP_PAIRS:
        p1 = pose.get(kp1)
        p2 = pose.get(kp2)
        if p1 and p2:
            cv2.line(frame,
                     (int(p1[0]), int(p1[1])),
                     (int(p2[0]), int(p2[1])),
                     COLOR_LINE, 3)

            cv2.circle(frame, (int(p1[0]), int(p1[1])), 5, COLOR_KP, -1)
            cv2.circle(frame, (int(p2[0]), int(p2[1])), 5, COLOR_KP, -1)

    return frame


def draw_club(frame, pose):
    """Estimate and draw club using wrist → extrapolated club head."""
    lw = pose.get("LEFT_WRIST")
    rw = pose.get("RIGHT_WRIST")
    if lw and rw:
        hands = ((lw[0] + rw[0]) / 2, (lw[1] + rw[1]) / 2)

        # Fake club head 30% further in wrist-elbow direction
        le = pose.get("LEFT_ELBOW")
        re = pose.get("RIGHT_ELBOW")
        if le and re:
            elbows = ((le[0] + re[0]) / 2, (le[1] + re[1]) / 2)
            vec = np.array(hands) - np.array(elbows)
            club_head = tuple((np.array(hands) + 1.3 * vec).astype(int))

            cv2.line(frame,
                     (int(hands[0]), int(hands[1])),
                     (int(club_head[0]), int(club_head[1])),
                     (255, 0, 0), 3)

    return frame


def highlight_phase(frame, label):
    """Draw a red label on the frame to indicate phase."""
    cv2.putText(frame, f"{label}",
                (40, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                COLOR_PHASE,
                4)
    return frame


def create_overlay_video(original_frames, pose_by_frame, phases, output_path):
    address_f = phases["address"]
    top_f = phases["top"]
    impact_f = phases["impact"]

    # Prepare video writer
    h, w, _ = original_frames[0][1].shape
    out = cv2.VideoWriter(output_path,
                          cv2.VideoWriter_fourcc(*"mp4v"),
                          15,
                          (w, h))

    for idx, frame in original_frames:
        f = frame.copy()

        # draw pose
        pose = pose_by_frame[idx]["pose"]
        f = draw_pose(f, pose)
        f = draw_club(f, pose)

        # phase label
        if idx == address_f:
            f = highlight_phase(f, "ADDRESS")
        elif idx == top_f:
            f = highlight_phase(f, "TOP")
        elif idx == impact_f:
            f = highlight_phase(f, "IMPACT")

        out.write(f)

    out.release()
    return output_path

# swing_analyzer/metrics.py
import numpy as np
import math

def _angle_of_vec(v):
    # angle vs horizontal in degrees
    return math.degrees(math.atan2(v[1], v[0] + 1e-6))

def _get_point(pose, names):
    pts = [pose.get(n) for n in names if pose.get(n) is not None]
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


# ---------------------------
# SWING PLANE DEVIATION
# ---------------------------
def compute_plane_deviation(pose_by_frame, frames_back, frames_down):
    angles_back = []
    angles_down = []

    for f in frames_back:
        pose = pose_by_frame[f]["pose"]
        hands = _get_point(pose, ["LEFT_WRIST", "RIGHT_WRIST"])
        elbows = _get_point(pose, ["LEFT_ELBOW", "RIGHT_ELBOW"])
        if hands and elbows:
            v = np.array(hands) - np.array(elbows)
            angles_back.append(_angle_of_vec(v))

    for f in frames_down:
        pose = pose_by_frame[f]["pose"]
        hands = _get_point(pose, ["LEFT_WRIST", "RIGHT_WRIST"])
        elbows = _get_point(pose, ["LEFT_ELBOW", "RIGHT_ELBOW"])
        if hands and elbows:
            v = np.array(hands) - np.array(elbows)
            angles_down.append(_angle_of_vec(v))

    if not angles_back or not angles_down:
        return None

    back_mean = np.mean(angles_back)
    down_mean = np.mean(angles_down)
    return abs(back_mean - down_mean)



# ---------------------------
# ROTATION METRICS
# ---------------------------
def compute_rotation_metrics(pose_by_frame, address_f, top_f):
    def line_angle(p, left, right):
        L = p.get(left)
        R = p.get(right)
        if not L or not R:
            return None
        v = np.array(R[:2]) - np.array(L[:2])
        return _angle_of_vec(v)

    pose_addr = pose_by_frame[address_f]["pose"]
    pose_top = pose_by_frame[top_f]["pose"]

    shoulder_addr = line_angle(pose_addr, "LEFT_SHOULDER", "RIGHT_SHOULDER")
    shoulder_top = line_angle(pose_top, "LEFT_SHOULDER", "RIGHT_SHOULDER")

    hip_addr = line_angle(pose_addr, "LEFT_HIP", "RIGHT_HIP")
    hip_top = line_angle(pose_top, "LEFT_HIP", "RIGHT_HIP")

    shoulder_turn = None
    hip_turn = None
    x_factor = None

    if shoulder_addr is not None and shoulder_top is not None:
        shoulder_turn = abs(shoulder_top - shoulder_addr)
    if hip_addr is not None and hip_top is not None:
        hip_turn = abs(hip_top - hip_addr)
    if shoulder_turn is not None and hip_turn is not None:
        x_factor = abs(shoulder_turn - hip_turn)

    return {
        "shoulder_turn": shoulder_turn,
        "hip_turn": hip_turn,
        "x_factor": x_factor,
    }



# ---------------------------
# STABILITY (HEAD & HIPS)
# ---------------------------
def compute_stability_metrics(pose_by_frame, address_f, all_frames):

    def center(p, left, right):
        L = p.get(left)
        R = p.get(right)
        if not L or not R:
            return None
        return ((L[0] + R[0]) / 2.0, (L[1] + R[1]) / 2.0)

    addr_pose = pose_by_frame[address_f]["pose"]
    head_addr = addr_pose.get("NOSE")
    hip_addr = center(addr_pose, "LEFT_HIP", "RIGHT_HIP")

    head_disp = 0.0
    hip_lat_disp = 0.0

    for f in all_frames:
        pose = pose_by_frame[f]["pose"]
        head = pose.get("NOSE")
        hip_c = center(pose, "LEFT_HIP", "RIGHT_HIP")

        if head and head_addr:
            d = np.linalg.norm(np.array(head[:2]) - np.array(head_addr[:2]))
            head_disp = max(head_disp, d)

        if hip_c and hip_addr:
            dx = abs(hip_c[0] - hip_addr[0])  # lateral movement (x-axis)
            hip_lat_disp = max(hip_lat_disp, dx)

    return {
        "head_movement": head_disp,
        "hip_lateral_movement": hip_lat_disp
    }



# ---------------------------
# TEMPO METRIC
# ---------------------------
def compute_tempo(address_f, top_f, impact_f):
    T_back = top_f - address_f
    T_down = impact_f - top_f
    if T_down <= 0:
        return None
    ratio = T_back / T_down
    return ratio
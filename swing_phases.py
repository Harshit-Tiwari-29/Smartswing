import numpy as np

def _wrist_center(pose):
    lw = pose.get("LEFT_WRIST")
    rw = pose.get("RIGHT_WRIST")
    if lw and rw:
        return ((lw[0] + rw[0]) / 2, (lw[1] + rw[1]) / 2)
    return None

def detect_swing_segment(poses, motion_thresh=5.0):
    frames = sorted(poses.keys())
    motions = []

    prev = None
    for f in frames:
        p = poses[f]["pose"]
        wc = _wrist_center(p)
        if wc is None:
            motions.append(0)
            continue
        if prev is None:
            motions.append(0)
        else:
            motions.append(np.linalg.norm(np.array(wc) - np.array(prev)))
        prev = wc

    motions = np.array(motions)
    baseline = np.median(motions[:5])
    high = baseline + motion_thresh
    low = baseline + motion_thresh * 0.5

    start = None
    end = None

    for i, m in enumerate(motions):
        if m > high:
            start = frames[i]
            break

    if start is None:
        return None, None

    for j in range(i, len(motions)):
        if motions[j] < low:
            end = frames[j]
            break

    if end is None:
        end = frames[-1]

    return start, end


def estimate_key_phases(poses, start, end):
    frames = [f for f in poses.keys() if start <= f <= end]

    # ADDRESS = first frame
    address = frames[0]

    # TOP = max wrist-hip distance
    def hip_center(p):
        lh = p.get("LEFT_HIP")
        rh = p.get("RIGHT_HIP")
        if lh and rh:
            return ((lh[0] + rh[0]) / 2, (lh[1] + rh[1]) / 2)
        return None

    dists = []
    for f in frames:
        p = poses[f]["pose"]
        wc = _wrist_center(p)
        hc = hip_center(p)
        if wc and hc:
            d = np.linalg.norm(np.array(wc) - np.array(hc))
            dists.append((f, d))
    top = max(dists, key=lambda x: x[1])[0]

    # IMPACT = max wrist speed after top
    speeds = []
    prev = None
    for f in frames:
        wc = _wrist_center(poses[f]["pose"])
        if prev is None:
            speeds.append((f, 0))
        else:
            if wc and prev:
                v = np.linalg.norm(np.array(wc) - np.array(prev))
                speeds.append((f, v))
        prev = wc

    speeds_after_top = [s for s in speeds if s[0] >= top]
    impact = max(speeds_after_top, key=lambda x: x[1])[0]

    return {
        "address": address,
        "top": top,
        "impact": impact,
    }

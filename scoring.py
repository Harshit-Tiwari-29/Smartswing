# swing_analyzer/scoring.py
def score_linear(value, good_min, good_max, full_score):
    """
    Linear scoring:
    value inside [good_min, good_max] → full score
    outside → decreases linearly
    """
    if value is None:
        return 0
    
    if value <= good_min:
        return full_score
    if value >= good_max:
        return 0
    
    # linear drop
    return full_score * (1 - (value - good_min) / (good_max - good_min))



def compute_final_score(plane_dev, rotation, stability, tempo):
    """
    Inputs:
      - plane_dev (degrees)
      - rotation: dict(shoulder_turn, hip_turn, x_factor)
      - stability: dict(head_movement, hip_lateral_movement)
      - tempo: ratio (ideal ≈ 3.0)
    """

    # ------------------
    # 1. PLANE (0–30)
    # ------------------
    plane_score = score_linear(plane_dev, good_min=0, good_max=20, full_score=30)


    # ------------------
    # 2. ROTATION (0–30)
    # ------------------
    rot_score = 0

    # shoulder turn ideal ~60–100 degrees
    s = rotation["shoulder_turn"]
    rot_score += score_linear(abs(s - 80), 0, 60, 10) if s else 0

    # hip turn ideal ~40–60
    h = rotation["hip_turn"]
    rot_score += score_linear(abs(h - 50), 0, 40, 10) if h else 0

    # x-factor ~20–50
    x = rotation["x_factor"]
    rot_score += score_linear(abs(x - 35), 0, 25, 10) if x else 0


    # ------------------
    # 3. STABILITY (0–30)
    # ------------------
    stab_score = 0

    # head movement ideally < 20 px
    stab_score += score_linear(stability["head_movement"], 0, 50, 15)

    # hips lateral ideally < 30 px
    stab_score += score_linear(stability["hip_lateral_movement"], 0, 70, 15)


    # ------------------
    # 4. TEMPO (0–10)
    # ------------------
    # ideal tempo ratio ≈ 3:1
    if tempo:
        tempo_score = score_linear(abs(tempo - 3.0), 0, 2.5, 10)
    else:
        tempo_score = 0

    total = plane_score + rot_score + stab_score + tempo_score

    return {
        "plane_score": plane_score,
        "rotation_score": rot_score,
        "stability_score": stab_score,
        "tempo_score": tempo_score,
        "total_score": round(total, 2)
    }

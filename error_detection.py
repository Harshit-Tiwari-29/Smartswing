# swing_analyzer/error_detection.py
import math


def detect_over_the_top(plane_dev, rotation, stability):
    """
    Super simple heuristic:
    - large plane deviation
    - low shoulder turn
    -> likely coming over-the-top
    """
    s_turn = rotation.get("shoulder_turn") or 0
    if plane_dev is None:
        return False, ""
    if plane_dev > 15 and s_turn < 40:
        return True, (
            "Your downswing appears to be coming over-the-top. "
            "Try feeling the club drop more from the inside at the start of the downswing."
        )
    return False, ""


def detect_limited_rotation(rotation):
    """
    Limited shoulder / hip turn.
    """
    s_turn = rotation.get("shoulder_turn") or 0
    h_turn = rotation.get("hip_turn") or 0

    msgs = []
    flagged = False

    if s_turn < 40:
        flagged = True
        msgs.append("Shoulder turn is quite small; try allowing your shoulders to rotate more in the backswing.")
    if h_turn < 20:
        flagged = True
        msgs.append("Hip turn is restricted; let your hips rotate a bit more to load properly.")

    return flagged, " ".join(msgs)


def detect_excess_sway(stability):
    """
    Excessive lateral hip movement.
    """
    hip_lat = stability.get("hip_lateral_movement") or 0
    if hip_lat > 60:
        return True, (
            "There is a lot of lateral hip movement (sway/slide). "
            "Try feeling more rotation around a stable hip center instead of sliding sideways."
        )
    return False, ""


def detect_head_movement(stability):
    """
    Too much head movement up/down or side-to-side.
    """
    head_m = stability.get("head_movement") or 0
    if head_m > 50:
        return True, (
            "Your head is moving quite a lot during the swing. "
            "Try to keep your head more stable to improve contact consistency."
        )
    return False, ""


def detect_tempo_issue(tempo):
    """
    Tempo far from 3:1 backswing:downswing.
    """
    if tempo is None or tempo == 0:
        return False, ""
    diff = abs(tempo - 3.0)
    if diff > 1.5:
        return True, (
            f"Your tempo ratio is about {tempo:.1f}:1. "
            "A smoother rhythm with a backswing roughly three times as long as the downswing often works better."
        )
    return False, ""


def summarize_errors(plane_dev, rotation, stability, tempo):
    """
    Return a list of detected issues and simple coaching tips.
    """
    issues = []

    for detector in [
        detect_over_the_top,
        detect_limited_rotation,
        detect_excess_sway,
        detect_head_movement,
        detect_tempo_issue,
    ]:
        flagged, msg = detector(
            plane_dev,
            rotation,
            stability,
        ) if detector is detect_over_the_top else (
            detector(rotation) if detector in [detect_limited_rotation] else
            detector(stability) if detector in [detect_excess_sway, detect_head_movement] else
            detector(tempo)
        )

        if flagged and msg:
            issues.append(msg)

    # If nothing triggered, still return something friendly
    if not issues:
        issues.append(
            "No major issues detected from the current metrics. "
            "You can keep working on repeating this motion and capturing more swings for better trends."
        )

    return issues

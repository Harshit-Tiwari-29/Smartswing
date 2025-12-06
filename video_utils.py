import cv2

def iter_video_frames(video_path, target_fps=15):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video")

    orig_fps = cap.get(cv2.CAP_PROP_FPS)
    if orig_fps <= 0:
        orig_fps = target_fps

    frame_interval = max(int(orig_fps // target_fps), 1)
    frames = []
    idx = 0
    sampled = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if idx % frame_interval == 0:
            frames.append((sampled, frame))
            sampled += 1
        idx += 1

    cap.release()
    return frames

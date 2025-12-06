from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import tempfile
import uvicorn
from swing_analyzer.error_detection import summarize_errors
from swing_analyzer.video_utils import iter_video_frames
from swing_analyzer.pose_extractor import extract_pose_keypoints
from swing_analyzer.swing_phases import detect_swing_segment, estimate_key_phases
from swing_analyzer.metrics import (
    compute_plane_deviation,
    compute_rotation_metrics,
    compute_stability_metrics,
    compute_tempo,
)
from swing_analyzer.scoring import compute_final_score
from swing_analyzer.overlay import create_overlay_video

from database import init_db, save_session, get_history


# ---------------------------------------------------
# Create FastAPI app
# ---------------------------------------------------
app = FastAPI(
    title="SmartSwing API",
    version="1.0.0",
    # UI / Docs customization only – logic unchanged
    swagger_ui_parameters={
        # Collapse the huge "Schemas" section by default
        "defaultModelsExpandDepth": -1,
        "defaultModelExpandDepth": 1,
        "displayRequestDuration": True,
        "syntaxHighlight": True,
        "syntaxHighlight.theme": "monokai",
        # Inline custom CSS to make the UI look like a polished SmartSwing app
        "customCss": """
        body {
            background: #020617; /* slate-950 */
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .swagger-ui .topbar {
            background: linear-gradient(90deg, #16a34a, #22c55e); /* SmartSwing green */
            padding: 10px 24px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.25);
        }

        .swagger-ui .topbar-wrapper .link span {
            font-weight: 700;
            font-size: 20px;
            letter-spacing: 0.03em;
        }

        .swagger-ui .topbar-wrapper .link span:before {
            content: "SmartSwing · ";
            font-weight: 600;
            color: #bbf7d0;
        }

        /* Main background + card look */
        .swagger-ui .wrapper {
            padding-top: 30px;
        }

        .swagger-ui .opblock {
            border-radius: 18px;
            border: 1px solid #1f2937;
            box-shadow: 0 18px 40px rgba(15,23,42,0.55);
            overflow: hidden;
            background: #020617;
        }

        .swagger-ui .opblock-summary {
            padding: 14px 20px;
        }

        .swagger-ui .opblock-body {
            background: #020617;
        }

        .swagger-ui .opblock-tag {
            font-size: 18px;
            font-weight: 600;
            color: #e5e7eb;
        }

        /* Better "Try it out" + Execute buttons */
        .swagger-ui .btn.execute {
            background-color: #16a34a;
            border-radius: 999px;
            padding: 6px 18px;
            border: none;
        }
        .swagger-ui .btn.execute:hover {
            background-color: #22c55e;
        }

        .swagger-ui .btn.try-out__btn {
            border-radius: 999px;
        }

        /* INPUTS / SELECTS */
        .swagger-ui input[type="text"],
        .swagger-ui input[type="search"],
        .swagger-ui textarea,
        .swagger-ui select {
            background: #020617;
            border-radius: 10px;
            border: 1px solid #1f2937;
            color: #e5e7eb;
        }

        .swagger-ui input::placeholder,
        .swagger-ui textarea::placeholder {
            color: #6b7280;
        }

        /* 🔥 CODE / JSON BLOCKS – main issue from your screenshot */
        .swagger-ui .microlight,        /* request/response examples */
        .swagger-ui pre {
            background: #020617;       /* dark slate */
            border-radius: 14px;
            border: 1px solid #1f2937;
            padding: 14px 16px;
            font-size: 13px;
            line-height: 1.5;
            font-family: "JetBrains Mono", "Fira Code", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            color: #e5e7eb;
            overflow-x: auto;
        }

        .swagger-ui code {
            font-family: inherit;
        }

        /* Make keywords softer and less "screaming"  */
        .swagger-ui .microlight .k,
        .swagger-ui .microlight .kn,
        .swagger-ui .microlight .kc {
            color: #a5b4fc; /* soft indigo */
        }

        .swagger-ui .microlight .s,
        .swagger-ui .microlight .s2 {
            color: #f97316; /* warm orange for strings */
        }

        .swagger-ui .microlight .mi,
        .swagger-ui .microlight .mf {
            color: #38bdf8; /* cyan numbers */
        }

        /* SCHEMA / MODELS PANEL – less noisy */
        .swagger-ui .models {
            background: transparent;
            border-radius: 18px;
            border: 1px solid #1f2937;
            box-shadow: 0 12px 30px rgba(15,23,42,0.55);
            margin-top: 24px;
        }

        .swagger-ui .model-container {
            background: #020617;
        }

        .swagger-ui .model-box {
            border-radius: 12px;
        }

        /* Headings + text colors */
        .swagger-ui h2,
        .swagger-ui h3,
        .swagger-ui h4 {
            color: #e5e7eb;
        }

        .swagger-ui .info .title {
            font-size: 26px;
            font-weight: 700;
            color: #e5e7eb;
        }

        .swagger-ui .info p,
        .swagger-ui .opblock-description-wrapper p,
        .swagger-ui .response-col_description__inner p {
            color: #9ca3af;
        }

        /* Make layout more compact on mobile */
        @media (max-width: 768px) {
            .swagger-ui .wrapper {
                padding: 12px;
            }

            .swagger-ui .opblock {
                margin-bottom: 18px;
            }
        }
        """
    },
)


# Initialize SQLite DB on startup
init_db()


# ---------------------------------------------------
# Root route (so / is not "Not Found")
# ---------------------------------------------------
@app.get("/")
def home():
    return {"message": "SmartSwing API is running"}


# ---------------------------------------------------
# Analyze Swing Endpoint
# ---------------------------------------------------
@app.post("/analyze_swing")
async def analyze_swing(video: UploadFile = File(...), user_id: str = "user1"):
    """
    Upload a golf swing video and get:
    - swing phases (address, top, impact)
    - plane deviation
    - rotation metrics
    - stability metrics
    - tempo
    - final 0–100 score
    - path to overlay video
    """

    try:
        # 1. Save uploaded video to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(await video.read())
            video_path = tmp.name

        # 2. Extract frames
        frames = iter_video_frames(video_path)

        if not frames:
            return JSONResponse({"error": "Could not read frames from video"}, status_code=400)

        # 3. Pose estimation for each frame
        poses = extract_pose_keypoints(frames)

        # 4. Detect swing start & end
        start_f, end_f = detect_swing_segment(poses)
        if start_f is None or end_f is None:
            return JSONResponse({"error": "No swing detected"}, status_code=400)

        # 5. Key phases: address, top, impact
        phases = estimate_key_phases(poses, start_f, end_f)
        addr = phases["address"]
        top = phases["top"]
        impact = phases["impact"]

        # 6. Metric frames
        frames_back = list(range(addr, top)) if top > addr else [addr]
        frames_down = list(range(top, impact)) if impact > top else [top]

        # 7. Compute metrics
        plane_dev = compute_plane_deviation(poses, frames_back, frames_down)
        rotation = compute_rotation_metrics(poses, addr, top)
        stability = compute_stability_metrics(poses, addr, sorted(poses.keys()))
        tempo = compute_tempo(addr, top, impact)

        # 8. Compute score
        score = compute_final_score(plane_dev, rotation, stability, tempo)

        # 8.5 Detect issues / coaching tips
        issues = summarize_errors(plane_dev, rotation, stability, tempo)


        # 9. Generate overlay video with skeleton + phases
        output_video_path = video_path.replace(".mp4", "_overlay.mp4")
        create_overlay_video(frames, poses, phases, output_video_path)

        # 10. Save session in DB
        save_session(
            user_id=user_id,
            score=score["total_score"],
            plane_dev=plane_dev,
            rotation=rotation,
            stability=stability,
            tempo=tempo,
            phases=phases,
            overlay_path=output_video_path,
        )

        # 11. Return response
        return {
            "user_id": user_id,
            "phases": phases,
            "plane_deviation": plane_dev,
            "rotation": rotation,
            "stability": stability,
            "tempo": tempo,
            "score": score,
            "issues": issues,               
            "overlay_video_path": output_video_path,
        }



    except Exception as e:
        # catch-all error to avoid crashing server
        return JSONResponse({"error": str(e)}, status_code=500)


# ---------------------------------------------------
# History Endpoint
# ---------------------------------------------------
@app.get("/history")
def history(user_id: str = "user1"):
    """
    Get all past swing sessions for a user.
    Useful for plotting progress over time.
    """
    data = get_history(user_id)
    return {"user_id": user_id, "history": data}


# ---------------------------------------------------
# Run with: uvicorn main:app --reload
# ---------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

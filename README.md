# Smartswing-
SmartSwing – AI-Powered Golf Swing Analyzer

A mobile-first computer vision system for real-time golf swing analysis.

🎯 Overview

SmartSwing is an AI-powered golf swing analysis system that helps golfers understand and improve their swing mechanics using only a smartphone camera.
The system automatically detects the swing, extracts pose keypoints, computes biomechanical metrics, identifies common swing faults, and provides a 0–100 swing accuracy score—no expensive hardware or sensors required.

This project was built as part of an assignment involving computer vision, pose estimation, data analytics, and UI/UX design.

🚀 Key Features
🎥 1. Automated Swing Detection

Detects the start and end of the swing from raw video.

Works with single-view face-on or down-the-line recordings.

🏌️‍♂️ 2. Pose Estimation

Uses MediaPipe Pose to extract keypoints (shoulders, hips, wrists, elbows, head, knees).

Accurate frame-by-frame skeleton generation.

📊 3. Biomechanical Metrics

Computes essential performance metrics:

Swing Plane Deviation

Shoulder & Hip Rotation

X-Factor

Head Movement

Lateral Hip Sway

Tempo Ratio (backswing : downswing)

🧮 4. Swing Scoring (0–100)

Weighted scoring based on:

Plane (30 points)

Rotation (30 points)

Stability (30 points)

Tempo (10 points)

🧠 5. Error Detection & Coaching Tips

Identifies common swing faults:

Over-the-top downswing

Limited rotation

Excessive sway

Unstable head movement

Tempo imbalance

Each issue generates a clear, actionable improvement suggestion.

🎨 6. Visual Overlay Video

Pose skeleton + club path + phase labels (ADDRESS / TOP / IMPACT)

Helps golfers visualize movement patterns.

🗂️ 7. Progress Tracking

SQLite database stores each session.

Users can monitor improvement over time.

🌐 8. Custom Web UI

Accessible via /ui, featuring:

Clean SmartSwing-themed design

Video upload

Score + metrics display

Coaching cues

History viewer

Raw JSON response viewer

🏗️ System Architecture
User Uploads Video
        ↓
Video Frame Sampling (OpenCV)
        ↓
Pose Estimation (MediaPipe)
        ↓
Swing Segmentation (Wrist Movement)
        ↓
Key Phase Detection (Address, Top, Impact)
        ↓
Biomechanical Metrics + Tempo Analysis
        ↓
Final Scoring (0–100)
        ↓
Error Detection (Rule-Based)
        ↓
Overlay Video Generation
        ↓
DB Storage & History Tracking

📁 Repository Structure
├── main.py                  # FastAPI server + UI route (/ui)
├── database.py              # SQLite DB handling
├── smartswing.db            # Stored history
│
├── swing_analyzer/
│   ├── video_utils.py       # Frame sampling
│   ├── pose_extractor.py    # MediaPipe keypoint extraction
│   ├── swing_phases.py      # Swing detection + key phases
│   ├── metrics.py           # Plane, rotation, stability, tempo
│   ├── scoring.py           # Final scoring logic
│   ├── error_detection.py   # Coaching cue generation
│   ├── overlay.py           # Skeleton + phase overlay video
│
└── README.md

⚙️ Installation & Setup
1. Clone the Repository
git clone https://github.com/your-username/SmartSwing.git
cd SmartSwing

2. Create a Virtual Environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Run the Server
uvicorn main:app --reload

🖥️ Usage
Open the Custom SmartSwing UI:
http://localhost:8000/ui

Upload a swing video (.mp4)

→ System analyzes swing, displays results, generates coaching tips, and saves session history.

API Docs (Swagger):
http://localhost:8000/docs

Endpoints:
POST /analyze_swing

Upload a video and receive:

phases

metrics

scores

coaching tips

overlay video path

GET /history

Retrieve past swing sessions for progress tracking.

📽️ Sample Output (Screenshots)

Add these after running the UI:

Swing score dashboard

Metrics display

Coaching cues

Overlay skeleton video

History JSON

(Place screenshots here in your GitHub repo)

🧪 Technologies Used

FastAPI – Backend API

MediaPipe – Pose estimation

OpenCV – Video processing

NumPy – Numerical computation

SQLite – Lightweight storage

HTML/CSS/JS – Custom UI

Uvicorn – Local server

📌 Future Improvements

Add clubhead speed estimation

Integrate smartphone motion sensor data

Build progressive web app version

Add 3D pose estimation (moveNet 3D)

Cloud sync for history & user profiles

📄 License

This project is created for academic and demonstration purposes.
You may modify or extend it with attribution.

🙋‍♂️ Author

Harshit Tiwari

Feel free to fork, submit issues, or contribute enhancements!

If you want, I can also generate:

✅ requirements.txt
✅ A GitHub-friendly preview.gif
✅ Short description for repo sidebar

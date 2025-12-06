# database.py
import sqlite3
import json

DB_PATH = "smartswing.db"


def init_db():
    """Create tables if not exist."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp TEXT,
            score REAL,
            plane_dev REAL,
            rotation_json TEXT,
            stability_json TEXT,
            tempo REAL,
            phases_json TEXT,
            overlay_path TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_session(user_id, score, plane_dev, rotation, stability, tempo, phases, overlay_path):
    """Store one swing analysis result."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO sessions (
            user_id, timestamp, score, plane_dev,
            rotation_json, stability_json, tempo,
            phases_json, overlay_path
        )
        VALUES (
            ?, datetime('now'), ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        user_id,
        score,
        plane_dev,
        json.dumps(rotation),
        json.dumps(stability),
        tempo,
        json.dumps(phases),
        overlay_path
    ))

    conn.commit()
    conn.close()


def get_history(user_id):
    """Retrieve all swing sessions for given user."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT timestamp, score, plane_dev, rotation_json,
               stability_json, tempo, phases_json
        FROM sessions
        WHERE user_id = ?
        ORDER BY timestamp ASC
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    history = []
    for r in rows:
        history.append({
            "timestamp": r[0],
            "score": r[1],
            "plane_dev": r[2],
            "rotation": json.loads(r[3]),
            "stability": json.loads(r[4]),
            "tempo": r[5],
            "phases": json.loads(r[6]),
        })
    return history
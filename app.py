"""Quick Note Application - Flask backend + SQLite storage."""
import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, g, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("NOTES_DB", os.path.join(BASE_DIR, "notes.db"))
MAX_NOTE_LENGTH = 5000

app = Flask(__name__, static_folder="static", static_url_path="/static")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                content    TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def row_to_dict(row):
    return {"id": row["id"], "content": row["content"], "created_at": row["created_at"]}


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/notes")
def list_notes():
    rows = get_db().execute(
        "SELECT id, content, created_at FROM notes ORDER BY id DESC"
    ).fetchall()
    return jsonify([row_to_dict(r) for r in rows])


@app.post("/api/notes")
def create_note():
    data = request.get_json(silent=True) or {}
    content = data.get("content")
    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "Note can't be empty."}), 400
    content = content.strip()
    if len(content) > MAX_NOTE_LENGTH:
        return jsonify({"error": f"Note is too long (max {MAX_NOTE_LENGTH} characters)."}), 400

    created_at = datetime.now(timezone.utc).isoformat()
    db = get_db()
    cur = db.execute(
        "INSERT INTO notes (content, created_at) VALUES (?, ?)", (content, created_at)
    )
    db.commit()
    return jsonify({"id": cur.lastrowid, "content": content, "created_at": created_at}), 201


@app.delete("/api/notes/<int:note_id>")
def delete_note(note_id):
    db = get_db()
    cur = db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Note not found."}), 404
    return "", 204


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=True)
# Quick Note Application (task1)

Single-page app: write a note, send it to a Python (Flask) backend, store it in SQLite, and see it listed on the same page.

## Request–response flow
1. Browser `POST /api/notes` with JSON `{"content": "..."}`.
2. Flask validates it, inserts a row into SQLite, returns the saved note (`201`).
3. The page prepends the returned note to the list. On load, `GET /api/notes` fills the list.

## Run
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## API
| Method | Path | Description |
|---|---|---|
| GET | `/api/notes` | List notes, newest first |
| POST | `/api/notes` | Create a note (`content`, max 5000 chars) |
| DELETE | `/api/notes/<id>` | Delete a note |

## Known limitations
- No authentication: every visitor sees the same notes.
- SQLite and the Flask dev server are for local use only.
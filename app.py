from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "rsvp.sqlite3"

EVENT_CONFIG = {
    "couple_names": "Hortense & Benoit",
    "wedding_date": "28 août 2027",
    "ceremony_time": "16h00",
    "venue": "Tarascon",
    "response_deadline": "31 mai 2026",
    "hero_message": "Nous serions ravis de célébrer cette journée avec vous.",
}

ALLOWED_ATTENDANCE = {"yes", "no", "maybe"}
STATIC_CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
}


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS rsvps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                attendance TEXT NOT NULL CHECK(attendance IN ('yes', 'no', 'maybe')),
                guest_count INTEGER NOT NULL DEFAULT 1,
                dietary_requirements TEXT,
                song_request TEXT,
                message TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def normalize_text(value: object, max_length: int = 500) -> str:
    if value is None:
        return ""
    cleaned = str(value).strip()
    return cleaned[:max_length]


def parse_guest_count(value: object, attendance: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = 1 if attendance == "yes" else 0

    if attendance == "yes":
        return min(max(parsed, 1), 10)
    if attendance == "maybe":
        return min(max(parsed, 1), 10)
    return 0


def validate_payload(payload: dict[str, object]) -> dict[str, object]:
    full_name = normalize_text(payload.get("full_name"), 120)
    email = normalize_text(payload.get("email"), 160).lower()
    phone = normalize_text(payload.get("phone"), 40)
    attendance = normalize_text(payload.get("attendance"), 16)
    dietary_requirements = normalize_text(payload.get("dietary_requirements"), 500)
    song_request = normalize_text(payload.get("song_request"), 160)
    message = normalize_text(payload.get("message"), 600)

    if not full_name:
        raise ValueError("Le nom complet est obligatoire.")
    if "@" not in email or "." not in email:
        raise ValueError("Une adresse e-mail valide est obligatoire.")
    if attendance not in ALLOWED_ATTENDANCE:
        raise ValueError("Le statut de présence est invalide.")

    guest_count = parse_guest_count(payload.get("guest_count"), attendance)

    return {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "attendance": attendance,
        "guest_count": guest_count,
        "dietary_requirements": dietary_requirements,
        "song_request": song_request,
        "message": message,
    }


def save_rsvp(payload: dict[str, object]) -> None:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO rsvps (
                full_name,
                email,
                phone,
                attendance,
                guest_count,
                dietary_requirements,
                song_request,
                message,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                full_name = excluded.full_name,
                phone = excluded.phone,
                attendance = excluded.attendance,
                guest_count = excluded.guest_count,
                dietary_requirements = excluded.dietary_requirements,
                song_request = excluded.song_request,
                message = excluded.message,
                updated_at = excluded.updated_at
            """,
            (
                payload["full_name"],
                payload["email"],
                payload["phone"],
                payload["attendance"],
                payload["guest_count"],
                payload["dietary_requirements"],
                payload["song_request"],
                payload["message"],
                now,
                now,
            ),
        )


def fetch_dashboard_data() -> dict[str, object]:
    with get_connection() as connection:
        responses = connection.execute(
            """
            SELECT
                id,
                full_name,
                email,
                phone,
                attendance,
                guest_count,
                dietary_requirements,
                song_request,
                message,
                created_at,
                updated_at
            FROM rsvps
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()

    serialized = [dict(row) for row in responses]
    summary = {
        "total_responses": len(serialized),
        "confirmed_households": sum(1 for row in serialized if row["attendance"] == "yes"),
        "declined_households": sum(1 for row in serialized if row["attendance"] == "no"),
        "tentative_households": sum(1 for row in serialized if row["attendance"] == "maybe"),
        "confirmed_guests": sum(row["guest_count"] for row in serialized if row["attendance"] == "yes"),
    }
    return {"summary": summary, "responses": serialized}


class RSVPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self.serve_static_file("index.html")
            return
        if parsed.path == "/dashboard":
            self.serve_static_file("dashboard.html")
            return
        if parsed.path.startswith("/static/"):
            relative_path = parsed.path.removeprefix("/static/")
            self.serve_static_file(relative_path)
            return
        if parsed.path == "/api/event":
            self.send_json(EVENT_CONFIG)
            return
        if parsed.path == "/api/rsvps":
            self.send_json(fetch_dashboard_data())
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Page introuvable.")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path != "/api/rsvp":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint introuvable.")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
            validated = validate_payload(payload)
            save_rsvp(validated)
        except json.JSONDecodeError:
            self.send_json({"error": "Le corps de la requête doit être au format JSON."}, HTTPStatus.BAD_REQUEST)
            return
        except ValueError as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        except sqlite3.DatabaseError:
            self.send_json(
                {"error": "Une erreur base de données est survenue lors de l'enregistrement."},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return

        self.send_json({"ok": True, "message": "Votre RSVP a bien été enregistré."}, HTTPStatus.CREATED)

    def serve_static_file(self, relative_path: str) -> None:
        safe_relative_path = Path(relative_path)
        file_path = (STATIC_DIR / safe_relative_path).resolve()

        if STATIC_DIR not in file_path.parents and file_path != STATIC_DIR:
            self.send_error(HTTPStatus.FORBIDDEN, "Accès refusé.")
            return
        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Fichier introuvable.")
            return

        content_type = STATIC_CONTENT_TYPES.get(file_path.suffix, "application/octet-stream")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(file_path.read_bytes())

    def send_json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def run() -> None:
    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), RSVPRequestHandler)
    print("RSVP Mariage disponible sur http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    run()

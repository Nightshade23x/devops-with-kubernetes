
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

import psycopg


PORT = int(os.environ.get("PORT", 3000))

DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ["DB_PORT"])
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]


def connect():
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=5,
    )


def initialize_database(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ping_count (
            id INTEGER PRIMARY KEY,
            value INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        INSERT INTO ping_count (id, value)
        VALUES (1, 0)
        ON CONFLICT (id) DO NOTHING
    """)


class Handler(BaseHTTPRequestHandler):
    def send_text(self, status, text):
        body = text.encode()

        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_text(200, "OK")
            return

        if self.path not in ("/", "/pings", "/ready"):
            self.send_error(404)
            return

        try:
            with connect() as connection:
                with connection.cursor() as cursor:
                    initialize_database(cursor)

                    if self.path == "/ready":
                        cursor.execute(
                            "SELECT value FROM ping_count WHERE id = 1"
                        )
                        if cursor.fetchone() is None:
                            raise RuntimeError("Ping counter not initialized")
                        response = "Ready"

                    elif self.path == "/":
                        cursor.execute("""
                            UPDATE ping_count
                            SET value = value + 1
                            WHERE id = 1
                            RETURNING value
                        """)
                        count = cursor.fetchone()[0]
                        response = f"pong {count - 1}"

                    else:
                        cursor.execute(
                            "SELECT value FROM ping_count WHERE id = 1"
                        )
                        response = str(cursor.fetchone()[0])

        except (psycopg.Error, OSError, RuntimeError) as error:
            print(f"Database unavailable: {error}", flush=True)
            self.send_error(503, "Database unavailable")
            return

        self.send_text(200, response)


print(f"Server started on port {PORT}", flush=True)
HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

import json
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import psycopg

HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])
TODOS_PATH = os.environ["TODOS_PATH"]
_initialized = False
_init_lock = threading.Lock()


def connect():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
    )


def ensure_database():
    """Create or upgrade the existing table without deleting stored todos."""
    global _initialized
    if _initialized:
        return
    with _init_lock:
        if _initialized:
            return
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS todos (
                        id SERIAL PRIMARY KEY,
                        content VARCHAR(140) NOT NULL
                    )
                """)
                cursor.execute("""
                    ALTER TABLE todos
                    ADD COLUMN IF NOT EXISTS done BOOLEAN NOT NULL DEFAULT FALSE
                """)
                cursor.execute("SELECT COUNT(*) FROM todos")
                if cursor.fetchone()[0] == 0:
                    for todo in (
                        "Learn Kubernetes basics",
                        "Deploy application to cluster",
                        "Configure persistent volumes",
                    ):
                        cursor.execute(
                            "INSERT INTO todos (content) VALUES (%s)", (todo,)
                        )
        _initialized = True
        print("Database initialized or existing todos upgraded", flush=True)


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"status": "alive"})
            return
        if self.path not in ("/ready", TODOS_PATH):
            self.send_error(404)
            return
        try:
            ensure_database()
            with connect() as connection:
                with connection.cursor() as cursor:
                    if self.path == "/ready":
                        cursor.execute("SELECT done FROM todos LIMIT 1")
                        self.send_json(200, {"status": "ready"})
                    else:
                        cursor.execute(
                            "SELECT id, content, done FROM todos ORDER BY id"
                        )
                        todos = [
                            {"id": row[0], "content": row[1], "done": row[2]}
                            for row in cursor.fetchall()
                        ]
                        self.send_json(200, todos)
        except (psycopg.Error, OSError) as error:
            print(f"Database unavailable: {error}", flush=True)
            self.send_json(503, {"error": "Database unavailable"})

    def do_POST(self):
        if self.path != TODOS_PATH:
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 10000:
                raise ValueError("Invalid body length")
            data = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            print("TODO_REJECTED reason=invalid_json", flush=True)
            self.send_json(400, {"error": "Invalid JSON"})
            return

        if not isinstance(data, dict) or not isinstance(data.get("todo"), str):
            print("TODO_REJECTED reason=invalid_todo", flush=True)
            self.send_json(400, {"error": "Invalid todo"})
            return

        todo = data["todo"].strip()
        print(
            f"TODO_RECEIVED length={len(todo)} "
            f"content={json.dumps(todo, ensure_ascii=False)}",
            flush=True,
        )
        if not todo or len(todo) > 140:
            print(f"TODO_REJECTED reason=invalid_length length={len(todo)}", flush=True)
            self.send_json(400, {"error": "Todo must have 1-140 characters"})
            return

        try:
            ensure_database()
            with connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO todos (content) VALUES (%s) RETURNING id",
                        (todo,),
                    )
                    todo_id = cursor.fetchone()[0]
            print(
                f"TODO_SAVED id={todo_id} content={json.dumps(todo, ensure_ascii=False)}",
                flush=True,
            )
            self.send_json(201, {"id": todo_id, "todo": todo, "done": False})
        except (psycopg.Error, OSError) as error:
            print(f"TODO_FAILED database_error={error}", flush=True)
            self.send_json(503, {"error": "Database unavailable"})

    def do_PUT(self):
        # The exercise uses PUT /todos/<id> to mark an existing todo as done.
        match = re.fullmatch(re.escape(TODOS_PATH) + r"/([1-9][0-9]*)", self.path)
        if match is None:
            self.send_error(404)
            return
        todo_id = int(match.group(1))
        try:
            ensure_database()
            with connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE todos SET done = TRUE WHERE id = %s
                        RETURNING id, content, done
                        """,
                        (todo_id,),
                    )
                    row = cursor.fetchone()
            if row is None:
                self.send_json(404, {"error": "Todo not found"})
                return
            print(f"TODO_DONE id={todo_id}", flush=True)
            self.send_json(
                200, {"id": row[0], "content": row[1], "done": row[2]}
            )
        except (psycopg.Error, OSError) as error:
            print(f"TODO_UPDATE_FAILED database_error={error}", flush=True)
            self.send_json(503, {"error": "Database unavailable"})


print(f"Todo backend running on port {PORT}", flush=True)
ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

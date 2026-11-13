
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

import psycopg


HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])
TODOS_PATH = os.environ["TODOS_PATH"]


def connect():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
    )


def initialize_database():
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    content VARCHAR(140) NOT NULL
                )
            """)

            cursor.execute("SELECT COUNT(*) FROM todos")
            if cursor.fetchone()[0] == 0:
                for todo in [
                    "Learn Kubernetes basics",
                    "Deploy application to cluster",
                    "Configure persistent volumes",
                ]:
                    cursor.execute(
                        "INSERT INTO todos (content) VALUES (%s)",
                        (todo,),
                    )


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != TODOS_PATH:
            self.send_error(404)
            return

        try:
            with connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT content FROM todos ORDER BY id"
                    )
                    todos = [row[0] for row in cursor.fetchall()]

            self.send_json(200, todos)

        except psycopg.Error as error:
            print(error, flush=True)
            self.send_error(503, "Database unavailable")

    
    def do_POST(self):
        if self.path != TODOS_PATH:
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            print("TODO_REJECTED reason=invalid_json", flush=True)
            self.send_error(400, "Invalid JSON")
            return

        if not isinstance(data, dict) or not isinstance(data.get("todo"), str):
            print("TODO_REJECTED reason=invalid_todo", flush=True)
            self.send_error(400, "Invalid todo")
            return

        todo = data["todo"].strip()

        print(
            f"TODO_RECEIVED length={len(todo)} "
            f"content={json.dumps(todo, ensure_ascii=False)}",
            flush=True
        )

        if not todo or len(todo) > 140:
            print(
                f"TODO_REJECTED reason=invalid_length "
                f"length={len(todo)} "
                f"content={json.dumps(todo, ensure_ascii=False)}",
                flush=True
            )
            self.send_error(400, "Todo must have 1-140 characters")
            return

        try:
            with connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO todos (content) VALUES (%s)",
                        (todo,)
                    )

            print(
                f"TODO_SAVED content={json.dumps(todo, ensure_ascii=False)}",
                flush=True
            )

            self.send_json(201, {"todo": todo})

        except psycopg.Error as error:
            print(f"TODO_FAILED database_error={error}", flush=True)
            self.send_error(503, "Database unavailable")



initialize_database()

print(f"Todo backend running on port {PORT}", flush=True)

HTTPServer((HOST, PORT), Handler).serve_forever()


import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
PORT = int(os.environ["PORT"])
HOST = os.environ["HOST"]
TODOS_PATH = os.environ["TODOS_PATH"]
todos = [
    "Learn Kubernetes basics",
    "Deploy application to cluster",
    "Configure persistent volumes"
]

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != TODOS_PATH:
            self.send_error(404)
            return

        self.respond(200, todos)

    def do_POST(self):
        if self.path != TODOS_PATH:
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            todo = data["todo"].strip()

            if not 0 < len(todo) <= 140:
                self.send_error(400, "Todo must be 1-140 characters")
                return

        except (ValueError, KeyError, AttributeError, TypeError):
            self.send_error(400, "Invalid todo")
            return

        todos.append(todo)
        self.respond(201, {"todo": todo})

    def respond(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

print(f"Todo backend started on port {PORT}", flush=True)
HTTPServer((HOST, PORT), Handler).serve_forever()

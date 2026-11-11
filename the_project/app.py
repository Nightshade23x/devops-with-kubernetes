
import os
import time
from pathlib import Path
from urllib.request import urlopen
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ["PORT"])
HOST = os.environ["HOST"]
IMAGE = Path(os.environ["IMAGE_FILE"])
CACHE_TIME = int(os.environ["CACHE_SECONDS"])
PICSUM_URL = os.environ["PICSUM_URL"]
TODO_PAGE_PATH = os.environ["TODO_PAGE_PATH"]
IMAGE_ROUTE = os.environ["IMAGE_ROUTE"]
TODOS_PATH = os.environ["TODOS_PATH"]


def get_image():
    if not IMAGE.exists() or time.time() - IMAGE.stat().st_mtime >= CACHE_TIME:
        url = f"{PICSUM_URL}?random={time.time_ns()}"

        try:
            with urlopen(url, timeout=15) as response:
                image = response.read()

            temporary = IMAGE.with_suffix(".tmp")
            temporary.write_bytes(image)
            temporary.replace(IMAGE)
        except Exception:
            if not IMAGE.exists():
                raise

    return IMAGE.read_bytes()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", TODO_PAGE_PATH, TODO_PAGE_PATH + "/"):
            content = b"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Todo App</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 700px;
                        margin: 40px auto;
                        text-align: center;
                    }
                    img {
                        width: 80%;
                        max-width: 500px;
                        border-radius: 8px;
                    }
                    .form {
                        display: flex;
                        gap: 10px;
                        margin-top: 30px;
                    }
                    input {
                        flex: 1;
                        padding: 12px;
                    }
                    button {
                        padding: 12px 20px;
                        cursor: pointer;
                    }
                    li {
                        text-align: left;
                        padding: 12px;
                        margin: 8px 0;
                        background: #f5f5f5;
                        border-left: 4px solid green;
                        list-style: none;
                    }
                    ul { padding: 0; }
                </style>
            </head>
            <body>
                <h1>Todo App</h1>
                <img src="__IMAGE_ROUTE__" alt="Random image">

                <form class="form" id="todo-form">
                    <input id="todo-input" type="text"
                           maxlength="140" required
                           placeholder="Enter a new todo (max 140 characters)">
                    <button type="submit">Send</button>
                </form>

                <h2>Todos</h2>
                <ul id="todo-list"></ul>

                <p>DevOps with Kubernetes 2026</p>

                <script>
                    async function loadTodos() {
                        const response = await fetch("__TODOS_PATH__");
                        if (!response.ok) throw new Error("Could not load todos");
                        const todos = await response.json();

                        const list = document.getElementById("todo-list");
                        list.replaceChildren();

                        todos.forEach(todo => {
                            const item = document.createElement("li");
                            item.textContent = todo;
                            list.appendChild(item);
                        });
                    }

                    document.getElementById("todo-form")
                        .addEventListener("submit", async (event) => {
                            event.preventDefault();

                            const input = document.getElementById("todo-input");
                            const todo = input.value.trim();
                            if (!todo || todo.length > 140) return;

                            try {
                                const response = await fetch("/todos", {
                                    method: "POST",
                                    headers: {"Content-Type": "application/json"},
                                    body: JSON.stringify({todo: todo})
                                });

                                if (!response.ok) throw new Error("Could not add todo");

                                input.value = "";
                                await loadTodos();
                            } catch (error) {
                                alert(error.message);
                            }
                        });

                    loadTodos().catch(error => alert(error.message));
                </script>
            </body>
            </html>
            """
            content = content.replace(
                b"__IMAGE_ROUTE__", IMAGE_ROUTE.encode()
            )
            content = content.replace(
                b"__TODOS_PATH__", TODOS_PATH.encode()
            )
            self.respond(200, "text/html", content)

        elif self.path == IMAGE_ROUTE:
            try:
                self.respond(200, "image/jpeg", get_image())
            except Exception:
                self.respond(503, "text/plain", b"Image unavailable")

        else:
            self.send_error(404)

    def respond(self, status, content_type, content):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


print(f"Server started in port {PORT}", flush=True)
HTTPServer((HOST, PORT), Handler).serve_forever()

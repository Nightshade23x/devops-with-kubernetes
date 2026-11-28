import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen

PORT = int(os.environ["PORT"])
HOST = os.environ["HOST"]
IMAGE = Path(os.environ["IMAGE_FILE"])
CACHE_TIME = int(os.environ["CACHE_SECONDS"])
PICSUM_URL = os.environ["PICSUM_URL"]
TODO_PAGE_PATH = os.environ["TODO_PAGE_PATH"]
IMAGE_ROUTE = os.environ["IMAGE_ROUTE"]
TODOS_PATH = os.environ["TODOS_PATH"]
BACKEND_READY_URL = os.environ.get(
    "BACKEND_READY_URL", "http://todo-backend:3000/ready"
)

# The break button changes only process memory; restarting the container repairs it.
is_healthy = True


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


FAILURE_PAGE = b"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><title>System Failure</title>
<style>
body { font-family: Arial, sans-serif; background: #fff6f6; text-align: center; padding: 60px 20px; }
.panel { max-width: 700px; margin: auto; padding: 40px; background: #fee2e2;
         border: 1px solid #f5a5a5; border-radius: 10px; color: #8b1b1b; }
h1 { font-size: 42px; }
</style>
</head>
<body><div class="panel"><h1>System Failure</h1>
<p>The Todo App is currently unhealthy. Please wait for recovery.</p>
</div></body></html>"""


TODO_PAGE = b"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Todo App</title>
<style>
body { font-family: Arial, sans-serif; max-width: 700px; margin: 40px auto; text-align: center; }
img { width: 80%; max-width: 500px; border-radius: 8px; }
.form { display: flex; gap: 10px; margin-top: 30px; }
input { flex: 1; padding: 12px; }
button { padding: 12px 20px; cursor: pointer; }
li { text-align: left; padding: 12px; margin: 8px 0; background: #f5f5f5;
     border-left: 4px solid green; list-style: none;
     display: flex; align-items: center; justify-content: space-between; gap: 12px; }
li.done { border-left-color: #999; background: #ededed; }
.todo-text { overflow-wrap: anywhere; flex: 1; }
li.done .todo-text { text-decoration: line-through; color: #777; }
.mark-done { background: #1674d2; color: white; border: 0; border-radius: 4px; white-space: nowrap; }
.done-label { color: #278136; font-weight: bold; }
ul { padding: 0; }
#break-button { background: #d43636; color: white; border: 0; border-radius: 4px; margin-top: 18px; }
#error { color: #a11b1b; }
</style>
</head>
<body>
<h1>Todo App</h1>
<img src="__IMAGE_ROUTE__" alt="Random image">
<form class="form" id="todo-form">
  <input id="todo-input" type="text" maxlength="140" required
         placeholder="Enter a new todo (max 140 characters)">
  <button type="submit">Send</button>
</form>
<h2>Todos</h2>
<ul id="todo-list"></ul>
<p id="error" role="alert"></p>
<p>DevOps with Kubernetes 2026</p>
<button type="button" id="break-button">break the app</button>
<script>
async function loadTodos() {
  const response = await fetch("__TODOS_PATH__");
  if (!response.ok) throw new Error("Could not load todos");
  const todos = await response.json();
  const list = document.getElementById("todo-list");
  list.replaceChildren();
  todos.forEach(todo => {
    const item = document.createElement("li");
    if (todo.done) item.classList.add("done");

    const text = document.createElement("span");
    text.className = "todo-text";
    text.textContent = todo.content;
    item.appendChild(text);

    if (todo.done) {
      const doneLabel = document.createElement("span");
      doneLabel.className = "done-label";
      doneLabel.textContent = "Done";
      item.appendChild(doneLabel);
    } else {
      const button = document.createElement("button");
      button.className = "mark-done";
      button.type = "button";
      button.textContent = "Mark done";
      button.addEventListener("click", async () => {
        button.disabled = true;
        document.getElementById("error").textContent = "";
        try {
          const response = await fetch("__TODOS_PATH__/" + todo.id, {
            method: "PUT"
          });
          if (!response.ok) throw new Error("Could not mark todo as done");
          await loadTodos();
        } catch (error) {
          document.getElementById("error").textContent = error.message;
          button.disabled = false;
        }
      });
      item.appendChild(button);
    }
    list.appendChild(item);
  });
}

document.getElementById("todo-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("todo-input");
  const todo = input.value.trim();
  if (!todo || todo.length > 140) return;
  try {
    const response = await fetch("__TODOS_PATH__", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({todo: todo})
    });
    if (!response.ok) throw new Error("Could not add todo");
    input.value = "";
    await loadTodos();
  } catch (error) {
    document.getElementById("error").textContent = error.message;
  }
});

document.getElementById("break-button").addEventListener("click", async () => {
  const button = document.getElementById("break-button");
  button.disabled = true;
  try {
    const response = await fetch("/break", {method: "POST"});
    if (!response.ok) throw new Error("Unable to trigger failure");
    document.body.innerHTML = `
      <div style="font: 22px Arial; color: #8b1b1b; background: #fee2e2;
                  padding: 50px; margin: 40px auto; max-width: 700px;
                  text-align: center; border-radius: 10px;">
        <h1>System Failure</h1>
        <p>The Todo App is currently unhealthy. Please wait for recovery.</p>
      </div>`;
    setTimeout(() => window.location.reload(), 15000);
  } catch (error) {
    document.getElementById("error").textContent = error.message;
    button.disabled = false;
  }
});

loadTodos().catch(error => {
  document.getElementById("error").textContent = error.message;
});
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, content_type, content):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path == "/health":
            status = 200 if is_healthy else 500
            self.respond(status, "text/plain", b"OK" if is_healthy else b"Unhealthy")
            return

        if self.path == "/ready":
            if not is_healthy:
                self.respond(503, "text/plain", b"Unhealthy")
                return
            try:
                with urlopen(BACKEND_READY_URL, timeout=3) as response:
                    if response.status != 200:
                        raise RuntimeError("Backend not ready")
            except Exception as error:
                print(f"Frontend not ready: {error}", flush=True)
                self.respond(503, "text/plain", b"Backend unavailable")
                return
            self.respond(200, "text/plain", b"Ready")
            return

        if not is_healthy:
            self.respond(503, "text/html; charset=utf-8", FAILURE_PAGE)
            return

        if self.path in ("/", TODO_PAGE_PATH, TODO_PAGE_PATH + "/"):
            page = TODO_PAGE.replace(b"__IMAGE_ROUTE__", IMAGE_ROUTE.encode())
            page = page.replace(b"__TODOS_PATH__", TODOS_PATH.encode())
            self.respond(200, "text/html; charset=utf-8", page)
        elif self.path == IMAGE_ROUTE:
            try:
                self.respond(200, "image/jpeg", get_image())
            except Exception as error:
                print(f"Image unavailable: {error}", flush=True)
                self.respond(503, "text/plain", b"Image unavailable")
        else:
            self.send_error(404)

    def do_POST(self):
        global is_healthy
        if self.path != "/break":
            self.send_error(404)
            return
        if not is_healthy:
            self.respond(503, "text/plain", b"Already unhealthy")
            return
        is_healthy = False
        print("BREAK_TRIGGERED: frontend deliberately unhealthy", flush=True)
        self.respond(200, "text/plain", b"App marked unhealthy")


print(f"Todo frontend running on port {PORT}", flush=True)
ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

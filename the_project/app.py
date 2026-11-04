
import os
import time
from pathlib import Path
from urllib.request import urlopen
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 3000))
IMAGE = Path("/data/image.jpg")
CACHE_TIME = 600  # 10 minutes


def get_image():
    if not IMAGE.exists() or time.time() - IMAGE.stat().st_mtime >= CACHE_TIME:
        url = f"https://picsum.photos/800/500.jpg?random={time.time_ns()}"

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
        
        if self.path in ("/", "/todo", "/todo/"):
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
                    ul {
                        padding: 0;
                    }
                </style>
            </head>
            <body>
                <h1>Todo App</h1>

                <img src="/todo/image" alt="Random image">

                <div class="form">
                    <input type="text"
                           maxlength="140"
                           placeholder="Enter a new todo (max 140 characters)">
                    <button type="button">Send</button>
                </div>

                <h2>Todos</h2>

                <ul>
                    <li>Learn Kubernetes basics</li>
                    <li>Deploy application to cluster</li>
                    <li>Configure persistent volumes</li>
                </ul>

                <p>DevOps with Kubernetes 2026</p>
            </body>
            </html>
            """
            self.respond(200, "text/html", content)


        elif self.path == "/todo/image":
            try:
                self.respond(200, "image/jpeg", get_image())
            except Exception as error:
                print(error, flush=True)
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
HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

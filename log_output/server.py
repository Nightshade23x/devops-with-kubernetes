
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

status_file = Path("/shared/status.txt")
count_file = Path("/data/count.txt")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return

        if not status_file.exists():
            self.send_error(503, "Status not ready")
            return

        status = status_file.read_text()
        count = count_file.read_text() if count_file.exists() else "0"

        response = f"{status}\nPing / Pongs: {count}"

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(response.encode())

print("Server started in port 3000", flush=True)
HTTPServer(("0.0.0.0", 3000), Handler).serve_forever()

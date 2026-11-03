
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

file_path = Path("/shared/status.txt")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return

        if not file_path.exists():
            self.send_error(503, "Status not ready")
            return

        response = file_path.read_text().encode()

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(response)

print("Server started in port 3000", flush=True)
HTTPServer(("0.0.0.0", 3000), Handler).serve_forever()

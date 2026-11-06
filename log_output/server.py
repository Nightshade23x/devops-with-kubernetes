
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.request import urlopen

status_file = Path("/shared/status.txt")
ping_url = "http://ping-pong:3000/pings"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return

        if not status_file.exists():
            self.send_error(503, "Status not ready")
            return

        try:
            with urlopen(ping_url, timeout=5) as response:
                count = response.read().decode()
        except Exception:
            self.send_error(503, "Ping-pong unavailable")
            return

        status = status_file.read_text()
        content = f"{status}\nPing / Pongs: {count}".encode()

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(content)

print("Server started in port 3000", flush=True)
HTTPServer(("0.0.0.0", 3000), Handler).serve_forever()

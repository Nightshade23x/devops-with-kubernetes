
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.request import urlopen

status_file = Path("/shared/status.txt")
info_file = Path("/config/information.txt")
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

            file_content = info_file.read_text().strip()
            message = os.environ["MESSAGE"]
            status = status_file.read_text().strip()

        except Exception as error:
            print(error, flush=True)
            self.send_error(503, "Data unavailable")
            return

        content = (
            f"file content: {file_content}\n"
            f"env variable: MESSAGE={message}\n"
            f"{status}\n"
            f"Ping / Pongs: {count}"
        ).encode()

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

print("Server started in port 3000", flush=True)
HTTPServer(("0.0.0.0", 3000), Handler).serve_forever()

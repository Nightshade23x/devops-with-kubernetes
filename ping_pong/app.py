
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 3000))
count_file = Path("/data/count.txt")

counter = int(count_file.read_text()) if count_file.exists() else 0

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global counter

        if self.path != "/pingpong":
            self.send_error(404)
            return

        response = f"pong {counter}"
        counter += 1
        count_file.write_text(str(counter))

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(response.encode())

print(f"Server started in port {PORT}", flush=True)
HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

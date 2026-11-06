
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 3000))
counter = 0

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global counter

        if self.path == "/pingpong":
            response = f"pong {counter}"
            counter += 1
        elif self.path == "/pings":
            response = str(counter)
        else:
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(response.encode())

print(f"Server started in port {PORT}", flush=True)
HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

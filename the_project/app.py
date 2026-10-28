
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 3000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

server = HTTPServer(("0.0.0.0", PORT), Handler)

print(f"Server started in port {PORT}", flush=True)

server.serve_forever()

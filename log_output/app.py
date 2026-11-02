
import uuid
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

random_string = str(uuid.uuid4())

def get_status():
    timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    return f"{timestamp}: {random_string}"

def print_logs():
    while True:
        print(get_status(), flush=True)
        time.sleep(5)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return

        response = get_status().encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(response)

Thread(target=print_logs, daemon=True).start()

HTTPServer(("0.0.0.0", 3000), Handler).serve_forever()

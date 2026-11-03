
import uuid
import time
from datetime import datetime, timezone
from pathlib import Path

random_string = str(uuid.uuid4())
file_path = Path("/shared/status.txt")

while True:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    status = f"{timestamp}: {random_string}"

    file_path.write_text(status)
    print(status, flush=True)

    time.sleep(5)

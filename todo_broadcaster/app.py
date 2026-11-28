import asyncio
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import nats

NATS_URL = os.environ.get("NATS_URL", "nats://todo-nats:4222")
NATS_SUBJECT = "todos.events"
QUEUE_GROUP = "todo-broadcasters"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")


def send_webhook(event):
    if not WEBHOOK_URL:
        print("WEBHOOK_SKIPPED: WEBHOOK_URL is not configured", flush=True)
        return
    kind = event.get("event")
    content = event.get("content")
    if kind not in ("created", "completed") or not isinstance(content, str):
        print("WEBHOOK_SKIPPED: invalid event", flush=True)
        return
    verb = "created" if kind == "created" else "completed"
    message = f"Todo {verb}: {content} (ID {event.get('id')})"
    body = json.dumps({"user": "bot", "message": message}).encode("utf-8")
    request = Request(
        WEBHOOK_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        # Exactly one attempt. No retry on timeout/HTTP failure: avoid duplicates.
        with urlopen(request, timeout=8) as response:
            print(
                f"WEBHOOK_SENT event={kind} id={event.get('id')} "
                f"status={response.status}", flush=True,
            )
    except (HTTPError, URLError, OSError, TimeoutError) as error:
        print(
            f"WEBHOOK_FAILED event={kind} id={event.get('id')}: {error}",
            flush=True,
        )


async def run():
    async def on_message(message):
        try:
            event = json.loads(message.data.decode("utf-8"))
            if not isinstance(event, dict):
                return
            print(
                f"NATS_RECEIVED event={event.get('event')} id={event.get('id')}",
                flush=True,
            )
            await asyncio.to_thread(send_webhook, event)
        except (UnicodeError, ValueError, TypeError) as error:
            print(f"NATS_INVALID_MESSAGE: {error}", flush=True)

    while True:
        try:
            nc = await nats.connect(servers=[NATS_URL], connect_timeout=2)
            await nc.subscribe(NATS_SUBJECT, queue=QUEUE_GROUP, cb=on_message)
            await nc.flush(timeout=3)
            print(f"Broadcaster subscribed to {NATS_SUBJECT} queue={QUEUE_GROUP}", flush=True)
            while not nc.is_closed:
                await asyncio.sleep(1)
        except Exception as error:
            print(f"NATS_DISCONNECTED: {error}", flush=True)
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(run())

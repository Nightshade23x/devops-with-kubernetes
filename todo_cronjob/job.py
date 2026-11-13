
import json
import os
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import (
    Request,
    HTTPRedirectHandler,
    build_opener,
    urlopen,
)


WIKIPEDIA_URL = os.environ["WIKIPEDIA_URL"]
TODO_API_URL = os.environ["TODO_API_URL"]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def get_random_article():
    opener = build_opener(NoRedirect)

    for _ in range(10):
        request = Request(
            WIKIPEDIA_URL,
            headers={
                "User-Agent": "KubernetesTodoCourse/1.0 (educational project)"
            },
        )

        try:
            with opener.open(request, timeout=20) as response:
                raise RuntimeError(
                    f"Expected Wikipedia redirect, got {response.status}"
                )

        except HTTPError as error:
            if error.code not in (301, 302, 303, 307, 308):
                raise

            location = error.headers.get("Location")

            if not location:
                raise RuntimeError("Wikipedia returned no Location header")

            url = urljoin(WIKIPEDIA_URL, location)

            if (
                url.startswith("https://en.wikipedia.org/wiki/")
                and "Special:Random" not in url
                and len("Read " + url) <= 140
            ):
                return url

    raise RuntimeError("Could not find a URL within 140 characters")


def main():
    article_url = get_random_article()
    todo = f"Read {article_url}"

    data = json.dumps({"todo": todo}).encode("utf-8")

    request = Request(
        TODO_API_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=20) as response:
        if response.status != 201:
            raise RuntimeError(f"Unexpected status: {response.status}")

    print(f"Created todo: {todo}", flush=True)


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request


def main() -> int:
    base_url = os.getenv("PLNRAG_BASE_URL", "http://pln-rag:8000").rstrip("/")
    health_url = f"{base_url}/health"
    max_wait_seconds = int(os.getenv("PLNRAG_WAIT_TIMEOUT_SECONDS", "180"))
    poll_interval_seconds = float(os.getenv("PLNRAG_WAIT_POLL_SECONDS", "2"))

    deadline = time.time() + max_wait_seconds
    while time.time() < deadline:
        try:
            req = urllib.request.Request(
                url=health_url,
                headers={"Accept": "application/json"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                body = response.read().decode("utf-8", errors="replace")
                data = json.loads(body) if body else {}
                if response.status == 200 and isinstance(data, dict):
                    status = str(data.get("status", ""))
                    if status in {"ok", "degraded"}:
                        print(f"[wait_for_pln] PLN health is ready: status={status}")
                        return 0
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
            pass

        print("[wait_for_pln] waiting for PLN health...")
        time.sleep(poll_interval_seconds)

    print(
        f"[wait_for_pln] timed out waiting for PLN health after {max_wait_seconds}s: {health_url}"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())


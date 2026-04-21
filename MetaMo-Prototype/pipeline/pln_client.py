from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

DEFAULT_PLNRAG_BASE_URL = "http://localhost:8001"
DEFAULT_TIMEOUT_SECONDS = 20


def get_plnrag_base_url() -> str:
    return os.getenv("PLNRAG_BASE_URL", DEFAULT_PLNRAG_BASE_URL).strip().rstrip("/")


class PLNClient:
    def __init__(self, base_url: str | None = None, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        self.base_url = (base_url or get_plnrag_base_url()).rstrip("/")
        self.timeout_seconds = timeout_seconds

    def health(self) -> dict[str, Any]:
        return self._request_json("GET", "/health")

    def reset(self) -> dict[str, Any]:
        return self._request_json("POST", "/reset")

    def ingest(self, texts: list[str]) -> dict[str, Any]:
        cleaned_texts = [text.strip() for text in texts if text and text.strip()]
        if not cleaned_texts:
            return {"status": "skipped", "reason": "no_non_empty_texts"}
        payload = {"texts": cleaned_texts}
        return self._request_json("POST", "/ingest", payload=payload)

    def query(self, question: str, top_k: int = 5) -> dict[str, Any]:
        payload = {"question": question, "top_k": top_k}
        return self._request_json("POST", "/query", payload=payload)

    def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        body: bytes | None = None
        headers: dict[str, str] = {"Accept": "application/json"}

        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            url=url,
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8", errors="replace")
                if not raw_body.strip():
                    return {"status": "ok", "http_status": response.status}
                return json.loads(raw_body)
        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"PLN request failed: {method} {url} -> HTTP {error.code}; body={error_body}"
            ) from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"PLN request failed: {method} {url}; error={error.reason}") from error


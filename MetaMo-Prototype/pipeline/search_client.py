from __future__ import annotations

import json
import os
from typing import Any

import requests
from bs4 import BeautifulSoup

DEFAULT_SERPER_API_URL = "https://google.serper.dev/search"
DEFAULT_SEARCH_ENGINE = "google"
DEFAULT_RESULTS_LIMIT = 2
DEFAULT_TIMEOUT_SECONDS = 25
DEFAULT_SCRAPE_TIMEOUT_SECONDS = 12


def _scrape_url_text(url: str) -> str | None:
    if not url:
        return None

    timeout_seconds = int(
        os.getenv("SCRAPER_TIMEOUT_SECONDS", str(DEFAULT_SCRAPE_TIMEOUT_SECONDS))
    )
    try:
        response = requests.get(
            url,
            timeout=timeout_seconds,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        if not text:
            return None
        return text
    except Exception:
        return None


def _normalize_serper_response(response: dict[str, Any]) -> dict[str, Any]:
    organic = response.get("organic", [])
    if not isinstance(organic, list):
        organic = []

    normalized_results: list[dict[str, str]] = []
    top_k = int(os.getenv("SEARCH_TOP_K", str(DEFAULT_RESULTS_LIMIT)))
    top_k = max(1, min(top_k, 10))

    for item in organic[:top_k]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        url = str(item.get("link", "")).strip()
        snippet = str(item.get("snippet", "")).strip()
        scraped_text = _scrape_url_text(url) if url else None
        content_for_ingest = scraped_text if scraped_text else snippet
        content_source = "scraped" if scraped_text else "snippet"

        normalized_results.append(
            {
                "title": title,
                "url": url,
                "snippet": snippet,
                "content": content_for_ingest,
                "content_source": content_source,
            }
        )

    return {
        "results": normalized_results,
        "answer": "",
        "provider": "serper",
        "top_k": top_k,
        "raw": response,
    }


def search_web(query: str) -> dict[str, Any]:
    api_key = os.getenv("SERPER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("SERPER_API_KEY is missing (check .env)")

    endpoint = os.getenv("SERPER_API_URL", DEFAULT_SERPER_API_URL).strip() or DEFAULT_SERPER_API_URL
    country = os.getenv("SERPER_GL", "").strip()
    language = os.getenv("SERPER_HL", "").strip()
    search_type = os.getenv("SERPER_TYPE", DEFAULT_SEARCH_ENGINE).strip() or DEFAULT_SEARCH_ENGINE

    payload: dict[str, Any] = {"q": query}
    if country:
        payload["gl"] = country
    if language:
        payload["hl"] = language

    if search_type == "news":
        endpoint = endpoint.replace("/search", "/news")
    elif search_type == "scholar":
        endpoint = endpoint.replace("/search", "/scholar")

    timeout_seconds = int(os.getenv("SERPER_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))
    try:
        response = requests.post(
            endpoint,
            data=json.dumps(payload),
            timeout=timeout_seconds,
            headers={
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        )
        response.raise_for_status()
        parsed = response.json()
        if not isinstance(parsed, dict):
            raise RuntimeError("Serper response is not a JSON object")
        return _normalize_serper_response(parsed)
    except requests.HTTPError as error:
        error_body = error.response.text if error.response is not None else ""
        raise RuntimeError(
            f"Serper request failed: HTTP {error.response.status_code if error.response is not None else 'unknown'}; body={error_body}"
        ) from error
    except requests.RequestException as error:
        raise RuntimeError(f"Serper request failed: {error}") from error

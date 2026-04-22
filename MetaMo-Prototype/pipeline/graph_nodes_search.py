from __future__ import annotations

from typing import Any

from pipeline.graph_shared import GraphState
from pipeline.pln_client import PLNClient
from pipeline.search_client import search_web


def _format_search_findings(search_response: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    results = search_response.get("results", [])
    if not isinstance(results, list):
        return findings

    for index, result in enumerate(results[:5], start=1):
        if not isinstance(result, dict):
            continue
        title = str(result.get("title", "")).strip() or "(untitled)"
        url = str(result.get("url", "")).strip() or "(no-url)"
        snippet = str(result.get("snippet", "")).strip()
        if not snippet:
            snippet = str(result.get("content", "")).strip()
        snippet_short = snippet[:280] + ("..." if len(snippet) > 280 else "")
        findings.append(f"Finding {index}: {title} | {url} | {snippet_short}")
    return findings


def _collect_pln_ingest_texts(search_response: dict[str, Any]) -> list[str]:
    texts: list[str] = []
    answer = str(search_response.get("answer", "")).strip()
    if answer:
        texts.append(answer)

    results = search_response.get("results", [])
    if isinstance(results, list):
        for result in results:
            if not isinstance(result, dict):
                continue
            title = str(result.get("title", "")).strip()
            url = str(result.get("url", "")).strip()
            content = str(result.get("content", "")).strip()
            if content:
                prefix = f"{title} ({url})" if title or url else ""
                text = f"{prefix}\n{content}".strip()
                texts.append(text)

    return texts


def node_simulated_search(state: GraphState) -> GraphState:
    query = state["query"].strip()
    action = str((state.get("decision") or {}).get("action", ""))

    if action not in {"act_search", "act_synthesize"}:
        findings = [
            f"Finding 1: Key facts relevant to '{query}'.",
            f"Finding 2: Important distinctions and examples for '{query}'.",
            f"Finding 3: Common pitfalls and clarifications for '{query}'.",
        ]
        return {"findings": findings}

    integration: dict[str, Any] = {}

    try:
        search_response = search_web(query)
        findings = _format_search_findings(search_response)
        if not findings:
            findings = [f"No search findings returned for '{query}'."]

        results_raw = search_response.get("results", [])
        result_count = len(results_raw) if isinstance(results_raw, list) else 0
        integration["search"] = {
            "query": query,
            "result_count": result_count,
            "urls": [
                str(item.get("url", "")).strip()
                for item in (results_raw if isinstance(results_raw, list) else [])
                if isinstance(item, dict) and str(item.get("url", "")).strip()
            ],
            "documents": [
                {
                    "title": str(item.get("title", "")).strip(),
                    "url": str(item.get("url", "")).strip(),
                    "snippet": str(item.get("snippet", "")).strip(),
                    "content": str(item.get("content", "")).strip(),
                    "content_source": str(item.get("content_source", "")).strip(),
                }
                for item in (results_raw if isinstance(results_raw, list) else [])
                if isinstance(item, dict)
            ],
        }

        try:
            texts_to_ingest = _collect_pln_ingest_texts(search_response)
            ingest_result = PLNClient().ingest(texts_to_ingest)
            processed_count = ingest_result.get("processed_count", 0)
            findings.append(f"PLN ingest status: processed_count={processed_count}")
            integration["pln_ingest"] = {
                "attempted_text_count": len(texts_to_ingest),
                "processed_count": processed_count,
                "status": "ok",
            }
        except Exception as exc:
            findings.append(f"PLN ingest failed: {exc}")

        return {"findings": findings, "integration": integration}
    except Exception as exc:
        fallback_findings = [
            f"Search unavailable: {exc}",
            f"Fallback note 1 for '{query}': collect key facts manually.",
            f"Fallback note 2 for '{query}': verify with trusted sources.",
        ]
        integration["search"] = {
            "query": query,
            "status": "failed",
            "error": str(exc),
        }
        return {"findings": fallback_findings, "integration": integration}

from __future__ import annotations

from typing import Any

from pipeline.graph_shared import GraphState, history_block, llm, llm_text
from pipeline.pln_client import PLNClient


def _format_pln_section(pln_result: dict[str, Any]) -> str:
    status = str(pln_result.get("query_status", "unknown"))
    answer = str(pln_result.get("answer", "")).strip() or "(no PLN answer)"
    sources_raw = pln_result.get("sources", [])
    sources: list[str] = []
    if isinstance(sources_raw, list):
        for source in sources_raw[:5]:
            sources.append(str(source))

    lines = [
        "PLN Reasoning",
        f"- query_status: {status}",
        f"- answer: {answer}",
    ]
    if sources:
        lines.append("- sources:")
        for source in sources:
            lines.append(f"  - {source}")
    return "\n".join(lines)


def _build_pln_prompt_context(pln_result: dict[str, Any]) -> str:
    answer = str(pln_result.get("answer", "")).strip()
    sources_raw = pln_result.get("sources", [])
    sources: list[str] = []
    if isinstance(sources_raw, list):
        for source in sources_raw[:3]:
            sources.append(str(source))

    if not answer and not sources:
        return ""

    lines = ["PLN context (use carefully as supporting evidence):"]
    if answer:
        lines.append(f"- PLN answer: {answer}")
    if sources:
        lines.append("- PLN sources:")
        for source in sources:
            lines.append(f"  - {source}")
    return "\n" + "\n".join(lines)


def node_think(state: GraphState) -> GraphState:
    client = llm()
    integration: dict[str, Any] = {}
    pln_prompt_context = ""
    pln_output_section = ""

    try:
        pln_result = PLNClient().query(state["query"])
        pln_prompt_context = _build_pln_prompt_context(pln_result)
        pln_output_section = _format_pln_section(pln_result)
        sources_raw = pln_result.get("sources", [])
        source_count = len(sources_raw) if isinstance(sources_raw, list) else 0
        integration["pln_query"] = {
            "status": "ok",
            "query_status": str(pln_result.get("query_status", "unknown")),
            "source_count": source_count,
            "fallback_used": bool(pln_result.get("fallback_used", False)),
        }
    except Exception as exc:
        pln_output_section = f"PLN Reasoning\n- unavailable: {exc}"
        integration["pln_query"] = {"status": "failed", "error": str(exc)}

    prompt = (
        state["system_prompt"]
        + history_block(state)
        + ("\n\n" + pln_prompt_context if pln_prompt_context else "")
        + "\n\nUser query: "
        + state["query"]
    )
    out = client.invoke(prompt)
    answer = llm_text(out)
    if pln_output_section:
        answer = f"{answer}\n\n---\n{pln_output_section}"
    return {"answer": answer, "integration": integration}

from __future__ import annotations

from pipeline.graph_shared import GraphState, history_block, llm, llm_text


def node_quick_answer(state: GraphState) -> GraphState:
    client = llm()
    prompt = (
        state["system_prompt"] + history_block(state) + "\n\nUser query: " + state["query"]
    )
    out = client.invoke(prompt)
    return {"answer": llm_text(out)}


def node_clarify(state: GraphState) -> GraphState:
    client = llm()
    prompt = (
        state["system_prompt"] + history_block(state) + "\n\nUser query: " + state["query"]
    )
    out = client.invoke(prompt)
    return {"answer": llm_text(out)}


def node_decompose(state: GraphState) -> GraphState:
    client = llm()
    prompt = (
        state["system_prompt"] + history_block(state) + "\n\nUser query: " + state["query"]
    )
    out = client.invoke(prompt)
    return {"answer": llm_text(out)}


def node_search_evidence(state: GraphState) -> GraphState:
    integration = state.get("integration", {})
    if isinstance(integration, dict):
        search_meta = integration.get("search", {})
        if isinstance(search_meta, dict) and str(search_meta.get("status", "")) == "failed":
            error_text = str(search_meta.get("error", "")).strip() or "unknown error"
            return {
                "answer": (
                    "Search is currently unavailable, so I cannot provide source-backed findings right now.\n"
                    f"Reason: {error_text}\n"
                    "Please retry in a moment, or provide specific URLs for me to analyze."
                )
            }

    client = llm()
    findings_text = "\n".join(f"- {f}" for f in state.get("findings", []))
    prompt = (
        state["system_prompt"]
        + history_block(state)
        + "\n\nEvidence notes gathered:\n"
        + findings_text
        + "\n\nUser query: "
        + state["query"]
        + "\n\nReturn only: (1) key evidence bullets, (2) open uncertainties."
    )
    out = client.invoke(prompt)
    return {"answer": llm_text(out)}


def node_research_synthesis(state: GraphState) -> GraphState:
    integration = state.get("integration", {})
    if isinstance(integration, dict):
        search_meta = integration.get("search", {})
        if isinstance(search_meta, dict) and str(search_meta.get("status", "")) == "failed":
            error_text = str(search_meta.get("error", "")).strip() or "unknown error"
            return {
                "answer": (
                    "Search is currently unavailable, so I cannot produce a source-backed synthesis right now.\n"
                    f"Reason: {error_text}\n"
                    "Please retry in a moment, or provide specific URLs/findings for me to synthesize."
                )
            }

    client = llm()
    findings_text = "\n".join(f"- {f}" for f in state.get("findings", []))
    prompt = (
        state["system_prompt"]
        + history_block(state)
        + "\n\nUse these notes:\n"
        + findings_text
        + "\n\nUser query: "
        + state["query"]
    )
    out = client.invoke(prompt)
    return {"answer": llm_text(out)}


def node_verify_synthesis(state: GraphState) -> GraphState:
    client = llm()
    findings_text = "\n".join(f"- {f}" for f in state.get("findings", []))
    prompt = (
        state["system_prompt"]
        + history_block(state)
        + "\n\nVerification notes:\n"
        + findings_text
        + "\n\nUser query: "
        + state["query"]
    )
    out = client.invoke(prompt)
    return {"answer": llm_text(out)}

from __future__ import annotations

import os
from typing import Any, Literal, TypedDict

from dotenv import load_dotenv

from pipeline.llm_client import build_chat_llm
from utils import resolve_provider_and_model_name


Action = Literal[
    "act_respond",
    "act_search",
    "act_verify",
    "act_clarify",
    "act_decompose",
    "act_think",
    "act_synthesize",
]


class GraphState(TypedDict, total=False):
    query: str
    context: dict[str, Any]
    decision: dict[str, Any]
    system_prompt: str
    findings: list[str]
    integration: dict[str, Any]
    answer: str
    engine_state: dict[str, Any]


def llm() -> Any:
    load_dotenv()
    provider, model_name = resolve_provider_and_model_name()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is missing (check .env)")
        return build_chat_llm(
            provider_name="openai",
            model=model_name,
            temperature=0.3,
            api_key=api_key,
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing (check .env)")
    return build_chat_llm(
        provider_name="gemini",
        model=model_name,
        temperature=0.3,
        api_key=api_key,
    )


def llm_text(output: Any) -> str:
    content = output.content if hasattr(output, "content") else output

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts)

    if isinstance(content, dict) and isinstance(content.get("text"), str):
        return content["text"]

    return str(content)


def context_config(state: GraphState) -> tuple[bool, int]:
    engine_state = state.get("engine_state") or {}
    params = engine_state.get("params", {})
    enabled = bool(params.get("enable_context_memory", False))
    window = int(params.get("context_window_turns", 2))
    return enabled, window


def recent_history(state: GraphState) -> list[dict[str, str]]:
    enabled, window = context_config(state)
    if not enabled or window <= 0:
        return []

    engine_state = state.get("engine_state") or {}
    context_history = engine_state.get("context_history", [])
    if not isinstance(context_history, list):
        return []

    recent = context_history[-window:]
    turns: list[dict[str, str]] = []
    for item in recent:
        if isinstance(item, dict):
            turns.append(
                {
                    "query": str(item.get("query", "")),
                    "answer": str(item.get("answer", "")),
                }
            )
    return turns


def history_block(state: GraphState) -> str:
    turns = recent_history(state)
    if not turns:
        return ""

    lines = ["Recent conversation context:"]
    for i, turn in enumerate(turns, start=1):
        idx = len(turns) - i + 1
        lines.append(f"Turn -{idx} user: {turn.get('query', '')}")
        lines.append(f"Turn -{idx} assistant: {turn.get('answer', '')}")
    return "\n\n" + "\n".join(lines)

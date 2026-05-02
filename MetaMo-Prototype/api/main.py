from __future__ import annotations

import copy
from threading import Lock
from typing import Any
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from core.state import init_state as init_engine_state
from pipeline.graph import build_graph
from run_logger import RunLogger


class ChatRequest(BaseModel):
    query: str = Field(min_length=1)
    session_id: str = Field(default="default", min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    action: str
    answer: str
    decision: dict[str, Any]
    context: dict[str, Any]


app = FastAPI(
    title="MetaMo API",
    description="MetaMo chat orchestration API",
    version="0.1.0",
)

_graph = build_graph()
_session_states: dict[str, dict[str, Any]] = {}
_session_turns: dict[str, int] = {}
_lock = Lock()
_base_dir = Path(__file__).resolve().parent.parent
_api_logger = RunLogger([{"name": "api_chat"}], _base_dir)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    with _lock:
        engine_state = _session_states.get(request.session_id)
        if engine_state is None:
            engine_state = init_engine_state()
            _session_states[request.session_id] = engine_state
        turn_index = _session_turns.get(request.session_id, 0) + 1
        _session_turns[request.session_id] = turn_index
        pre_engine_state = copy.deepcopy(engine_state)

    try:
        output = _graph.invoke({"query": request.query, "engine_state": engine_state})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    updated_engine_state = output.get("engine_state", engine_state)
    with _lock:
        _session_states[request.session_id] = updated_engine_state

    decision = output.get("decision", {})
    context = output.get("context", {})
    params = updated_engine_state.get("params", {})
    action = str(decision.get("action", "unknown"))
    answer = str(output.get("answer", ""))
    integration = output.get("integration", {})
    if not isinstance(integration, dict):
        integration = {}

    homeo_debug = updated_engine_state.get("homeostasis_debug", {})
    homeo_mode, homeo_trigger_count, homeo_trigger_keys, _ = (
        _api_logger.extract_homeostasis(homeo_debug)
    )
    _, score_top3_text = _api_logger.format_score_top3(decision.get("score_top3", []))
    style_modifier = str(decision.get("style_modifier") or "")

    log_payload = {
        "session_name": f"api:{request.session_id}",
        "turn": turn_index,
        "query": request.query,
        "action": action,
        "style_modifier": style_modifier,
        "intent_type": str(decision.get("intent_type", "mixed")),
        "complexity": float(context.get("complexity", 0.0)),
        "ambiguity": float(context.get("ambiguity", 0.0)),
        "threshold": float(decision.get("threshold", 0.0)),
        "arousal": float(decision.get("arousal", 0.0)),
        "risk_aversion": float(decision.get("risk_aversion", 0.0)),
        "resolution": float(decision.get("resolution", 0.0)),
        "topic_familiarity": float(decision.get("topic_familiarity", 0.0)),
        "confidence": float(decision.get("confidence", 0.0)),
        "low_confidence": float(decision.get("low_confidence", 0.0)),
        "over_beneficial": float(decision.get("over_beneficial", 0.0)),
        "over_safety": float(decision.get("over_safety", 0.0)),
        "over_honesty": float(decision.get("over_honesty", 0.0)),
        "hallucinate": float(decision.get("anti_hallucinate", 0.0)),
        "redundant": float(decision.get("anti_redundant", 0.0)),
        "rabbit_hole": float(decision.get("anti_rabbit_hole", 0.0)),
        "premature": float(decision.get("anti_premature", 0.0)),
        "homeo_mode": homeo_mode,
        "homeo_trigger_count": homeo_trigger_count,
        "homeo_trigger_keys": homeo_trigger_keys,
        "context_memory_enabled": bool(params.get("enable_context_memory", False)),
        "context_window_turns": int(params.get("context_window_turns", 0)),
        "score_top3_text": score_top3_text,
        "answer": answer,
        "context": context if isinstance(context, dict) else {},
        "decision": {
            "action": action,
            "style_modifier": style_modifier if action == "act_respond" else None,
            "reason": str(decision.get("reason", "")),
            "score_top3": copy.deepcopy(decision.get("score_top3", [])),
        },
        "pre_update": {
            "cold_weight": float(decision.get("cold_weight", 0.0)),
            "modulators": copy.deepcopy(pre_engine_state.get("modulators", {})),
            "goals": copy.deepcopy(pre_engine_state.get("goals", {})),
            "anti_goals": copy.deepcopy(pre_engine_state.get("anti_goals", {})),
        },
        "post_update": {
            "modulators": copy.deepcopy(updated_engine_state.get("modulators", {})),
            "goals": copy.deepcopy(updated_engine_state.get("goals", {})),
            "anti_goals": copy.deepcopy(updated_engine_state.get("anti_goals", {})),
        },
    }
    if integration:
        log_payload["integration"] = copy.deepcopy(integration)
    _api_logger.log_turn(log_payload)

    return ChatResponse(
        session_id=request.session_id,
        action=action,
        answer=answer,
        decision=decision if isinstance(decision, dict) else {},
        context=context if isinstance(context, dict) else {},
    )

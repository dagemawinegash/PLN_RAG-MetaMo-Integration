from __future__ import annotations

import importlib

from config import get_action_system_prompt
from core.decision import post_update as engine_post_update
from core.decision import step as engine_step
from core.state import init_state as init_engine_state
from dotenv import load_dotenv
from pipeline.graph_nodes_answer import (
    node_clarify,
    node_decompose,
    node_quick_answer,
    node_research_synthesis,
    node_search_evidence,
    node_verify_synthesis,
)
from pipeline.graph_nodes_search import node_simulated_search
from pipeline.graph_nodes_think import node_think
from pipeline.graph_shared import Action, GraphState, recent_history
from pipeline.parser import parse_context
from utils import resolve_provider_and_model_name


def node_context_parser(state: GraphState) -> GraphState:
    query = state["query"]
    history_turns = recent_history(state)
    load_dotenv()
    provider_name, model_name = resolve_provider_and_model_name()

    context = parse_context(
        query,
        history_turns=history_turns,
        model=model_name,
        provider=provider_name,
    )
    return {"context": context}


def node_engine(state: GraphState) -> GraphState:
    engine_state = state.get("engine_state") or init_engine_state()
    decision = engine_step(state["context"], engine_state)
    return {"decision": decision, "engine_state": engine_state}


def node_prompt_shaper(state: GraphState) -> GraphState:
    decision = state["decision"]

    urgency = float(decision.get("urgency", 0.0))
    expertise = float(decision.get("user_expertise", 0.5))

    if decision["action"] == "act_respond":
        style_modifier = str(decision.get("style_modifier") or "style_concise")
        style_map = {
            "style_concise": "Be concise and direct.",
            "style_thorough": "Be thorough, structured, and complete.",
            "style_exploratory": "Be exploratory and connect non-obvious ideas carefully.",
            "style_cautious": "Be cautious, explicit about uncertainty, and avoid overclaiming.",
            "style_tutorial": "Be tutorial and beginner-friendly with simple explanations.",
        }
        style = style_map.get(style_modifier, "Be concise and direct.")
        if style_modifier != "style_tutorial":
            if expertise <= 0.4:
                style += " Use beginner-friendly language."
            elif expertise >= 0.7:
                style += " Use expert-level concise wording."
        if urgency >= 0.6 and style_modifier == "style_concise":
            style = "Be extremely concise and direct."
        system = (
            f"You are Qwestor. {style} "
            "Avoid unsupported precise numeric claims (percentages, exact rates, exact counts) unless grounded in provided evidence. "
            "Do not add greetings or self-introductions."
        )
    else:
        try:
            system = get_action_system_prompt(str(decision["action"]))
        except KeyError as exc:
            raise RuntimeError(str(exc)) from exc

    return {"system_prompt": system}


def route_action(state: GraphState) -> Action:
    return state["decision"]["action"]


def node_post_update(state: GraphState) -> GraphState:
    engine_state = state.get("engine_state") or init_engine_state()
    updated_state = engine_post_update(
        context=state["context"], state=engine_state, decision=state["decision"]
    )
    context_history = updated_state.get("context_history", [])
    if not isinstance(context_history, list):
        context_history = []
    context_history.append(
        {
            "query": str(state.get("query", "")),
            "answer": str(state.get("answer", "")),
        }
    )
    updated_state["context_history"] = context_history
    return {"engine_state": updated_state}


def build_graph():
    graph_mod = importlib.import_module("langgraph.graph")
    StateGraph = getattr(graph_mod, "StateGraph")
    END = getattr(graph_mod, "END")

    graph = StateGraph(GraphState)

    graph.add_node("context_parser", node_context_parser)
    graph.add_node("engine", node_engine)
    graph.add_node("prompt_shaper", node_prompt_shaper)
    graph.add_node("quick_answer", node_quick_answer)
    graph.add_node("clarify", node_clarify)
    graph.add_node("decompose", node_decompose)
    graph.add_node("think", node_think)
    graph.add_node("simulated_search", node_simulated_search)
    graph.add_node("search_evidence", node_search_evidence)
    graph.add_node("research_synthesis", node_research_synthesis)
    graph.add_node("verify_synthesis", node_verify_synthesis)
    graph.add_node("post_update", node_post_update)

    graph.set_entry_point("context_parser")
    graph.add_edge("context_parser", "engine")
    graph.add_edge("engine", "prompt_shaper")

    graph.add_conditional_edges(
        "prompt_shaper",
        route_action,
        {
            "act_respond": "quick_answer",
            "act_clarify": "clarify",
            "act_decompose": "decompose",
            "act_think": "think",
            "act_search": "simulated_search",
            "act_verify": "simulated_search",
            "act_synthesize": "simulated_search",
        },
    )

    graph.add_edge("quick_answer", "post_update")
    graph.add_edge("clarify", "post_update")
    graph.add_edge("decompose", "post_update")
    graph.add_edge("think", "post_update")
    graph.add_conditional_edges(
        "simulated_search",
        route_action,
        {
            "act_search": "search_evidence",
            "act_verify": "verify_synthesis",
            "act_synthesize": "research_synthesis",
        },
    )
    graph.add_edge("search_evidence", "post_update")
    graph.add_edge("research_synthesis", "post_update")
    graph.add_edge("verify_synthesis", "post_update")
    graph.add_edge("post_update", END)

    return graph.compile()

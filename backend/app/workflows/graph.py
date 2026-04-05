from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.workflows.nodes import (
    agent_reason_node,
    classify_document_node,
    clean_text_node,
    document_intake_node,
    extract_fields_node,
    index_document_node,
    log_kpis_node,
    validate_document_node,
)
from app.workflows.state import DocumentWorkflowState


def route_agent_action(state: DocumentWorkflowState) -> str:
    action = state.get("agent_action", "finish")
    return action


def build_document_workflow():
    graph = StateGraph(DocumentWorkflowState)

    graph.add_node("document_intake", document_intake_node)
    graph.add_node("agent_reason", agent_reason_node)
    graph.add_node("clean_text", clean_text_node)
    graph.add_node("classify_document", classify_document_node)
    graph.add_node("index_document", index_document_node)
    graph.add_node("extract_fields", extract_fields_node)
    graph.add_node("validate_document", validate_document_node)
    graph.add_node("log_kpis", log_kpis_node)

    graph.add_edge(START, "document_intake")
    graph.add_edge("document_intake", "agent_reason")

    graph.add_conditional_edges(
        "agent_reason",
        route_agent_action,
        {
            "clean_text": "clean_text",
            "classify_document": "classify_document",
            "index_document": "index_document",
            "extract_fields": "extract_fields",
            "validate_document": "validate_document",
            "log_kpis": "log_kpis",
            "finish": END,
        },
    )

    graph.add_edge("clean_text", "agent_reason")
    graph.add_edge("classify_document", "agent_reason")
    graph.add_edge("index_document", "agent_reason")
    graph.add_edge("extract_fields", "agent_reason")
    graph.add_edge("validate_document", "agent_reason")
    graph.add_edge("log_kpis", "agent_reason")

    return graph.compile()


document_workflow = build_document_workflow()
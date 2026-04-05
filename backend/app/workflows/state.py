from __future__ import annotations

from typing import Literal, TypedDict


AgentAction = Literal[
    "clean_text",
    "classify_document",
    "index_document",
    "extract_fields",
    "validate_document",
    "log_kpis",
    "finish",
]


class AgentHistoryItem(TypedDict, total=False):
    action: str
    reasoning: str
    loop_count: int


class DocumentWorkflowState(TypedDict, total=False):
    file_path: str
    filename: str
    project_id: str

    parsed_document: object
    classification: object
    extraction: object
    validation: object

    indexed_chunk_count: int
    namespace: str

    agent_action: AgentAction
    agent_reasoning: str
    agent_history: list[AgentHistoryItem]
    steps_taken: list[str]
    loop_count: int
    max_loops: int

    error: str
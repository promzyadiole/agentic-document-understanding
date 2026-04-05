from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings
from app.workflows.graph import document_workflow


def save_workflow_graph_png(filename: str = "document_workflow_graph.png") -> str:
    """
    Export the LangGraph workflow as a PNG image.
    """
    settings = get_settings()
    output_dir = Path(settings.graph_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / filename

    png_bytes = document_workflow.get_graph().draw_mermaid_png()
    output_path.write_bytes(png_bytes)

    return str(output_path)
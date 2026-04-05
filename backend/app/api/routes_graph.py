from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.workflows.visualize import save_workflow_graph_png

from fastapi.responses import FileResponse
from app.core.config import get_settings

router = APIRouter()


@router.get("/export")
def export_graph():
    try:
        graph_path = save_workflow_graph_png()
        filename = Path(graph_path).name
        return {
            "message": "Workflow graph exported successfully.",
            "graph_path": graph_path,
            "image_url": f"http://127.0.0.1:8000/graph/file/{filename}",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    


@router.get("/file/{filename}")
def get_graph_file(filename: str):
    settings = get_settings()
    path = Path(settings.graph_output_dir) / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Graph file not found.")
    return FileResponse(path)
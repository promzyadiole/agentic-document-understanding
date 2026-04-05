from fastapi import APIRouter, HTTPException

from app.models.responses import QueryResponseModel
from app.models.schemas import QueryRequest
from app.services.rag import answer_with_rag

router = APIRouter()


@router.post("", response_model=QueryResponseModel)
def ask_question(request: QueryRequest):
    try:
        filter_dict = None
        if request.document_ids:
            filter_dict = {"document_id": {"$in": request.document_ids}}

        result = answer_with_rag(
            question=request.question,
            namespace=request.project_id or "default",
            top_k=request.top_k,
            filter_dict=filter_dict,
        )
        return QueryResponseModel(result=result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
from __future__ import annotations

from openai import OpenAI

from app.core.config import get_settings
from app.models.enums import DocumentType
from app.models.schemas import ClassificationResult

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)


def classify_document(text: str) -> ClassificationResult:
    """
    Classify document type using LLM.
    """

    snippet = text[:4000]  # avoid sending full doc

    prompt = f"""
You are an expert in document understanding for construction and finance.

Classify the following document into ONE of these types:

- invoice
- purchase_order
- delivery_note
- financial_report
- site_report
- unknown

Return ONLY JSON:

{{
  "document_type": "...",
  "confidence_score": 0.0,
  "reasoning": "..."
}}

Document:
{snippet}
"""

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You classify documents."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    content = response.choices[0].message.content

    try:
        import json
        data = json.loads(content)

        doc_type_map = {
            "invoice": DocumentType.INVOICE,
            "purchase_order": DocumentType.PURCHASE_ORDER,
            "delivery_note": DocumentType.DELIVERY_NOTE,
            "financial_report": DocumentType.FINANCIAL_REPORT,
            "site_report": DocumentType.SITE_REPORT,
            "unknown": DocumentType.UNKNOWN,
        }

        return ClassificationResult(
            document_type=doc_type_map.get(
                data.get("document_type", "unknown").lower(),
                DocumentType.UNKNOWN,
            ),
            confidence_score=float(data.get("confidence_score", 0.0)),
            reasoning=data.get("reasoning", ""),
        )

    except Exception:
        return ClassificationResult(
            document_type=DocumentType.UNKNOWN,
            confidence_score=0.0,
            reasoning="Failed to parse LLM response.",
        )
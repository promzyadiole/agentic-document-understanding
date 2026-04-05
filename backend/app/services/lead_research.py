from __future__ import annotations

import json
from typing import Any

from openai import OpenAI
from tavily import TavilyClient

from app.core.config import get_settings
from app.models.schemas import LeadCompany

settings = get_settings()
tavily_client = TavilyClient(api_key=settings.tavily_api_key)
openai_client = OpenAI(api_key=settings.openai_api_key)


def search_construction_leads(
    query: str,
    *,
    max_results: int = 10,
    location_hint: str | None = None,
) -> list[LeadCompany]:
    """
    Search for candidate construction companies using Tavily,
    then score and normalize them with an LLM.
    """
    enriched_query = query
    if location_hint:
        enriched_query += f" in or near {location_hint}"

    response = tavily_client.search(
        query=enriched_query,
        max_results=max_results,
        topic="general",
        search_depth="advanced",
    )

    raw_results = response.get("results", [])
    if not raw_results:
        return []

    leads: list[LeadCompany] = []

    for result in raw_results:
        title = result.get("title", "")
        url = result.get("url", "")
        content = result.get("content", "")

        lead = _score_lead_with_llm(
            title=title,
            url=url,
            content=content,
        )
        if lead:
            leads.append(lead)

    # deduplicate by company name
    deduped: dict[str, LeadCompany] = {}
    for lead in leads:
        key = lead.company_name.strip().lower()
        if key not in deduped or lead.relevance_score > deduped[key].relevance_score:
            deduped[key] = lead

    ranked = sorted(
        deduped.values(),
        key=lambda x: x.relevance_score,
        reverse=True,
    )

    return ranked[:max_results]


def _score_lead_with_llm(title: str, url: str, content: str) -> LeadCompany | None:
    snippet = (content or "")[:2000]

    prompt = f"""
You are evaluating whether a company could benefit from CONXAI-style AI services for construction workflow automation.

A strong candidate is likely to have:
- construction or infrastructure focus
- multiple projects or operational complexity
- fragmented workflows, documentation burden, or coordination needs
- signs of scale, digital transformation, or process complexity

Return ONLY valid JSON:
{{
  "company_name": "...",
  "website": "...",
  "location": "...",
  "summary": "...",
  "relevance_score": 0.0,
  "evidence": ["...", "..."]
}}

Search title: {title}
Search URL: {url}
Search content: {snippet}
""".strip()

    try:
        response = openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You score construction company leads."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        content = response.choices[0].message.content or ""
        data = json.loads(content)

        return LeadCompany(
            company_name=data.get("company_name", title[:120] or "Unknown Company"),
            website=data.get("website") or url,
            location=data.get("location"),
            summary=data.get("summary", ""),
            relevance_score=float(data.get("relevance_score", 0.0)),
            evidence=data.get("evidence", []),
        )
    except Exception:
        return LeadCompany(
            company_name=title[:120] or "Unknown Company",
            website=url,
            location=None,
            summary=snippet[:300],
            relevance_score=0.4,
            evidence=["Recovered from raw Tavily result due to parsing fallback."],
        )
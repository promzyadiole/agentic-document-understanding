from __future__ import annotations

"""
Proposal-copy generation with OpenAI (structured outputs).

Given a company (and, ideally, its website), this produces a full, structured
proposal tailored to that company and aligned with Proziem Digital Global's
credibility. The company's website is fetched and summarized so the copy is
grounded in what the company actually does — not invented.

OpenAI is called with a strict JSON schema so the output always has the fixed
template shape (hero, four deliverables, four process-step descriptions, a
pricing framing, and a scope/terms summary). Same OpenAI key used everywhere
else in the platform.
"""

import json
import re
from uuid import uuid4

import httpx
from openai import OpenAI

from app.core.agency_profile import CAPABILITY_STATEMENT, FIRM_NAME, PROCESS_STEPS, STATS
from app.core.config import get_settings
from app.models.schemas import (
    Proposal,
    ProposalContent,
    ProposalHero,
    ProposalItem,
    ProposalStep,
)
from app.services.proposal_store import save_proposal

settings = get_settings()
openai_client = OpenAI(api_key=settings.openai_api_key)


_TAG_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_HTML_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def fetch_company_context(website: str | None) -> str:
    """Fetch and lightly clean a company's homepage text for grounding."""
    if not website:
        return ""
    url = website if website.startswith("http") else f"https://{website}"
    try:
        with httpx.Client(timeout=12.0, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as client:
            resp = client.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception:
        return ""
    text = _TAG_RE.sub(" ", html)
    text = _HTML_RE.sub(" ", text)
    return _WS_RE.sub(" ", text).strip()[:4000]


# Strict JSON schema matching the fixed proposal template.
_PROPOSAL_SCHEMA = {
    "type": "object",
    "properties": {
        "hero": {
            "type": "object",
            "properties": {
                "eyebrow": {"type": "string"},
                "headline": {"type": "string"},
                "subheadline": {"type": "string"},
            },
            "required": ["eyebrow", "headline", "subheadline"],
            "additionalProperties": False,
        },
        "deliverables": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"title": {"type": "string"}, "description": {"type": "string"}},
                "required": ["title", "description"],
                "additionalProperties": False,
            },
        },
        "process": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"description": {"type": "string"}},
                "required": ["description"],
                "additionalProperties": False,
            },
        },
        "pricing": {
            "type": "object",
            "properties": {"framing": {"type": "string"}},
            "required": ["framing"],
            "additionalProperties": False,
        },
        "terms": {
            "type": "object",
            "properties": {"scopeSummary": {"type": "string"}},
            "required": ["scopeSummary"],
            "additionalProperties": False,
        },
    },
    "required": ["hero", "deliverables", "process", "pricing", "terms"],
    "additionalProperties": False,
}


def _build_system_prompt() -> str:
    step_titles = ", ".join(f'"{s["title"]}"' for s in PROCESS_STEPS)
    stats = "; ".join(f'{s["value"]} {s["label"]}' for s in STATS)
    return (
        f"You write concise, high-converting proposal copy for {FIRM_NAME}, filling a fixed page template. "
        f"About {FIRM_NAME}: {CAPABILITY_STATEMENT} Track record: {stats}. "
        "Produce EXACTLY these sections: a hero (short eyebrow line, bold headline, one-sentence subheadline), "
        "EXACTLY 4 deliverables (each a 2-4 word title and a one-sentence description), EXACTLY 4 process-step "
        f"descriptions tailored to these fixed step titles in order — {step_titles} — a one-paragraph pricing "
        "framing, and a one-paragraph scope/terms summary. Ground the copy in the client's real business as "
        "described in the provided context; do not invent facts about them. Align our capabilities with their "
        "needs, be specific and confident, and avoid generic marketing filler."
    )


def generate_proposal(
    *,
    company_name: str,
    website: str | None,
    price_cents: int,
    currency: str,
    brief: str,
    outreach_id: str | None = None,
) -> Proposal:
    company_context = fetch_company_context(website)

    user_parts = [f"Client: {company_name}"]
    if website:
        user_parts.append(f"Website: {website}")
    user_parts.append(f"Price: {(price_cents / 100):.2f} {currency.upper()}")
    if brief:
        user_parts.append(f"\nEngagement brief:\n{brief}")
    if company_context:
        user_parts.append(f"\nWhat the company does (from their website — use this to align the proposal):\n{company_context}")
    else:
        user_parts.append("\n(No website content was available; rely on the brief and company name.)")

    response = openai_client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": _build_system_prompt()},
            {"role": "user", "content": "\n".join(user_parts)},
        ],
        temperature=0.4,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "proposal_content", "strict": True, "schema": _PROPOSAL_SCHEMA},
        },
    )
    data = json.loads(response.choices[0].message.content or "{}")

    content = ProposalContent(
        hero=ProposalHero(**data["hero"]),
        deliverables=[ProposalItem(**d) for d in data.get("deliverables", [])[:4]],
        process=[ProposalStep(**p) for p in data.get("process", [])[:4]],
        pricing_framing=data.get("pricing", {}).get("framing", ""),
        scope_summary=data.get("terms", {}).get("scopeSummary", ""),
    )

    proposal = Proposal(
        id=uuid4().hex,
        company_name=company_name,
        website=website,
        company_context=company_context[:600] or None,
        price_cents=price_cents,
        currency=currency,
        brief=brief,
        content=content,
        status="draft",
        share_token=uuid4().hex,
        outreach_id=outreach_id,
    )
    return save_proposal(proposal)

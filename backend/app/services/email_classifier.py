from __future__ import annotations

"""
Lightweight email / message classifier for faster tracking and action.

Classifies an inbound message (contact-form submission or forwarded email) into
an intent category, a priority, and a suggested next action, so inbound demand
can be triaged quickly. Uses the OpenAI structured-JSON path already configured
for the platform.
"""

import json

from openai import OpenAI

from app.core.config import get_settings
from app.models.schemas import EmailClassification

settings = get_settings()
_client = OpenAI(api_key=settings.openai_api_key)

CATEGORIES = [
    "new_business",       # a prospect interested in our services
    "proposal_reply",     # replying to a proposal we sent
    "payment",            # about payment / invoicing
    "support",            # existing client needs help
    "partnership",        # collaboration / vendor
    "recruitment",        # jobs / hiring
    "spam",               # junk / irrelevant
    "other",
]

_PROMPT = """
You triage inbound messages for Proziem Digital Global (an AI, automation, and
digital-growth firm). Classify the message below.

Return ONLY valid JSON:
{{
  "category": one of {categories},
  "priority": "high" | "medium" | "low",
  "suggested_action": "a short next step, e.g. 'Reply with a discovery-call link'",
  "summary": "one sentence summary of what they want"
}}

From: {name} <{email}>{company}
Message:
{message}
""".strip()


def classify_message(name: str, email: str, message: str, company: str | None = None) -> EmailClassification:
    prompt = _PROMPT.format(
        categories=CATEGORIES,
        name=name,
        email=email,
        company=f" (company: {company})" if company else "",
        message=message[:4000],
    )
    try:
        resp = _client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You classify inbound business messages. Return JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content or "{}")
        category = data.get("category", "other")
        if category not in CATEGORIES:
            category = "other"
        return EmailClassification(
            category=category,
            priority=data.get("priority", "medium"),
            suggested_action=data.get("suggested_action", ""),
            summary=data.get("summary", ""),
        )
    except Exception:
        return EmailClassification(category="other", priority="medium", suggested_action="Review manually.", summary=message[:120])

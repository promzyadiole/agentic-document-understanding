from __future__ import annotations

from openai import OpenAI

from app.core.config import get_settings
from app.models.schemas import EmailDraft

settings = get_settings()
openai_client = OpenAI(api_key=settings.openai_api_key)


def draft_outreach_email(
    company_name: str,
    company_summary: str,
    *,
    website: str | None = None,
    location: str | None = None,
    recipient_email: str | None = None,
) -> EmailDraft:
    """
    Draft a marketing/outreach email for human review.
    This function does NOT send email.
    """
    prompt = f"""
You are drafting a concise, professional outreach email on behalf of CONXAI.

About CONXAI:
- CONXAI helps construction firms automate knowledge-intensive workflows
- It improves project control and reduces knowledge loss
- It supports high-stakes workflows trapped in fragmented tools, siloed data, and undocumented knowledge

Target company:
- Company name: {company_name}
- Summary: {company_summary}
- Website: {website or "N/A"}
- Location: {location or "N/A"}

Write:
1. A professional subject line
2. A short email body
Requirements:
- polite and personalized
- specific to construction workflow pain points
- no hypey language
- no false claims
- clearly suggests a conversation/demo
- keep it brief

Return in this format exactly:

SUBJECT: ...
BODY:
...
""".strip()

    response = openai_client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You write B2B outreach emails."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    content = response.choices[0].message.content or ""

    subject = "Exploring workflow automation opportunities"
    body = content.strip()

    if "SUBJECT:" in content and "BODY:" in content:
        try:
            subject_part = content.split("SUBJECT:", 1)[1].split("BODY:", 1)[0].strip()
            body_part = content.split("BODY:", 1)[1].strip()
            subject = subject_part
            body = body_part
        except Exception:
            pass

    return EmailDraft(
        company_name=company_name,
        recipient_email=recipient_email,
        subject=subject,
        body=body,
        approval_required=True,
        approved=False,
    )
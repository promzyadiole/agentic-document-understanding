from __future__ import annotations

from openai import OpenAI

from app.core.agency_profile import CAPABILITY_STATEMENT, FIRM_NAME, SENDER_EMAIL
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
You are drafting a concise, professional outreach email on behalf of {FIRM_NAME}.

About {FIRM_NAME}:
{CAPABILITY_STATEMENT}

Target company:
- Company name: {company_name}
- Summary: {company_summary}
- Website: {website or "N/A"}
- Location: {location or "N/A"}

Write:
1. A professional subject line
2. A short email body
Requirements:
- polite and personalized to this specific company and its likely pain points
- grounded in the target company summary above; do not invent facts about them
- no hypey language, no false claims
- clearly suggests a short conversation or demo
- keep it brief (under ~150 words)
- sign off as the {FIRM_NAME} team, and you may reference {SENDER_EMAIL}

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


def draft_thank_you_email(
    company_name: str,
    *,
    amount_label: str | None = None,
    recipient_email: str | None = None,
) -> EmailDraft:
    """
    Draft a warm thank-you email after a client has paid, assuring them of
    best-quality delivery. Requires human confirmation before sending.
    """
    prompt = f"""
Write a warm, professional thank-you email on behalf of {FIRM_NAME} to a client who has just
made a payment{f' of {amount_label}' if amount_label else ''}.

The email should:
- thank them sincerely for their trust and payment
- assure them of the highest-quality deliverables and clear communication
- state that work begins now and we'll follow up with next steps / a kickoff
- be concise, genuine, and free of hype
- sign off as the {FIRM_NAME} team, reachable at {SENDER_EMAIL}

Client company: {company_name}

Return in this format exactly:

SUBJECT: ...
BODY:
...
""".strip()

    response = openai_client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You write warm, professional client emails."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    content = response.choices[0].message.content or ""

    subject = f"Thank you from {FIRM_NAME}"
    body = content.strip()
    if "SUBJECT:" in content and "BODY:" in content:
        try:
            subject = content.split("SUBJECT:", 1)[1].split("BODY:", 1)[0].strip()
            body = content.split("BODY:", 1)[1].strip()
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
from __future__ import annotations

"""
Minimal, dependency-light PDF rendering with PyMuPDF (already a project dep).

Used to turn a generated proposal (or an inbound inquiry) into a real PDF file
that can be run back through the document-understanding workflow — closing the
loop between the outreach side of the product and the document side.
"""

import textwrap
from pathlib import Path
from uuid import uuid4

import fitz  # PyMuPDF

from app.core.config import get_settings


def _render(path: Path, title: str, sections: list[tuple[str, str]]) -> str:
    doc = fitz.open()

    lines: list[tuple[str, bool]] = [(title, True), ("", False)]
    for heading, body in sections:
        if heading:
            lines.append((heading.upper(), True))
        for para in (body or "").split("\n"):
            for wrapped in (textwrap.wrap(para, width=95) or [""]):
                lines.append((wrapped, False))
        lines.append(("", False))

    per_page = 50
    for i in range(0, len(lines), per_page):
        page = doc.new_page(width=595, height=842)  # A4
        y = 64
        for text, bold in lines[i : i + per_page]:
            page.insert_text(
                (60, y),
                text,
                fontsize=15 if (bold and y == 64 and i == 0) else 11,
                fontname="hebo" if bold else "helv",
            )
            y += 16

    doc.save(str(path))
    doc.close()
    return str(path)


def _upload_path(prefix: str) -> Path:
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir / f"{uuid4().hex}_{prefix}.pdf"


def render_proposal_pdf(proposal) -> str:
    """Render a Proposal model into a PDF and return its file path."""
    c = proposal.content
    sections: list[tuple[str, str]] = [
        ("Proziem Digital Global", ""),
        (proposal.company_name, f"{c.hero.headline}\n\n{c.hero.subheadline}"),
        ("Deliverables", "\n".join(f"- {d.title}: {d.description}" for d in c.deliverables)),
        ("Process", "\n".join(f"{i + 1}. {s.description}" for i, s in enumerate(c.process))),
        ("Investment", f"{proposal.price_cents / 100:.0f} {proposal.currency.upper()}\n\n{c.pricing_framing}"),
        ("Scope & Terms", c.scope_summary),
    ]
    path = _upload_path(f"proposal_{proposal.company_name[:24].replace(' ', '_')}")
    return _render(path, f"Proposal — {proposal.company_name}", sections)


def render_inquiry_pdf(name: str, email: str, company: str | None, message: str) -> str:
    """Render an inbound contact inquiry into a PDF and return its file path."""
    sections = [
        ("Contact", f"Name: {name}\nEmail: {email}\nCompany: {company or 'N/A'}"),
        ("Message", message),
    ]
    path = _upload_path("inbound_inquiry")
    return _render(path, "Inbound Inquiry — Proziem Digital Global", sections)

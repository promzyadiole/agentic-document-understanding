from __future__ import annotations

"""
Single source of truth for the firm's own (agency-owned) content.

This is the Python port of the proposal app's `agencyProfile.ts`. Everything the
outreach emails, generated proposals, and the services landing page say about
"us" comes from here, so updating this file updates all of them at once.
"""

from typing import Any

FIRM_NAME = "Proziem Digital Global"
FIRM_TAGLINE = "AI, automation, and digital growth for ambitious teams."
CONTACT_EMAIL = "promzy007adiole@yahoo.com"
# The address outreach & thank-you emails are sent from / reply to.
SENDER_EMAIL = "promzy007adiole100@gmail.com"

# A compact capability statement injected into outreach + proposal prompts so the
# copy is grounded in what we actually do and can credibly claim.
CAPABILITY_STATEMENT = (
    f"{FIRM_NAME} builds AI systems and digital products that automate "
    "knowledge-intensive workflows: agentic document understanding (OCR, structured "
    "extraction, validation, and retrieval), LLM and RAG applications, computer vision, "
    "robotics, and digital growth/marketing. We help teams cut documentation burden, "
    "reduce knowledge loss, improve project control, and turn fragmented data into "
    "grounded, auditable decisions."
)

STATS = [
    {"value": "$13M+", "label": "Revenue generated for clients"},
    {"value": "75+", "label": "Projects delivered"},
    {"value": "6 yrs", "label": "In business"},
]

SERVICES = [
    {
        "title": "Agentic Document Intelligence",
        "description": "OCR, LLM extraction, validation, and grounded RAG over invoices, contracts, and reports.",
    },
    {
        "title": "LLM & RAG Applications",
        "description": "Custom copilots and retrieval systems that answer from your own documents with citations.",
    },
    {
        "title": "Computer Vision & Robotics",
        "description": "Perception, segmentation, and language-grounded autonomy for real-world systems.",
    },
    {
        "title": "Digital Growth & Automation",
        "description": "Lead generation, outreach, and marketing systems that compound into measurable revenue.",
    },
]

PORTFOLIO = [
    {
        "title": "Jama's Concept Digital Growth Campaign",
        "subtitle": "45% increase in online tech-course enrollments in 60 days.",
        "tag": "Growth",
    },
    {
        "title": "MediNotes Pro",
        "subtitle": "AI assistant that turns consultation notes into summaries, action items, and patient emails.",
        "tag": "Product",
    },
    {
        "title": "Language-Vision Robot Navigation",
        "subtitle": "A ROS 2 robot that navigates using natural language and vision-language models.",
        "tag": "R&D",
    },
    {
        "title": "ConstructionFlow AI",
        "subtitle": "Agentic document understanding for construction & procurement, with self-correcting extraction.",
        "tag": "Platform",
    },
]

TEAM = [
    {"name": "Promise Adiole", "role": "CEO", "bio": "Leads Proziem Digital Global from strategy through delivery."},
    {"name": "Favour Emeziem", "role": "Data & AI", "bio": "Leads data and AI initiatives at Proziem Digital Global."},
]

PROCESS_STEPS = [
    {"label": "Step 01", "title": "Discovery call"},
    {"label": "Step 02", "title": "Proposal"},
    {"label": "Step 03", "title": "Project"},
    {"label": "Step 04", "title": "Ongoing support"},
]

TERMS_BOILERPLATE = (
    "Payment is due upon signing unless otherwise agreed in writing. Work begins once "
    "payment is received. Either party may cancel with written notice; work completed to "
    "date will be invoiced accordingly."
)


def public_profile() -> dict[str, Any]:
    """Serializable profile for the frontend landing page."""
    return {
        "firm_name": FIRM_NAME,
        "tagline": FIRM_TAGLINE,
        "contact_email": CONTACT_EMAIL,
        "capability_statement": CAPABILITY_STATEMENT,
        "stats": STATS,
        "services": SERVICES,
        "portfolio": PORTFOLIO,
        "team": TEAM,
        "process_steps": PROCESS_STEPS,
    }

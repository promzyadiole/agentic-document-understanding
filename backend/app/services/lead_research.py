from __future__ import annotations

"""
Hybrid lead research.

Backbone (from the original workflow — better *query* grounding, more results,
locations, robust): Tavily "advanced" search ranks pages by relevance to the
query, and an LLM scores each result's query-relevant snippet into a lead
(company, location, summary, evidence, score).

Grounded website + email (added): the blog/listicle URL a company was *mentioned*
on is never used as its website or email. For each shortlisted lead we resolve
the company's OWN domain (a targeted lookup when needed), then fetch its
homepage + /contact + /kontakt + /impressum + /about for a real, domain-matching
email. Aggregator/blog/news/social domains are excluded throughout.
"""

import json
import re
import time
from urllib.parse import urlparse

import httpx
from openai import OpenAI
from tavily import TavilyClient

from app.core.agency_profile import CAPABILITY_STATEMENT, FIRM_NAME
from app.core.config import get_settings
from app.models.schemas import LeadCompany

settings = get_settings()
tavily_client = TavilyClient(api_key=settings.tavily_api_key)
openai_client = OpenAI(api_key=settings.openai_api_key)

_UA = "Mozilla/5.0 (compatible; ProziemLeadBot/1.0)"
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_TAG_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_HTML_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

_CONTACT_PATHS = ["", "/contact", "/contact-us", "/kontakt", "/impressum", "/about", "/about-us"]

# Directories/blogs/news/socials/business-registries — never a company's own site.
_AGGREGATOR_DOMAINS = (
    "indeed.", "linkedin.", "glassdoor.", "crunchbase.", "wikipedia.", "medium.",
    "facebook.", "twitter.", "x.com", "youtube.", "reddit.", "quora.", "pinterest.",
    "blackridgeresearch.", "blog.", "news.", "clutch.co", "g2.com", "trustpilot.",
    "yelp.", "bloomberg.", "forbes.", "techcrunch.", "github.", "stackoverflow.",
    "trackunit.", "constructiondigital.", "marketresearchfuture.", "statista.",
    "mordorintelligence.", "grandviewresearch.", "researchandmarkets.", "bimkit.",
    "designrush.", "goodfirms.", "expertise.", "sortlist.", "ycombinator.",
    # Company/business directories & data brokers
    "f6s.", "dnb.", "dun", "northdata.", "opencorporates.", "companieshouse.",
    "kompass.", "europages.", "wlw.", "gelbeseiten.", "yellowpages.", "zoominfo.",
    "apollo.io", "rocketreach.", "lusha.", "leadiq.", "manta.", "bbb.org", "cylex.",
    "yalwa.", "local.ch", "wer-zu-wem.", "firmenwissen.", "unternehmensregister.",
    "handelsregister.", "getapp.", "capterra.", "softwareadvice.", "producthunt.",
    "owler.", "pitchbook.", "tracxn.", "dealroom.", "eu-startups.", "startus.",
)

# Titles/names that are reports/rankings, not companies.
_NON_COMPANY = (
    "market", "report", "top ", "list of", "best ", "guide", "overview", "ranking",
    "general contractor", "companies in", "software market", "statistics", "trends",
    "vs ", "comparison", "directory",
)

_EMAIL_NOISE = (
    "example.com", "sentry.io", "wixpress.com", "godaddy.com", "your-email", "email.com",
    "domain.com", "cloudflare", "googleapis", "gstatic", "w3.org", "schema.org",
    ".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", "@2x", "sentry-next",
)


class LeadSearchUnavailable(Exception):
    """Raised when the research provider can't be reached (network/DNS/quota)."""


def _is_network_error(exc: Exception) -> bool:
    text = f"{type(exc).__name__} {exc}".lower()
    return any(s in text for s in ("connection", "resolve", "name resolution", "timed out", "timeout", "temporarily", "max retries"))


def _tavily_search_with_retry(query: str, *, max_results: int, attempts: int = 3):
    last: Exception | None = None
    for i in range(attempts):
        try:
            return tavily_client.search(query=query, max_results=max_results, topic="general", search_depth="advanced", include_raw_content=True)
        except Exception as exc:  # noqa: BLE001
            last = exc
            if _is_network_error(exc) and i < attempts - 1:
                time.sleep(1.2 * (i + 1))
                continue
            break
    raise LeadSearchUnavailable(
        "Lead research is temporarily unavailable — could not reach the research provider. Please try again in a moment."
    ) from last


def _domain(url: str | None) -> str | None:
    if not url:
        return None
    try:
        netloc = urlparse(url if "//" in url else f"//{url}").netloc.lower()
        return netloc[4:] if netloc.startswith("www.") else netloc
    except Exception:
        return None


def _base_url(website: str | None) -> str | None:
    if not website:
        return None
    p = urlparse(website if "//" in website else f"https://{website}")
    return f"{p.scheme or 'https'}://{p.netloc}" if p.netloc else None


def _is_aggregator(domain: str | None) -> bool:
    return bool(domain) and any(a in domain for a in _AGGREGATOR_DOMAINS)


def _looks_like_company(name: str | None) -> bool:
    n = (name or "").lower().strip()
    return bool(n) and len(n) >= 2 and not any(k in n for k in _NON_COMPANY)


def _dedup_key(name: str) -> str:
    """Normalize a company name for dedup: drop legal suffixes/punctuation."""
    n = re.sub(r"[^a-z0-9 ]", " ", (name or "").lower())
    n = re.sub(r"\b(gmbh|ag|inc|llc|ltd|co|kg|se|plc|group|holding|holdings)\b", " ", n)
    return _WS_RE.sub(" ", n).strip()


def _clean_html(html: str) -> str:
    text = _TAG_RE.sub(" ", html)
    text = _HTML_RE.sub(" ", text)
    return _WS_RE.sub(" ", text).strip()


def _extract_emails(blob: str, *, site_domain: str | None) -> list[str]:
    found: list[str] = []
    for raw in _EMAIL_RE.findall(blob or ""):
        email = raw.strip().strip(".").lower()
        if any(n in email for n in _EMAIL_NOISE) or email in found:
            continue
        found.append(email)
    if site_domain:
        # Only keep emails that belong to the company's own domain.
        return [e for e in found if e.split("@")[-1].endswith(site_domain)][:3]
    return found[:3]


def _fetch_html(url: str, *, timeout: float = 6.0) -> str:
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True, headers={"User-Agent": _UA}) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.text
    except Exception:
        return ""


def _name_tokens(name: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", (name or "").lower()) if len(t) > 2 and t not in ("the", "and", "gmbh", "inc", "llc", "group", "ltd", "ag", "co")]


def _resolve_official_site(company_name: str, location: str | None) -> str | None:
    """Find a company's OWN website via a targeted lookup (not the blog it was listed on)."""
    q = f"{company_name} official website"
    if location:
        q += f" {location}"
    try:
        resp = _tavily_search_with_retry(q, max_results=5)
    except LeadSearchUnavailable:
        return None
    tokens = _name_tokens(company_name)
    candidates: list[str] = []
    for r in resp.get("results", []):
        base = _base_url(r.get("url"))
        dom = _domain(base)
        if base and not _is_aggregator(dom):
            candidates.append(base)
    # Prefer a domain that shares a token with the company name.
    for base in candidates:
        dom = _domain(base) or ""
        if any(tok in dom for tok in tokens):
            return base
    return candidates[0] if candidates else None


def _emails_from_site(website: str | None) -> list[str]:
    base = _base_url(website)
    if not base:
        return []
    site_domain = _domain(base)
    if _is_aggregator(site_domain):
        return []
    fetches = 0
    for path in _CONTACT_PATHS:
        if fetches >= 3:
            break
        html = _fetch_html(base + path)
        if not html:
            continue
        fetches += 1
        emails = _extract_emails(html + " " + _clean_html(html), site_domain=site_domain)
        if emails:
            return emails
    return []


def _gather_results(query: str, location_hint: str | None, breadth: int) -> list[dict]:
    """Run complementary Tavily searches and merge unique results by URL (wider net)."""
    base = f"{query} in or near {location_hint}" if location_hint else query
    variants = [base, f"{query} company" + (f" {location_hint}" if location_hint else "")]

    seen: set[str] = set()
    merged: list[dict] = []
    first_error: Exception | None = None
    for q in variants:
        try:
            resp = _tavily_search_with_retry(q, max_results=min(breadth, 20))
        except LeadSearchUnavailable as exc:  # tolerate one failing variant
            first_error = first_error or exc
            continue
        for r in resp.get("results", []):
            key = (r.get("url") or "").rstrip("/").lower()
            if key and key not in seen:
                seen.add(key)
                merged.append(r)

    if not merged and first_error:
        raise first_error
    return merged


def _score_lead_from_result(title: str, url: str, content: str, raw_content: str) -> LeadCompany | None:
    """Query-grounded scoring from the search snippet (website/email resolved later)."""
    snippet = f"{content}\n\n{raw_content}"[:2500]
    source_domain = _domain(url)
    source_is_company_site = not _is_aggregator(source_domain)
    # Only trust emails from the page if the page itself is the company's own site.
    snippet_emails = _extract_emails(snippet, site_domain=source_domain) if source_is_company_site else []

    prompt = f"""
You are evaluating whether a company could benefit from services by {FIRM_NAME}.

What we offer (only claim fit the evidence supports):
{CAPABILITY_STATEMENT}

A strong candidate shows: operational complexity, multiple projects, documentation
or coordination burden, fragmented workflows, or signs of scale / digital
transformation. Ground your summary in the search content and why it fits the
search intent. Do not invent facts. Score relevance honestly from 0.0 to 1.0.

If the result is a market report, ranking, or listicle, name the actual COMPANY it
is about (a real company). If there is no specific real company, set company_name to null.

Return ONLY valid JSON:
{{
  "company_name": "a real company, or null",
  "official_website": "the company's OWN domain if you know it, else null",
  "location": "... or null",
  "summary": "1-2 sentences grounded in the content, noting why it fits",
  "relevance_score": 0.0,
  "evidence": ["short fact from the content", "..."]
}}

Search title: {title}
Search URL: {url}
Search content:
{snippet}
""".strip()

    try:
        response = openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You score B2B leads strictly from the provided search content. Return JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content or "{}")
    except Exception:
        data = {}

    name = (data.get("company_name") or "").strip() or None
    if not _looks_like_company(name):
        return None

    official = data.get("official_website")
    website = _base_url(official) if official and not _is_aggregator(_domain(official)) else None
    # Only keep the source URL as the website if it IS the company's own site.
    if website is None and source_is_company_site:
        website = _base_url(url)

    return LeadCompany(
        company_name=name,
        website=website,
        email=snippet_emails[0] if snippet_emails else None,
        contact_url=url,
        location=data.get("location"),
        summary=data.get("summary", ""),
        relevance_score=float(data.get("relevance_score", 0.0) or 0.0),
        evidence=data.get("evidence", []) or [],
    )


def search_construction_leads(query: str, *, max_results: int = 10, location_hint: str | None = None) -> list[LeadCompany]:
    """
    Hybrid discovery:
      1. Tavily advanced search ranks pages by relevance to the query.
      2. Each result is scored into a lead from its query-relevant snippet.
      3. Non-companies (reports/rankings) are dropped.
      4. For each shortlisted lead, the company's OWN domain is resolved and its
         site fetched for a real, domain-matching contact email.
    """
    # Cast a wide net (two complementary searches, merged) so that after
    # non-companies and directories are filtered out, enough real companies
    # remain to fill max_results.
    breadth = min(max_results + 12, 20)
    raw_results = _gather_results(query, location_hint, breadth)
    if not raw_results:
        return []
    # Cap how many we score, to bound cost/latency on very wide result sets.
    raw_results = raw_results[: min(max_results + 14, 28)]

    leads: list[LeadCompany] = []
    for result in raw_results:
        lead = _score_lead_from_result(
            title=result.get("title", ""),
            url=result.get("url", ""),
            content=result.get("content", ""),
            raw_content=result.get("raw_content") or "",
        )
        if lead:
            leads.append(lead)

    # Deduplicate by company name (keep the highest-scoring/most-complete).
    deduped: dict[str, LeadCompany] = {}
    for lead in leads:
        key = _dedup_key(lead.company_name)
        existing = deduped.get(key)
        if existing is None or lead.relevance_score > existing.relevance_score:
            if existing:
                lead.website = lead.website or existing.website
                lead.email = lead.email or existing.email
                lead.location = lead.location or existing.location
            deduped[key] = lead

    ranked = sorted(deduped.values(), key=lambda x: x.relevance_score, reverse=True)[:max_results]

    # Resolve the real company domain (if unknown) and fetch a real email.
    for lead in ranked:
        if not lead.website:
            official = _resolve_official_site(lead.company_name, lead.location or location_hint)
            if official:
                lead.website = official
                lead.contact_url = official
        if not lead.email and lead.website:
            found = _emails_from_site(lead.website)
            if found:
                lead.email = found[0]
        # Final safety net: never surface an email from a directory/aggregator.
        if lead.email and _is_aggregator(lead.email.split("@")[-1]):
            lead.email = None

    return ranked

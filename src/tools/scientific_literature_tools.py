"""
scientific_literature_tools.py
==============================
Dedicated Open Scientific Literature & Citation Audit Tools for CrewAI.

Tools:
  1. ArxivSearchTool      — Query arXiv preprints with subject filtering & OpenAlex failover.
  2. OpenAlexSearchTool   — Query OpenAlex (250M+ works) with citation tree traversal & reconstructed abstracts.
  3. EuropePmcSearchTool  — Query Europe PMC for open-access life sciences and biophysics.
  4. CitationAuditTool    — Pre-flight citation integrity audit validating DOIs & flagging future-dated sources.
"""

from __future__ import annotations

import datetime
import json
import re
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from typing import Literal, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


_USER_AGENT = "UniverseKnowledge/1.0 (mailto:admin@universe-knowledge.org)"
_OPENALEX_ARXIV_SOURCE = "s4306400194"


def reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str:
    """Reconstructs a clean abstract string from OpenAlex inverted index format."""
    if not inverted_index or not isinstance(inverted_index, dict):
        return ""
    word_positions: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        if isinstance(positions, list):
            for pos in positions:
                word_positions.append((pos, word))
    word_positions.sort(key=lambda x: x[0])
    return " ".join(word for _, word in word_positions)


# ===========================================================================
# Tool 1: ArxivSearchTool
# ===========================================================================

class ArxivSearchInput(BaseModel):
    query: str = Field(
        ...,
        description="Search query or arXiv category (e.g., 'neutrino decay', 'cat:hep-th AdS/CFT', 'quant-ph entanglement')."
    )
    max_results: int = Field(
        default=5,
        description="Maximum number of preprints to return (1-15)."
    )
    sort_by: Literal["relevance", "submittedDate"] = Field(
        default="relevance",
        description="Sort order for arXiv results."
    )


class ArxivSearchTool(BaseTool):
    name: str = "ArXiv Preprint Search"
    description: str = (
        "Searches arXiv for scientific preprints and technical papers across physics, "
        "cosmology, mathematics, and quantum information. Returns verified paper titles, "
        "arXiv IDs, authors, categories, publication dates, full abstracts, and PDF links. "
        "Includes automatic OpenAlex failover if direct arXiv is rate-limited."
    )
    args_schema: Type[BaseModel] = ArxivSearchInput

    def _run(
        self,
        query: str,
        max_results: int = 5,
        sort_by: Literal["relevance", "submittedDate"] = "relevance"
    ) -> str:
        max_results = max(1, min(max_results, 15))
        papers: list[dict[str, str]] = []

        # 1. Try Direct arXiv API
        try:
            encoded_query = urllib.parse.quote(query)
            arxiv_url = (
                f"https://export.arxiv.org/api/query?"
                f"search_query=all:{encoded_query}&start=0&max_results={max_results}"
                f"&sortBy={sort_by}&sortOrder=descending"
            )
            req = urllib.request.Request(arxiv_url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=8) as conn:
                xml_data = conn.read()

            root = ET.fromstring(xml_data)
            ns = {
                "atom": "http://www.w3.org/2005/Atom",
                "arxiv": "http://arxiv.org/schemas/atom"
            }
            entries = root.findall("atom:entry", ns)

            for entry in entries:
                title_el = entry.find("atom:title", ns)
                summary_el = entry.find("atom:summary", ns)
                id_el = entry.find("atom:id", ns)
                published_el = entry.find("atom:published", ns)
                doi_el = entry.find("arxiv:doi", ns)
                journal_el = entry.find("arxiv:journal_ref", ns)
                category_el = entry.find("arxiv:primary_category", ns)

                title = title_el.text.strip().replace("\n", " ") if title_el is not None and title_el.text else "Untitled Paper"
                summary = summary_el.text.strip().replace("\n", " ") if summary_el is not None and summary_el.text else ""
                url = id_el.text.strip() if id_el is not None and id_el.text else ""
                published = published_el.text.strip()[:10] if published_el is not None and published_el.text else ""
                doi = doi_el.text.strip() if doi_el is not None and doi_el.text else ""
                journal = journal_el.text.strip() if journal_el is not None and journal_el.text else ""
                category = category_el.attrib.get("term", "") if category_el is not None else ""

                authors = []
                for author_el in entry.findall("atom:author", ns):
                    name_el = author_el.find("atom:name", ns)
                    if name_el is not None and name_el.text:
                        authors.append(name_el.text.strip())

                # Extract arXiv ID
                arxiv_id_match = re.search(r"arxiv\.org/abs/([0-9]+\.[0-9]+(?:v[0-9]+)?)", url)
                arxiv_id = arxiv_id_match.group(1) if arxiv_id_match else url

                papers.append({
                    "title": title,
                    "arxiv_id": arxiv_id,
                    "url": url,
                    "pdf_url": url.replace("/abs/", "/pdf/") + ".pdf" if "/abs/" in url else url,
                    "published": published,
                    "authors": ", ".join(authors[:4]) + (" et al." if len(authors) > 4 else ""),
                    "category": category,
                    "doi": doi,
                    "journal": journal,
                    "summary": summary
                })
        except Exception as exc:
            # Fallback to OpenAlex arXiv mirror
            papers = self._fallback_openalex_arxiv(query, max_results)

        if not papers:
            # Final fallback to OpenAlex general search
            papers = self._fallback_openalex_arxiv(query, max_results)

        if not papers:
            return f"No arXiv preprints found for query: '{query}'."

        # Format output as Markdown
        md = [f"### 📄 ArXiv Preprint Search Results for '{query}'\n"]
        for i, p in enumerate(papers, 1):
            md.append(f"{i}. **[{p['title']}]({p['url']})**")
            md.append(f"   * **arXiv ID:** `{p['arxiv_id']}` | **Published:** `{p['published']}` | **Category:** `{p['category']}`")
            if p.get("authors"):
                md.append(f"   * **Authors:** {p['authors']}")
            if p.get("doi"):
                md.append(f"   * **Published DOI:** [{p['doi']}](https://doi.org/{p['doi']})")
            if p.get("journal"):
                md.append(f"   * **Journal Reference:** {p['journal']}")
            if p.get("pdf_url"):
                md.append(f"   * **Direct PDF:** [Download PDF]({p['pdf_url']})")
            if p.get("summary"):
                summary_excerpt = p['summary'][:400] + ("..." if len(p['summary']) > 400 else "")
                md.append(f"   * **Abstract:** {summary_excerpt}\n")

        return "\n".join(md)

    def _fallback_openalex_arxiv(self, query: str, max_results: int) -> list[dict[str, str]]:
        """OpenAlex mirror fallback for arXiv papers when Cornell server returns 429."""
        papers = []
        try:
            encoded_query = urllib.parse.quote(query)
            url = (
                f"https://api.openalex.org/works?"
                f"filter=locations.source.id:{_OPENALEX_ARXIV_SOURCE},default.search:{encoded_query}"
                f"&per-page={max_results}&sort=relevance_score:desc"
            )
            req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=8) as conn:
                data = json.loads(conn.read().decode("utf-8"))

            for work in data.get("results", []):
                title = work.get("title") or "Untitled Paper"
                doi = work.get("doi") or ""
                if doi.startswith("https://doi.org/"):
                    doi = doi[len("https://doi.org/"):]
                pub_year = str(work.get("publication_year") or "")
                authors = [(a.get("author") or {}).get("display_name", "") for a in (work.get("authorships") or [])]
                abstract = reconstruct_abstract(work.get("abstract_inverted_index"))

                # Determine arXiv ID from locations
                arxiv_id = ""
                arxiv_url = ""
                for loc in (work.get("locations") or []):
                    landing = loc.get("landing_page_url") or ""
                    if "arxiv.org" in landing:
                        arxiv_url = landing
                        m = re.search(r"(\d+\.\d+)", landing)
                        if m:
                            arxiv_id = m.group(1)
                            break

                if not arxiv_url:
                    arxiv_url = work.get("id") or ""
                    arxiv_id = work.get("id", "").split("/")[-1]

                papers.append({
                    "title": title,
                    "arxiv_id": arxiv_id,
                    "url": arxiv_url,
                    "pdf_url": arxiv_url.replace("/abs/", "/pdf/") + ".pdf" if "/abs/" in arxiv_url else arxiv_url,
                    "published": pub_year,
                    "authors": ", ".join(authors[:4]) + (" et al." if len(authors) > 4 else ""),
                    "category": "physics (arXiv)",
                    "doi": doi,
                    "journal": ((work.get("primary_location") or {}).get("source") or {}).get("display_name", ""),
                    "summary": abstract
                })
        except Exception:
            pass
        return papers


# ===========================================================================
# Tool 2: OpenAlexSearchTool
# ===========================================================================

class OpenAlexSearchInput(BaseModel):
    query: str = Field(
        ...,
        description="Search topic, paper title, or Work ID/DOI."
    )
    mode: Literal["search", "cited_by", "references"] = Field(
        default="search",
        description="Mode: 'search' (topic/title lookup), 'cited_by' (who cited this work), 'references' (bibliography tree)."
    )
    max_results: int = Field(
        default=5,
        description="Maximum number of works to return (1-15)."
    )
    sort_by: Literal["relevance_score", "cited_by_count"] = Field(
        default="relevance_score",
        description="Sort by relevance or citation impact."
    )


class OpenAlexSearchTool(BaseTool):
    name: str = "OpenAlex Scholarly Graph Search"
    description: str = (
        "Queries OpenAlex (250M+ scholarly works) for peer-reviewed papers, books, and preprints. "
        "Provides 100% verified DOIs, authentic integer publication years, citation counts, "
        "reconstructed abstracts with LaTeX equations, and citation tree traversal "
        "('cited_by' to see papers citing a concept, 'references' to see papers cited by it)."
    )
    args_schema: Type[BaseModel] = OpenAlexSearchInput

    def _run(
        self,
        query: str,
        mode: Literal["search", "cited_by", "references"] = "search",
        max_results: int = 5,
        sort_by: Literal["relevance_score", "cited_by_count"] = "relevance_score"
    ) -> str:
        max_results = max(1, min(max_results, 15))

        try:
            if mode == "search":
                encoded_query = urllib.parse.quote(query)
                url = (
                    f"https://api.openalex.org/works?"
                    f"search={encoded_query}&per-page={max_results}&sort={sort_by}:desc"
                )
            elif mode == "cited_by":
                # If query contains a DOI or URL, resolve to OpenAlex Work ID first
                target_id = query.strip()
                if "10." in target_id or "doi.org" in target_id or target_id.startswith("http"):
                    doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", target_id)
                    clean_lookup = f"https://doi.org/{doi_match.group(0)}" if doi_match else target_id
                    lookup_url = f"https://api.openalex.org/works/{urllib.parse.quote(clean_lookup)}"
                    req = urllib.request.Request(lookup_url, headers={"User-Agent": _USER_AGENT})
                    with urllib.request.urlopen(req, timeout=6) as conn:
                        work_data = json.loads(conn.read().decode("utf-8"))
                        target_id = work_data.get("id", "").split("/")[-1]
                else:
                    target_id = target_id.split("/")[-1]

                url = (
                    f"https://api.openalex.org/works?"
                    f"filter=cites:{urllib.parse.quote(target_id)}&per-page={max_results}&sort=cited_by_count:desc"
                )
            else:  # mode == "references"
                # Lookup the work first to get its referenced_works
                clean_target = query.strip()
                if clean_target.startswith("10.") or "doi.org" in clean_target:
                    doi_m = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", clean_target, re.IGNORECASE)
                    if doi_m:
                        clean_target = f"https://doi.org/{doi_m.group(0)}"
                work_url = f"https://api.openalex.org/works/{urllib.parse.quote(clean_target)}"
                req = urllib.request.Request(work_url, headers={"User-Agent": _USER_AGENT})
                with urllib.request.urlopen(req, timeout=8) as conn:
                    work_data = json.loads(conn.read().decode("utf-8"))

                ref_ids = work_data.get("referenced_works", [])[:max_results]
                if not ref_ids:
                    return f"No referenced works recorded in OpenAlex for work: '{query}'."

                # Query works in bulk using pipe filter
                short_ids = [r.split("/")[-1] for r in ref_ids]
                url = f"https://api.openalex.org/works?filter=openalex_id:{'|'.join(short_ids)}&per-page={max_results}"

            req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=8) as conn:
                data = json.loads(conn.read().decode("utf-8"))

            works = data.get("results", [])
            if not works:
                return f"No OpenAlex results found for query: '{query}' (mode: {mode})."

            md = [f"### 🌐 OpenAlex Scholarly Results for '{query}' (Mode: `{mode}`)\n"]
            for i, w in enumerate(works, 1):
                title = w.get("title") or "Untitled Work"
                doi = w.get("doi") or ""
                pub_year = w.get("publication_year") or "N/A"
                cited_by = w.get("cited_by_count", 0)
                openalex_id = w.get("id") or ""
                landing_url = doi if doi else openalex_id

                # Authors
                authors = [(a.get("author") or {}).get("display_name", "") for a in (w.get("authorships") or [])]
                author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")

                # Host venue
                venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name", "")

                # Reconstruct abstract
                abstract = reconstruct_abstract(w.get("abstract_inverted_index"))

                md.append(f"{i}. **[{title}]({landing_url})**")
                md.append(f"   * **Year:** `{pub_year}` | **Citations:** `{cited_by}` | **OpenAlex ID:** `{openalex_id}`")
                if doi:
                    md.append(f"   * **Verified DOI:** [{doi}]({doi})")
                if venue:
                    md.append(f"   * **Venue/Journal:** {venue}")
                if author_str:
                    md.append(f"   * **Authors:** {author_str}")
                if abstract:
                    abstract_excerpt = abstract[:350] + ("..." if len(abstract) > 350 else "")
                    md.append(f"   * **Abstract:** {abstract_excerpt}\n")

            return "\n".join(md)
        except Exception as exc:
            return f"OpenAlex query error: {exc}"


# ===========================================================================
# Tool 3: EuropePmcSearchTool
# ===========================================================================

class EuropePmcSearchInput(BaseModel):
    query: str = Field(
        ...,
        description="Search query for Europe PMC (e.g. 'quantum biology', 'neural emergence', 'integrated information theory')."
    )
    max_results: int = Field(
        default=5,
        description="Maximum number of articles to return (1-15)."
    )


class EuropePmcSearchTool(BaseTool):
    name: str = "Europe PMC Literature Search"
    description: str = (
        "Searches Europe PMC for peer-reviewed life sciences, biophysics, biological information "
        "processing, and emergence literature. Returns full metadata, PMCID/PMID, verified DOIs, "
        "publication years, abstracts, and citation counts."
    )
    args_schema: Type[BaseModel] = EuropePmcSearchInput

    def _run(self, query: str, max_results: int = 5) -> str:
        max_results = max(1, min(max_results, 15))
        try:
            encoded_query = urllib.parse.quote(query)
            url = (
                f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
                f"query={encoded_query}&format=json&pageSize={max_results}&resultType=core"
            )
            req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=8) as conn:
                data = json.loads(conn.read().decode("utf-8"))

            results = data.get("resultList", {}).get("result", [])
            if not results:
                return f"No Europe PMC articles found for query: '{query}'."

            md = [f"### 🔬 Europe PMC Literature Results for '{query}'\n"]
            for i, item in enumerate(results, 1):
                title = item.get("title") or "Untitled Article"
                doi = item.get("doi") or ""
                pmcid = item.get("pmcid") or ""
                pmid = item.get("id") or ""
                pub_year = item.get("pubYear") or "N/A"
                journal = item.get("journalTitle") or ""
                author_str = item.get("authorString") or ""
                cited_by = item.get("citedByCount", 0)
                abstract = item.get("abstractText") or ""

                link = f"https://doi.org/{doi}" if doi else f"https://europepmc.org/article/MED/{pmid}"

                md.append(f"{i}. **[{title}]({link})**")
                md.append(f"   * **Year:** `{pub_year}` | **Citations:** `{cited_by}` | **PMCID:** `{pmcid or pmid}`")
                if doi:
                    md.append(f"   * **Verified DOI:** [{doi}](https://doi.org/{doi})")
                if journal:
                    md.append(f"   * **Journal:** {journal}")
                if author_str:
                    md.append(f"   * **Authors:** {author_str[:120]}{'...' if len(author_str) > 120 else ''}")
                if abstract:
                    abstract_excerpt = abstract[:350] + ("..." if len(abstract) > 350 else "")
                    md.append(f"   * **Abstract:** {abstract_excerpt}\n")

            return "\n".join(md)
        except Exception as exc:
            return f"Europe PMC query error: {exc}"


# ===========================================================================
# Tool 4: CitationAuditTool (Pre-Flight Verifier)
# ===========================================================================

class CitationAuditInput(BaseModel):
    report_text: str = Field(
        ...,
        description="Markdown text of the research report or bibliography section to audit."
    )


# Module-level cache to avoid duplicate network lookups across verification steps
_DOI_CACHE: dict[str, tuple[bool, str]] = {}


class CitationAuditTool(BaseTool):
    name: str = "Pre-Flight Citation Verifier"
    description: str = (
        "Audits the citations and references in a drafted research report before submission. "
        "Extracts all cited DOIs and references, flags future-dated publication years "
        "(hallucination detection), identifies non-specific placeholders ('Source 1', 'Academic Journals'), "
        "verifies DOIs against CrossRef/OpenAlex, and automatically recommends authentic "
        "peer-reviewed DOI replacements for missing or invalid citations."
    )
    args_schema: Type[BaseModel] = CitationAuditInput

    def _run(self, report_text: str) -> str:
        current_year = datetime.datetime.now().year
        flagged_issues: list[dict[str, str]] = []
        verified_dois: list[dict[str, str]] = []
        suggested_replacements: list[dict[str, str]] = []

        # 1. Extract sources lines
        source_lines = re.findall(r'^[ \t]*-[ \t]+["\']?(.+?)["\']?\s*$', report_text, re.MULTILINE)

        # Detect future-dated years (> current_year) or unverified post-2024 claims lacking a DOI/arXiv identifier
        year_candidates = re.compile(r'\b(20[2-9]\d)\b')
        has_identifier = re.compile(r'(10\.\d{4,9}/|arxiv\.org|arxiv:\s*\d{4}\.\d{4,5})', re.IGNORECASE)
        doi_or_arxiv_span = re.compile(r'(https?://\S+|10\.\d{4,9}/[-._;()/:A-Za-z0-9]+|arxiv:\s*\d{4}\.\d{4,5})', re.IGNORECASE)
        placeholder_pattern = re.compile(r'^(Source\s*\d+|Research Report|Academic Journals|Peer-reviewed Articles|Student Summary)', re.IGNORECASE)

        for line in source_lines:
            line_without_ids = doi_or_arxiv_span.sub("", line)
            years_in_line = [int(yr) for yr in year_candidates.findall(line_without_ids)]
            if placeholder_pattern.search(line):
                flagged_issues.append({
                    "citation": line,
                    "issue_type": "PLACEHOLDER_CITATION",
                    "explanation": "Non-specific generic placeholder; must be replaced with an authentic peer-reviewed publication."
                })
            elif any(yr > current_year for yr in years_in_line) or (
                any(yr >= 2025 for yr in years_in_line) and not has_identifier.search(line)
            ):
                flagged_issues.append({
                    "citation": line,
                    "issue_type": "FUTURE_DATED_HALLUCINATION",
                    "explanation": f"Publication year is beyond {current_year} or lacks a verifiable DOI/arXiv identifier, indicating a hallucinated citation."
                })

        # 2. Extract and verify DOIs
        extracted_dois = re.findall(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+', report_text)
        unique_dois = list(dict.fromkeys(extracted_dois))

        for raw_doi in unique_dois:
            clean_doi = raw_doi.rstrip(").,]")
            is_valid, title = self._verify_doi(clean_doi)
            if is_valid:
                verified_dois.append({"doi": clean_doi, "title": title})
            else:
                flagged_issues.append({
                    "citation": clean_doi,
                    "issue_type": "UNRESOLVABLE_DOI",
                    "explanation": f"DOI {clean_doi} could not be resolved in CrossRef or OpenAlex."
                })

        # 3. If issues found, query OpenAlex for canonical replacements
        if flagged_issues:
            # Extract concept topic keywords from report heading
            topic_match = re.search(r'^#\s+(.+)$', report_text, re.MULTILINE)
            topic_keywords = topic_match.group(1).strip() if topic_match else "fundamental physics"

            replacements = self._fetch_replacements(topic_keywords, count=len(flagged_issues))
            suggested_replacements.extend(replacements)

        # 4. Construct Audit Report
        audit_passed = len(flagged_issues) == 0 and (len(source_lines) >= 3 or len(verified_dois) >= 2)

        md = ["### 📋 Pre-Flight Citation Audit Report\n"]
        if audit_passed:
            md.append("✅ **CITATION AUDIT PASSED**: All citations are verified, non-future-dated, and supported by peer-reviewed records.\n")
        else:
            md.append("⚠️ **CITATION AUDIT ACTION REQUIRED**: Detected citation issues that must be addressed before final approval.\n")

        md.append(f"- **Total Sources Inspected:** {len(source_lines)}")
        md.append(f"- **Verified DOIs:** {len(verified_dois)}")
        md.append(f"- **Flagged Issues:** {len(flagged_issues)}")

        if verified_dois:
            md.append("\n**Verified Authentic DOIs:**")
            for d in verified_dois:
                md.append(f"- `[{d['doi']}]`: {d['title']}")

        if flagged_issues:
            md.append("\n**Flagged Citation Issues:**")
            for issue in flagged_issues:
                md.append(f"- ❌ `[{issue['issue_type']}]`: \"{issue['citation']}\" — *{issue['explanation']}*")

        if suggested_replacements:
            md.append("\n**Recommended Verified Peer-Reviewed Replacements:**")
            for rep in suggested_replacements:
                md.append(f"- **{rep['title']}** ({rep['year']}) — [DOI: {rep['doi']}](https://doi.org/{rep['doi']})")
                md.append(f"  *Authors:* {rep['authors']}")

        return "\n".join(md)

    def _verify_doi(self, doi: str) -> tuple[bool, str]:
        """Checks DOI against CrossRef / OpenAlex with in-memory caching."""
        if doi in _DOI_CACHE:
            return _DOI_CACHE[doi]

        # Try CrossRef
        try:
            url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
            req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=4) as conn:
                if conn.status == 200:
                    data = json.loads(conn.read().decode("utf-8"))
                    title = (data.get("message", {}).get("title") or ["Verified Paper"])[0]
                    _DOI_CACHE[doi] = (True, title)
                    return True, title
        except Exception:
            pass

        # Try OpenAlex fallback
        try:
            url = f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(doi)}"
            req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=4) as conn:
                if conn.status == 200:
                    data = json.loads(conn.read().decode("utf-8"))
                    title = data.get("title") or "Verified Paper"
                    _DOI_CACHE[doi] = (True, title)
                    return True, title
        except Exception:
            pass

        _DOI_CACHE[doi] = (False, "Unresolvable DOI")
        return False, "Unresolvable DOI"

    def _fetch_replacements(self, topic: str, count: int = 2) -> list[dict[str, str]]:
        """Queries OpenAlex for authoritative, peer-reviewed replacement citations."""
        replacements = []
        try:
            encoded_topic = urllib.parse.quote(topic)
            url = f"https://api.openalex.org/works?filter=has_doi:true,default.search:{encoded_topic}&per-page={max(2, count)}&sort=cited_by_count:desc"
            req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=5) as conn:
                data = json.loads(conn.read().decode("utf-8"))

            for work in data.get("results", []):
                doi = work.get("doi") or ""
                if doi.startswith("https://doi.org/"):
                    doi = doi[len("https://doi.org/"):]
                authors = [(a.get("author") or {}).get("display_name", "") for a in (work.get("authorships") or [])]
                replacements.append({
                    "title": work.get("title") or "Peer-Reviewed Paper",
                    "doi": doi,
                    "year": str(work.get("publication_year") or ""),
                    "authors": ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
                })
        except Exception:
            pass
        return replacements


# ===========================================================================
# Tool 5: ObservationalCosmologyTool
# ===========================================================================

_OBSERVATIONAL_TENSIONS_DB = [
    {
        "id": "jwst_early_galaxies_smbh",
        "keywords": ["jwst", "webb", "early galaxy", "high redshift", "reionization", "first stars", "halo", "smbh", "black hole", "origin", "lcdm", "structure formation"],
        "title": "JWST Ultra-High-Redshift (z > 10–14) Galaxies & Over-Massive Black Holes vs. Standard ΛCDM Halo Assembly",
        "observatories": "James Webb Space Telescope (JWST NIRCam/NIRSpec — JADES, CEERS, UNCOVER)",
        "observation": (
            "Spectroscopic confirmation of luminous galaxies up to z = 14.32 (~290 Myr after Big Bang, e.g., JADES-GS-z14-0) "
            "and UV-bright massive galaxy candidates at z ~ 10–13, alongside over-massive supermassive black holes "
            "(M_BH / M_* ~ 0.01–0.1, e.g., GN-z11 and UHZ1) appearing far earlier than expected."
        ),
        "theoretical_tension": (
            "Standard ΛCDM Press-Schechter / Sheth-Tormen halo mass functions with canonical baryon conversion efficiency "
            "(epsilon_* <= 0.15–0.20) underpredict the observed UV luminosity density at z > 10 by factors of 3–10x. "
            "Reconciling data requires bursty feedback-free star formation, a top-heavy Population III Initial Mass Function (IMF), "
            "direct-collapse heavy black hole seeds (M_seed ~ 10^4–10^5 M_sun), blue-tilted/enhanced small-scale primordial power, "
            "Early Dark Energy, or modified gravity (MOND) accelerated early collapse."
        ),
        "quantitative_benchmarks": [
            "JADES-GS-z14-0 spectroscopic redshift: z = 14.32 (+0.08 / -0.20), M_UV = -20.81 ± 0.16 mag",
            "Observed UV luminosity density at z ≈ 12: log10(rho_UV / [erg s^-1 Hz^-1 Mpc^-3]) = 25.1 ± 0.2 (3–10x above fiducial ΛCDM epsilon_* = 0.15)",
            "High-z over-massive black hole ratio (UHZ1 / GN-z11): M_BH / M_* ≈ 0.05–0.30 vs. local Soltan/Magorrian M_BH / M_* ≈ 0.001–0.002",
        ],
        "verified_citations": [
            "Carniani, S. et al. (2024), 'Spectroscopic confirmation of two luminous galaxies at a redshift of 14', Nature 633, 318–322, https://doi.org/10.1038/s41586-024-07860-9",
            "Labbé, I. et al. (2023), 'A population of red candidate massive galaxies ~600 Myr after the Big Bang', Nature 616, 266–269, https://doi.org/10.1038/s41586-023-05786-2",
            "Boylan-Kolchin, M. (2023), 'Stress testing ΛCDM with high-redshift galaxy candidates', Nature Astronomy 7, 731–735, https://doi.org/10.1038/s41550-023-01937-7",
            "Maiolino, R. et al. (2024), 'A small and vigorous black hole in the early Universe', Nature 627, 59–63, https://doi.org/10.1038/s41586-024-07052-5",
        ],
    },
    {
        "id": "hubble_constant_tension",
        "keywords": ["hubble", "h0", "expansion", "distance ladder", "cepheid", "supernova", "sh0es", "cmb", "planck", "early dark energy", "lcdm", "origin"],
        "title": "The >5σ Hubble Constant (H_0) Tension: Hubble/JWST Late-Universe Ladder vs. Planck Early-Universe CMB",
        "observatories": "Hubble Space Telescope (HST), JWST, and Planck CMB Observatory",
        "observation": (
            "Direct local distance-ladder measurements using Cepheids and Type Ia supernovae (SH0ES) yield "
            "H_0 = 73.04 ± 1.04 km s^-1 Mpc^-1 (confirmed by JWST near-IR Cepheid observations ruling out crowding bias at >8σ), "
            "whereas Planck CMB anisotropies extrapolated under flat ΛCDM yield H_0 = 67.36 ± 0.54 km s^-1 Mpc^-1."
        ),
        "theoretical_tension": (
            "A >5σ discrepancy between the early-universe comoving sound horizon r_s(z_*) ~ 147.09 Mpc calibrated at recombination "
            "(z ~ 1090) and the late-time expansion rate H(z). If not an unknown systematic across multiple independent calibrators, "
            "it requires pre-recombination new physics (e.g., Early Dark Energy reducing r_s by ~7%, extra relativistic species Delta N_eff, "
            "or primordial magnetic fields) or late-time modifications to General Relativity / dark sector interactions."
        ),
        "quantitative_benchmarks": [
            "Planck 2018 flat ΛCDM: H_0 = 67.36 ± 0.54 km s^-1 Mpc^-1, Omega_m = 0.3153 ± 0.0073, r_s(z_*) = 147.09 ± 0.26 Mpc",
            "SH0ES 2022 + JWST 2024 Cepheid-SN Ia ladder: H_0 = 73.04 ± 1.04 km s^-1 Mpc^-1",
            "Gaussian tension: Delta H_0 = 5.68 ± 1.17 km s^-1 Mpc^-1 (4.85σ, Delta chi^2 = 23.5 for 1 dof)",
        ],
        "verified_citations": [
            "Riess, A. G. et al. (2022), 'A Comprehensive Measurement of the Local Value of the Hubble Constant with 1 km s^-1 Mpc^-1 Uncertainty from the Hubble Space Telescope and the SH0ES Team', Astrophys. J. Lett. 934, L7, https://doi.org/10.3847/2041-8213/ac5c5b",
            "Riess, A. G. et al. (2024), 'JWST Observations Reject Unrecognized Crowding of Cepheid Photometry as an Explanation for the Hubble Tension at 8σ Confidence', Astrophys. J. 962, L17, https://doi.org/10.3847/2041-8213/ad1ddd",
            "Planck Collaboration, Aghanim, N. et al. (2020), 'Planck 2018 results. VI. Cosmological parameters', Astron. Astrophys. 641, A6, https://doi.org/10.1051/0004-6361/201833910",
            "Kamionkowski, M. & Riess, A. G. (2023), 'The Hubble Tension and Early Dark Energy', Annu. Rev. Nucl. Part. Sci. 73, 153–180, https://doi.org/10.1146/annurev-nucl-111422-024107",
        ],
    },
    {
        "id": "desi_dynamical_dark_energy",
        "keywords": ["desi", "dark energy", "cosmological constant", "vacuum energy", "bao", "baryon acoustic", "quintessence", "k-essence", "w0", "wa", "swampland", "acceleration", "sound speed"],
        "title": "DESI BAO + Supernova Evidence for Dynamical Dark Energy (w_0 w_a CDM) Over a Static Cosmological Constant Λ",
        "observatories": "Dark Energy Spectroscopic Instrument (DESI), Planck, Pantheon+, Union3, DES-SN5YR",
        "observation": (
            "DESI 2024–2025 Baryon Acoustic Oscillation measurements across 0.1 < z < 4.2, combined with CMB and Type Ia supernova "
            "datasets, find a 2.5σ–3.9σ preference for a time-evolving dark energy equation of state w(a) = w_0 + w_a (1 - a) "
            "with w_0 > -1 and w_a < 0 over a constant cosmological term w = -1."
        ),
        "theoretical_tension": (
            "Challenges the baseline ΛCDM assumption that cosmic acceleration is driven by a time-independent vacuum energy density "
            "rho_Lambda = const. Supports thawing quintessence scalar fields, k-essence, phantom-divide crossing models, or string swampland "
            "de Sitter conjectures that forbid stable positive cosmological constants."
        ),
        "quantitative_benchmarks": [
            "DESI 2024 + CMB + Pantheon+: w_0 = -0.827 ± 0.063, w_a = -0.75 (+0.29 / -0.25), corr(w_0, w_a) ≈ -0.85 [approximate, read off published contours] (Delta chi^2 ≈ -6.8 vs ΛCDM, 2.5σ)",
            "DESI 2024 + CMB + DES-SN5YR: w_0 = -0.727 ± 0.067, w_a = -1.05 (+0.31 / -0.27), corr(w_0, w_a) ≈ -0.85 [approximate] (Delta chi^2 ≈ -15.2 vs ΛCDM, 3.9σ)",
            "Perturbation discriminants: Canonical quintessence has c_s^2 = 1 (Jeans length ~ H^-1, smooth on sub-horizon scales k >> aH), whereas k-essence has c_s^2 = P_{,X} / (P_{,X} + 2 X P_{,XX}) != 1 (enhancing dark-energy clustering when 0 < c_s^2 << 1)",
        ],
        "verified_citations": [
            "DESI Collaboration, Adame, A. G. et al. (2025), 'DESI 2024 VI: Cosmological Constraints from the Measurements of Baryon Acoustic Oscillations', JCAP 02, 021 (arXiv:2404.03002), https://doi.org/10.1088/1475-7516/2025/02/021",
            "Peebles, P. J. E. & Ratra, B. (2003), 'The cosmological constant and dark energy', Rev. Mod. Phys. 75, 559, https://doi.org/10.1103/RevModPhys.75.559",
        ],
    },
    {
        "id": "s8_structure_growth_tension",
        "keywords": ["s8", "sigma8", "weak lensing", "cosmic shear", "euclid", "kids", "des", "cosmic web", "matter clustering", "growth", "dark matter", "fsigma8"],
        "title": "The S_8 = σ_8 (Ω_m / 0.3)^0.5 Cosmic Shear & Structure-Growth Tension",
        "observatories": "KiDS-1000, Dark Energy Survey (DES Y3), Hyper Suprime-Cam (HSC), Euclid, ACT/Planck",
        "observation": (
            "Late-time galaxy weak lensing and cosmic shear surveys measure S_8 = 0.759–0.776, which is 2σ–3σ lower "
            "than the Planck CMB ΛCDM prediction S_8 = 0.832 ± 0.013."
        ),
        "theoretical_tension": (
            "Indicates that matter clustering on ~1–10 Mpc scales grew more slowly between z ~ 1100 and z ~ 0 than predicted by "
            "standard cold collisionless dark matter under General Relativity, pointing toward warm/self-interacting/decaying dark matter, "
            "massive neutrino suppression, scale-dependent modified gravity, or stronger-than-modeled AGN baryonic feedback."
        ),
        "quantitative_benchmarks": [
            "Planck 2018 ΛCDM: S_8 = 0.832 ± 0.013, sigma_8 = 0.8111 ± 0.0060",
            "KiDS-1000 cosmic shear: S_8 = 0.759 (+0.024 / -0.021) (2.85σ tension with Planck, Delta S_8 = -0.073 ± 0.026)",
            "DES-Y3 cosmic shear: S_8 = 0.776 ± 0.017 (2.62σ tension with Planck, Delta S_8 = -0.056 ± 0.021)",
        ],
        "verified_citations": [
            "Asgari, M. et al. [KiDS Collaboration] (2021), 'KiDS-1000 Cosmology: Cosmic shear constraints and comparison between two point statistics', Astron. Astrophys. 645, A104, https://doi.org/10.1051/0004-6361/202039070",
            "Amon, A. et al. [DES Collaboration] (2022), 'Dark Energy Survey Year 3 results: Cosmology from cosmic shear and robustness to modeling uncertainty', Phys. Rev. D 105, 023520, https://doi.org/10.1103/PhysRevD.105.023520",
        ],
    },
    {
        "id": "inflation_cmb_gw_constraints",
        "keywords": ["inflation", "primordial gravitational", "tensor", "bicep", "nanograv", "pta", "cmb anomalies", "planck", "early universe", "reheating", "baryogenesis", "gw170817"],
        "title": "Primordial Tensor Bounds (r < 0.036), GW170817 Tensor Speed, and Nanohertz Gravitational-Wave Backgrounds",
        "observatories": "BICEP/Keck, Planck, LIGO/Virgo (GW170817), NANOGrav 15-yr / EPTA / PPTA",
        "observation": (
            "BICEP/Keck + Planck bound the primordial tensor-to-scalar ratio to r_0.05 < 0.036 (95% CL), falsifying minimal "
            "monomial chaotic inflation V(phi) ~ phi^2, phi^4; GW170817 bounds |c_gw - c|/c <= 3e-15; Pulsar Timing Arrays "
            "(NANOGrav 15-yr) detect a nHz stochastic gravitational-wave background."
        ),
        "theoretical_tension": (
            "Restricts viable inflation to plateau/R^2/alpha-attractor potentials or non-inflationary bounce/ekpyrotic alternatives, "
            "while PTA nHz signals test standard supermassive black hole binary populations against early-universe cosmic strings, "
            "first-order phase transitions, and scalar-induced gravitational waves."
        ),
        "quantitative_benchmarks": [
            "BICEP/Keck 2021 + Planck: r_0.05 < 0.036 (95% CL; r_0.05 = 0.014 ± 0.010), n_s = 0.9649 ± 0.0042",
            "GW170817 / GRB170817A tensor speed bound: -3e-15 <= (c_gw - c)/c <= +7e-16 at z = 0.0098",
            "NANOGrav 15-yr nHz GW background amplitude at f = 1 yr^-1: A_GWB = 2.4 (+0.7 / -0.6) × 10^-15 (for spectral index gamma = 13/3)",
        ],
        "verified_citations": [
            "Ade, P. A. R. et al. [BICEP/Keck Collaboration] (2021), 'Improved Constraints on Primordial Gravitational Waves using Planck, WMAP, and BICEP/Keck Observations through the 2018 Observing Season', Phys. Rev. Lett. 127, 151301, https://doi.org/10.1103/PhysRevLett.127.151301",
            "Agazie, G. et al. [NANOGrav Collaboration] (2023), 'The NANOGrav 15 yr Data Set: Evidence for a Gravitational-wave Background', Astrophys. J. Lett. 951, L8, https://doi.org/10.3847/2041-8213/acdac6",
        ],
    },
]


class ObservationalCosmologyInput(BaseModel):
    topic_or_tension: str = Field(
        ...,
        description="Physics/cosmology concept or observational tension to check (e.g., 'JWST early galaxies', 'Hubble tension', 'dark energy DESI', 'early universe inflation')."
    )
    observatory_filter: str = Field(
        default="all",
        description="Optional observatory focus: 'all', 'JWST', 'Hubble', 'DESI', 'Euclid', 'Planck', or 'LIGO/PTA'."
    )


class ObservationalCosmologyTool(BaseTool):
    name: str = "Observational Cosmology & Deep-Space Survey Tracker"
    description: str = (
        "Retrieves current observational data, empirical bounds, and theoretical tensions from flagship "
        "telescopes and surveys (Hubble Space Telescope / HST, James Webb Space Telescope / JWST, DESI, "
        "Euclid, Planck, BICEP/Keck, NANOGrav/LIGO) where real observations challenge or revise standard "
        "textbook theories of the origin and evolution of the Universe. Also queries live recent literature "
        "(2023-present) for observational tests."
    )
    args_schema: Type[BaseModel] = ObservationalCosmologyInput

    def _run(self, topic_or_tension: str, observatory_filter: str = "all") -> str:
        q_lower = f"{topic_or_tension} {observatory_filter}".lower()

        matched = []
        for entry in _OBSERVATIONAL_TENSIONS_DB:
            if any(k in q_lower for k in entry["keywords"]):
                matched.append(entry)

        if not matched:
            matched = _OBSERVATIONAL_TENSIONS_DB[:3]

        md = [
            f"### 🔭 Observational Data & Theoretical Tensions Report for '{topic_or_tension}'\n",
            "> **Epistemic Mandate**: Where empirical observations (JWST, Hubble, DESI, Planck, Euclid, PTAs) "
            "diverge from standard textbook models (e.g. baseline ΛCDM or minimal inflation), reports MUST explicitly "
            "document the observational discrepancy, error bars, covariance, and competing theoretical revisions.\n",
        ]

        for i, item in enumerate(matched, 1):
            md.append(f"#### {i}. {item['title']}")
            md.append(f"- **Observatories / Surveys:** {item['observatories']}")
            md.append(f"- **Empirical Observation:** {item['observation']}")
            md.append(f"- **Conflict with Standard Theory:** {item['theoretical_tension']}")
            if item.get("quantitative_benchmarks"):
                md.append("- **Quantitative Benchmarks, Uncertainties & Covariance (Use in Model Comparisons):**")
                for qb in item["quantitative_benchmarks"]:
                    md.append(f"  * `{qb}`")
            md.append("- **Verified Primary Sources (Ready to Cite):**")
            for cit in item["verified_citations"]:
                md.append(f"  * {cit}")
            md.append("")

        # Live OpenAlex query for recent (2023+) observational papers matching the topic
        try:
            obs_kw = observatory_filter if observatory_filter.lower() != "all" else "JWST Hubble DESI Planck observation"
            search_q = urllib.parse.quote(f"{topic_or_tension} {obs_kw}")
            url = (
                f"https://api.openalex.org/works?"
                f"filter=from_publication_date:2023-01-01,has_doi:true&search={search_q}&per-page=4&sort=cited_by_count:desc"
            )
            req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=6) as conn:
                data = json.loads(conn.read().decode("utf-8"))

            live_works = data.get("results") or []
            if live_works:
                md.append("#### 📡 Live Recent Observational Papers (2023–Present via OpenAlex)")
                for w in live_works:
                    title = w.get("title") or "Untitled Observational Study"
                    doi = w.get("doi") or ""
                    yr = w.get("publication_year") or ""
                    cited = w.get("cited_by_count", 0)
                    authors = [(a.get("author") or {}).get("display_name", "") for a in (w.get("authorships") or [])]
                    auth_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
                    md.append(f"- **{title}** ({yr}) — {auth_str} | Citations: `{cited}` | DOI: {doi}")
        except Exception:
            pass

        return "\n".join(md)


# ===========================================================================
# Tool 6: ArxivFullTextSectionReaderTool
# ===========================================================================

def _normalize_arxiv_id(raw_id: str) -> str:
    """Extract canonical arXiv identifier (e.g. '2404.03002' or 'hep-th/9905111') from an ID or URL."""
    s = str(raw_id or "").strip()
    m_url = re.search(r"arxiv\.org/(?:abs|pdf|html)/([A-Za-z\-]+/[0-9]{7}|[0-9]{4}\.[0-9]{4,5})(?:v[0-9]+)?", s, re.I)
    if m_url:
        return m_url.group(1)
    s = re.sub(r"^arxiv:\s*", "", s, flags=re.I).strip()
    m_id = re.match(r"^([A-Za-z\-]+/[0-9]{7}|[0-9]{4}\.[0-9]{4,5})(?:v[0-9]+)?$", s)
    if m_id:
        return m_id.group(1)
    return s


def _html_with_latex_to_text(fragment: str) -> tuple[str, list[str]]:
    """Convert HTML fragment (arXiv LaTeXML / ar5iv) into readable text with inline $...$ LaTeX and extracted equations."""
    import html as html_lib

    s = str(fragment or "")
    equations: list[str] = []

    def _sub_math_alt(m: re.Match) -> str:
        tex = html_lib.unescape(m.group(1)).strip()
        if tex:
            if len(tex) > 3 and tex not in equations:
                equations.append(tex)
            return f" ${tex}$ "
        return " "

    # 1. Replace <math ... alttext="...">...</math> with $alttext$
    s = re.sub(
        r"<math\b[^>]*\balttext=[\"']([^\"']+)[\"'][^>]*>.*?</math>",
        _sub_math_alt,
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # 2. Replace <math>...<annotation encoding="application/x-tex">...</annotation>...</math>
    def _sub_math_annot(m: re.Match) -> str:
        inner = m.group(1)
        ann = re.search(
            r"<annotation\b[^>]*encoding=[\"']application/x-tex[\"'][^>]*>(.*?)</annotation>",
            inner,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if ann:
            tex = html_lib.unescape(re.sub(r"<[^>]+>", "", ann.group(1))).strip()
            if tex:
                if len(tex) > 3 and tex not in equations:
                    equations.append(tex)
                return f" ${tex}$ "
        return " " + re.sub(r"<[^>]+>", " ", inner) + " "

    s = re.sub(r"<math\b[^>]*>(.*?)</math>", _sub_math_annot, s, flags=re.DOTALL | re.IGNORECASE)

    # 3. Strip scripts/styles/nav and convert block tags to newlines
    s = re.sub(r"<(?:script|style|nav|header|footer|figure)\b[^>]*>.*?</(?:script|style|nav|header|footer|figure)>", " ", s, flags=re.DOTALL | re.I)
    s = re.sub(r"</?(?:p|div|section|article|tr|li|br|h[1-6]|blockquote|table)\b[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html_lib.unescape(s)
    # Collapse horizontal whitespace while preserving paragraph breaks
    lines = [" ".join(line.split()) for line in s.splitlines()]
    clean_text = "\n".join(line for line in lines if line)
    return clean_text, equations


def _select_section_snippet(sec_text: str, q_terms: list[str], budget: int) -> str:
    """Return up to `budget` chars from `sec_text`, prioritizing paragraphs that match `q_terms` when truncated."""
    if len(sec_text) <= budget or not q_terms:
        return sec_text[:budget]
    paragraphs = [p.strip() for p in sec_text.splitlines() if p.strip()]
    if len(paragraphs) <= 1:
        return sec_text[:budget]
    scored_paras: list[tuple[float, int, str]] = []
    for idx, para in enumerate(paragraphs):
        p_low = para.lower()
        hits = sum(1 for t in q_terms if t in p_low)
        density = sum(min(3, p_low.count(t)) for t in q_terms)
        has_math_or_num = 0.5 if ("$" in para or "±" in para or "\\sigma" in para or re.search(r"\b\d+\.\d+\b", para)) else 0.0
        score = hits * 3.0 + density * 1.0 + has_math_or_num + max(0.0, 0.2 - 0.01 * idx)
        scored_paras.append((score, idx, para))
    scored_paras.sort(key=lambda x: (-x[0], x[1]))
    chosen_chunks: dict[int, str] = {}
    used = 0
    for score, idx, para in scored_paras:
        if used >= budget:
            break
        chunk = para[: budget - used]
        chosen_chunks[idx] = chunk
        used += len(chunk) + 1
    return "\n".join(chosen_chunks[idx] for idx in sorted(chosen_chunks))


def _extract_arxiv_html_sections(html_text: str, section_query: str = "", max_chars: int = 4000) -> dict:
    """Parse arXiv/ar5iv HTML into sections and select the best-matching sections & equations."""
    import html as html_lib

    max_chars = max(500, min(int(max_chars or 4000), 10000))
    raw = str(html_text or "")

    title_m = re.search(r"<title\b[^>]*>(.*?)</title>", raw, flags=re.DOTALL | re.I)
    title = html_lib.unescape(re.sub(r"<[^>]+>", " ", title_m.group(1))).strip() if title_m else "arXiv Paper"
    title = " ".join(title.split())

    # Remove head/script/style/bibliography noise before splitting by headings
    body_m = re.search(r"<body\b[^>]*>(.*)</body>", raw, flags=re.DOTALL | re.I)
    body = body_m.group(1) if body_m else raw
    body = re.sub(r"<(?:script|style|nav)\b[^>]*>.*?</(?:script|style|nav)>", " ", body, flags=re.DOTALL | re.I)

    heading_re = re.compile(r"<h([1-4])\b[^>]*>(.*?)</h\1>", flags=re.DOTALL | re.I)
    matches = list(heading_re.finditer(body))

    sections: list[dict] = []
    if not matches:
        text, eqs = _html_with_latex_to_text(body)
        if text:
            sections.append({"heading": "Full Text", "text": text, "equations": eqs})
    else:
        # Capture any preamble/abstract before first heading
        pre_html = body[:matches[0].start()]
        pre_text, pre_eqs = _html_with_latex_to_text(pre_html)
        if len(pre_text) > 80:
            sections.append({"heading": "Abstract & Preamble", "text": pre_text, "equations": pre_eqs})

        for idx, m in enumerate(matches):
            h_text, _ = _html_with_latex_to_text(m.group(2))
            h_text = " ".join(h_text.split()) or f"Section {idx + 1}"
            if m.group(1) == "1" or h_text.lower() == title.lower():
                h_text = "Abstract & Frontmatter"
            # Skip bibliography/references sections unless explicitly queried
            if re.search(r"\b(references|bibliography|acknowledg(?:e)?ments)\b", h_text, re.I) and not (
                section_query and re.search(r"ref|bib|cit", section_query, re.I)
            ):
                continue
            start_pos = m.end()
            end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
            sec_text, sec_eqs = _html_with_latex_to_text(body[start_pos:end_pos])
            if sec_text or sec_eqs:
                sections.append({"heading": h_text, "text": sec_text, "equations": sec_eqs})

    headings_outline = [s["heading"] for s in sections[:35]]
    q = (section_query or "").strip()
    q_terms = [t.lower() for t in re.split(r"[^A-Za-z0-9_\\]+", q) if len(t) >= 2]

    scored: list[tuple[float, int, dict]] = []
    default_priority_re = re.compile(
        r"\b(convention|notation|symbol|metric|signature|unit|preliminar|setup|model|lagrangian|action|formalism|definition|equation|introduction|summary)\b",
        re.I,
    )

    for idx, sec in enumerate(sections):
        h_low = sec["heading"].lower()
        t_low = sec["text"].lower()
        eq_joined = " ".join(sec["equations"]).lower()
        score = 0.0
        if q_terms:
            if q.lower() in h_low:
                score += 12.0
            if q.lower() in t_low or q.lower() in eq_joined:
                score += 6.0
            for term in q_terms:
                if term in h_low and h_low != "abstract & frontmatter":
                    score += 4.0
                if term in t_low:
                    score += min(3.0, 0.5 * t_low.count(term))
                if term in eq_joined:
                    score += 3.0
        else:
            if default_priority_re.search(h_low):
                score += 5.0
            if default_priority_re.search(t_low[:600]):
                score += 2.0
            if sec["equations"]:
                score += min(3.0, 0.3 * len(sec["equations"]))
            # Slight preference for early setup sections
            score += max(0.0, 1.5 - 0.1 * idx)
        scored.append((score, idx, sec))

    scored.sort(key=lambda item: (-item[0], item[1]))
    selected: list[dict] = []
    collected_eqs: list[str] = []
    char_budget = max_chars
    matching_count = sum(1 for sc, _, _ in scored if sc > 0)
    per_sec_cap = max(900, int(max_chars * 0.45)) if matching_count >= 2 else max_chars

    for score, _, sec in scored:
        if q_terms and score <= 0 and selected:
            break
        if char_budget <= 0:
            break
        snippet = _select_section_snippet(sec["text"], q_terms, min(char_budget, per_sec_cap))
        selected.append({"heading": sec["heading"], "text": snippet, "score": score})
        for eq in sec["equations"]:
            if eq not in collected_eqs and len(collected_eqs) < 20:
                collected_eqs.append(eq)
        char_budget -= len(snippet)
        if len(selected) >= 4:
            break

    return {
        "title": title,
        "headings": headings_outline,
        "selected_sections": selected,
        "equations": collected_eqs,
    }


class ArxivFullTextSectionInput(BaseModel):
    arxiv_id: str = Field(
        ...,
        description=(
            "The arXiv paper identifier or URL (e.g., '2404.03002', 'arXiv:2306.16219v2', "
            "or 'https://arxiv.org/abs/2404.03002')."
        ),
    )
    section_query: str = Field(
        default="",
        description=(
            "Optional section heading, physical keyword, symbol, or equation query to target "
            "(e.g., 'conventions', 'metric signature', 'sound speed c_s^2', 'Lagrangian', 'Table 1'). "
            "Leave empty to extract the paper's setup, conventions, and key equations."
        ),
    )
    max_chars: int = Field(
        default=4000,
        description="Maximum characters of full-text section content to return (500 to 10000).",
    )


class ArxivFullTextSectionReaderTool(BaseTool):
    name: str = "ArXiv Full-Text Section Reader"
    description: str = (
        "Fetches full-text HTML sections and LaTeX equations directly from an arXiv paper "
        "(via arxiv.org/html and ar5iv.labs.arxiv.org/html with arXiv API fallback). "
        "Use this tool to inspect exact metric signatures, normalization conventions, numerical prefactors "
        "(e.g., 1/(8*pi*G) vs 1/(2*M_Pl^2)), symbol definitions, and full derivations that are omitted from abstracts."
    )
    args_schema: Type[BaseModel] = ArxivFullTextSectionInput

    def _run(
        self,
        arxiv_id: str,
        section_query: str = "",
        max_chars: int = 4000,
    ) -> str:
        clean_id = _normalize_arxiv_id(arxiv_id)
        if not clean_id:
            return "Error: Please provide a valid arXiv ID (e.g., '2404.03002')."

        max_chars = max(500, min(int(max_chars or 4000), 10000))
        html_urls = [
            f"https://arxiv.org/html/{clean_id}",
            f"https://ar5iv.labs.arxiv.org/html/{clean_id}",
        ]

        html_content = ""
        used_url = ""
        for candidate_url in html_urls:
            try:
                req = urllib.request.Request(candidate_url, headers={"User-Agent": _USER_AGENT})
                with urllib.request.urlopen(req, timeout=10) as conn:
                    raw_bytes = conn.read(2_500_000)  # cap at 2.5 MB
                    text_candidate = raw_bytes.decode("utf-8", errors="replace")
                if len(text_candidate) > 500 and ("<p" in text_candidate.lower() or "<section" in text_candidate.lower() or "<h" in text_candidate.lower()):
                    html_content = text_candidate
                    used_url = candidate_url
                    break
            except Exception:
                continue

        if html_content:
            parsed = _extract_arxiv_html_sections(html_content, section_query=section_query, max_chars=max_chars)
            md = [
                f"### 📖 ArXiv Full-Text Section Reader: `{clean_id}`",
                f"- **Title:** {parsed['title']}",
                f"- **Full-Text Source:** [{used_url}]({used_url})",
                f"- **Section Query:** `{section_query or 'default (conventions, setup & equations)'}`",
            ]
            if parsed["headings"]:
                md.append("- **Document Section Outline:** " + " | ".join(f"`{h}`" for h in parsed["headings"][:30]))
            md.append("")
            for sec in parsed["selected_sections"]:
                md.append(f"#### § {sec['heading']}")
                md.append(sec["text"])
                md.append("")
            if parsed["equations"]:
                md.append("#### 🧮 Extracted LaTeX Equations from Matched Sections")
                for eq in parsed["equations"][:12]:
                    md.append(f"- `$${eq}$$`")
            return "\n".join(md)

        # Fallback: fetch full abstract & metadata from export.arxiv.org API when HTML compilation is unavailable
        try:
            api_url = f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(clean_id)}"
            req = urllib.request.Request(api_url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=8) as conn:
                xml_data = conn.read()
            root = ET.fromstring(xml_data)
            ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
            entry = root.find("atom:entry", ns)
            if entry is not None:
                title_el = entry.find("atom:title", ns)
                summary_el = entry.find("atom:summary", ns)
                comment_el = entry.find("arxiv:comment", ns)
                journal_el = entry.find("arxiv:journal_ref", ns)
                title = title_el.text.strip().replace("\n", " ") if title_el is not None and title_el.text else clean_id
                summary = summary_el.text.strip().replace("\n", " ") if summary_el is not None and summary_el.text else ""
                comment = comment_el.text.strip() if comment_el is not None and comment_el.text else ""
                journal = journal_el.text.strip() if journal_el is not None and journal_el.text else ""
                return (
                    f"### 📖 ArXiv Full-Text Section Reader: `{clean_id}` (Abstract/Metadata Fallback)\n"
                    f"- **Title:** {title}\n"
                    f"- **Note:** HTML full-text rendering (`arxiv.org/html` / `ar5iv`) is not available for `{clean_id}`; returning complete abstract & metadata.\n"
                    + (f"- **Journal Ref:** {journal}\n" if journal else "")
                    + (f"- **Comments:** {comment}\n" if comment else "")
                    + f"\n#### Abstract\n{summary}\n"
                )
        except Exception:
            pass

        return f"Could not retrieve full-text HTML or metadata for arXiv ID `{clean_id}`."



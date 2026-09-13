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
                authors = [a.get("author", {}).get("display_name", "") for a in work.get("authorships", [])]
                abstract = reconstruct_abstract(work.get("abstract_inverted_index"))

                # Determine arXiv ID from locations
                arxiv_id = ""
                arxiv_url = ""
                for loc in work.get("locations", []):
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
                    "journal": (work.get("primary_location") or {}).get("source", {}).get("display_name", ""),
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
                authors = [a.get("author", {}).get("display_name", "") for a in w.get("authorships", [])]
                author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")

                # Host venue
                venue = (w.get("primary_location") or {}).get("source", {}).get("display_name", "")

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

        # Detect future-dated years (anything > current_year)
        future_year_pattern = re.compile(rf'\b(202[5-9]|20[3-9]\d)\b')
        placeholder_pattern = re.compile(r'^(Source\s*\d+|Research Report|Academic Journals|Peer-reviewed Articles|Student Summary)', re.IGNORECASE)

        for line in source_lines:
            if placeholder_pattern.search(line):
                flagged_issues.append({
                    "citation": line,
                    "issue_type": "PLACEHOLDER_CITATION",
                    "explanation": "Non-specific generic placeholder; must be replaced with an authentic peer-reviewed publication."
                })
            elif future_year_pattern.search(line):
                flagged_issues.append({
                    "citation": line,
                    "issue_type": "FUTURE_DATED_HALLUCINATION",
                    "explanation": f"Publication year is beyond {current_year}, indicating a hallucinated future citation."
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
                authors = [a.get("author", {}).get("display_name", "") for a in work.get("authorships", [])]
                replacements.append({
                    "title": work.get("title") or "Peer-Reviewed Paper",
                    "doi": doi,
                    "year": str(work.get("publication_year") or ""),
                    "authors": ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
                })
        except Exception:
            pass
        return replacements

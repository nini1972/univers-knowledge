import os
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from crewai.tools import BaseTool


class ScholarlySearchTool(BaseTool):
    name: str = "Scholarly Tavily Search"
    description: str = (
        "A search tool that queries Tavily for high-quality scientific and academic sources. "
        "It prioritizes peer-reviewed and open-access portals (arXiv, NASA, CERN, DOI, and .edu/.ac domains), "
        "filters out non-scholarly sources (forums, social media), verifies URL health, "
        "and automatically generates citation/BibTeX links for academic papers."
    )

    def _run(self, query: str) -> str:
        print(f"[Scholarly Search] Executing optimized academic query: '{query}'")
        raw_results = []
        tavily_key = os.getenv("TAVILY_API_KEY")
        
        # 1. Try Tavily first
        if tavily_key:
            try:
                url = "https://api.tavily.com/search"
                payload = {
                    "api_key": tavily_key,
                    "query": query,
                    "search_depth": "advanced",
                    "include_images": False,
                    "include_answer": False,
                    "include_raw_content": True,
                    "max_results": 15,
                }
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    raw_results = data.get("results", [])
                    print(f"[Scholarly Search] Tavily succeeded: found {len(raw_results)} results.")
                else:
                    print(f"Warning: Tavily returned status {response.status_code}: {response.text}")
            except Exception as exc:
                print(f"Warning: Tavily connection failed: {exc}")
        else:
            print("[Scholarly Search] TAVILY_API_KEY not configured. Skipping Tavily...")

        # 2. Try Serper Fallback if no results
        serper_key = os.getenv("SERPER_API_KEY")
        if not raw_results and serper_key:
            try:
                print("[Scholarly Search] Trying Serper API fallback...")
                headers = {
                    "X-API-KEY": serper_key,
                    "Content-Type": "application/json"
                }
                payload = {"q": query, "num": 15}
                res = requests.post("https://google.serper.dev/search", json=payload, headers=headers, timeout=10)
                if res.status_code == 200:
                    serper_data = res.json()
                    organic = serper_data.get("organic", [])
                    for item in organic:
                        raw_results.append({
                            "url": item.get("link", ""),
                            "title": item.get("title", ""),
                            "content": item.get("snippet", ""),
                            "raw_content": None
                        })
                    print(f"[Scholarly Search] Serper fallback succeeded: found {len(raw_results)} results.")
                else:
                    print(f"Warning: Serper API returned status {res.status_code}: {res.text}")
            except Exception as exc:
                print(f"Warning: Serper fallback failed: {exc}")

        # 3. Try Exa Fallback if no results
        exa_key = os.getenv("EXA_API_KEY")
        if not raw_results and exa_key:
            try:
                print("[Scholarly Search] Trying Exa API fallback...")
                headers = {
                    "x-api-key": exa_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "query": query,
                    "useAutoprompt": False,
                    "numResults": 10,
                    "text": True
                }
                res = requests.post("https://api.exa.ai/search", json=payload, headers=headers, timeout=10)
                if res.status_code == 200:
                    exa_data = res.json()
                    results = exa_data.get("results", [])
                    for item in results:
                        raw_results.append({
                            "url": item.get("url", ""),
                            "title": item.get("title", ""),
                            "content": item.get("text", "") or item.get("author", "") or "",
                            "raw_content": item.get("text", "")
                        })
                    print(f"[Scholarly Search] Exa fallback succeeded: found {len(raw_results)} results.")
                else:
                    print(f"Warning: Exa API returned status {res.status_code}: {res.text}")
            except Exception as exc:
                print(f"Warning: Exa fallback failed: {exc}")

        # 4. Try Public ArXiv API Fallback if no results
        if not raw_results:
            try:
                print("[Scholarly Search] Falling back to Public ArXiv Search API...")
                import urllib.request
                import urllib.parse
                import xml.etree.ElementTree as ET
                
                escaped_query = urllib.parse.quote(query)
                arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{escaped_query}&max_results=12"
                
                with urllib.request.urlopen(arxiv_url, timeout=8) as conn:
                    xml_data = conn.read()
                    
                root = ET.fromstring(xml_data)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                entries = root.findall('atom:entry', ns)
                
                for entry in entries:
                    title_el = entry.find('atom:title', ns)
                    summary_el = entry.find('atom:summary', ns)
                    id_el = entry.find('atom:id', ns)
                    
                    title = title_el.text.strip().replace('\n', ' ') if title_el is not None else "ArXiv Paper"
                    summary = summary_el.text.strip().replace('\n', ' ') if summary_el is not None else ""
                    url = id_el.text.strip() if id_el is not None else ""
                    
                    if url:
                        raw_results.append({
                            "url": url,
                            "title": title,
                            "content": summary,
                            "raw_content": summary
                        })
                print(f"[Scholarly Search] ArXiv fallback succeeded: found {len(raw_results)} papers.")
            except Exception as exc:
                print(f"Warning: ArXiv fallback failed: {exc}")

        if not raw_results:
            return "ERROR: All search APIs (Tavily, Serper, Exa, ArXiv) failed or returned no results."

        # 2. Filter, Rank, and Deduplicate results
        ACADEMIC_DOMAINS = {
            "arxiv.org", "nasa.gov", "cern.ch", "doi.org", "sciencedirect.com",
            "nature.com", "springer.com", "aps.org", "iop.org", "annualreviews.org",
            "nih.gov", "ncbi.nlm.nih.gov", "princeton.edu", "harvard.edu",
            "mit.edu", "stanford.edu", "cam.ac.uk", "ox.ac.uk", "caltech.edu",
            "lbl.gov", "fnal.gov", "slac.stanford.edu", "arxiv-vanity.com",
            "academic.oup.com", "royalsocietypublishing.org", "pnas.org", "unige.ch"
        }

        NON_SCHOLARLY_DOMAINS = {
            "facebook.com", "quora.com", "reddit.com", "twitter.com", "x.com",
            "instagram.com", "youtube.com", "pinterest.com", "vimeo.com",
            "github.com/blog", "medium.com", "buzzfeed.com"
        }

        LOGIN_WALL_DOMAINS = {
            "academia.edu", "researchgate.net"
        }

        seen_urls = set()
        seen_titles = set()
        filtered_results = []

        for item in raw_results:
            url_str = item.get("url", "").strip()
            title_str = item.get("title", "").strip()
            content_str = item.get("content", "").strip()
            raw_content = item.get("raw_content")

            if not url_str:
                continue

            # Parse domain
            domain_match = re.search(r"https?://([^/]+)", url_str)
            domain = domain_match.group(1).lower() if domain_match else ""
            
            # Standardize domain (strip www.)
            if domain.startswith("www."):
                domain = domain[4:]

            # Filter out non-scholarly domains
            if any(ns in domain for ns in NON_SCHOLARLY_DOMAINS):
                continue

            # Deduplicate by URL and Title
            normalized_url = re.sub(r"^https?://", "", url_str).rstrip("/")
            if normalized_url in seen_urls:
                continue
            seen_urls.add(normalized_url)

            normalized_title = re.sub(r"[^a-zA-Z0-9]", "", title_str).lower()
            if normalized_title in seen_titles:
                continue
            seen_titles.add(normalized_title)

            # Assign Tier
            tier = "Tier 2: Standard Reference"
            is_academic = False

            # Check if domain or top-level is explicitly academic
            if any(ad in domain for ad in ACADEMIC_DOMAINS) or domain.endswith((".edu", ".ac.uk", ".gov", ".ac")):
                tier = "Tier 1: Academic & Institutional"
                is_academic = True
            elif any(lw in domain for ad in LOGIN_WALL_DOMAINS for lw in [ad]):
                tier = "Tier 3: Login Wall / Aggregator"

            filtered_results.append({
                "url": url_str,
                "title": title_str,
                "snippet": content_str,
                "raw_content": raw_content,
                "domain": domain,
                "tier": tier,
                "is_academic": is_academic
            })

        # 3. Perform Rapid Parallel Link Health Verification
        def check_url_health(result):
            url_str = result["url"]
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                # Short timeout, allow redirects
                resp = requests.head(url_str, timeout=1.5, headers=headers, allow_redirects=True)
                if resp.status_code == 404:
                    return False
                if resp.status_code in {403, 405}:
                    # Double check with a small stream GET request to avoid false negatives on HEAD blockers
                    resp_get = requests.get(url_str, timeout=1.5, headers=headers, stream=True)
                    if resp_get.status_code == 404:
                        return False
                return True
            except Exception:
                # Keep the link if it just timed out or had SSL issues to avoid over-filtering
                return True

        healthy_results = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_result = {executor.submit(check_url_health, r): r for r in filtered_results}
            for future in as_completed(future_to_result):
                result = future_to_result[future]
                is_healthy = True
                try:
                    is_healthy = future.result()
                except Exception:
                    is_healthy = True
                if is_healthy:
                    healthy_results.append(result)

        # 4. Sort results: Academic (Tier 1) -> Standard (Tier 2) -> Login Wall (Tier 3)
        def sorting_key(r):
            if "Tier 1" in r["tier"]:
                return 1
            if "Tier 2" in r["tier"]:
                return 2
            return 3

        healthy_results.sort(key=sorting_key)

        # 5. Build final Markdown output
        md_output = []
        md_output.append("### 🔎 Scholarly Search Results")
        md_output.append(f"Successfully processed academic query. Retrained {len(healthy_results)} healthy sources.")
        md_output.append("")

        for idx, item in enumerate(healthy_results[:8], start=1):
            url_str = item["url"]
            title_str = item["title"]
            snippet = item["snippet"] or "No snippet extracted."
            tier = item["tier"]
            raw_content = item["raw_content"]

            md_output.append(f"{idx}. **[{title_str}]({url_str})**")
            md_output.append(f"   * **Classification**: `{tier}` | **Domain**: `{item['domain']}`")
            
            # Content verification note
            if not raw_content:
                md_output.append("   * **Extraction Note**: *Metadata snippet only (restricted/full content unavailable)*")
            
            # Generate Citation helpers
            # 1. arXiv ID
            arxiv_match = re.search(r"arxiv\.org/(?:abs|pdf)/(\d+\.\d+)", url_str, re.IGNORECASE)
            if arxiv_match:
                arxiv_id = arxiv_match.group(1)
                md_output.append(f"   * **Citation (BibTeX)**: [ArXiv BibTeX Export](https://arxiv.org/hypertex/bibstyles/) (ID: `{arxiv_id}`)")
            
            # 2. DOI
            doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", url_str, re.IGNORECASE)
            if doi_match:
                doi = doi_match.group(0).rstrip(").,")
                md_output.append(f"   * **Citation (BibTeX)**: [CrossRef Resolver](https://api.crossref.org/works/{doi}/transform/application/x-bibtex) (DOI: `{doi}`)")

            md_output.append(f"   * **Summary**: {snippet}")
            md_output.append("")

        return "\n".join(md_output)

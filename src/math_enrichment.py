"""
math_enrichment.py
==================
Retroactive Math Verification & Derivation Enrichment Pipeline

Scans all existing knowledge base Markdown documents and enriches them with:
  - ## 8. Mathematical Derivation  (Tier 2 — Derivation Architect)
  - ## 9. Mathematical Integrity Report (Tier 1 — Math Physicist tools, direct)
  - YAML frontmatter: math_status, math_score fields

Usage:
  uv run python src/math_enrichment.py --level 1
  uv run python src/math_enrichment.py --level all
  uv run python src/math_enrichment.py --concept quantum_electrodynamics_qed
  uv run python src/math_enrichment.py --concept quantum_electrodynamics_qed --dry-run

Produces a run log at: knowledge_base/logs/math_enrichment.jsonl
"""
from __future__ import annotations

import sys
import os
import argparse
import json
import re
import time
from pathlib import Path
from datetime import datetime, timezone

# Ensure venv site-packages for crewai and tools
REPO_ROOT = Path(__file__).resolve().parent.parent
VENV_SP = REPO_ROOT / ".venv" / "Lib" / "site-packages"
if VENV_SP.exists():
    import site; site.addsitedir(str(VENV_SP))

sys.path.insert(0, str(REPO_ROOT / "src"))

from dotenv import load_dotenv
load_dotenv(dotenv_path=REPO_ROOT / ".env")

try:
    from tools.math_tools import (
        EquationExtractorTool,
        DimensionalConsistencyTool,
        TopologyClassifierTool,
        NumericalBenchmarkTool,
    )
    from workflow_contracts import parse_math_score, parse_math_status
except ImportError as e:
    print(f"ERROR: Could not import math tools: {e}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LEVEL_DIRS = {
    "1": "level_1_fundamental_physics",
    "2": "level_2_advanced_frameworks",
    "3": "level_3_emergence_and_intelligence",
}
KB_ROOT = REPO_ROOT / "knowledge_base"
LOG_FILE = KB_ROOT / "logs" / "math_enrichment.jsonl"
RATE_LIMIT_SECONDS = 3  # seconds between concepts to respect API limits


# ---------------------------------------------------------------------------
# YAML frontmatter helpers
# ---------------------------------------------------------------------------

def read_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML-style frontmatter block from markdown. Returns (meta_dict, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    frontmatter_block = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    meta = {}
    for line in frontmatter_block.splitlines():
        if ":" in line and not line.strip().startswith("-"):
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip().strip('"')
    return meta, body


def write_frontmatter(meta: dict, body: str) -> str:
    """Reconstruct markdown file with updated frontmatter."""
    lines = ["---"]
    for key, val in meta.items():
        if key == "sources":
            lines.append("sources:")
            if isinstance(val, list):
                for s in val:
                    lines.append(f"  - {s}")
            else:
                lines.append(f"  - {val}")
        else:
            lines.append(f'{key}: "{val}"')
    lines.append("---")
    lines.append("")
    lines.append(body)
    return "\n".join(lines)


def update_doc_frontmatter(filepath: Path, math_status: str, math_score: str):
    """Update math_status and math_score in a document's YAML frontmatter."""
    text = filepath.read_text(encoding="utf-8")
    meta, body = read_frontmatter(text)

    # Detect existing sources list
    if "sources:" in text and isinstance(meta.get("sources"), str):
        # Re-parse sources as list from raw text
        raw_lines = text.split("\n")
        sources = []
        in_sources = False
        for ln in raw_lines:
            if ln.strip() == "sources:":
                in_sources = True
                continue
            if in_sources:
                if ln.startswith("  - "):
                    sources.append(ln[4:].strip())
                elif ln.startswith("-"):
                    break
                else:
                    break
        if sources:
            meta["sources"] = sources

    meta["math_status"] = f"[{math_status}]"
    meta["math_score"] = math_score

    # Rebuild the full file preserving the body
    updated = write_frontmatter(meta, body)
    filepath.write_text(updated, encoding="utf-8")


# ---------------------------------------------------------------------------
# Section injection helpers
# ---------------------------------------------------------------------------

SECTION_8_MARKER = "## 8. Mathematical Derivation"
SECTION_9_MARKER = "## 9. Mathematical Integrity Report"


def has_math_sections(text: str) -> bool:
    """Returns True if doc already has both math sections."""
    return SECTION_8_MARKER in text and SECTION_9_MARKER in text


def inject_math_sections(filepath: Path, section8: str, section9: str):
    """Append or replace sections 8 and 9 in a markdown document."""
    text = filepath.read_text(encoding="utf-8")

    # Remove existing math sections if present (for overwrite mode)
    for marker in [SECTION_8_MARKER, SECTION_9_MARKER]:
        idx = text.find(f"\n{marker}")
        if idx != -1:
            text = text[:idx]

    text = text.rstrip("\n") + "\n\n" + section8.strip() + "\n\n" + section9.strip() + "\n"
    filepath.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Tier 1: Direct tool run (no LLM needed)
# ---------------------------------------------------------------------------

def run_tier1_tools(concept_name: str, doc_text: str) -> tuple[str, str, str]:
    """
    Run the 4 Tier-1 math tools directly (no agent/LLM overhead).
    Returns (section9_markdown, math_status_str, math_score_str)
    """
    extractor = EquationExtractorTool()
    dim_checker = DimensionalConsistencyTool()
    topo_classifier = TopologyClassifierTool()
    num_benchmark = NumericalBenchmarkTool()

    # Step 1: Extract equations
    eq_result_json = extractor._run(doc_text)
    eq_data = json.loads(eq_result_json)
    equations = eq_data.get("equations", [])
    eq_count = eq_data.get("count", 0)

    # Step 2: Dimensional consistency
    dim_result_json = dim_checker._run(eq_result_json)
    dim_data = json.loads(dim_result_json)
    dim_verdict = dim_data.get("overall_verdict", "ALL_UNDECIDABLE")
    consistent = dim_data.get("consistent_count", 0)
    inconsistent = dim_data.get("inconsistent_count", 0)

    # Step 3: Topology
    topo_result_json = topo_classifier._run(concept_name, doc_text)
    topo_data = json.loads(topo_result_json)
    is_topo = topo_data.get("is_topological", False)
    topo_structures = topo_data.get("detected_structures", [])

    # Step 4: Numerical benchmark
    bench_result_json = num_benchmark._run(concept_name, eq_result_json)
    bench_data = json.loads(bench_result_json)
    bench_verdict = bench_data.get("verdict", "BENCHMARK_UNAVAILABLE")
    bench_matched = bench_data.get("matched_benchmarks", 0)

    # Compute Math Score
    points = 0
    if eq_count > 0:
        points += 1
    if dim_verdict == "ALL_CONSISTENT" or (is_topo and dim_verdict != "INCONSISTENCY_DETECTED"):
        points += 1
    if is_topo or dim_verdict == "ALL_CONSISTENT":
        points += 1
    if bench_verdict == "BENCHMARK_MATCHES" or (eq_count == 0 and bench_verdict == "BENCHMARK_UNAVAILABLE"):
        points += 1

    math_score_str = f"{points}/4"

    # Assign math_status
    if inconsistent > 0:
        math_status = "MATH_FLAWED"
    elif is_topo:
        math_status = "MATH_TOPOLOGICAL"
    elif points == 4:
        math_status = "MATH_PROVEN"
    elif points >= 2:
        math_status = "MATH_CONSISTENT"
    elif eq_count == 0:
        math_status = "MATH_PENDING"
    else:
        math_status = "MATH_CONJECTURED"

    # Build Section 9 markdown
    eq_list = "\n".join(f"- `{eq[:100]}`" for eq in equations[:10]) or "None found"
    dim_rows = ""
    for r in dim_data.get("results", [])[:8]:
        dim_rows += f"| `{r['equation'][:60]}` | {r['verdict']} | {r['explanation'][:80]} |\n"
    if not dim_rows:
        dim_rows = "| — | UNDECIDABLE | No equations to check |\n"

    topo_text = "Not topological — standard physics formalism."
    if topo_structures:
        topo_text = "\n".join(
            f"- **{s['topology_type']}**: {s['note'][:120]}"
            for s in topo_structures[:5]
        )

    bench_text = "Not applicable — no matching physical constants found."
    if bench_data.get("results"):
        bench_text = "\n".join(
            f"- **{r['benchmark']}** ({r['symbol']}): {r['formula']} [{r['source']}]"
            for r in bench_data["results"][:5]
        )

    assessment = (
        f"Mathematical integrity check found {eq_count} equation(s). "
        f"Dimensional analysis: {dim_verdict.lower().replace('_', ' ')} "
        f"({consistent} consistent, {inconsistent} inconsistent). "
        + (f"Topological structures detected: {', '.join(s['topology_type'] for s in topo_structures[:3])}. " if is_topo else "")
        + (f"Benchmark: {bench_matched} physical constant(s) referenced. " if bench_matched else "")
        + f"Assigned math_status: [{math_status}]."
    )

    section9 = f"""## 9. Mathematical Integrity Report
*(Auto-generated by Math Physicist agent — Tier 1 check)*

**Math Score:** {math_score_str}
**Math Status:** [{math_status}]

### Equations Extracted
{eq_list}

### Dimensional Consistency
| Equation | Verdict | Explanation |
|---|---|---|
{dim_rows}
**Overall:** {dim_verdict}

### Topological Analysis
{topo_text}

### Numerical Benchmarks
{bench_text}

### Assessment
{assessment}
"""

    return section9, math_status, math_score_str


# ---------------------------------------------------------------------------
# Tier 2: Derivation Architect via CrewAI (LLM-powered)
# ---------------------------------------------------------------------------

def run_tier2_derivation(concept_name: str, doc_text: str, dry_run: bool = False) -> str:
    """
    Run the Derivation Architect agent (Tier 2) to produce section 8.
    Returns the ## 8. Mathematical Derivation section as a markdown string.
    """
    if dry_run:
        return f"""## 8. Mathematical Derivation
*(Dry-run mode — placeholder generated)*

### Starting Axioms
- [AXIOM] Placeholder axiom for {concept_name}

### Step-by-Step Derivation
**Step 1** [STEP_ASSUMED]: Dry-run placeholder step.

### Final Result
$$\\text{{Derivation pending full run}}$$

### Proof Boundary
| Category | Count | Interpretation |
|---|---|---|
| Proven steps | 0 | Not yet verified |
| Assumed steps | 1 | Placeholder |
| Conjectured steps | 0 | — |

### Mathematical Status
**{concept_name}** receives: `[MATH_PENDING]`

Derivation not yet run in production mode.
"""

    try:
        from crewai import Crew, Process
        from agents.universe_agents import UniverseAgents
        from tasks.universe_tasks import UniverseTasks

        agents = UniverseAgents()
        tasks_factory = UniverseTasks()
        architect = agents.derivation_architect_agent()

        task = tasks_factory.derivation_deep_dive_task(
            agent=architect,
            concept=concept_name,
            research_text=doc_text[:4000],
        )

        crew = Crew(
            agents=[architect],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )

        result = str(crew.kickoff()).strip()

        # Ensure it starts with the correct heading
        if SECTION_8_MARKER not in result:
            result = SECTION_8_MARKER + "\n\n" + result

        return result

    except Exception as exc:
        return f"""## 8. Mathematical Derivation
*(Derivation Architect encountered an error: {exc})*

[DERIVATION_PENDING — rerun with: python src/math_enrichment.py --concept {concept_name.lower().replace(' ', '_')}]
"""


# ---------------------------------------------------------------------------
# Log helpers
# ---------------------------------------------------------------------------

def append_log(record: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


# ---------------------------------------------------------------------------
# Main enrichment logic
# ---------------------------------------------------------------------------

def enrich_document(filepath: Path, dry_run: bool = False, force: bool = False) -> dict:
    """
    Enrich a single concept markdown file with math sections.
    Returns a status dict for logging.
    """
    concept_name = filepath.stem.replace("_", " ").title()
    print(f"\n{'='*60}")
    print(f"Enriching: {concept_name}")
    print(f"File: {filepath.name}")

    text = filepath.read_text(encoding="utf-8")
    meta, _ = read_frontmatter(text)

    # Skip if already enriched (unless force flag)
    if not force and has_math_sections(text):
        existing_status = meta.get("math_status", "[MATH_PENDING]")
        if existing_status and "[MATH_PENDING]" not in existing_status:
            print(f"  SKIP — already enriched with {existing_status}")
            return {"concept": concept_name, "status": "skipped", "reason": "already_enriched"}

    start = time.time()

    # Tier 1: Direct tools (no LLM)
    print("  [Tier 1] Running math tool checks...")
    section9, math_status, math_score_str = run_tier1_tools(concept_name, text)
    print(f"  [Tier 1] Math Score: {math_score_str} | Status: [{math_status}]")

    # Tier 2: LLM Derivation Architect
    print("  [Tier 2] Running Derivation Architect...")
    section8 = run_tier2_derivation(concept_name, text, dry_run=dry_run)
    print(f"  [Tier 2] Derivation section generated.")

    if not dry_run:
        # Inject sections into document
        inject_math_sections(filepath, section8, section9)
        # Update frontmatter
        update_doc_frontmatter(filepath, math_status, math_score_str)
        print(f"  Saved enriched document.")
    else:
        print(f"  [DRY RUN] Would write sections 8 & 9 with status [{math_status}]")

    duration = time.time() - start
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "concept": concept_name,
        "file": str(filepath.name),
        "math_status": math_status,
        "math_score": math_score_str,
        "duration_seconds": round(duration, 1),
        "dry_run": dry_run,
        "status": "dry_run" if dry_run else "enriched"
    }
    append_log(record)
    return record


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Retroactive Math Enrichment Pipeline for Univers Knowledge"
    )
    parser.add_argument(
        "--level", choices=["1", "2", "3", "all"], default="all",
        help="Knowledge base level to enrich (default: all)"
    )
    parser.add_argument(
        "--concept", type=str, default=None,
        help="Enrich a single concept by filename (e.g. quantum_electrodynamics_qed)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Run without writing files (preview mode)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-enrich even if math sections already exist"
    )
    parser.add_argument(
        "--rate-limit", type=int, default=RATE_LIMIT_SECONDS,
        help=f"Seconds between concepts to respect API limits (default: {RATE_LIMIT_SECONDS})"
    )
    args = parser.parse_args()

    print("\n[MATH] Univers Knowledge -- Math Enrichment Pipeline")
    print(f"   Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"   Rate limit: {args.rate_limit}s between concepts")
    print()

    # Collect files to process
    if args.concept:
        # Single concept mode
        concept_key = args.concept.lower().replace(" ", "_")
        found = list(KB_ROOT.rglob(f"{concept_key}.md"))
        if not found:
            # Try partial match
            found = [f for f in KB_ROOT.rglob("*.md") if concept_key in f.stem]
        if not found:
            print(f"ERROR: No file found matching '{args.concept}'")
            sys.exit(1)
        files = found[:1]
        print(f"Single concept mode: {files[0]}")
    else:
        # Multi-level mode
        levels = ["1", "2", "3"] if args.level == "all" else [args.level]
        files = []
        for lvl in levels:
            lvl_dir = KB_ROOT / LEVEL_DIRS[lvl]
            if lvl_dir.exists():
                lvl_files = sorted(lvl_dir.glob("*.md"))
                print(f"Level {lvl}: {len(lvl_files)} files in {LEVEL_DIRS[lvl]}/")
                files.extend(lvl_files)
            else:
                print(f"WARNING: Level {lvl} directory not found: {lvl_dir}")

    # Filter out template and index files
    files = [f for f in files if not f.name.startswith("_") and f.name != "concept_template.md"]

    print(f"\nTotal files to process: {len(files)}")
    if args.dry_run:
        print("DRY RUN: No files will be modified.\n")

    results = {"enriched": 0, "skipped": 0, "errors": 0}

    for i, filepath in enumerate(files, 1):
        try:
            print(f"\n[{i}/{len(files)}]", end="")
            record = enrich_document(filepath, dry_run=args.dry_run, force=args.force)
            if record["status"] == "skipped":
                results["skipped"] += 1
            else:
                results["enriched"] += 1
        except Exception as exc:
            print(f"  ERROR: {exc}")
            append_log({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "concept": filepath.stem,
                "status": "error",
                "error": str(exc)
            })
            results["errors"] += 1

        # Rate limiting (skip on last item)
        if i < len(files) and not args.dry_run:
            print(f"  Waiting {args.rate_limit}s before next concept...")
            time.sleep(args.rate_limit)

    print(f"\n{'='*60}")
    print(f"[DONE] Math Enrichment Complete")
    print(f"   Enriched: {results['enriched']}")
    print(f"   Skipped:  {results['skipped']}")
    print(f"   Errors:   {results['errors']}")
    print(f"   Log:      {LOG_FILE}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

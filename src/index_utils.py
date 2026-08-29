import re
import json
from pathlib import Path


def index_heading_for_level(level_folder: str, default_heading: str) -> str:
    mapping = {
        "level_1_fundamental_physics": "## Level 1: Fundamental Physics",
        "level_2_advanced_frameworks": "## Level 2: Advanced Frameworks",
        "level_3_emergence_and_intelligence": "## Level 3: Emergence and Intelligence",
    }
    return mapping.get(level_folder, default_heading)


def extract_title_from_md(file_path: Path) -> str:
    """Extracts title from YAML frontmatter or first # heading in a markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return file_path.stem.replace("_", " ").title()

    # Try YAML frontmatter
    frontmatter_match = re.search(r"^---\s*\n([\s\S]*?)\n---\s*", content)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        for line in frontmatter.splitlines():
            if line.strip().lower().startswith("title:"):
                title_val = line.split(":", 1)[1].strip()
                # strip outer quotes if any
                title_val = re.sub(r'^["\']|["\']$', '', title_val).strip()
                if title_val:
                    return title_val

    # Try first # heading
    heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if heading_match:
        return heading_match.group(1).strip()

    # Fallback to stem
    return file_path.stem.replace("_", " ").title()


def parse_concept_md(file_path: Path, folder_name: str) -> dict:
    """Parses a single markdown concept file to extract structured metadata, images, and relations."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        content = ""

    title = extract_title_from_md(file_path)
    stem = file_path.stem

    # Defaults
    level = 1
    if "level_2" in folder_name:
        level = 2
    elif "level_3" in folder_name:
        level = 3

    status = "THEORETICAL"
    math_status = "MATH_PENDING"
    math_score = "0/4"
    sources = []

    # Parse YAML frontmatter
    frontmatter_match = re.search(r"^---\s*\n([\s\S]*?)\n---\s*", content)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        for line in frontmatter.splitlines():
            line_str = line.strip()
            if line_str.lower().startswith("level:"):
                try:
                    level = int(line_str.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line_str.lower().startswith("status:"):
                val = line_str.split(":", 1)[1].strip().upper()
                if "VERIFIED" in val:
                    status = "VERIFIED"
                elif "THEORETICAL" in val:
                    status = "THEORETICAL"
                elif "REJECTED" in val:
                    status = "REJECTED"
            elif line_str.lower().startswith("math_status:"):
                raw = line_str.split(":", 1)[1].strip().strip('"').strip("'").upper()
                # Normalize: strip brackets → e.g. [MATH_PROVEN] → MATH_PROVEN
                math_status = raw.replace("[", "").replace("]", "").strip()
            elif line_str.lower().startswith("math_score:"):
                raw_score = line_str.split(":", 1)[1].strip().strip('"').strip("'")
                if "/" in raw_score:
                    math_score = raw_score

        # Extract sources list
        sources_match = re.search(r"sources:\s*\n((?:\s*-\s*.+\n?)+)", frontmatter)
        if sources_match:
            for s_line in sources_match.group(1).splitlines():
                s_val = s_line.strip().lstrip("-").strip()
                if s_val:
                    sources.append(s_val)

    # Extract image path if any (e.g. ![caption](image_path))
    image_path = None
    img_match = re.search(r"!\[[^\]]*\]\(([^)]+)\)", content)
    if img_match:
        image_path = img_match.group(1).strip()
        # Strip any leading ../ or relative prefixes
        if image_path.startswith("../"):
            image_path = image_path.replace("../", "")

    # Extract related concepts (from both markdown links and bullet points under "Related Concepts" section)
    related = []
    links = re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", content)
    for l in links:
        target_stem = Path(l).stem
        if target_stem != stem and target_stem not in related:
            related.append(target_stem)

    # Also parse bullet points under the "Related Concepts" heading
    rc_match = re.search(r"##\s+\d+\.\s+Related Concepts\s*\n([\s\S]*?)(?=\n##|$)", content, re.IGNORECASE)
    if rc_match:
        section_text = rc_match.group(1)
        items = re.findall(r"^\s*[-*]\s+(.+)$", section_text, re.MULTILINE)
        for item in items:
            item_clean = item.strip()
            # If it's a markdown link [Text](file.md), extract the stem
            link_match = re.match(r"\[([^\]]+)\]\(([^)]+\.md)\)", item_clean)
            if link_match:
                target_stem = Path(link_match.group(2)).stem
            else:
                # Sanitize plain text title to standard lowercase snake_case ID
                t = item_clean.strip().lower()
                t = re.sub(r'[\s\-]+', '_', t)
                t = re.sub(r'[^\w]', '', t)
                t = re.sub(r'_+', '_', t)
                target_stem = t
            
            if target_stem and target_stem != stem and target_stem not in related:
                related.append(target_stem)


    # Extract overview summary from section "## 1. Overview"
    overview = ""
    overview_match = re.search(r"## 1\.\s+Overview\s*\n([\s\S]*?)(?=\n##|$)", content)
    if overview_match:
        overview = overview_match.group(1).strip()

    return {
        "id": stem,
        "title": title,
        "level": level,
        "status": status,
        "math_status": math_status,
        "math_score": math_score,
        "sources": sources,
        "path": f"{folder_name}/{file_path.name}",
        "image_path": image_path,
        "overview": overview,
        "related": related,
        "content": content
    }


def prune_stale_index_links(index_lines, repo_root: Path):
    out = []
    for line in index_lines:
        match = re.search(r"\[[^\]]+\]\(([^)]+\.md)\)", line)
        if match and line.lstrip().startswith("-"):
            target = repo_root / "knowledge_base" / match.group(1)
            if not target.exists():
                continue
        out.append(line)
    return out


def generate_mermaid_diagram(concepts: list) -> list:
    """Generates a beautiful Mermaid.js flowchart string from parsed concepts."""
    lines = ["```mermaid", "graph TD", "    %% Custom Stylings for Glow Aesthetics"]
    lines.append("    classDef verified fill:#072b22,stroke:#10b981,stroke-width:2px,color:#d1fae5;")
    lines.append("    classDef theoretical fill:#241d08,stroke:#f59e0b,stroke-width:2px,color:#fef3c7;")
    lines.append("")

    # Map for easy lookup
    concept_map = {c["id"]: c for c in concepts}

    # Add Nodes
    lines.append("    %% Concept Nodes")
    for c in concepts:
        style_cls = "verified" if c["status"] == "VERIFIED" else "theoretical"
        safe_title = c["title"].replace('"', '\\"')
        lines.append(f'    {c["id"]}["{safe_title}"]:::{style_cls}')

    lines.append("")

    # Add Edges (only if both nodes exist to prevent dangling links)
    lines.append("    %% Connections & Prerequisites")
    edges_drawn = set()
    for c in concepts:
        for r in c["related"]:
            if r in concept_map:
                # To prevent duplicate reciprocal edges, sort alphabetically
                edge = tuple(sorted([c["id"], r]))
                if edge not in edges_drawn:
                    # Foundational concept in related goes first
                    if concept_map[r]["level"] < c["level"]:
                        lines.append(f"    {r} --> {c['id']}")
                    elif concept_map[r]["level"] > c["level"]:
                        lines.append(f"    {c['id']} --> {r}")
                    else:
                        lines.append(f"    {r} --- {c['id']}")
                    edges_drawn.add(edge)

    lines.append("```")
    return lines


def synchronize_index(index_path: str, repo_root: Path) -> str:
    """
    Scans the knowledge base folders, extracts metadata,
    writes a compiled JSON database for the dashboard,
    and updates the index file with a stunning Mermaid.js diagram and accurate links.
    """
    kb_dir = repo_root / "knowledge_base"
    idx_file = repo_root / index_path

    # Define the levels we support and their headings
    levels = [
        ("level_1_fundamental_physics", "## Level 1: Fundamental Physics"),
        ("level_2_advanced_frameworks", "## Level 2: Advanced Frameworks"),
        ("level_3_emergence_and_intelligence", "## Level 3: Emergence and Intelligence"),
    ]

    all_concepts = []

    # Read and parse all concepts from disk
    for folder_name, heading in levels:
        folder_path = kb_dir / folder_name
        if folder_path.exists() and folder_path.is_dir():
            md_files = list(folder_path.glob("*.md"))
            for f in md_files:
                concept_data = parse_concept_md(f, folder_name)
                all_concepts.append(concept_data)

    # Write the compiled JSON database for the futuristic dashboard
    db_file = kb_dir / "database.json"
    kb_dir.mkdir(parents=True, exist_ok=True)
    db_file.write_text(json.dumps(all_concepts, indent=2, ensure_ascii=False), encoding="utf-8")

    # Start compiling the _index.md content
    index_lines = ["# Knowledge Base Index", ""]

    # Inject Mermaid.js visual graph
    if all_concepts:
        index_lines.append("## Interactive Concept Network")
        index_lines.append("")
        index_lines.extend(generate_mermaid_diagram(all_concepts))
        index_lines.append("")

    # Add the alphabetical lists for each level folder
    for folder_name, heading in levels:
        index_lines.append(heading)
        index_lines.append("")

        folder_concepts = [c for c in all_concepts if c["path"].startswith(folder_name)]
        # Sort alphabetically by title
        folder_concepts.sort(key=lambda x: x["title"].lower())

        for c in folder_concepts:
            status_tag = " [VERIFIED]" if c["status"] == "VERIFIED" else " [THEORETICAL]"
            index_lines.append(f"- [{c['title']}]({c['path']}){status_tag}")

        if not folder_concepts:
            index_lines.append("- (other entries)")

        index_lines.append("")

    # Write back the generated index
    new_index_content = "\n".join(index_lines).rstrip() + "\n"
    idx_file.write_text(new_index_content, encoding="utf-8")
    return new_index_content


def sanitize_index_file(index_path: str, repo_root: Path) -> str:
    return synchronize_index(index_path, repo_root)


def generate_clean_topic_digest(all_concepts: list = None, repo_root: Path = None, target_level: int = None) -> str:
    """
    Generates a clean, structured, and lightweight topic digest for CrewAI agents.
    Completely excludes Mermaid diagrams, visual formatting syntax, and file paths to minimize token load.
    """
    if all_concepts is None:
        if repo_root is None:
            repo_root = Path(__file__).resolve().parent.parent
        db_file = repo_root / "knowledge_base" / "database.json"
        if db_file.exists():
            try:
                all_concepts = json.loads(db_file.read_text(encoding="utf-8"))
            except Exception:
                all_concepts = []
        else:
            all_concepts = []

    level_headings = {
        1: "Level 1: Fundamental Physics",
        2: "Level 2: Advanced Frameworks (Debates & Competing Theories)",
        3: "Level 3: Emergence, Intelligence & Cosmological Architecture",
    }

    lines = [f"# Knowledge Base Summary ({len(all_concepts)} Topics Already Covered)", ""]

    for lvl in [1, 2, 3]:
        lvl_concepts = [c for c in all_concepts if c.get("level") == lvl or (lvl == 1 and "level_1" in c.get("path", "")) or (lvl == 2 and "level_2" in c.get("path", "")) or (lvl == 3 and "level_3" in c.get("path", ""))]
        lvl_concepts.sort(key=lambda x: x["title"].lower())

        heading = level_headings.get(lvl, f"Level {lvl}")
        lines.append(f"## {heading} ({len(lvl_concepts)} covered)")
        lines.append("")
        for c in lvl_concepts:
            status = str(c.get("status", "THEORETICAL")).strip("[]")
            status_tag = f"[{status}]"
            math_status = str(c.get("math_status", "")).strip("[]")
            math_tag = f" [{math_status}]" if math_status and math_status != "MATH_UNKNOWN" else ""
            lines.append(f"- {c['title']} {status_tag}{math_tag}")

        if not lvl_concepts:
            lines.append("- (no entries yet)")
        lines.append("")

    return "\n".join(lines).strip()


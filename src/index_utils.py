import re
import json
from pathlib import Path


def index_heading_for_level(level_folder: str, default_heading: str) -> str:
    mapping = {
        "level_1_fundamental_physics": "## Level 1: Fundamental Physics",
        "level_2_advanced_frameworks": "## Level 2: Advanced Frameworks",
        "level_3_cosmology_and_astrophysics": "## Level 3: Cosmology and Astrophysics",
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

    # Extract related concepts (links)
    related = []
    links = re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", content)
    for l in links:
        target_stem = Path(l).stem
        if target_stem != stem and target_stem not in related:
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
        ("level_3_cosmology_and_astrophysics", "## Level 3: Cosmology and Astrophysics"),
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

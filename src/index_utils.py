import re
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


def synchronize_index(index_path: str, repo_root: Path) -> str:
    """
    Scans the knowledge base folders, extracts the titles of all existing md files,
    and updates the index file to match exactly.
    """
    kb_dir = repo_root / "knowledge_base"
    idx_file = repo_root / index_path

    # Define the levels we support and their headings
    levels = [
        ("level_1_fundamental_physics", "## Level 1: Fundamental Physics"),
        ("level_2_advanced_frameworks", "## Level 2: Advanced Frameworks"),
        ("level_3_cosmology_and_astrophysics", "## Level 3: Cosmology and Astrophysics"),
    ]

    index_lines = ["# Knowledge Base Index", ""]

    for folder_name, heading in levels:
        folder_path = kb_dir / folder_name
        index_lines.append(heading)
        index_lines.append("")

        if folder_path.exists() and folder_path.is_dir():
            # Find all .md files (excluding index or templates)
            md_files = sorted(list(folder_path.glob("*.md")))
            entries = []
            for f in md_files:
                title = extract_title_from_md(f)
                rel_path = f"{folder_name}/{f.name}"
                entries.append((title, rel_path))
            
            # Sort entries alphabetically by title
            entries.sort(key=lambda x: x[0].lower())

            for title, rel_path in entries:
                index_lines.append(f"- [{title}]({rel_path})")
            
            if not entries:
                index_lines.append("- (other entries)")
        else:
            index_lines.append("- (other entries)")

        index_lines.append("")

    # Write back the generated index
    new_index_content = "\n".join(index_lines).rstrip() + "\n"
    idx_file.write_text(new_index_content, encoding="utf-8")
    return new_index_content


def sanitize_index_file(index_path: str, repo_root: Path) -> str:
    return synchronize_index(index_path, repo_root)

import re
from pathlib import Path


def index_heading_for_level(level_folder: str, default_heading: str) -> str:
    mapping = {
        "level_1_fundamental_physics": "## Level 1: Fundamental Physics",
        "level_2_advanced_frameworks": "## Level 2: Advanced Frameworks",
    }
    return mapping.get(level_folder, default_heading)


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


def sanitize_index_file(index_path: str, repo_root: Path):
    idx = repo_root / index_path
    if not idx.exists():
        return "Index not found. Start with basic physics."
    lines = idx.read_text(encoding="utf-8").splitlines()
    lines = prune_stale_index_links(lines, repo_root)
    idx.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return idx.read_text(encoding="utf-8")

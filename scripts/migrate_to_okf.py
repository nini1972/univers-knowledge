#!/usr/bin/env python3
"""
OKF Migration Utility for Universe Knowledge.

Scans all existing markdown concept files across Level 1 and Level 2,
replaces/upgrades their YAML frontmatter blocks to be fully compliant with
the Open Knowledge Format (OKF) schema, including explicit 'id', 'dependencies', and 'tags'.
"""

import re
from pathlib import Path

def sanitize_slug(name: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9\s]', '', str(name)).strip().replace(' ', '_').lower()
    return re.sub(r'_+', '_', s)

def parse_existing_frontmatter(text: str):
    if not text.startswith("---"):
        return {}, text

    end_match = re.search(r"\n---\s*\n", text[3:])
    if not end_match:
        return {}, text

    end_idx = end_match.start() + 3
    fm_text = text[3:end_idx].strip()
    body_text = text[end_idx + len(end_match.group(0)):].strip()

    data = {}
    current_key = None

    for line in fm_text.splitlines():
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("#"):
            continue

        if line_clean.startswith("-") and current_key:
            item = line_clean.lstrip("-").strip().strip('"').strip("'")
            if not isinstance(data.get(current_key), list):
                data[current_key] = []
            data[current_key].append(item)
            continue

        if ":" in line_clean:
            key, val = line_clean.split(":", 1)
            key = key.strip().lower()
            val = val.strip()

            if val.startswith("-"):
                item = val.lstrip("-").strip().strip('"').strip("'")
                data[key] = [item]
                current_key = key
            elif not val:
                data[key] = []
                current_key = key
            else:
                val_clean = val.strip('"').strip("'")
                data[key] = val_clean
                current_key = key

    return data, body_text

def extract_title_and_links(body_text: str, stem: str):
    title_match = re.search(r"^#\s+(.+)$", body_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else stem.replace("_", " ").title()

    # Extract links in body
    links = []
    for match in re.finditer(r'\[([^\]]+)\]\(([^)]+\.md)\)', body_text):
        target_path = match.group(2)
        target_stem = Path(target_path).stem
        slug = sanitize_slug(target_stem)
        if slug and slug != sanitize_slug(stem):
            links.append(slug)

    return title, list(set(links))

def generate_okf_frontmatter(node_id: str, title: str, level: int, status: str, math_status: str, math_score: str, sources: list, dependencies: list, tags: list) -> str:
    lines = ["---"]
    lines.append(f"id: \"{node_id}\"")
    lines.append(f"title: \"{title}\"")
    lines.append(f"level: {level}")
    lines.append(f"status: \"{status}\"")
    lines.append(f"math_status: \"{math_status}\"")
    lines.append(f"math_score: \"{math_score}\"")

    lines.append("sources:")
    if sources:
        for s in sources:
            lines.append(f"  - \"{s}\"")
    else:
        lines.append("  - \"Standard scientific consensus\"")

    lines.append("dependencies:")
    clean_deps = [d for d in dependencies if d and d != "[]"]
    if clean_deps:
        for d in clean_deps:
            lines.append(f"  - \"{d}\"")
    else:
        lines.append("  []")

    lines.append("tags:")
    if tags:
        for t in tags:
            lines.append(f"  - \"{t}\"")
    else:
        lines.append("  - \"physics\"")

    lines.append("---")
    return "\n".join(lines)

def migrate_kb(repo_root: Path):
    kb_dir = repo_root / "knowledge_base"
    migrated_count = 0

    level_folders = {
        "level_1_fundamental_physics": 1,
        "level_2_advanced_frameworks": 2,
        "level_3_emergence_and_intelligence": 3
    }

    for folder_name, level_num in level_folders.items():
        folder_path = kb_dir / folder_name
        if not folder_path.exists():
            continue

        for filepath in sorted(folder_path.glob("*.md")):
            if filepath.name.startswith("_") or filepath.name == "concept_template.md":
                continue

            content = filepath.read_text(encoding="utf-8")
            fm, body = parse_existing_frontmatter(content)
            stem_slug = sanitize_slug(filepath.stem)

            node_id = fm.get("id", stem_slug)
            title, body_links = extract_title_and_links(body, filepath.stem)

            if "title" in fm:
                title = str(fm["title"]).strip('"').strip("'")

            status = str(fm.get("status", "[THEORETICAL]")).strip('"').strip("'")
            math_status = str(fm.get("math_status", "MATH_UNKNOWN")).strip('"').strip("'")
            math_score = str(fm.get("math_score", "0/4")).strip('"').strip("'")

            sources = fm.get("sources", [])
            if isinstance(sources, str):
                sources = [sources]

            dependencies = fm.get("dependencies", [])
            if isinstance(dependencies, str):
                dependencies = [dependencies]
            dependencies = list(set([sanitize_slug(d) for d in dependencies if d] + body_links))

            tags = fm.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]
            if not tags:
                tag_set = {folder_name.split("_")[1]}
                if "dark_matter" in stem_slug:
                    tag_set.add("dark_matter")
                if "quantum" in stem_slug:
                    tag_set.add("quantum_physics")
                if "gravity" in stem_slug:
                    tag_set.add("gravity")
                if "inflation" in stem_slug:
                    tag_set.add("cosmology")
                tags = sorted(list(tag_set))

            okf_fm = generate_okf_frontmatter(
                node_id=node_id,
                title=title,
                level=level_num,
                status=status,
                math_status=math_status,
                math_score=math_score,
                sources=sources,
                dependencies=dependencies,
                tags=tags
            )

            # Ensure body has # Title
            if not re.search(r"^#\s+", body, re.MULTILINE):
                body = f"# {title}\n\n" + body

            new_content = f"{okf_fm}\n\n{body.strip()}\n"
            filepath.write_text(new_content, encoding="utf-8")
            migrated_count += 1

    print(f"Migrated {migrated_count} concept files to OKF format.")

if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    migrate_kb(repo_root)

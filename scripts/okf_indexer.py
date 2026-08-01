#!/usr/bin/env python3
"""
Open Knowledge Format (OKF) Graph Indexer and Validator for Universe Knowledge.

Scans all concept documents in knowledge_base/, validates OKF YAML frontmatter schemas,
builds dependency edges, and compiles a unified knowledge_base/graph.json manifest.
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

def parse_yaml_frontmatter(text: str):
    """Parses simple YAML frontmatter block from markdown text."""
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
                # Handle inline item
                item = val.lstrip("-").strip().strip('"').strip("'")
                data[key] = [item]
                current_key = key
            elif not val:
                data[key] = []
                current_key = key
            else:
                # Strip quotes
                val_clean = val.strip('"').strip("'")
                # Parse numeric/bool
                if val_clean.isdigit():
                    val_clean = int(val_clean)
                data[key] = val_clean
                current_key = key

    return data, body_text

def sanitize_slug(name: str) -> str:
    """Generates a clean normalized OKF concept ID slug."""
    s = re.sub(r'[^a-zA-Z0-9\s]', '', str(name)).strip().replace(' ', '_').lower()
    return re.sub(r'_+', '_', s)

def extract_related_links(body_text: str):
    """Extracts target concept slugs linked in markdown or listed in Section 7."""
    links = []
    # Markdown link pattern [Text](path/to/file.md)
    for match in re.finditer(r'\[([^\]]+)\]\(([^)]+\.md)\)', body_text):
        target_path = match.group(2)
        target_stem = Path(target_path).stem
        links.append(sanitize_slug(target_stem))
    return list(set(links))

def scan_okf_bundle(repo_root: Path):
    """Scans knowledge_base/ for OKF concept nodes and builds the graph structure."""
    kb_dir = repo_root / "knowledge_base"
    nodes = []
    node_map = {}
    edges = []
    errors = []
    warnings = []

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

            try:
                content = filepath.read_text(encoding="utf-8")
            except Exception as err:
                errors.append(f"Failed to read file {filepath.relative_to(repo_root)}: {err}")
                continue

            fm, body = parse_yaml_frontmatter(content)
            stem_slug = sanitize_slug(filepath.stem)

            # Determine Node ID
            node_id = fm.get("id")
            if not node_id:
                node_id = stem_slug
            else:
                node_id = sanitize_slug(str(node_id))

            # Determine Title
            title = fm.get("title")
            if not title:
                title_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else filepath.stem.replace("_", " ").title()

            # Determine Status
            status_raw = str(fm.get("status", "[THEORETICAL]")).upper()
            if "VERIFIED" in status_raw:
                status = "VERIFIED"
            elif "REJECTED" in status_raw:
                status = "REJECTED"
            else:
                status = "THEORETICAL"

            # Parse dependencies and sources
            dependencies = fm.get("dependencies", [])
            if isinstance(dependencies, str):
                dependencies = [dependencies]
            dependencies = [sanitize_slug(d) for d in dependencies if d and sanitize_slug(d)]

            # Merge body links into dependencies if not present
            body_links = extract_related_links(body)
            for link_slug in body_links:
                if link_slug and link_slug not in dependencies and link_slug != node_id:
                    dependencies.append(link_slug)

            sources = fm.get("sources", [])
            if isinstance(sources, str):
                sources = [sources]

            tags = fm.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]
            if not tags:
                # Infer basic tags from category / title
                tags = [folder_name.split("_")[1]]

            node = {
                "id": node_id,
                "title": title,
                "level": level_num,
                "category": folder_name,
                "status": status,
                "math_status": fm.get("math_status", "MATH_UNKNOWN"),
                "math_score": fm.get("math_score", "0/4"),
                "dependencies": dependencies,
                "tags": tags,
                "sources": sources,
                "path": str(filepath.relative_to(repo_root)).replace("\\", "/")
            }

            if node_id in node_map:
                errors.append(f"Duplicate node ID '{node_id}' found in {filepath.relative_to(repo_root)} and {node_map[node_id]['path']}")
            else:
                node_map[node_id] = node
                nodes.append(node)

def _resolve_smart_edges(nodes):
    """Smartly extracts directed prerequisite and dependency edges across all nodes."""
    node_map = {n["id"]: n for n in nodes}
    
    # Build title and alias lookup dictionary
    title_lookup = {}
    for n in nodes:
        clean_title = sanitize_slug(n["title"])
        title_lookup[clean_title] = n["id"]
        title_lookup[n["id"]] = n["id"]

    edges = []
    seen_edges = set()

    def add_edge(src_id, tgt_id, edge_type="prerequisite"):
        if src_id and tgt_id and src_id != tgt_id and src_id in node_map and tgt_id in node_map:
            edge_key = (src_id, tgt_id)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                edges.append({
                    "source": src_id,
                    "target": tgt_id,
                    "type": edge_type
                })
                # Keep node dependencies list synchronized
                if src_id not in node_map[tgt_id]["dependencies"]:
                    node_map[tgt_id]["dependencies"].append(src_id)

    # 1. Parse frontmatter dependencies & links
    for node in nodes:
        for dep_id in list(node["dependencies"]):
            dep_slug = sanitize_slug(dep_id)
            if dep_slug in node_map:
                add_edge(dep_slug, node["id"], "prerequisite")

    # 2. Parse Level 2 & 3 Debate Titles (Theory A vs Theory B)
    for node in nodes:
        title = node["title"]
        # Match "Theory A vs Theory B" patterns
        vs_match = re.split(r'\s+(?:vs\.?|versus|against)\s+', title, flags=re.IGNORECASE)
        if len(vs_match) >= 2:
            part_a = sanitize_slug(vs_match[0])
            part_b = sanitize_slug(re.split(r'\s+in\s+|\s+for\s+|\s+debate', vs_match[1], flags=re.IGNORECASE)[0])
            
            # Fuzzy match parts against existing node IDs/titles
            for target_part in [part_a, part_b]:
                for ref_id, ref_node in node_map.items():
                    if ref_id == node["id"]:
                        continue
                    # Match if key tokens of ref_id match target_part
                    ref_slug = ref_id.replace("_", "")
                    clean_part = target_part.replace("_", "")
                    if ref_slug in clean_part or clean_part in ref_slug:
                        add_edge(ref_id, node["id"], "component_theory")
                        break

    # 3. Match Section 7 Related Concepts & Body References
    # Sort L1 concept titles by length (longest first) to prevent partial substring false positives
    l1_nodes = sorted([n for n in nodes if n["level"] == 1], key=lambda x: len(x["title"]), reverse=True)
    
    for node in nodes:
        if node["level"] in (2, 3):
            # Check if Level 2 or 3 document content mentions Level 1 fundamental concepts
            for l1_node in l1_nodes:
                l1_id = l1_node["id"]
                l1_title_clean = re.sub(r'[^a-zA-Z0-9\s]', '', l1_node["title"]).lower()
                l1_words = [w for w in l1_title_clean.split() if len(w) > 3]
                
                # Check title slug or core title phrase
                node_id_clean = node["id"].replace("_", " ")
                if len(l1_words) >= 2:
                    phrase = " ".join(l1_words[:4])
                    if phrase in node_id_clean or l1_id in node["id"]:
                        add_edge(l1_id, node["id"], "foundational_prerequisite")

    return edges

def scan_okf_bundle(repo_root: Path):
    """Scans knowledge_base/ for OKF concept nodes and builds the graph structure."""
    kb_dir = repo_root / "knowledge_base"
    nodes = []
    node_map = {}
    errors = []
    warnings = []

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

            try:
                content = filepath.read_text(encoding="utf-8")
            except Exception as err:
                errors.append(f"Failed to read file {filepath.relative_to(repo_root)}: {err}")
                continue

            fm, body = parse_yaml_frontmatter(content)
            stem_slug = sanitize_slug(filepath.stem)

            # Determine Node ID
            node_id = fm.get("id")
            if not node_id:
                node_id = stem_slug
            else:
                node_id = sanitize_slug(str(node_id))

            # Determine Title
            title = fm.get("title")
            if not title:
                title_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else filepath.stem.replace("_", " ").title()

            # Determine Status
            status_raw = str(fm.get("status", "[THEORETICAL]")).upper()
            if "VERIFIED" in status_raw:
                status = "VERIFIED"
            elif "REJECTED" in status_raw:
                status = "REJECTED"
            else:
                status = "THEORETICAL"

            # Parse dependencies and sources
            dependencies = fm.get("dependencies", [])
            if isinstance(dependencies, str):
                dependencies = [dependencies]
            dependencies = [sanitize_slug(d) for d in dependencies if d and sanitize_slug(d)]

            # Merge body links into dependencies if not present
            body_links = extract_related_links(body)
            for link_slug in body_links:
                if link_slug and link_slug not in dependencies and link_slug != node_id:
                    dependencies.append(link_slug)

            sources = fm.get("sources", [])
            if isinstance(sources, str):
                sources = [sources]

            tags = fm.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]
            if not tags:
                tags = [folder_name.split("_")[1]]

            node = {
                "id": node_id,
                "title": title,
                "level": level_num,
                "category": folder_name,
                "status": status,
                "math_status": fm.get("math_status", "MATH_UNKNOWN"),
                "math_score": fm.get("math_score", "0/4"),
                "dependencies": dependencies,
                "tags": tags,
                "sources": sources,
                "path": str(filepath.relative_to(repo_root)).replace("\\", "/")
            }

            if node_id in node_map:
                errors.append(f"Duplicate node ID '{node_id}' found in {filepath.relative_to(repo_root)} and {node_map[node_id]['path']}")
            else:
                node_map[node_id] = node
                nodes.append(node)

    # Smart Graph Edge Resolution
    edges = _resolve_smart_edges(nodes)

    # Validate dependencies against node_map
    for node in nodes:
        for dep_id in node["dependencies"]:
            if dep_id not in node_map:
                warnings.append(f"Node '{node['id']}' references unresolved dependency/link: '{dep_id}'")

    # Generate Frontier Nodes
    frontier = []
    unresolved_deps = set()
    for node in nodes:
        for dep_id in node["dependencies"]:
            if dep_id not in node_map:
                unresolved_deps.add(dep_id)

    for dep_slug in sorted(unresolved_deps):
        frontier.append({
            "id": dep_slug,
            "suggested_title": dep_slug.replace("_", " ").title(),
            "target_level": 1,
            "reason": "Referenced as prerequisite link in existing verified concept"
        })

    # Stats summary
    stats = {
        "total_nodes": len(nodes),
        "level_1_count": sum(1 for n in nodes if n["level"] == 1),
        "level_2_count": sum(1 for n in nodes if n["level"] == 2),
        "level_3_count": sum(1 for n in nodes if n["level"] == 3),
        "total_edges": len(edges),
        "frontier_count": len(frontier)
    }

    graph_data = {
        "version": "1.0.0",
        "format": "Open Knowledge Format (OKF)",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "stats": stats,
        "nodes": nodes,
        "edges": edges,
        "frontier": frontier
    }

    return graph_data, errors, warnings

def main():
    parser = argparse.ArgumentParser(description="OKF Graph Indexer & Validator")
    parser.add_argument("--validate", action="store_true", help="Validate OKF bundle schemas and exit with status code")
    parser.add_argument("--build", action="store_true", help="Build knowledge_base/graph.json file")
    parser.add_argument("--repo-root", type=str, default=".", help="Path to repository root")

    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()

    graph_data, errors, warnings = scan_okf_bundle(repo_root)

    print(f"--- OKF Graph Indexer Report ---")
    print(f"Total Nodes: {graph_data['stats']['total_nodes']} (L1: {graph_data['stats']['level_1_count']}, L2: {graph_data['stats']['level_2_count']}, L3: {graph_data['stats']['level_3_count']})")
    print(f"Total Edges: {graph_data['stats']['total_edges']}")
    print(f"Frontier Nodes: {graph_data['stats']['frontier_count']}")

    if warnings:
        print(f"\n[OKF WARNINGS] ({len(warnings)} detected):")
        for w in warnings[:10]:
            print(f"  [WARN] {w}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more warnings.")

    if errors:
        print(f"\n[OKF ERRORS] ({len(errors)} detected):")
        for e in errors:
            print(f"  [ERROR] {e}")
        if args.validate:
            sys.exit(1)

    output_path = repo_root / "knowledge_base" / "graph.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2, ensure_ascii=False)
    print(f"\nSuccessfully written OKF Graph to {output_path.relative_to(repo_root)}")

    if args.validate and errors:
        sys.exit(1)

if __name__ == "__main__":
    main()

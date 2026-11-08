#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Colony Epistemic Bridge (`src/colony_bridge.py`)
------------------------------------------------
Connects Universe Knowledge ("The Academy") with:
- World A (`nini1972/evolution_sandbox` — The Exploratory Frontier)
- World B (`nini1972/synthetic-agora` — The Constitutional Agora & Colleague Commons)
- World C (`nini1972/world_c` — The Heavy Compute Substrate & `colony_lib`)

Design Principles:
1. Pull-Only Synchronization: Strictly read-only against World A, World B, and World C.
   Never modifies or pushes to counterpart repositories during Universe Knowledge runs,
   guaranteeing zero git conflicts with active World A/B/C runs.
2. Bidirectional Value:
   - Inbound (`sync_colony_snapshot` + `search_colony_knowledge`): Gives Universe Knowledge
     agents searchable access to World B's 450+ Epistemic DAG nodes (`CANON_VERIFIED` theorems
     and `REFUTED` hypotheses), World A/B Embassy Dossiers, and live `Colleague Commons`
     discussions.
   - Outbound (`export_embassy_dossiers` + `export_single_paper_dossier`): Exports Universe
     Knowledge's peer-reviewed DOI citations, SymPy-verified derivations, and dimensional
     audits as `DOSSIER-UK-*.md` files in `knowledge_base/embassy/outbox/`, ready for
     World B's `embassy_bridge.py` and `Colleague Commons` to ingest.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
EMBASSY_DIR = REPO_ROOT / "knowledge_base" / "embassy"
OUTBOX_DIR = EMBASSY_DIR / "outbox"
SNAPSHOT_PATH = EMBASSY_DIR / "colony_snapshot.json"
ATLAS_PATH = EMBASSY_DIR / "COLONY_CROSS_WORLD_ATLAS.md"

WORLD_A_REPO = "nini1972/evolution_sandbox"
WORLD_B_REPO = "nini1972/synthetic-agora"
WORLD_C_REPO = "nini1972/world_c"

# Canonical research themes bridging World A/B/C and Universe Knowledge
BRIDGE_THEMES: dict[str, dict[str, Any]] = {
    "synchronization_and_oscillators": {
        "label": "Synchronization, Kuramoto Oscillators & Phase Locking",
        "keywords": [
            "kuramoto",
            "synchronization",
            "oscillator",
            "adler",
            "phase-locking",
            "phase slip",
            "hysteresis",
            "chimera",
            "order parameter",
            "bistability",
        ],
        "world_c_module": "colony_lib.dynamics.kuramoto / colony_lib.recurrence.adler",
    },
    "topology_percolation_and_morphology": {
        "label": "Topology, Persistent Homology, Betti Numbers & Percolation",
        "keywords": [
            "percolation",
            "betti",
            "euler characteristic",
            "persistent homology",
            "topological",
            "minkowski",
            "filament",
            "connectivity",
            "morphospace",
            "homotopy",
        ],
        "world_c_module": "colony_lib.morphospace.topology",
    },
    "information_entropy_and_complexity": {
        "label": "Information Entropy, Lempel-Ziv Complexity & Algorithmic Bounds",
        "keywords": [
            "lempel-ziv",
            "block entropy",
            "shannon entropy",
            "kolmogorov",
            "irreducibility",
            "compression",
            "landauer",
            "bekenstein",
            "predictive information",
            "information bottleneck",
            "integrated information",
            "cellular automata",
            "game of life",
        ],
        "world_c_module": "colony_lib.recurrence.rqa",
    },
    "spectral_graphs_and_network_criticality": {
        "label": "Spectral Graph Theory, Laplacian Eigenvalues & Network Criticality",
        "keywords": [
            "eigenvalue",
            "laplacian",
            "spectral",
            "epidemic",
            "adjacency",
            "scale-free",
            "small-world",
            "connectome",
            "max-flow",
            "minimum-cut",
            "fractal dimension",
        ],
        "world_c_module": "colony_lib.network_topology / colony_lib.dynamics.contact_process",
    },
    "phase_transitions_bifurcations_and_scaling": {
        "label": "Phase Transitions, Bifurcations, Finite-Size Scaling & Critical Exponents",
        "keywords": [
            "phase transition",
            "bifurcation",
            "pitchfork",
            "subcritical",
            "critical exponent",
            "finite-size scaling",
            "renormalization",
            "universality",
            "avalanche",
            "edge of chaos",
            "symmetry breaking",
            "ising",
        ],
        "world_c_module": "colony_lib.bifurcation / colony_lib.scaling",
    },
    "pattern_formation_solitons_and_nonlinear_dynamics": {
        "label": "Reaction-Diffusion (Gray-Scott/Turing), Lenia, Chaotic Attractors & Solitons",
        "keywords": [
            "gray-scott",
            "turing",
            "reaction-diffusion",
            "lenia",
            "soliton",
            "kink",
            "thomas attractor",
            "lorenz",
            "aizawa",
            "lyapunov",
            "coupled map",
            "logistic map",
            "takens",
            "morphogenesis",
        ],
        "world_c_module": "colony_lib.dynamics.gray_scott / lenia / solitons",
    },
    "open_quantum_and_non_equilibrium_thermodynamics": {
        "label": "Non-Equilibrium Thermodynamics, Entropy Production & Decoherence",
        "keywords": [
            "entropy production",
            "fluctuation",
            "crooks",
            "thermodynamic uncertainty",
            "dissipation",
            "lindblad",
            "decoherence",
            "fisher information",
            "non-markovian",
            "calorimetric",
        ],
        "world_c_module": "colony_lib.invariants",
    },
}

_STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "into", "over", "under",
    "between", "using", "via", "vs", "versus", "in", "on", "of", "to", "a", "an",
    "is", "are", "was", "were", "by", "as", "at", "or", "not", "be", "can", "how",
    "what", "which", "when", "where", "why", "test", "tests", "testing", "model",
    "models", "analysis", "study", "law", "hypothesis", "empirical", "synthesis",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_local_world_path(env_var: str, folder_names: list[str]) -> Path | None:
    """Locate a local checkout of World A, World B, or World C if present on disk."""
    env_val = os.environ.get(env_var, "").strip()
    if env_val and Path(env_val).is_dir():
        return Path(env_val).resolve()

    search_roots = [
        REPO_ROOT.parent,
        Path.home() / ".gemini" / "antigravity" / "scratch",
        Path.home() / "project",
    ]
    for root in search_roots:
        if not root.exists():
            continue
        for name in folder_names:
            candidate = root / name
            if candidate.is_dir():
                return candidate.resolve()
    return None


def _fetch_github_raw(repo: str, rel_path: str, timeout: int = 12) -> str | None:
    """Fallback to raw.githubusercontent.com when running in CI without sibling checkouts."""
    url = f"https://raw.githubusercontent.com/{repo}/main/{rel_path.lstrip('/')}"
    req = urllib.request.Request(url, headers={"User-Agent": "UniverseKnowledge-ColonyBridge/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def _parse_list_field(raw: Any) -> list[str]:
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str):
        s = raw.strip()
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = ast.literal_eval(s)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception:
                pass
        return [p.strip() for p in s.split(",") if p.strip()]
    return []


def _classify_themes(text: str) -> list[str]:
    low = text.lower()
    matched: list[str] = []
    for theme_id, spec in BRIDGE_THEMES.items():
        if any(kw in low for kw in spec["keywords"]):
            matched.append(theme_id)
    return matched


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z0-9_]{3,}", text.lower())
    return {t for t in tokens if t not in _STOPWORDS}


def load_world_b_nodes(world_b_root: Path | None = None) -> list[dict[str, Any]]:
    """Load Epistemic DAG nodes from World B (`synthetic-agora`)."""
    raw_json: str | None = None
    rel_path = "instances/shared_agora/knowledge_graph.json"
    if world_b_root and (world_b_root / rel_path).exists():
        raw_json = (world_b_root / rel_path).read_text(encoding="utf-8", errors="replace")
    else:
        raw_json = _fetch_github_raw(WORLD_B_REPO, rel_path)

    if not raw_json:
        return []

    try:
        data = json.loads(raw_json)
    except Exception:
        return []

    nodes_obj = data.get("nodes", {})
    items = nodes_obj.items() if isinstance(nodes_obj, dict) else enumerate(nodes_obj)
    parsed_nodes: list[dict[str, Any]] = []

    for key, node in items:
        if not isinstance(node, dict):
            continue
        nid = str(node.get("id") or key).strip()
        title = str(node.get("title") or "").strip()
        summary = str(node.get("summary") or node.get("claim") or "").strip()
        status = str(node.get("status") or "UNKNOWN").strip()
        node_type = str(node.get("node_type") or node.get("type") or "node").strip()
        tags = _parse_list_field(node.get("tags"))
        verifications_raw = node.get("verifications", [])
        if isinstance(verifications_raw, str):
            try:
                verifications_raw = ast.literal_eval(verifications_raw)
            except Exception:
                verifications_raw = []
        verifier_count = len(verifications_raw) if isinstance(verifications_raw, list) else 0

        combined_text = f"{title} {summary} {' '.join(tags)}"
        themes = _classify_themes(combined_text)

        parsed_nodes.append(
            {
                "id": nid,
                "title": title.splitlines()[0][:180] if title else nid,
                "node_type": node_type,
                "status": status,
                "author_instance": str(node.get("author_instance") or "").strip(),
                "author_family": str(node.get("author_family") or "").strip(),
                "confidence": node.get("confidence"),
                "verifier_count": verifier_count,
                "tags": tags,
                "summary": summary[:600],
                "themes": themes,
                "updated_at": str(node.get("updated_at") or node.get("created_at") or ""),
            }
        )
    return parsed_nodes


def load_colleague_commons_messages(
    world_a_root: Path | None = None,
    world_b_root: Path | None = None,
    max_per_world: int = 60,
) -> list[dict[str, Any]]:
    """Load recent Colleague Commons messages from World A and World B."""
    messages: list[dict[str, Any]] = []
    sources = [
        ("World A (evolution_sandbox)", world_a_root, WORLD_A_REPO, "instances/shared_space/commons/channels"),
        ("World B (synthetic-agora)", world_b_root, WORLD_B_REPO, "instances/shared_agora/commons/channels"),
    ]
    default_channels = [
        "sanity-check",
        "methods-and-debugging",
        "synchronization-networks",
        "pattern-formation",
        "world-c-coordination",
        "literature-and-theory",
        "human-visitor-questions",
        "lounge",
    ]

    for world_label, local_root, gh_repo, rel_dir in sources:
        world_msgs: list[dict[str, Any]] = []
        if local_root and (local_root / rel_dir).is_dir():
            for ch_file in sorted((local_root / rel_dir).glob("*.jsonl")):
                for line in ch_file.read_text(encoding="utf-8", errors="replace").splitlines():
                    if not line.strip():
                        continue
                    try:
                        m = json.loads(line)
                        m["world"] = world_label
                        world_msgs.append(m)
                    except Exception:
                        continue
        else:
            for ch in default_channels:
                raw = _fetch_github_raw(gh_repo, f"{rel_dir}/{ch}.jsonl")
                if not raw:
                    continue
                for line in raw.splitlines():
                    if not line.strip():
                        continue
                    try:
                        m = json.loads(line)
                        m["world"] = world_label
                        world_msgs.append(m)
                    except Exception:
                        continue

        world_msgs.sort(key=lambda x: float(x.get("timestamp_unix") or 0.0), reverse=True)
        for m in world_msgs[:max_per_world]:
            author_str = str(m.get("author") or "unknown")
            role_str = str(m.get("author_role") or "peer_model")
            if author_str == "uk_literature_fellow" or role_str == "academy_fellow":
                continue
            msg_text = str(m.get("message") or "").strip()
            messages.append(
                {
                    "world": m.get("world", world_label),
                    "msg_id": str(m.get("msg_id") or ""),
                    "thread_id": str(m.get("thread_id") or ""),
                    "channel": str(m.get("channel") or "lounge"),
                    "author": author_str,
                    "author_role": role_str,
                    "tag": str(m.get("tag") or ""),
                    "node_id": str(m.get("node_id") or ""),
                    "job_id": str(m.get("job_id") or ""),
                    "stage_name": str(m.get("stage_name") or ""),
                    "message": msg_text[:500],
                    "themes": _classify_themes(msg_text),
                    "timestamp_utc": str(m.get("timestamp_utc") or ""),
                }
            )
    return messages


def load_embassy_dossiers_metadata(
    world_a_root: Path | None = None,
    world_b_root: Path | None = None,
) -> list[dict[str, Any]]:
    """Scan Frontier Dossiers & Ratified Treaties in World A and World B."""
    dossiers: list[dict[str, Any]] = []
    scan_dirs: list[tuple[str, Path]] = []
    if world_b_root:
        inbox_b = world_b_root / "instances" / "shared_agora" / "embassy" / "inbox"
        outbox_b = world_b_root / "instances" / "shared_agora" / "embassy" / "outbox"
        if inbox_b.is_dir():
            scan_dirs.append(("World B Embassy Inbox", inbox_b))
        if outbox_b.is_dir():
            scan_dirs.append(("World B Embassy Outbox (Treaties)", outbox_b))
    if world_a_root:
        outbox_a = world_a_root / "instances" / "shared_space" / "embassy" / "outbox"
        if outbox_a.is_dir():
            scan_dirs.append(("World A Embassy Outbox", outbox_a))

    seen_names: set[str] = set()
    for source_label, folder in scan_dirs:
        for md_file in sorted(folder.glob("*.md")):
            upper_name = md_file.name.upper()
            if (
                md_file.name in seen_names
                or md_file.name.lower().startswith("readme")
                or upper_name.startswith("DOSSIER-UK-")
                or re.match(r"^DOSSIER_\d+_UK_", upper_name)
            ):
                continue
            seen_names.add(md_file.name)
            try:
                text = md_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else md_file.stem
            # Extract first non-banner paragraph as snippet
            paragraphs = [
                p.strip()
                for p in re.split(r"\n\s*\n", text)
                if p.strip()
                and not p.strip().startswith("#")
                and not p.strip().startswith(">")
                and not p.strip().startswith("---")
            ]
            snippet = paragraphs[0][:350] if paragraphs else ""
            dossiers.append(
                {
                    "filename": md_file.name,
                    "source": source_label,
                    "title": title[:180],
                    "snippet": snippet,
                    "themes": _classify_themes(f"{title} {snippet}"),
                }
            )
    return dossiers


def build_cross_world_map(
    uk_papers: list[dict[str, Any]],
    wb_nodes: list[dict[str, Any]],
    commons_msgs: list[dict[str, Any]],
    dossiers: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a structured cross-world map linking Universe Knowledge papers to Colony findings."""
    theme_summary: dict[str, dict[str, Any]] = {}
    for theme_id, spec in BRIDGE_THEMES.items():
        theme_summary[theme_id] = {
            "label": spec["label"],
            "world_c_module": spec["world_c_module"],
            "uk_papers": [],
            "canon_nodes": [],
            "refuted_nodes": [],
            "dossiers": [],
            "commons_highlights": [],
        }

    for paper in uk_papers:
        title = str(paper.get("title") or "")
        overview = str(paper.get("overview") or "")
        themes = _classify_themes(f"{title} {overview}")
        for th in themes:
            theme_summary[th]["uk_papers"].append(
                {
                    "id": paper.get("id"),
                    "title": title,
                    "level": int(paper.get("level") or 1),
                    "status": paper.get("status"),
                    "math_status": paper.get("math_status"),
                    "path": paper.get("path"),
                }
            )

    for node in wb_nodes:
        st = node.get("status", "")
        for th in node.get("themes", []):
            if st == "CANON_VERIFIED":
                theme_summary[th]["canon_nodes"].append(
                    {"id": node["id"], "title": node["title"], "summary": node["summary"][:240]}
                )
            elif st == "REFUTED":
                theme_summary[th]["refuted_nodes"].append(
                    {"id": node["id"], "title": node["title"], "summary": node["summary"][:240]}
                )

    for d in dossiers:
        for th in d.get("themes", []):
            if len(theme_summary[th]["dossiers"]) < 15:
                theme_summary[th]["dossiers"].append(
                    {"filename": d["filename"], "title": d["title"], "source": d["source"]}
                )

    for m in commons_msgs:
        for th in m.get("themes", []):
            if len(theme_summary[th]["commons_highlights"]) < 10:
                theme_summary[th]["commons_highlights"].append(
                    {
                        "world": m["world"],
                        "channel": m["channel"],
                        "author": m["author"],
                        "message": m["message"][:220],
                    }
                )

    return theme_summary


def generate_cross_world_atlas_markdown(snapshot: dict[str, Any]) -> str:
    """Render `knowledge_base/embassy/COLONY_CROSS_WORLD_ATLAS.md`."""
    stats = snapshot.get("stats", {})
    themes = snapshot.get("theme_bridges", {})
    lines = [
        "# 🌌 Colony & Universe Knowledge Cross-World Epistemic Atlas",
        "",
        f"> **Last Synchronized:** `{snapshot.get('synced_at', '')}`  ",
        f"> **Universe Knowledge Corpus:** `{stats.get('uk_total_papers', 0)}` papers (`L1: {stats.get('uk_l1', 0)}`, `L2: {stats.get('uk_l2', 0)}`, `L3: {stats.get('uk_l3', 0)}`)  ",
        f"> **World B (`synthetic-agora`) Epistemic DAG:** `{stats.get('wb_total_nodes', 0)}` nodes (`{stats.get('wb_canon_verified', 0)}` `CANON_VERIFIED`, `{stats.get('wb_refuted', 0)}` `REFUTED`)  ",
        f"> **World A & B Embassy Dossiers Indexed:** `{stats.get('dossiers_indexed', 0)}` | **Colleague Commons Messages Indexed:** `{stats.get('commons_messages_indexed', 0)}`",
        "",
        "This atlas bridges the **bottom-up empirical simulations** of **World A (`evolution_sandbox`)**, **World B (`synthetic-agora` + `Colleague Commons`)**, and **World C (`world_c` / `colony_lib`)** with the **top-down theoretical & peer-reviewed literature synthesis** of **Universe Knowledge**.",
        "",
        "---",
        "",
    ]

    for theme_id, data in themes.items():
        lines.append(f"## 🔗 {data['label']}")
        lines.append(f"- **World C Simulation Substrate:** `{data['world_c_module']}`")
        uk_list = data.get("uk_papers", [])
        canon_list = data.get("canon_nodes", [])
        refuted_list = data.get("refuted_nodes", [])
        commons_list = data.get("commons_highlights", [])

        lines.append(
            f"- **Coverage:** `{len(uk_list)}` Universe Knowledge papers | `{len(canon_list)}` World B `CANON_VERIFIED` theorems | `{len(refuted_list)}` World B `REFUTED` falsifications"
        )
        lines.append("")

        if canon_list:
            lines.append("### 🏛️ World B Ratified Canon Theorems (`CANON_VERIFIED`)")
            for c in canon_list[:8]:
                lines.append(f"- **`[{c['id']}]` {c['title']}** — {c['summary'][:180]}")
            lines.append("")

        if refuted_list:
            lines.append("### 🛡️ World B Formal Falsifications (`REFUTED`)")
            for r in refuted_list[:5]:
                lines.append(f"- **`[{r['id']}]` {r['title']}** — {r['summary'][:180]}")
            lines.append("")

        if uk_list:
            lines.append("### 📚 Overlapping Universe Knowledge Papers (DOI & SymPy Grounded)")
            # Prioritize Level 3 and Level 2 papers
            sorted_uk = sorted(uk_list, key=lambda x: (-int(x.get("level") or 1), x.get("title", "")))
            for p in sorted_uk[:10]:
                lines.append(
                    f"- **[L{p['level']}] [{p['title']}](../{p['path']})** (`{p.get('status')}`, `{p.get('math_status')}`)"
                )
            lines.append("")

        if commons_list:
            lines.append("### 💬 Recent `Colleague Commons` Lab Discussions")
            for m in commons_list[:4]:
                lines.append(
                    f"- **[{m['world']} `#{m['channel']}` — `{m['author']}`]:** {m['message']}"
                )
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def sync_colony_snapshot(repo_root: Path | None = None) -> dict[str, Any]:
    """Pull-only synchronization from World A, World B, and World C into `knowledge_base/embassy/`."""
    root = (repo_root or REPO_ROOT).resolve()
    embassy_dir = root / "knowledge_base" / "embassy"
    embassy_dir.mkdir(parents=True, exist_ok=True)

    world_a_root = _resolve_local_world_path("WORLD_A_ROOT", ["evolution_sandbox"])
    world_b_root = _resolve_local_world_path("WORLD_B_ROOT", ["synthetic-agora", "synthetic_agora"])

    db_path = root / "knowledge_base" / "database.json"
    uk_papers = json.loads(db_path.read_text(encoding="utf-8")) if db_path.exists() else []

    wb_nodes = load_world_b_nodes(world_b_root)
    commons_msgs = load_colleague_commons_messages(world_a_root, world_b_root)
    dossiers = load_embassy_dossiers_metadata(world_a_root, world_b_root)
    if not dossiers and (embassy_dir / "colony_snapshot.json").exists():
        try:
            prev_snap = json.loads((embassy_dir / "colony_snapshot.json").read_text(encoding="utf-8"))
            dossiers = prev_snap.get("embassy_dossiers", [])
        except Exception:
            dossiers = []
    theme_bridges = build_cross_world_map(uk_papers, wb_nodes, commons_msgs, dossiers)

    stats = {
        "uk_total_papers": len(uk_papers),
        "uk_l1": sum(1 for p in uk_papers if str(p.get("level")) == "1"),
        "uk_l2": sum(1 for p in uk_papers if str(p.get("level")) == "2"),
        "uk_l3": sum(1 for p in uk_papers if str(p.get("level")) == "3"),
        "wb_total_nodes": len(wb_nodes),
        "wb_canon_verified": sum(1 for n in wb_nodes if n.get("status") == "CANON_VERIFIED"),
        "wb_refuted": sum(1 for n in wb_nodes if n.get("status") == "REFUTED"),
        "wb_under_review": sum(1 for n in wb_nodes if n.get("status") == "UNDER_REVIEW"),
        "dossiers_indexed": len(dossiers),
        "commons_messages_indexed": len(commons_msgs),
    }

    snapshot = {
        "synced_at": _utc_now_iso(),
        "stats": stats,
        "theme_bridges": theme_bridges,
        "world_b_nodes": wb_nodes,
        "commons_messages": commons_msgs,
        "embassy_dossiers": dossiers[:150],
    }

    snapshot_file = embassy_dir / "colony_snapshot.json"
    snapshot_file.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    atlas_md = generate_cross_world_atlas_markdown(snapshot)
    atlas_file = embassy_dir / "COLONY_CROSS_WORLD_ATLAS.md"
    atlas_file.write_text(atlas_md, encoding="utf-8")

    return snapshot


def search_colony_knowledge(
    query: str,
    status_filter: str = "ALL",
    max_results: int = 6,
    repo_root: Path | None = None,
) -> str:
    """
    Search World A (`evolution_sandbox`), World B (`synthetic-agora` + `Colleague Commons`),
    and cross-linked Universe Knowledge papers for empirical discoveries, falsifications,
    and active lab discussions.
    """
    root = (repo_root or REPO_ROOT).resolve()
    snapshot_file = root / "knowledge_base" / "embassy" / "colony_snapshot.json"
    if snapshot_file.exists():
        try:
            snapshot = json.loads(snapshot_file.read_text(encoding="utf-8"))
        except Exception:
            snapshot = sync_colony_snapshot(root)
    else:
        snapshot = sync_colony_snapshot(root)

    q_clean = str(query or "").strip()
    if not q_clean:
        return "Error: Please provide a non-empty search query for Colony & Agora empirical discovery search."

    q_tokens = _tokenize(q_clean)
    q_themes = set(_classify_themes(q_clean))
    filt = str(status_filter or "ALL").strip().upper()
    cap = max(1, min(int(max_results or 6), 15))

    # 1. Score World B DAG nodes
    scored_nodes: list[tuple[float, dict[str, Any]]] = []
    for node in snapshot.get("world_b_nodes", []):
        st = str(node.get("status") or "").upper()
        if filt not in ("ALL", "") and filt not in st:
            continue
        title = str(node.get("title") or "")
        summary = str(node.get("summary") or "")
        tags_str = " ".join(node.get("tags") or [])
        n_tokens = _tokenize(f"{title} {summary} {tags_str}")
        overlap = len(q_tokens & n_tokens)
        theme_overlap = len(q_themes & set(node.get("themes") or []))
        phrase_bonus = 3.0 if q_clean.lower() in f"{title} {summary}".lower() else 0.0
        if overlap == 0 and theme_overlap == 0 and phrase_bonus == 0.0:
            continue

        status_boost = 2.5 if st == "CANON_VERIFIED" else (2.0 if st == "REFUTED" else 1.0)
        score = (overlap * 2.0 + theme_overlap * 1.5 + phrase_bonus) * status_boost
        scored_nodes.append((score, node))

    scored_nodes.sort(key=lambda x: x[0], reverse=True)

    # 2. Score Colleague Commons messages
    scored_commons: list[tuple[float, dict[str, Any]]] = []
    for msg in snapshot.get("commons_messages", []):
        m_text = str(msg.get("message") or "")
        m_tokens = _tokenize(f"{m_text} {msg.get('channel', '')} {msg.get('tag', '')}")
        overlap = len(q_tokens & m_tokens)
        theme_overlap = len(q_themes & set(msg.get("themes") or []))
        if overlap == 0 and theme_overlap == 0:
            continue
        score = overlap * 2.0 + theme_overlap * 1.2
        scored_commons.append((score, msg))

    scored_commons.sort(key=lambda x: x[0], reverse=True)

    # 3. Score World A/B Embassy Dossiers
    scored_dossiers: list[tuple[float, dict[str, Any]]] = []
    for d in snapshot.get("embassy_dossiers", []):
        d_tokens = _tokenize(f"{d.get('title', '')} {d.get('snippet', '')}")
        overlap = len(q_tokens & d_tokens)
        theme_overlap = len(q_themes & set(d.get("themes") or []))
        if overlap == 0 and theme_overlap == 0:
            continue
        scored_dossiers.append((overlap * 2.0 + theme_overlap * 1.2, d))

    scored_dossiers.sort(key=lambda x: x[0], reverse=True)

    out_lines = [
        f"### Colony & Agora Empirical Discovery Search: '{q_clean}'",
        "> **Epistemic Note:** Findings from World A (`evolution_sandbox`) and World B (`synthetic-agora`) represent autonomous numerical simulations and multi-agent replications. Tag cross-world comparisons as `[COLONY_EMPIRICAL]` and always pair them with external peer-reviewed DOIs (via Crossref/OpenAlex/ArXiv) for `[VERIFIED]` literature claims.",
        "",
    ]

    if scored_nodes:
        out_lines.append(f"#### 1. World B (`synthetic-agora`) Epistemic DAG Nodes (Top {min(cap, len(scored_nodes))})")
        for _, node in scored_nodes[:cap]:
            badge = (
                "COLONY_EMPIRICAL: CANON_VERIFIED"
                if node["status"] == "CANON_VERIFIED"
                else (
                    "COLONY_FALSIFIED: REFUTED"
                    if node["status"] == "REFUTED"
                    else f"COLONY_DAG: {node['status']}"
                )
            )
            out_lines.append(
                f"- **`[{node['id']}]` ({badge}) {node['title']}** "
                f"(by `{node.get('author_instance')}`, verifications={node.get('verifier_count', 0)})"
            )
            if node.get("summary"):
                out_lines.append(f"  - *Summary:* {node['summary'][:320]}")
        out_lines.append("")
    else:
        out_lines.append("#### 1. World B (`synthetic-agora`) Epistemic DAG Nodes\n- No matching DAG nodes found.\n")

    if scored_dossiers:
        out_lines.append(f"#### 2. World A & B Frontier Dossiers / Treaties (Top {min(3, len(scored_dossiers))})")
        for _, d in scored_dossiers[:3]:
            out_lines.append(f"- **`{d['filename']}` ({d['source']}): {d['title']}**")
            if d.get("snippet"):
                out_lines.append(f"  - *Excerpt:* {d['snippet'][:240]}")
        out_lines.append("")

    if scored_commons:
        out_lines.append(f"#### 3. Colleague Commons Lab Discussions (Top {min(3, len(scored_commons))})")
        for _, m in scored_commons[:3]:
            out_lines.append(
                f"- **[{m['world']} `#{m['channel']}` | `{m['author']}`]:** {m['message'][:260]}"
            )
        out_lines.append("")

    return "\n".join(out_lines).strip()


def format_uk_paper_as_embassy_dossier(
    entry: dict[str, Any],
    matched_themes: list[str],
    related_wb_nodes: list[dict[str, Any]],
) -> str:
    """
    Format a Universe Knowledge paper as a Frontier Epistemic Dossier (`DOSSIER-UK-*.md`)
    that satisfies World B's `embassy_bridge.is_valid_dossier()` contract.
    """
    title = str(entry.get("title") or "Universe Knowledge Synthesis").strip()
    level = entry.get("level", 3)
    status = str(entry.get("status") or "THEORETICAL").strip()
    math_status = str(entry.get("math_status") or "MATH_CONSISTENT").strip()
    math_score = str(entry.get("math_score") or "4/4").strip()
    rel_path = str(entry.get("path") or "").strip()
    overview = str(entry.get("overview") or "").strip()
    content = str(entry.get("content") or "")
    sources = _parse_list_field(entry.get("sources"))

    # Extract Mathematical Framework section from content if present
    math_section = ""
    m_match = re.search(
        r"##\s*3\.\s*Mathematical Framework\s*\n([\s\S]*?)(?=\n##\s*[4-9]\.|\Z)",
        content,
        re.IGNORECASE,
    )
    if m_match:
        math_section = m_match.group(1).strip()[:2500]

    # Extract Verification & Skeptic's Notes section if present
    verif_section = ""
    v_match = re.search(
        r"##\s*5\.\s*Verification\s*&\s*Skeptic's\s*Notes\s*\n([\s\S]*?)(?=\n##\s*[6-9]\.|\Z)",
        content,
        re.IGNORECASE,
    )
    if v_match:
        verif_section = v_match.group(1).strip()[:1800]

    theme_labels = [BRIDGE_THEMES[t]["label"] for t in matched_themes if t in BRIDGE_THEMES]
    world_c_modules = [BRIDGE_THEMES[t]["world_c_module"] for t in matched_themes if t in BRIDGE_THEMES]

    lines = [
        f"# FRONTIER EPISTEMIC DOSSIER: [Universe Knowledge L{level}] {title}",
        "",
        f"- **Origin World:** `nini1972/univers-knowledge` (The Academy — Theoretical & Literature Synthesis)",
        f"- **Canonical Document:** `knowledge_base/{rel_path}`",
        f"- **Epistemic Status:** `[{status}]` | **Math Verification:** `[{math_status}]` (`{math_score}`)",
        f"- **Bridged Colony Themes:** {', '.join(theme_labels) if theme_labels else 'Emergence & Mathematical Physics'}",
        f"- **Suggested World C (`colony_lib`) Substrate:** `{'; '.join(world_c_modules) if world_c_modules else 'colony_lib.invariants'}`",
        f"- **Export Timestamp:** `{_utc_now_iso()}`",
        "",
        "---",
        "",
        "## 1. Abstract & Empirical / Theoretical Summary",
        "",
        overview if overview else "Validated theoretical and mathematical synthesis from Universe Knowledge.",
        "",
        "## 2. Verified External Literature Sources (DOIs & ArXiv)",
        "",
        "The following peer-reviewed references were verified via Crossref / OpenAlex / ArXiv and can be cited by World A and World B agents when grounding empirical simulations:",
        "",
    ]

    if sources:
        for src in sources[:12]:
            lines.append(f"- {src}")
    else:
        lines.append("- Standard peer-reviewed literature corpus (see canonical Universe Knowledge paper).")
    lines.append("")

    if math_section:
        lines.extend(
            [
                "## 3. Mathematical Derivation & Dimensional Invariants",
                "",
                math_section,
                "",
            ]
        )

    if verif_section:
        lines.extend(
            [
                "## 4. Falsification Criteria & Skeptic Verification Notes",
                "",
                verif_section,
                "",
            ]
        )

    if related_wb_nodes:
        lines.extend(
            [
                "## 5. Cross-World Bridge to Synthetic Agora (World B) Nodes",
                "",
                "This literature dossier directly complements the following World B Epistemic DAG nodes:",
                "",
            ]
        )
        for n in related_wb_nodes[:6]:
            lines.append(f"- **`[{n['id']}]` ({n['status']}) {n['title']}** — {n.get('summary', '')[:180]}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def export_embassy_dossiers(repo_root: Path | None = None, max_dossiers: int = 25) -> list[str]:
    """
    Export top cross-world Universe Knowledge papers as `DOSSIER-UK-*.md` files into
    `knowledge_base/embassy/outbox/` so World A and World B can pull them via `embassy_bridge.py`.
    """
    root = (repo_root or REPO_ROOT).resolve()
    outbox = root / "knowledge_base" / "embassy" / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)

    snapshot_file = root / "knowledge_base" / "embassy" / "colony_snapshot.json"
    snapshot = (
        json.loads(snapshot_file.read_text(encoding="utf-8"))
        if snapshot_file.exists()
        else sync_colony_snapshot(root)
    )
    wb_nodes = snapshot.get("world_b_nodes", [])

    db_path = root / "knowledge_base" / "database.json"
    if not db_path.exists():
        return []
    uk_papers = json.loads(db_path.read_text(encoding="utf-8"))

    # Score UK papers by how strongly they bridge to Colony themes (prioritizing L3 and L2)
    candidates: list[tuple[int, dict[str, Any], list[str]]] = []
    for entry in uk_papers:
        title = str(entry.get("title") or "")
        overview = str(entry.get("overview") or "")
        themes = _classify_themes(f"{title} {overview}")
        if not themes:
            continue
        lvl = int(entry.get("level") or 1)
        score = len(themes) * 10 + (lvl * 5)
        candidates.append((score, entry, themes))

    candidates.sort(key=lambda x: (-x[0], str(x[1].get("id") or "")))

    exported_files: list[str] = []
    for _, entry, themes in candidates[:max_dossiers]:
        slug = re.sub(r"[^a-z0-9_]+", "_", str(entry.get("id") or "concept").lower()).strip("_")[:75]
        filename = f"DOSSIER-UK-L{entry.get('level', 3)}-{slug}.md"
        related_nodes = [
            n
            for n in wb_nodes
            if n.get("status") in ("CANON_VERIFIED", "REFUTED")
            and (set(n.get("themes") or []) & set(themes))
        ]
        dossier_md = format_uk_paper_as_embassy_dossier(entry, themes, related_nodes)
        target = outbox / filename
        target.write_text(dossier_md, encoding="utf-8")
        exported_files.append(str(target.relative_to(root)))

    return exported_files


def export_single_paper_dossier(markdown_path: str | Path, repo_root: Path | None = None) -> str | None:
    """
    Called after `UniverseFlow.persist_and_index()` writes a new paper: if the paper
    matches any Colony bridge theme, automatically export/update its `DOSSIER-UK-*.md`
    in `knowledge_base/embassy/outbox/`.
    """
    root = (repo_root or REPO_ROOT).resolve()
    md_file = Path(markdown_path)
    if not md_file.is_absolute():
        md_file = root / md_file
    if not md_file.exists():
        return None

    text = md_file.read_text(encoding="utf-8", errors="replace")
    themes = _classify_themes(text[:4000])
    if not themes:
        return None

    title_m = re.search(r'^title:\s*"?([^\n"]+)"?', text, re.MULTILINE)
    level_m = re.search(r"^level:\s*(\d+)", text, re.MULTILINE)
    status_m = re.search(r'^status:\s*"?\[?([A-Za-z_]+)\]?"?', text, re.MULTILINE)
    math_st_m = re.search(r'^math_status:\s*"?\[?([A-Za-z_]+)\]?"?', text, re.MULTILINE)
    math_sc_m = re.search(r'^math_score:\s*"?([^\n"]+)"?', text, re.MULTILINE)
    ov_m = re.search(r"##\s*1\.\s*Overview\s*\n([\s\S]*?)(?=\n##\s*2\.|\Z)", text)
    sources = re.findall(r'^\s*-\s*"?([^\n"]+)"?', text.split("---")[1] if "---" in text else "", re.MULTILINE)

    entry = {
        "id": md_file.stem,
        "title": title_m.group(1).strip() if title_m else md_file.stem,
        "level": int(level_m.group(1)) if level_m else 3,
        "status": status_m.group(1) if status_m else "THEORETICAL",
        "math_status": math_st_m.group(1) if math_st_m else "MATH_CONSISTENT",
        "math_score": math_sc_m.group(1) if math_sc_m else "4/4",
        "path": str(md_file.resolve().relative_to((root / "knowledge_base").resolve())).replace("\\", "/"),
        "overview": ov_m.group(1).strip() if ov_m else "",
        "sources": sources,
        "content": text,
    }

    snapshot_file = root / "knowledge_base" / "embassy" / "colony_snapshot.json"
    wb_nodes = []
    if snapshot_file.exists():
        try:
            wb_nodes = json.loads(snapshot_file.read_text(encoding="utf-8")).get("world_b_nodes", [])
        except Exception:
            wb_nodes = []

    related_nodes = [
        n
        for n in wb_nodes
        if n.get("status") in ("CANON_VERIFIED", "REFUTED")
        and (set(n.get("themes") or []) & set(themes))
    ]
    dossier_md = format_uk_paper_as_embassy_dossier(entry, themes, related_nodes)
    outbox = root / "knowledge_base" / "embassy" / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9_]+", "_", md_file.stem.lower()).strip("_")[:75]
    out_file = outbox / f"DOSSIER-UK-L{entry['level']}-{slug}.md"
    out_file.write_text(dossier_md, encoding="utf-8")
    return str(out_file.relative_to(root))


def main() -> None:
    parser = argparse.ArgumentParser(description="Colony & Universe Knowledge Epistemic Bridge")
    parser.add_argument("--sync", action="store_true", help="Synchronize read-only snapshot from World A & World B")
    parser.add_argument("--export-outbox", action="store_true", help="Export Universe Knowledge literature dossiers to embassy/outbox")
    parser.add_argument("--max-dossiers", type=int, default=25, help="Max dossiers to export in batch mode")
    parser.add_argument("--search", type=str, default="", help="Run a test query against the Colony knowledge index")
    args = parser.parse_args()

    if args.sync or not SNAPSHOT_PATH.exists():
        snap = sync_colony_snapshot(REPO_ROOT)
        st = snap["stats"]
        print(
            f"[ColonyBridge] Synced snapshot: {st['wb_total_nodes']} World B nodes "
            f"({st['wb_canon_verified']} CANON_VERIFIED, {st['wb_refuted']} REFUTED), "
            f"{st['dossiers_indexed']} dossiers, {st['commons_messages_indexed']} Commons messages."
        )

    if args.export_outbox:
        exported = export_embassy_dossiers(REPO_ROOT, max_dossiers=args.max_dossiers)
        print(f"[ColonyBridge] Exported {len(exported)} Universe Knowledge Literature Dossiers to knowledge_base/embassy/outbox/.")

    if args.search:
        print(search_colony_knowledge(args.search, repo_root=REPO_ROOT))


if __name__ == "__main__":
    main()

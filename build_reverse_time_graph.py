"""
===============================================================================
🌌 REVERSE-TIME GRAPH & SEED CRYSTAL ARCHAEOLOGY BUILDER (DUAL-SOURCE)
===============================================================================
Parses both `knowledge_base/logs/equations.jsonl` AND `knowledge_base/database.json`.
Builds the topological network mapping Concepts <-> Equations <-> Seed Variables.

Seed Crystals: Mathematical symbols present across Level 1 (Fundamental),
Level 2 (Advanced Frameworks), and Level 3 (Emergence / Intelligence).
===============================================================================
"""

import os
import sys
import json
import re
from collections import defaultdict

# Ensure UTF-8 output formatting
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    HAS_PLOT_LIBS = True
except ImportError:
    HAS_PLOT_LIBS = False


# Symbol Definitions with exact Regex patterns and display names
SYMBOL_PATTERNS = [
    (r'\\hbar|\bhbar\b', r'\hbar', 'Reduced Planck Constant (Quantum Action)'),
    (r'\\Lambda|\bLambda\b', r'\Lambda', 'Cosmological Constant (Dark Energy Vacuum)'),
    (r'G_\{?\\?\\?mu\\?\\?nu\}?|G_{\\mu\\nu}', r'G_{\mu\nu}', 'Einstein Tensor (Spacetime Curvature)'),
    (r'T_\{?\\?\\?mu\\?\\?nu\}?|T_{\\mu\\nu}', r'T_{\mu\nu}', 'Stress-Energy Tensor (Matter-Energy Density)'),
    (r'g_\{?\\?\\?mu\\?\\?nu\}?|g_{\\mu\\nu}', r'g_{\mu\nu}', 'Spacetime Metric Tensor (Gravitational Geometry)'),
    (r'\\Phi|\bPhi\b', r'\Phi', 'Integrated Information / Scalar Field Potential'),
    (r'k_B|k_\{?\\rm B\}?|k_\{?\\text\{B\}\}?', r'k_B', 'Boltzmann Constant (Thermodynamic Entropy)'),
    (r'M_\{?\\rm Pl\}?|M_\{?Pl\}?|M_\{?\\text\{Pl\}\}?|m_\{?\\text\{Pl\}\}?', r'M_{\text{Pl}}', 'Planck Mass (Quantum Gravity Scale)'),
    (r'H_0', r'H_0', 'Hubble Expansion Parameter'),
    (r'\\Omega_\\Lambda|\\Omega_\{?\\Lambda\}?', r'\Omega_\Lambda', 'Dark Energy Density Parameter'),
    (r'\\Omega_m|\\Omega_\{?m\}?', r'\Omega_m', 'Matter Density Parameter'),
    (r'a_0|a_\\Lambda', r'a_0', 'Acceleration Scale / MOND Threshold'),
    (r'S_\{?\\rm EH\}?|S_\{?EH\}?', r'S_{\text{EH}}', 'Einstein-Hilbert Action Integral'),
    (r'D_\{?\\rm KL\}?|D_\{?KL\}?', r'D_{\text{KL}}', 'Kullback-Leibler Relative Entropy Divergence'),
    (r'R_\{?\\?\\?mu\\?\\?nu\}?|R_{\\mu\\nu}', r'R_{\mu\nu}', 'Ricci Curvature Tensor'),
    (r'\\tau|\\tau_\{?\\text\{dec\}\}?', r'\tau', 'Decay / Collapse Timescale')
]


def extract_symbols(text):
    """Extracts known mathematical symbols from LaTeX equation or markdown text."""
    found = set()
    for regex_pat, canonical_sym, desc in SYMBOL_PATTERNS:
        if re.search(regex_pat, text):
            found.add((canonical_sym, desc))
    return found


def build_reverse_time_graph(db_path, eq_log_path):
    """Builds the topological dual-source NetworkX graph and extracts Seed Crystals."""
    G = nx.Graph() if HAS_PLOT_LIBS else None
    symbol_levels = defaultdict(set)
    symbol_concepts = defaultdict(list)

    # 1. Parse equations.jsonl if available
    eq_records = []
    if os.path.exists(eq_log_path):
        with open(eq_log_path, 'r', encoding='utf-8') as f:
            eq_records = [json.loads(line) for line in f if line.strip()]

    for entry in eq_records:
        concept_title = entry.get('concept', 'Unknown')
        level = entry.get('level', 1)
        equations = entry.get('equations', [])

        if G is not None:
            G.add_node(concept_title, type='concept', level=level)

        for idx, eq_str in enumerate(equations):
            eq_node_id = f"{concept_title}_eq_{idx}"
            if G is not None:
                G.add_node(eq_node_id, type='equation', raw=eq_str, level=level)
                G.add_edge(concept_title, eq_node_id)

            symbols = extract_symbols(eq_str)
            for sym, desc in symbols:
                symbol_levels[sym].add(level)
                symbol_concepts[sym].append({'title': concept_title, 'level': level})

                if G is not None:
                    G.add_node(sym, type='symbol', description=desc)
                    G.add_edge(eq_node_id, sym)

    # 2. Parse database.json for master concept coverage
    concepts = []
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            concepts = json.load(f)

    for entry in concepts:
        concept_title = entry.get('title')
        level = entry.get('level', 1)
        content = entry.get('content', '')

        if G is not None and not G.has_node(concept_title):
            G.add_node(concept_title, type='concept', level=level)

        symbols = extract_symbols(content)
        for sym, desc in symbols:
            symbol_levels[sym].add(level)
            symbol_concepts[sym].append({'title': concept_title, 'level': level})

            if G is not None:
                if not G.has_node(sym):
                    G.add_node(sym, type='symbol', description=desc)
                G.add_edge(concept_title, sym)

    # 3. Find Seed Crystals (variables present across Levels 1, 2, & 3)
    seed_variables = []
    symbol_stats = []

    for sym, levels in symbol_levels.items():
        is_seed = {1, 2, 3}.issubset(levels)
        if is_seed:
            seed_variables.append(sym)

        desc = next((d for s, d in extract_symbols(sym)), 'Mathematical Variable')

        symbol_stats.append({
            'symbol': sym,
            'description': desc,
            'levels': sorted(list(levels)),
            'is_seed_crystal': is_seed,
            'concept_count': len(symbol_concepts[sym]),
            'concepts': symbol_concepts[sym]
        })

    return {
        'networkx_graph': G,
        'seed_variables': sorted(seed_variables),
        'symbol_stats': sorted(symbol_stats, key=lambda x: x['concept_count'], reverse=True)
    }


def export_graph_json(graph_data, output_json_path):
    """Exports structured graph data to JSON for web dashboard rendering."""
    export_payload = {
        'total_seed_crystals': len(graph_data['seed_variables']),
        'seed_variables': graph_data['seed_variables'],
        'symbols': graph_data['symbol_stats']
    }

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(export_payload, f, indent=2)

    print(f"Exported Reverse-Time Graph JSON to: {output_json_path}")


def visualize_graph(G, seed_variables, output_img_path):
    """Renders high-resolution graph visualization using Matplotlib & NetworkX."""
    if not HAS_PLOT_LIBS or G is None:
        print("Matplotlib / NetworkX not available. Skipping static plot generation.")
        return

    plt.figure(figsize=(18, 12), facecolor='#050811')
    ax = plt.gca()
    ax.set_facecolor('#050811')

    # Color map & sizes matching dark dashboard theme
    color_map = []
    node_sizes = []

    for node in G:
        node_type = G.nodes[node].get('type')

        if node_type == 'concept':
            level = G.nodes[node].get('level')
            if level == 1:
                color_map.append('#00f2fe')   # Cyan for L1
                node_sizes.append(70)
            elif level == 2:
                color_map.append('#ffab00')   # Amber for L2
                node_sizes.append(80)
            elif level == 3:
                color_map.append('#e0aaff')   # Electric Magenta for L3
                node_sizes.append(130)
            else:
                color_map.append('#888888')
                node_sizes.append(50)

        elif node_type == 'symbol':
            if node in seed_variables:
                color_map.append('#ffd700')   # Highlight Seed Variables in Gold
                node_sizes.append(280)
            else:
                color_map.append('#556677')
                node_sizes.append(40)
        else:
            # Equation nodes
            color_map.append('#223040')
            node_sizes.append(22)

    print(f"Calculating spring layout for {len(G)} nodes...")
    pos = nx.spring_layout(G, k=0.14, iterations=50, seed=42)

    # Draw faint edges
    nx.draw_networkx_edges(G, pos, alpha=0.15, edge_color='#334455', width=0.5)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=node_sizes, alpha=0.9)

    plt.axis('off')
    plt.tight_layout()

    os.makedirs(os.path.dirname(output_img_path), exist_ok=True)
    plt.savefig(output_img_path, dpi=300, bbox_inches='tight', facecolor='#050811', edgecolor='none')
    plt.close()

    print(f"Saved high-resolution visualization to: {output_img_path}")


if __name__ == "__main__":
    db_path = os.path.join('knowledge_base', 'database.json')
    eq_log_path = os.path.join('knowledge_base', 'logs', 'equations.jsonl')

    output_json = os.path.join('knowledge_base', 'reverse_time_graph.json')
    output_png = os.path.join('knowledge_base', 'images', 'reverse_time_graph.png')

    print("==================================================================")
    print("🌌 BUILDING THE REVERSE-TIME GRAPH & SEED CRYSTALS (DUAL-SOURCE)")
    print("==================================================================")

    data = build_reverse_time_graph(db_path, eq_log_path)

    print(f"\n=== 🌟 DISCOVERED SEED CRYSTALS ({len(data['seed_variables'])}) ===")
    for seed in data['seed_variables']:
        print(f"  - 🌟 {seed}")

    export_graph_json(data, output_json)
    if HAS_PLOT_LIBS:
        visualize_graph(data['networkx_graph'], data['seed_variables'], output_png)

    print("\n✅ REVERSE-TIME GRAPH BUILD COMPLETE!")

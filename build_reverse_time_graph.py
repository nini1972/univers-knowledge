"""
===============================================================================
🌌 REVERSE-TIME GRAPH & SEED CRYSTAL ARCHAEOLOGY BUILDER
===============================================================================
Treats Universe Knowledge concepts as nodes and mathematical variables
(\\hbar, \\Lambda, \\Phi, G_{\\mu\\nu}, g_{\\mu\\nu}, k_B, M_{\\text{Pl}}) as bridges.

Identifies 'Seed Crystals' — mathematical variables that originate in Level 1 (Fundamental),
survive through Level 2 (Advanced Framework Debates), and emerge in Level 3 (Intelligence & Emergence).
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


KNOWN_SYMBOL_DEFINITIONS = [
    (r'\\hbar|\bhbar\b', r'\hbar', 'Reduced Planck Constant (Quantum Action)'),
    (r'\\Lambda|\bLambda\b', r'\Lambda', 'Cosmological Constant (Dark Energy Density)'),
    (r'G_\{?\\?\\?mu\\?\\?nu\}?|G_{\\mu\\nu}', r'G_{\mu\nu}', 'Einstein Tensor (Spacetime Curvature)'),
    (r'T_\{?\\?\\?mu\\?\\?nu\}?|T_{\\mu\\nu}', r'T_{\mu\nu}', 'Stress-Energy Tensor (Matter-Energy Density)'),
    (r'g_\{?\\?\\?mu\\?\\?nu\}?|g_{\\mu\\nu}', r'g_{\mu\nu}', 'Spacetime Metric Tensor (Gravitational Geometry)'),
    (r'\\Phi|\bPhi\b', r'\Phi', 'Integrated Information / Scalar Field Potential'),
    (r'k_B|k_\{?\\rm B\}?|k_\{?\\text\{B\}\}?', r'k_B', 'Boltzmann Constant (Thermodynamic Entropy)'),
    (r'M_\{?\\rm Pl\}?|M_\{?Pl\}?|M_\{?\\text\{Pl\}\}?|m_\{?\\text\{Pl\}\}?', r'M_{\text{Pl}}', 'Planck Mass (Quantum Gravity Energy Scale)'),
    (r'H_0', r'H_0', 'Hubble Expansion Parameter'),
    (r'\\Omega_\\Lambda|\\Omega_\{?\\Lambda\}?', r'\Omega_\Lambda', 'Dark Energy Density Parameter'),
    (r'\\Omega_m|\\Omega_\{?m\}?', r'\Omega_m', 'Matter Density Parameter'),
    (r'S_\{?\\rm EH\}?|S_\{?EH\}?', r'S_{\text{EH}}', 'Einstein-Hilbert Action Integral'),
    (r'D_\{?\\rm KL\}?|D_\{?KL\}?', r'D_{\text{KL}}', 'Kullback-Leibler Relative Entropy Divergence'),
    (r'R_\{?\\?\\?mu\\?\\?nu\}?|R_{\\mu\\nu}', r'R_{\mu\nu}', 'Ricci Curvature Tensor'),
    (r'\\tau|\\tau_\{?\\text\{dec\}\}?', r'\tau', 'Decay / Collapse Timescale')
]


def extract_symbols_from_text(text):
    """Extracts known mathematical symbols from markdown text using regex matching."""
    found = set()
    for regex_pat, canonical_sym, desc in KNOWN_SYMBOL_DEFINITIONS:
        if re.search(regex_pat, text):
            found.add((canonical_sym, desc))
    return found


def build_reverse_time_graph(db_file_path):
    """Builds the topological NetworkX graph and extracts Seed Crystals."""
    if not os.path.exists(db_file_path):
        raise FileNotFoundError(f"Database file not found at: {db_file_path}")

    with open(db_file_path, 'r', encoding='utf-8') as f:
        concepts = json.load(f)

    G = nx.Graph() if HAS_PLOT_LIBS else None
    symbol_levels = defaultdict(set)
    symbol_concepts = defaultdict(list)
    concept_nodes = []

    for entry in concepts:
        concept_id = entry.get('id')
        concept_title = entry.get('title')
        level = entry.get('level', 1)
        status = entry.get('status', 'THEORETICAL')
        content = entry.get('content', '')

        concept_nodes.append({
            'id': concept_id,
            'title': concept_title,
            'level': level,
            'status': status
        })

        if G:
            G.add_node(concept_id, type='concept', label=concept_title, level=level, status=status)

        symbols = extract_symbols_from_text(content)

        for sym, desc in symbols:
            symbol_levels[sym].add(level)
            symbol_concepts[sym].append({
                'id': concept_id,
                'title': concept_title,
                'level': level
            })

            if G:
                G.add_node(sym, type='symbol', label=sym, description=desc)
                G.add_edge(concept_id, sym)

    # Find Seed Crystals (symbols present in Level 1, Level 2, and Level 3)
    seed_variables = []
    symbol_stats = []

    for sym, levels in symbol_levels.items():
        is_seed = {1, 2, 3}.issubset(levels)
        if is_seed:
            seed_variables.append(sym)

        # Get description
        desc = next((d for s, d in extract_symbols_from_text(sym)), 'Mathematical Variable')

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
        'symbol_stats': sorted(symbol_stats, key=lambda x: x['concept_count'], reverse=True),
        'concepts': concept_nodes
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

    # Color map for nodes
    color_map = []
    node_sizes = []

    for node in G:
        node_type = G.nodes[node].get('type')
        if node_type == 'concept':
            level = G.nodes[node].get('level')
            if level == 1:
                color_map.append('#00f2fe')   # Cyan for L1
                node_sizes.append(40)
            elif level == 2:
                color_map.append('#ffab00')   # Amber for L2
                node_sizes.append(50)
            elif level == 3:
                color_map.append('#e0aaff')   # Electric Magenta for L3
                node_sizes.append(120)
            else:
                color_map.append('#888888')
                node_sizes.append(30)
        else:
            # Symbol Node
            if node in seed_variables:
                color_map.append('#ffd700')   # Radiant Gold for Seed Crystals
                node_sizes.append(220)
            else:
                color_map.append('#445566')
                node_sizes.append(30)

    # Layout calculation
    pos = nx.spring_layout(G, k=0.18, iterations=60, seed=42)

    # Draw faint edges
    nx.draw_networkx_edges(G, pos, alpha=0.15, edge_color='#4a607a', width=0.8)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=node_sizes, alpha=0.9)

    # Draw labels ONLY for Seed Crystals
    labels = {node: node for node in seed_variables if node in G}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=11, font_color='#ffffff', font_weight='bold')

    plt.title(
        "REVERSE-TIME GRAPH: Mathematical Seed Crystals Across Cosmic Levels\n"
        "(Gold Nodes = Seed Crystals Bridging Level 1 -> Level 2 -> Level 3)",
        color='#ffffff', fontsize=14, pad=20, fontweight='bold'
    )
    plt.axis('off')

    os.makedirs(os.path.dirname(output_img_path), exist_ok=True)
    plt.savefig(output_img_path, dpi=300, bbox_inches='tight', facecolor='#050811')
    plt.close()

    print(f"Saved high-resolution visualization to: {output_img_path}")


if __name__ == "__main__":
    db_path = os.path.join('knowledge_base', 'database.json')
    output_json = os.path.join('knowledge_base', 'reverse_time_graph.json')
    output_png = os.path.join('knowledge_base', 'images', 'reverse_time_graph.png')

    print("==================================================================")
    print("🌌 BUILDING THE REVERSE-TIME GRAPH & SEED CRYSTALS")
    print("==================================================================")

    data = build_reverse_time_graph(db_path)

    print("\n=== 🌟 QUALIFIED SEED CRYSTALS (Variables present in Levels 1, 2, & 3) ===")
    for seed in data['seed_variables']:
        print(f"  - 🌟 {seed}")

    print("\n=== TOP MATHEMATICAL SYMBOL BRIDGES ===")
    for s in data['symbol_stats'][:10]:
        seed_badge = " [SEED CRYSTAL]" if s['is_seed_crystal'] else ""
        print(f"  - {s['symbol']:<15} ({s['concept_count']} concepts | Levels {s['levels']}){seed_badge}")

    export_graph_json(data, output_json)
    if HAS_PLOT_LIBS:
        visualize_graph(data['networkx_graph'], data['seed_variables'], output_png)

    print("\n✅ REVERSE-TIME GRAPH BUILD COMPLETE!")

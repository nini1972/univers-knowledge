import sys
import os
import re
import json
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

class EquationArchaeologist:
    """Mines knowledge_base/logs/equations.jsonl to discover cross-concept equation bridges,

    constructs a physical constant index, and builds a mathematical taxonomy.
    """

    KNOWN_CONSTANTS = {
        r"\Lambda": (r"\\Lambda", "Cosmological Constant", "m^-2", "1.089 x 10^-52"),
        r"c": (r"(?<![a-zA-Z\\])c(?![a-zA-Z0-9_])", "Speed of Light", "m/s", "2.998 x 10^8"),
        r"\hbar": (r"\\hbar", "Reduced Planck Constant", "J s", "1.054 x 10^-34"),
        r"G": (r"(?<![a-zA-Z\\])G(?![a-zA-Z])", "Gravitational Constant", "m^3 kg^-1 s^-2", "6.674 x 10^-11"),
        r"a_0": (r"a_0|a0", "MOND Acceleration Scale", "m s^-2", "1.2 x 10^-10"),
        r"M_{\text{Pl}}": (r"M_{\\rm Pl}|M_{Pl}|M_{\\text{Pl}}|m_{\\text{Pl}}|M_{Planck}", "Planck Mass", "GeV", "1.22 x 10^19"),
        r"N_{\text{eff}}": (r"N_{\\rm eff}|N_{eff}|N_{\\text{eff}}", "Effective Neutrino Species", "dimensionless", "3.044"),
        r"\Omega_c": (r"\\Omega_c|Omega_c", "Cold Dark Matter Density Parameter", "dimensionless", "0.120"),
    }

    def __init__(self, repo_root: Path = None):
        if repo_root is None:
            repo_root = Path(__file__).resolve().parent.parent
        self.repo_root = repo_root
        self.log_path = repo_root / "knowledge_base" / "logs" / "equations.jsonl"
        self.entries = []

    def load_equation_database(self):
        """Loads entries from equations.jsonl."""
        self.entries = []
        if not self.log_path.exists():
            print(f"Warning: Equation database {self.log_path} not found.")
            return self.entries

        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line_clean = line.strip()
                if not line_clean:
                    continue
                try:
                    data = json.loads(line_clean)
                    self.entries.append(data)
                except Exception as exc:
                    print(f"Warning: Failed to parse equation log line: {exc}")
        return self.entries

    def find_cross_concept_bridges(self):
        """Discovers identical or shared equations appearing across multiple concepts."""
        eq_map = defaultdict(list)
        for entry in self.entries:
            concept = entry.get("concept", "Unknown")
            level = entry.get("level", 1)
            for eq in entry.get("equations", []):
                eq_clean = eq.strip()
                if len(eq_clean) > 3:  # Filter single-symbol noises
                    eq_map[eq_clean].append((concept, level))

        bridges = []
        for eq, occurrences in eq_map.items():
            # Deduplicate by concept title
            unique_concepts = {}
            for c, l in occurrences:
                unique_concepts[c] = l

            if len(unique_concepts) > 1:
                bridges.append({
                    "equation": eq,
                    "concept_count": len(unique_concepts),
                    "concepts": [{"title": c, "level": l} for c, l in unique_concepts.items()]
                })

        bridges.sort(key=lambda x: x["concept_count"], reverse=True)
        return bridges

    def extract_constant_and_variable_index(self):
        """Scans all equations for physical constants and parameters using regex matching."""
        constant_occurrences = defaultdict(set)
        for entry in self.entries:
            concept = entry.get("concept", "Unknown")
            for eq in entry.get("equations", []):
                for const_sym, (pattern, name, unit, val) in self.KNOWN_CONSTANTS.items():
                    if re.search(pattern, eq):
                        constant_occurrences[const_sym].add(concept)

        index = []
        for const_sym, (pattern, name, unit, val) in self.KNOWN_CONSTANTS.items():
            occurring_concepts = list(constant_occurrences.get(const_sym, []))
            index.append({
                "symbol": const_sym,
                "name": name,
                "unit": unit,
                "typical_value": val,
                "occurrence_count": len(occurring_concepts),
                "referenced_in": sorted(occurring_concepts)
            })

        index.sort(key=lambda x: x["occurrence_count"], reverse=True)
        return index

    def build_equation_catalog(self):
        """Builds a structured catalog of equations by domain and level."""
        total_equations = sum(len(e.get("equations", [])) for e in self.entries)
        proven_count = sum(1 for e in self.entries if e.get("math_status") == "MATH_PROVEN")
        consistent_count = sum(1 for e in self.entries if e.get("math_status") == "MATH_CONSISTENT")

        bridges = self.find_cross_concept_bridges()
        constant_index = self.extract_constant_and_variable_index()

        catalog = {
            "version": "1.0.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "stats": {
                "total_entries": len(self.entries),
                "total_equations": total_equations,
                "math_proven_entries": proven_count,
                "math_consistent_entries": consistent_count,
                "total_bridges": len(bridges),
                "tracked_constants": len(constant_index)
            },
            "bridges": bridges,
            "constant_index": constant_index,
            "entries": self.entries
        }
        return catalog

    def generate_markdown_taxonomy(self, catalog):
        """Compiles human-readable Markdown taxonomy report."""
        lines = []
        lines.append("# 🧮 Equation Taxonomy & Cross-Concept Bridges Report")
        lines.append("")
        lines.append(f"> **Generated:** {catalog['updated_at']}  ")
        lines.append(f"> **Total Analyzed Concepts:** {catalog['stats']['total_entries']} | **Total Discovered Equations:** {catalog['stats']['total_equations']} | **Discovered Bridges:** {catalog['stats']['total_bridges']}")
        lines.append("")
        lines.append("## 🌉 1. Cross-Concept Equation Bridges")
        lines.append("These equations appear across multiple distinct concepts, serving as mathematical bridges between physics subfields.")
        lines.append("")

        if catalog["bridges"]:
            for b in catalog["bridges"][:15]:
                lines.append(f"### ` {b['equation']} `")
                lines.append(f"**Occurrences:** Appears in {b['concept_count']} concepts:")
                for c in b["concepts"]:
                    lines.append(f"- **Level {c['level']}**: {c['title']}")
                lines.append("")
        else:
            lines.append("No multi-concept equation bridges detected yet.")

        lines.append("## 📏 2. Fundamental Physical Constants Index")
        lines.append("| Symbol | Physical Quantity | Standard Units | Cited Value | Concept Count |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for c in catalog["constant_index"]:
            lines.append(f"| `{c['symbol']}` | {c['name']} | `{c['unit']}` | `{c['typical_value']}` | {c['occurrence_count']} |")
        lines.append("")

        lines.append("## 📊 3. Verification Status Summary")
        lines.append(f"- **MATH_PROVEN Entries:** {catalog['stats']['math_proven_entries']}")
        lines.append(f"- **MATH_CONSISTENT Entries:** {catalog['stats']['math_consistent_entries']}")
        lines.append("")
        return "\n".join(lines)

    def run(self):
        """Executes full equation analysis and writes Markdown and JSON outputs."""
        self.load_equation_database()
        catalog = self.build_equation_catalog()

        # Write JSON catalog
        json_path = self.repo_root / "knowledge_base" / "equation_index.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        print(f"Successfully written Equation Index to {json_path.relative_to(self.repo_root)}")

        # Write Markdown report
        md_text = self.generate_markdown_taxonomy(catalog)
        md_path = self.repo_root / "knowledge_base" / "equation_taxonomy_and_bridges.md"
        md_path.write_text(md_text, encoding="utf-8")
        print(f"Successfully written Equation Taxonomy Report to {md_path.relative_to(self.repo_root)}")

        return catalog


def main():
    repo_root = Path(__file__).resolve().parent.parent
    archaeologist = EquationArchaeologist(repo_root)
    archaeologist.run()


if __name__ == "__main__":
    main()

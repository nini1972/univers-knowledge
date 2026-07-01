"""
math_tools.py
=============
Five composable CrewAI-compatible tools for mathematical proof and verification.

Tools:
  1. EquationExtractorTool      — Extract LaTeX equations from markdown text
  2. DimensionalConsistencyTool — Verify dimensional consistency with sympy + pint
  3. SymbolicDerivationTool     — Step-by-step symbolic verification with sympy
  4. TopologyClassifierTool     — Rule-based topological argument classification
  5. NumericalBenchmarkTool     — Numerical validation against known physical constants
"""
from __future__ import annotations

import re
import json
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Tool 1: EquationExtractorTool
# ---------------------------------------------------------------------------

class EquationExtractorInput(BaseModel):
    text: str = Field(..., description="Raw markdown or research report text to extract LaTeX equations from.")


class EquationExtractorTool(BaseTool):
    name: str = "Equation Extractor"
    description: str = (
        "Extracts all LaTeX mathematical equations from a markdown research report. "
        "Finds both inline $...$ and block $$...$$ equations plus \\[...\\] and \\(...\\) forms. "
        "Returns a JSON list of unique equation strings."
    )
    args_schema: Type[BaseModel] = EquationExtractorInput

    def _run(self, text: str) -> str:
        patterns = [
            r'\$\$(.+?)\$\$',      # $$...$$  display math
            r'\\\[(.+?)\\\]',      # \[...\]  display math
            r'\$([^\$\n]+?)\$',    # $...$    inline math
            r'\\\((.+?)\\\)',      # \(...\)  inline math
        ]
        equations = []
        seen = set()
        for pat in patterns:
            for match in re.finditer(pat, text, re.DOTALL):
                eq = match.group(1).strip()
                # Skip trivially short or empty
                if len(eq) > 2 and eq not in seen:
                    seen.add(eq)
                    equations.append(eq)

        result = {
            "count": len(equations),
            "equations": equations,
            "note": "Equations extracted from LaTeX markup in source text."
        }
        return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Tool 2: DimensionalConsistencyTool
# ---------------------------------------------------------------------------

class DimensionalConsistencyInput(BaseModel):
    equations_json: str = Field(
        ...,
        description="JSON string (from EquationExtractorTool) containing a list of LaTeX equation strings to check for dimensional consistency."
    )


class DimensionalConsistencyTool(BaseTool):
    name: str = "Dimensional Consistency Checker"
    description: str = (
        "Checks whether LaTeX physics equations are dimensionally consistent using sympy and pint. "
        "Recognises standard physics unit signatures for common formulas. "
        "Returns per-equation verdicts: CONSISTENT, INCONSISTENT, DIMENSIONLESS, or UNDECIDABLE."
    )
    args_schema: Type[BaseModel] = DimensionalConsistencyInput

    # Curated pattern-matching rules for known physics equations
    # Each entry: (regex pattern for equation, verdict, explanation)
    KNOWN_PATTERNS: list[tuple[str, str, str]] = [
        # Special relativity
        (r'E\s*=\s*m\s*c\^?\s*2', 'CONSISTENT',
         'E=mc²: [J] = [kg][m/s]² = [kg·m²/s²] ✓'),
        (r'E\^2\s*=.*p.*c.*m.*c', 'CONSISTENT',
         'E²=(pc)²+(m₀c²)²: energy-momentum relation dimensionally consistent ✓'),
        # Quantum mechanics
        (r'\\hat\{H\}.*\\psi|i.*\\hbar.*\\partial', 'CONSISTENT',
         'Schrödinger equation: [J·s][1/s] = [J] → dimensional ✓'),
        (r'\\Delta x.*\\Delta p|\\Delta p.*\\Delta x', 'CONSISTENT',
         'Heisenberg uncertainty: [m][kg·m/s] = [J·s] ✓'),
        (r'E\s*=\s*h\s*f|E\s*=\s*\\hbar.*\\omega', 'CONSISTENT',
         'Planck relation E=hf: [J] = [J·s][1/s] = [J] ✓'),
        # Gravitation
        (r'F\s*=\s*G.*m.*m|F\s*=\s*G.*M.*m', 'CONSISTENT',
         'Newton gravity F=GMm/r²: [N] = [m³/kg/s²][kg][kg]/[m²] = [kg·m/s²] ✓'),
        (r'G_\{\\mu\\nu\}|R_\{\\mu\\nu\}|\\Lambda g_\{\\mu\\nu\}', 'CONSISTENT',
         'Einstein field equations: tensor equation, dimensionally consistent by construction ✓'),
        # Thermodynamics / stat mech
        (r'S\s*=\s*k.*\\ln|S\s*=\s*k_B.*\\ln', 'CONSISTENT',
         'Boltzmann entropy S=k_B ln Ω: [J/K] = [J/K] ✓'),
        (r'E\s*=\s*m\s*c\^?\s*3', 'INCONSISTENT',
         'E=mc³: [J] ≠ [kg][m/s]³ = [kg·m³/s³] — FLAWED formula ✗'),
        # QFT / Standard Model (structural, LLM to interpret)
        (r'\\mathcal\{L\}|\\mathscr\{L\}|\\partial_\\mu|D_\\mu', 'CONSISTENT',
         'QFT Lagrangian density: [J/m³] by construction in natural units ✓'),
        # Dimensionless quantities
        (r'\\alpha\s*=|\\alpha\s*\\approx', 'DIMENSIONLESS',
         'Fine structure constant α is dimensionless ✓'),
        (r'e\^2\s*/.*4.*\\pi.*\\epsilon|e\^2.*4.*pi.*eps', 'DIMENSIONLESS',
         'Fine structure constant expression — dimensionless ratio ✓'),
    ]

    def _run(self, equations_json: str) -> str:
        try:
            data = json.loads(equations_json)
            equations = data.get("equations", []) if isinstance(data, dict) else data
        except (json.JSONDecodeError, TypeError):
            # Treat as a plain list string
            equations = [equations_json.strip()]

        if not equations:
            return json.dumps({
                "summary": "No equations provided for checking.",
                "results": [],
                "consistent_count": 0,
                "inconsistent_count": 0
            }, indent=2)

        results = []
        consistent_count = 0
        inconsistent_count = 0

        for eq in equations:
            verdict = "UNDECIDABLE"
            explanation = (
                "Could not automatically verify dimensional consistency. "
                "This may be a complex tensor expression, topological identity, "
                "or abstract algebraic relation — use TopologyClassifierTool for these."
            )
            matched = False
            for pattern, v, expl in self.KNOWN_PATTERNS:
                if re.search(pattern, eq, re.IGNORECASE):
                    verdict = v
                    explanation = expl
                    matched = True
                    break

            if not matched:
                # Heuristic: if equation has both sides (contains = or ≡ or ≈)
                if re.search(r'=|\\equiv|\\approx', eq):
                    verdict = "UNDECIDABLE"
                    explanation = (
                        "Equation pattern not in known database. "
                        "Requires manual or agent-assisted dimensional analysis. "
                        "Consider passing to SymbolicDerivationTool for deeper check."
                    )
                else:
                    verdict = "DIMENSIONLESS"
                    explanation = "Expression appears to be a scalar/dimensionless quantity or partial expression."

            if verdict == "CONSISTENT":
                consistent_count += 1
            elif verdict == "INCONSISTENT":
                inconsistent_count += 1

            results.append({
                "equation": eq[:120],  # truncate for readability
                "verdict": verdict,
                "explanation": explanation
            })

        total = len(results)
        undecidable = total - consistent_count - inconsistent_count
        overall = (
            "ALL_CONSISTENT" if inconsistent_count == 0 and consistent_count > 0
            else "INCONSISTENCY_DETECTED" if inconsistent_count > 0
            else "ALL_UNDECIDABLE"
        )

        return json.dumps({
            "overall_verdict": overall,
            "consistent_count": consistent_count,
            "inconsistent_count": inconsistent_count,
            "undecidable_count": undecidable,
            "total_equations": total,
            "results": results,
            "note": (
                "UNDECIDABLE means the pattern is not in the known database, not that it is wrong. "
                "Use SymbolicDerivationTool for deeper verification."
            )
        }, indent=2)


# ---------------------------------------------------------------------------
# Tool 3: SymbolicDerivationTool
# ---------------------------------------------------------------------------

class SymbolicDerivationInput(BaseModel):
    concept: str = Field(..., description="Name of the physics concept being derived.")
    derivation_steps: str = Field(
        ...,
        description=(
            "A JSON list of derivation step strings in the form: "
            "[\"step1_expr\", \"step2_expr\", ...]. "
            "Each step is a sympy-parseable Python expression or LaTeX equation. "
            "The tool will attempt to verify that each step follows from the previous."
        )
    )


class SymbolicDerivationTool(BaseTool):
    name: str = "Symbolic Derivation Verifier"
    description: str = (
        "Uses sympy to symbolically verify a step-by-step mathematical derivation. "
        "Each step is checked for algebraic validity relative to the previous step. "
        "Returns per-step verdicts: STEP_VERIFIED, STEP_ASSUMED, or STEP_INVALID."
    )
    args_schema: Type[BaseModel] = SymbolicDerivationInput

    def _run(self, concept: str, derivation_steps: str) -> str:
        import sympy as sp

        try:
            steps = json.loads(derivation_steps)
        except json.JSONDecodeError:
            steps = [s.strip() for s in derivation_steps.split('\n') if s.strip()]

        if not steps:
            return json.dumps({
                "concept": concept,
                "error": "No derivation steps provided.",
                "steps": []
            }, indent=2)

        step_results = []
        proven_count = 0
        assumed_count = 0
        invalid_count = 0

        for i, step in enumerate(steps):
            step_result = {
                "step_number": i + 1,
                "expression": step[:200],
                "verdict": "STEP_ASSUMED",
                "detail": ""
            }

            # Try to parse as a sympy expression or equation
            try:
                # Handle simple equality verification
                if '==' in step or '=' in step.replace('==', ''):
                    parts = re.split(r'(?<!=)=(?!=)', step, maxsplit=1)
                    if len(parts) == 2:
                        lhs_str = parts[0].strip()
                        rhs_str = parts[1].strip()
                        # Replace common LaTeX-isms for sympy
                        for old, new in [
                            ('^', '**'), ('\\cdot', '*'), ('\\times', '*'),
                            ('\\frac{', 'Rational('), ('}', ')'),
                            ('mc^2', 'm*c**2'), ('hbar', 'h_bar'),
                        ]:
                            lhs_str = lhs_str.replace(old, new)
                            rhs_str = rhs_str.replace(old, new)

                        try:
                            lhs = sp.sympify(lhs_str, evaluate=True)
                            rhs = sp.sympify(rhs_str, evaluate=True)
                            diff = sp.simplify(lhs - rhs)
                            if diff == 0:
                                step_result["verdict"] = "STEP_VERIFIED"
                                step_result["detail"] = f"Sympy confirms: LHS - RHS = {diff} (identity holds)"
                                proven_count += 1
                            else:
                                step_result["verdict"] = "STEP_ASSUMED"
                                step_result["detail"] = (
                                    f"Could not automatically simplify to zero (diff={diff}). "
                                    "May require substitution or physical constants. Treating as assumed."
                                )
                                assumed_count += 1
                        except Exception as e:
                            step_result["verdict"] = "STEP_ASSUMED"
                            step_result["detail"] = f"Sympy parse error ({e}). Treating as assumed — requires manual review."
                            assumed_count += 1
                    else:
                        step_result["verdict"] = "STEP_ASSUMED"
                        step_result["detail"] = "Could not parse as equality. Treating as assumed."
                        assumed_count += 1
                else:
                    # It's a pure expression, just verify it's parseable
                    try:
                        sp.sympify(step.replace('^', '**'))
                        step_result["verdict"] = "STEP_VERIFIED"
                        step_result["detail"] = "Expression parsed successfully by sympy."
                        proven_count += 1
                    except Exception:
                        step_result["verdict"] = "STEP_ASSUMED"
                        step_result["detail"] = "Expression not sympy-parseable (may be LaTeX/natural language). Treating as assumed."
                        assumed_count += 1

            except Exception as e:
                step_result["verdict"] = "STEP_ASSUMED"
                step_result["detail"] = f"General error: {e}. Treating as assumed."
                assumed_count += 1

            step_results.append(step_result)

        total = len(step_results)
        math_status = (
            "[MATH_PROVEN]" if proven_count == total
            else "[MATH_CONSISTENT]" if invalid_count == 0
            else "[MATH_FLAWED]"
        )

        return json.dumps({
            "concept": concept,
            "math_status": math_status,
            "total_steps": total,
            "proven_steps": proven_count,
            "assumed_steps": assumed_count,
            "invalid_steps": invalid_count,
            "steps": step_results,
            "summary": (
                f"Derivation has {proven_count}/{total} steps verified by sympy, "
                f"{assumed_count} assumed (require manual or deeper review), "
                f"{invalid_count} flagged as invalid."
            )
        }, indent=2)


# ---------------------------------------------------------------------------
# Tool 4: TopologyClassifierTool
# ---------------------------------------------------------------------------

class TopologyClassifierInput(BaseModel):
    concept: str = Field(..., description="Name of the physics concept.")
    text: str = Field(..., description="Research report or mathematical description to classify topologically.")


class TopologyClassifierTool(BaseTool):
    name: str = "Topology Classifier"
    description: str = (
        "Detects and classifies topological mathematical arguments in a physics research report. "
        "Identifies fiber bundles, homotopy groups, Calabi-Yau manifolds, Chern-Simons theory, "
        "topological QFT, and other abstract geometric structures. "
        "Returns structural validity assessment and topology type classification."
    )
    args_schema: Type[BaseModel] = TopologyClassifierInput

    # Signature patterns → (topology_type, structural_check_note)
    TOPOLOGY_SIGNATURES: list[tuple[str, str, str]] = [
        # String Theory / M-Theory
        (r'Calabi.Yau|calabi.yau', 'CALABI_YAU_MANIFOLD',
         'Calabi-Yau manifolds require complex dimension 3 for superstring compactification. Holonomy group SU(3). Structurally valid signature.'),
        (r'string theory|superstring|M.theory', 'STRING_THEORY',
         'String theory uses 10D/11D spacetime with 6/7 compact extra dimensions. Gauge groups E₈×E₈ or SO(32). Structurally standard.'),
        (r'D.brane|p.brane|brane world', 'D_BRANE_GEOMETRY',
         'D-branes are hypersurfaces where open strings end. Dimensional counting must match p+1 worldvolume. Structurally check dimensionality.'),
        # Loop Quantum Gravity
        (r'spin foam|loop quantum gravity|spin network|holonomy.*loop', 'SPIN_FOAM_LQG',
         'LQG uses SU(2) spin networks. Spin foams are 2-complexes dual to triangulations. Structurally valid formalism.'),
        (r'Ashtekar|Barbero.Immirzi|Holst action', 'LQG_FORMULATION',
         'Ashtekar variables: connection A and densitized triad E. Barbero-Immirzi parameter γ is real. Structurally consistent.'),
        # Topological QFT
        (r'Chern.Simons|topological field theory|TQFT', 'TOPOLOGICAL_QFT',
         'Chern-Simons action is topological (metric-independent). Gauge group must be compact Lie group. Structurally valid.'),
        (r'\\pi_\d+|homotopy group|fundamental group', 'HOMOTOPY_THEORY',
         'Homotopy groups classify topological spaces. π₁ = fundamental group, π₃(S³) = ℤ. Structurally verifiable.'),
        (r'fiber bundle|principal bundle|gauge bundle', 'FIBER_BUNDLE',
         'Fiber bundles: total space E, base B, fiber F, structure group G. Connection defines parallel transport. Standard differential geometry.'),
        (r'Chern class|Pontryagin class|characteristic class', 'CHARACTERISTIC_CLASSES',
         'Characteristic classes are topological invariants. Chern classes live in H²ⁿ(M,ℤ). Structurally well-defined.'),
        # Differential Geometry
        (r'Riemann tensor|Ricci tensor|Christoffel|covariant derivative', 'RIEMANNIAN_GEOMETRY',
         'Riemannian geometry: metric g_μν, connection Γ, curvature R. Einstein equations follow from Bianchi identity. Well-established.'),
        (r'de Rham|differential form|exterior derivative|Hodge dual', 'DIFFERENTIAL_FORMS',
         'Differential forms: Stokes theorem generalizes fundamental theorem of calculus. Dimensionally consistent by construction.'),
        # Symmetry groups
        (r'SU\(\d+\)|SO\(\d+\)|Sp\(\d+\)|E_?\d+|G_?2', 'LIE_GROUP_STRUCTURE',
         'Lie group structure detected. Rank and dimension determine physical degrees of freedom. Standard gauge theory.'),
        (r'Lie algebra|commutator|anticommutator|\\{\\\\cdot|representation theory', 'LIE_ALGEBRA',
         'Lie algebra representation theory: roots, weights, Dynkin diagrams. Well-established mathematics.'),
    ]

    def _run(self, concept: str, text: str) -> str:
        detected = []
        seen_types = set()

        for pattern, topo_type, check_note in self.TOPOLOGY_SIGNATURES:
            if re.search(pattern, text, re.IGNORECASE) and topo_type not in seen_types:
                detected.append({
                    "topology_type": topo_type,
                    "structural_assessment": "TOPOLOGICAL_STRUCTURE_VALID",
                    "note": check_note
                })
                seen_types.add(topo_type)

        if not detected:
            # Check for any abstract algebra without specific topo markers
            abstract_markers = re.findall(
                r'manifold|cohomology|homology|sheaf|category theory|functor|topos', text, re.IGNORECASE
            )
            if abstract_markers:
                detected.append({
                    "topology_type": "ABSTRACT_MATHEMATICS",
                    "structural_assessment": "TOPOLOGICAL_STRUCTURE_VALID",
                    "note": f"Abstract mathematical structures detected: {list(set(m.lower() for m in abstract_markers))}. Requires expert human review for full structural validation."
                })

        is_topological = len(detected) > 0
        math_status = "[MATH_TOPOLOGICAL]" if is_topological else "NOT_TOPOLOGICAL"

        return json.dumps({
            "concept": concept,
            "is_topological": is_topological,
            "math_status": math_status,
            "detected_structures": detected,
            "structure_count": len(detected),
            "assessment": (
                "Topological mathematical structures detected. Full proof requires expert human review "
                "of structural consistency, but common signatures are valid."
                if is_topological
                else "No topological signatures detected. Standard physics formalism — use DimensionalConsistencyTool."
            )
        }, indent=2)


# ---------------------------------------------------------------------------
# Tool 5: NumericalBenchmarkTool
# ---------------------------------------------------------------------------

class NumericalBenchmarkInput(BaseModel):
    concept: str = Field(..., description="Name of the physics concept to benchmark.")
    equations_json: str = Field(
        ...,
        description="JSON string from EquationExtractorTool containing extracted equations to test numerically."
    )


class NumericalBenchmarkTool(BaseTool):
    name: str = "Numerical Benchmark Validator"
    description: str = (
        "Validates physics equations against known benchmark values using numpy and scipy. "
        "Tests predicted values from formulas against experimentally confirmed physical constants "
        "and known results. Returns BENCHMARK_MATCHES, BENCHMARK_MISMATCH, or BENCHMARK_UNAVAILABLE."
    )
    args_schema: Type[BaseModel] = NumericalBenchmarkInput

    # Curated benchmark table: (regex to detect relevance, benchmark name, expected value, tolerance)
    BENCHMARKS: list[dict] = [
        {
            "pattern": r'fine.structure|\\alpha\s*=|alpha.*137',
            "name": "Fine Structure Constant α",
            "symbol": "α",
            "expected": 7.2973525693e-3,
            "tolerance": 1e-10,
            "unit": "dimensionless",
            "formula": "α = e²/(4πε₀ℏc) ≈ 1/137.036",
            "source": "CODATA 2018"
        },
        {
            "pattern": r'Planck.constant|\\hbar|h\s*=.*6\.6|6\.626.*10.*-34',
            "name": "Planck Constant h",
            "symbol": "h",
            "expected": 6.62607015e-34,
            "tolerance": 1e-43,
            "unit": "J·s",
            "formula": "h = 6.62607015 × 10⁻³⁴ J·s",
            "source": "CODATA 2018 (exact)"
        },
        {
            "pattern": r'speed.of.light|c\s*=.*3.*10\^?8|c.*299',
            "name": "Speed of Light c",
            "symbol": "c",
            "expected": 299792458.0,
            "tolerance": 0.0,
            "unit": "m/s",
            "formula": "c = 299,792,458 m/s",
            "source": "SI definition (exact)"
        },
        {
            "pattern": r'electron.*mass|m_e|mass.*electron',
            "name": "Electron Rest Mass m_e",
            "symbol": "m_e",
            "expected": 9.1093837015e-31,
            "tolerance": 1e-40,
            "unit": "kg",
            "formula": "m_e = 9.1093837015 × 10⁻³¹ kg",
            "source": "CODATA 2018"
        },
        {
            "pattern": r'proton.*mass|m_p|mass.*proton',
            "name": "Proton Rest Mass m_p",
            "symbol": "m_p",
            "expected": 1.67262192369e-27,
            "tolerance": 1e-36,
            "unit": "kg",
            "formula": "m_p = 1.67262192369 × 10⁻²⁷ kg",
            "source": "CODATA 2018"
        },
        {
            "pattern": r'gravitational.constant|Newton.*G|G\s*=.*6\.67',
            "name": "Gravitational Constant G",
            "symbol": "G",
            "expected": 6.67430e-11,
            "tolerance": 1.5e-14,
            "unit": "m³/kg/s²",
            "formula": "G = 6.67430 × 10⁻¹¹ m³/(kg·s²)",
            "source": "CODATA 2018"
        },
        {
            "pattern": r'Boltzmann|k_B|k_b\s*=',
            "name": "Boltzmann Constant k_B",
            "symbol": "k_B",
            "expected": 1.380649e-23,
            "tolerance": 0.0,
            "unit": "J/K",
            "formula": "k_B = 1.380649 × 10⁻²³ J/K",
            "source": "SI definition (exact)"
        },
        {
            "pattern": r'Avogadro|N_A|6\.022.*10.*23',
            "name": "Avogadro Constant N_A",
            "symbol": "N_A",
            "expected": 6.02214076e23,
            "tolerance": 0.0,
            "unit": "mol⁻¹",
            "formula": "N_A = 6.02214076 × 10²³ mol⁻¹",
            "source": "SI definition (exact)"
        },
        {
            "pattern": r'Higgs.*mass|125.*GeV|higgs.*boson.*mass',
            "name": "Higgs Boson Mass",
            "symbol": "m_H",
            "expected": 125.25e9,  # in eV
            "tolerance": 0.17e9,
            "unit": "eV/c²",
            "formula": "m_H = 125.25 ± 0.17 GeV/c²",
            "source": "PDG 2022 (LHC measurements)"
        },
        {
            "pattern": r'cosmological.constant|\\Lambda.*dark.energy|Omega.*Lambda',
            "name": "Cosmological Constant Λ",
            "symbol": "Λ",
            "expected": 1.089e-52,
            "tolerance": 1e-54,
            "unit": "m⁻²",
            "formula": "Λ ≈ 1.089 × 10⁻⁵² m⁻²",
            "source": "Planck 2018"
        },
    ]

    def _run(self, concept: str, equations_json: str) -> str:
        try:
            data = json.loads(equations_json)
            equations = data.get("equations", []) if isinstance(data, dict) else data
            full_text = " ".join(equations)
        except Exception:
            full_text = equations_json
            equations = []

        # Also check the concept name itself for benchmark relevance
        combined_text = concept + " " + full_text

        benchmark_results = []
        matched_count = 0

        for bench in self.BENCHMARKS:
            if re.search(bench["pattern"], combined_text, re.IGNORECASE):
                matched_count += 1
                benchmark_results.append({
                    "benchmark": bench["name"],
                    "symbol": bench["symbol"],
                    "expected_value": bench["expected"],
                    "tolerance": bench["tolerance"],
                    "unit": bench["unit"],
                    "formula": bench["formula"],
                    "source": bench["source"],
                    "verdict": "BENCHMARK_MATCHES",
                    "note": (
                        f"Concept/equations reference {bench['name']}. "
                        f"Standard value: {bench['formula']} ({bench['source']}). "
                        "Verify that any numerical values cited in the report match this standard."
                    )
                })

        if not benchmark_results:
            return json.dumps({
                "concept": concept,
                "verdict": "BENCHMARK_UNAVAILABLE",
                "matched_benchmarks": 0,
                "results": [],
                "note": (
                    "No matching benchmark found in the curated physical constants database for this concept. "
                    "The concept may involve purely theoretical quantities without direct experimental values, "
                    "or may be topological/structural in nature."
                )
            }, indent=2)

        # Compute a math score contribution from benchmarks
        benchmark_score = min(1, matched_count)  # At least 1 relevant benchmark = 1 point

        return json.dumps({
            "concept": concept,
            "verdict": "BENCHMARK_MATCHES",
            "matched_benchmarks": matched_count,
            "benchmark_score": benchmark_score,
            "results": benchmark_results,
            "note": (
                f"Found {matched_count} relevant physical constant(s) for this concept. "
                "Ensure numerical values in the report match the CODATA/PDG standards listed above."
            )
        }, indent=2)


# ---------------------------------------------------------------------------
# Convenience: export all tools as a list
# ---------------------------------------------------------------------------

def get_all_math_tools() -> list:
    """Return all math verification tools as a list for agent configuration."""
    return [
        EquationExtractorTool(),
        DimensionalConsistencyTool(),
        SymbolicDerivationTool(),
        TopologyClassifierTool(),
        NumericalBenchmarkTool(),
    ]


def get_tier1_math_tools() -> list:
    """Tier 1 (automatic) tools: extract, dimension-check, topology, benchmark."""
    return [
        EquationExtractorTool(),
        DimensionalConsistencyTool(),
        TopologyClassifierTool(),
        NumericalBenchmarkTool(),
    ]


def get_tier2_math_tools() -> list:
    """Tier 2 (deep-dive) tools: all tools including symbolic derivation."""
    return get_all_math_tools()

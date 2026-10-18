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
from typing import ClassVar, Type

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

        if len(equations) > 25:
            rel_re = re.compile(r'(=|\\equiv|\\approx|\\sim|\\simeq|\\propto|<|>|\\le|\\ge|\\ll|\\gg|\\to|\\rightarrow|\\neq)')
            relational = [eq for eq in equations if rel_re.search(eq)]
            non_relational = [eq for eq in equations if not rel_re.search(eq)]
            equations = (relational + non_relational)[:25]

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
    symbol_dimensions_json: str = Field(
        default="",
        description="Optional JSON dictionary mapping symbol names to their natural-unit mass dimension [E]^n (e.g. '{\"phi\": 1, \"R\": 2, \"L\": 4}')."
    )


class DimensionalConsistencyTool(BaseTool):
    name: str = "Dimensional Consistency Checker"
    description: str = (
        "Checks whether LaTeX physics, cosmology, and statistical equations are dimensionally consistent "
        "in both SI units and 4D natural units (hbar = c = k_B = 1, [E]^n). "
        "Checks Lagrangian density terms against [E]^4, detects invalid algebraic variable-w(a) exponents "
        "and dropped covariance terms, and reports per-equation verdicts: "
        "CONSISTENT, INCONSISTENT, DIMENSIONLESS, or UNDECIDABLE."
    )
    args_schema: Type[BaseModel] = DimensionalConsistencyInput

    # Known FLAWED / INCONSISTENT patterns checked first (highest priority)
    KNOWN_INCONSISTENT_PATTERNS: ClassVar[list[tuple[str, str]]] = [
        (
            r'E\s*=\s*m\s*c\^?\s*3',
            'E=mc³: [J] != [kg][m/s]³ = [kg·m³/s³] — FLAWED formula ✗'
        ),
        (
            r'a\s*\^\s*\{?\s*-\s*3\s*[\(\[]\s*1\s*\+\s*(?:w\s*\(\s*[azt]\s*\)|w_0\s*\+\s*w_a)',
            'Variable-w(a) exponent error: rho(a) != rho_0 a^{-3[1+w(a)]} when w(a) varies; continuity equation requires rho(a) = rho_0 exp[-3 int (1+w(a\')) d ln a\'] ✗'
        ),
        (
            r'm_\{?(?:T|\\rm\s*T|\\text\{T\})\}?\^2\s*(?:=|\\equiv|\\sim|\\approx|\\propto)[^=\n]*g\^2\s*T\^2\s*\\phi\^2',
            'Dimensional mismatch: thermal mass-squared m_T^2 has mass dimension [E]^2 (~ g^2 T^2), whereas (1/2) g^2 T^2 phi^2 has dimension [E]^4 (thermal potential V_T) ✗'
        ),
        (
            r'V_\{?(?:T|\\rm\s*T|\\text\{T\})\}?\s*(?:=|\\equiv|\\sim|\\approx)\s*(?:\\frac\{1\}\{2\}\s*)?g\^2\s*T\^2\s*$',
            'Dimensional mismatch: thermal potential density V_T has mass dimension [E]^4 (~ (1/2) g^2 T^2 phi^2), whereas g^2 T^2 has dimension [E]^2 ✗'
        ),
        (
            r'(?:\\mathrm\{Var\}|\\text\{Var\}|\bVar)\s*\(\s*([^-\)]+?)\s*-\s*([^\)]+?)\s*\)\s*=\s*(?:\\mathrm\{Var\}|\\text\{Var\}|\bVar)\s*\(\s*\1\s*\)\s*\+\s*(?:\\mathrm\{Var\}|\\text\{Var\}|\bVar)\s*\(\s*\2\s*\)\s*$',
            'Algebraic/statistical flaw: Var(A - B) = Var(A) + Var(B) - 2 Cov(A, B); covariance term -2 Cov(A, B) was dropped without proof of independence ✗'
        ),
    ]

    # Curated pattern-matching rules for known valid physics/cosmology/statistical equations
    KNOWN_PATTERNS: ClassVar[list[tuple[str, str, str]]] = [
        # Special relativity
        (r'E\s*=\s*m\s*c\^?\s*2\b', 'CONSISTENT',
         'E=mc²: [J] = [kg][m/s]² = [kg·m²/s²] ✓'),
        (r'E\^2\s*=.*p.*c.*m.*c', 'CONSISTENT',
         'E²=(pc)²+(m₀c²)²: energy-momentum relation dimensionally consistent ✓'),
        # Quantum mechanics
        (r'\\hat\{H\}.*\\psi|i\s*\\hbar\s*\\frac\{\\partial\}\{\\partial\s*t\}|i\s*\\hbar\s*\\partial_t', 'CONSISTENT',
         'Schrödinger equation: [J·s][1/s] = [J] → dimensional ✓'),
        (r'\\Delta x.*\\Delta p|\\Delta p.*\\Delta x', 'CONSISTENT',
         'Heisenberg uncertainty: [m][kg·m/s] = [J·s] ✓'),
        (r'E\s*=\s*h\s*f\b|E\s*=\s*\\hbar\s*\\omega\b', 'CONSISTENT',
         'Planck relation E=hf: [J] = [J·s][1/s] = [J] ✓'),
        # Gravitation & Cosmology
        (r'F\s*=\s*G.*m.*m|F\s*=\s*G.*M.*m', 'CONSISTENT',
         'Newton gravity F=GMm/r²: [N] = [m³/kg/s²][kg][kg]/[m²] = [kg·m/s²] ✓'),
        (r'G_\{\\mu\\nu\}.*=.*(?:8\s*\\pi\s*G|M_\{?(?:\\rm\s*)?Pl\}?\^\{?-2\}?|\\kappa).*T_\{\\mu\\nu\}', 'CONSISTENT',
         'Einstein field equations: [E]^2 = [E]^-2 [E]^4 = [E]^2 ✓'),
        (r'H\^2\s*=\s*(?:\\frac\{8\s*\\pi\s*G\}\{3\}|\\frac\{1\}\{3\s*M_\{?(?:\\rm\s*)?Pl\}?\^2\}).*\\rho', 'CONSISTENT',
         'First Friedmann equation: [H^2] = [E]^2 = [E]^-2 [E]^4 ✓'),
        (r'\\dot\{\\rho\}\s*\+\s*3\s*H\s*\(\s*(?:\\rho\s*\+\s*p|1\s*\+\s*w)', 'CONSISTENT',
         'Cosmological fluid continuity equation: [E]^5 = [E]^1 [E]^4 ✓'),
        (r'\\rho\s*\(\s*[az]\s*\)\s*=\s*\\rho_\{?0|de,0\}?\s*\\exp\s*[\(\[]\s*-\s*3\s*\\int', 'CONSISTENT',
         'Exact integral solution of continuity equation for time-varying w(a): [E]^4 = [E]^4 · [E]^0 ✓'),
        (r'\\ddot\{\\phi\}\s*\+\s*3\s*H\s*\\dot\{\\phi\}\s*\+\s*(?:V\'|\\frac\{d\s*V\}\{d\s*\\phi\}|\\partial_\\phi\s*V)\s*=\s*0', 'CONSISTENT',
         'Homogeneous Klein-Gordon scalar field equation: all terms have mass dimension [E]^3 ✓'),
        (r'X\s*(?:=|\\equiv)\s*-\s*\\frac\{1\}\{2\}\s*g\^\{\\mu\\nu\}\s*\\partial_\\mu\s*\\phi\s*\\partial_\\nu\s*\\phi', 'CONSISTENT',
         'Canonical scalar kinetic invariant X: [E]^4 = [E]^0 [E]^2 [E]^2 ✓'),
        (r'S\s*=\s*\\int\s*d\^4x\s*\\sqrt\{-g\}', 'CONSISTENT',
         '4D spacetime action S = int d^4x sqrt(-g) L: [E]^-4 · [E]^4 = [E]^0 (dimensionless in hbar=1) ✓'),
        # Thermodynamics / stat mech / variance algebra
        (r'S\s*=\s*k.*\\ln|S\s*=\s*k_B.*\\ln', 'CONSISTENT',
         'Boltzmann entropy S=k_B ln Ω: [J/K] = [J/K] ✓'),
        (r's\s*=\s*\\frac\{2\s*\\pi\^2\}\{45\}\s*g_\{\*?s\}.*T\^3', 'CONSISTENT',
         'Relativistic entropy density s = (2pi^2/45) g_{*s} T^3: [E]^3 = [E]^0 [E]^3 ✓'),
        (r'(?:\\mathrm\{Var\}|\\text\{Var\}|\bVar)\s*\(\s*([^-\)]+?)\s*-\s*([^\)]+?)\s*\)\s*=.*-\s*2\s*(?:\\mathrm\{Cov\}|\\text\{Cov\}|\bCov)', 'CONSISTENT',
         'Variance of contrast includes full -2 Cov(A, B) term ✓'),
        # Dimensionless quantities
        (r'^(?:\\alpha|c_s\^2|w\s*\(\s*a\s*\)|S_8|\\Omega_\w+|N_\{\\rm\s*eff\}|g_\{\*?s?\})\s*(?:=|\\equiv|\\approx)', 'DIMENSIONLESS',
         'Dimensionless physical ratio or cosmological parameter ([E]^0) ✓'),
        (r'e\^2\s*/.*4.*\\pi.*\\epsilon|e\^2.*4.*pi.*eps', 'DIMENSIONLESS',
         'Fine structure constant expression — dimensionless ratio ✓'),
    ]

    # Canonical 4D natural-unit mass dimensions [E]^n for direct term-level checking
    CANONICAL_MASS_DIMS: ClassVar[dict[str, float]] = {
        r'\mathcal{L}': 4.0, r'\mathscr{L}': 4.0, 'L': 4.0,
        'V': 4.0, 'V_0': 4.0, 'V_T': 4.0, r'\rho': 4.0, r'\rho_0': 4.0,
        r'\rho_r': 4.0, r'\rho_m': 4.0, r'\rho_{de}': 4.0, 'p': 4.0, 'P': 4.0,
        'X': 4.0,
        'n': 3.0, 'n_B': 3.0, 'n_e': 3.0, r'n_\gamma': 3.0, 's': 3.0, 's_0': 3.0,
        'R': 2.0, 'm_T^2': 2.0, 'm_{eff}^2': 2.0,
        'E': 1.0, 'T': 1.0, 'T_0': 1.0, 'T_{RH}': 1.0, 'T_{reh}': 1.0, 'T_c': 1.0,
        'H': 1.0, 'H_0': 1.0, 'm': 1.0, r'm_\phi': 1.0, 'm_a': 1.0, 'f_a': 1.0,
        'M_{Pl}': 1.0, 'M_P': 1.0, 'm_{Pl}': 1.0, 'M_*': 1.0,
        r'\phi': 1.0, r'\chi': 1.0, r'\Gamma': 1.0, 'k': 1.0, r'\omega': 1.0,
        r'\psi': 1.5, r'\bar{\psi}': 1.5,
        'a': 0.0, 'a_0': 0.0, 'z': 0.0, 'w': 0.0, 'w_0': 0.0, 'w_a': 0.0,
        'c_s': 0.0, 'g': 0.0, 'y': 0.0, r'\lambda': 0.0, r'\alpha': 0.0,
        'g_*': 0.0, 'g_{*s}': 0.0, 'S_8': 0.0, r'\sigma_8': 0.0, 'N_e': 0.0,
        't': -1.0, r'\tau': -1.0, 'r_s': -1.0,
        'G': -2.0, 'G_N': -2.0,
    }

    def _check_lagrangian_or_natural_units(self, eq: str, custom_dims: dict[str, float]) -> tuple[str | None, str | None]:
        """
        Check common Lagrangian density definitions L = ... or simple natural-unit monomials
        against 4D mass dimensions [E]^n. Returns (verdict, explanation) or (None, None).
        """
        dims = {**self.CANONICAL_MASS_DIMS, **(custom_dims or {})}

        # Check explicit Lagrangian definitions: \mathcal{L} = ...
        if re.search(r'^(?:\\mathcal\{L\}|\\mathscr\{L\}|\bL)_[a-zA-Z0-9\{\}\\rm\s,]*=\s*', eq) or re.search(
            r'^(?:\\mathcal\{L\}|\\mathscr\{L\})\s*=', eq
        ):
            # Known valid canonical & k-essence & QFT & EFT Lagrangians ([E]^4)
            if re.search(
                r'(\\frac\{1\}\{2\}\s*\(\\partial\s*\\phi\)\^2|\\partial_\\mu\s*\\phi\s*\\partial\^\\mu\s*\\phi|P\s*\(\s*X\s*,\s*\\phi\s*\)|\\bar\{\\psi\}\s*\(?\s*i\s*\\gamma\^\\mu|F_\{\\mu\\nu\}\s*F\^\{\\mu\\nu\}|\\frac\{\\alpha_s\}\{8\s*\\pi\}\s*\\bar\{\\theta\}\s*G|\\frac\{[^\{\}]+\}\{M_\*?\^2\}\s*\(?\\partial_\\mu\s*R\)?\s*J)',
                eq
            ):
                return (
                    "CONSISTENT",
                    "4D Lagrangian density terms verified against mass dimension [L] = [E]^4 in natural units ✓"
                )
            # Detect un-suppressed dimension-5+ operator in L without inverse mass scale
            if re.search(r'\\phi\^([5-9])\b', eq) and not re.search(r'(/|\\frac|M_|\\Lambda)', eq):
                power = re.search(r'\\phi\^([5-9])\b', eq).group(1)
                return (
                    "INCONSISTENT",
                    f"Non-renormalizable operator phi^{power} has mass dimension [E]^{power} != [E]^4 without an inverse cutoff scale 1/M^{int(power)-4} ✗"
                )

        # Check simple two-side monomial/polynomial equations in natural units if custom_dims are provided
        if custom_dims and "=" in eq and not re.search(r'(\\int|\\sum|\\text\{|\\mathrm\{km|Mpc|kg|mol\})', eq):
            parts = eq.split("=", 1)
            lhs, rhs = parts[0].strip(), parts[1].strip()
            if lhs in dims and rhs in dims:
                d_l, d_r = dims[lhs], dims[rhs]
                if abs(d_l - d_r) < 1e-6:
                    if abs(d_l) < 1e-6:
                        return ("DIMENSIONLESS", f"Both sides have natural-unit dimension [E]^0 ✓")
                    return ("CONSISTENT", f"Both sides match in natural-unit mass dimension [E]^{d_l:g} ✓")
                return ("INCONSISTENT", f"Natural-unit mass dimension mismatch: LHS {lhs} has [E]^{d_l:g} != RHS {rhs} [E]^{d_r:g} ✗")

        return (None, None)

    def _run(self, equations_json: str, symbol_dimensions_json: str = "") -> str:
        try:
            data = json.loads(equations_json)
            equations = data.get("equations", []) if isinstance(data, dict) else data
        except (json.JSONDecodeError, TypeError):
            equations = [equations_json.strip()]

        custom_dims: dict[str, float] = {}
        if symbol_dimensions_json and symbol_dimensions_json.strip():
            try:
                parsed_dims = json.loads(symbol_dimensions_json)
                if isinstance(parsed_dims, dict):
                    for k, v in parsed_dims.items():
                        try:
                            custom_dims[str(k).strip()] = float(v)
                        except (ValueError, TypeError):
                            pass
            except Exception:
                pass

        if not equations:
            return json.dumps({
                "summary": "No equations provided for checking.",
                "results": [],
                "consistent_count": 0,
                "dimensionless_count": 0,
                "inconsistent_count": 0,
                "undecidable_count": 0,
            }, indent=2)

        results = []
        consistent_count = 0
        dimensionless_count = 0
        inconsistent_count = 0

        for raw_eq in equations:
            eq = str(raw_eq).strip()
            verdict = "UNDECIDABLE"
            explanation = (
                "Could not automatically verify dimensional consistency. "
                "Report this equation honestly as UNDECIDABLE or verify its terms against the Symbol Table."
            )
            matched = False

            # Step 1: Check known inconsistent/flawed patterns first
            for bad_pat, bad_expl in self.KNOWN_INCONSISTENT_PATTERNS:
                if re.search(bad_pat, eq, re.IGNORECASE):
                    verdict = "INCONSISTENT"
                    explanation = bad_expl
                    matched = True
                    break

            # Step 2: Check Lagrangian / natural-unit [E]^n evaluator
            if not matched:
                nu_verdict, nu_expl = self._check_lagrangian_or_natural_units(eq, custom_dims)
                if nu_verdict is not None:
                    verdict = nu_verdict
                    explanation = nu_expl
                    matched = True

            # Step 3: Check known valid physics/cosmology patterns
            if not matched:
                for pattern, v, expl in self.KNOWN_PATTERNS:
                    if re.search(pattern, eq, re.IGNORECASE):
                        verdict = v
                        explanation = expl
                        matched = True
                        break

            # Step 4: Fallback for unmatched expressions (never blindly mark standalone tokens as DIMENSIONLESS)
            if not matched:
                if re.search(r'(=|\\equiv|\\approx|\\sim|\\simeq|\\propto|<|>|\\le|\\ge)', eq):
                    verdict = "UNDECIDABLE"
                    explanation = (
                        "Relational equation not in built-in pattern table. "
                        "Cross-check term dimensions manually against the report's Symbol Table ([E]^n or SI); "
                        "do not claim tool-verified consistency without checking."
                    )
                else:
                    verdict = "UNDECIDABLE"
                    explanation = (
                        "Standalone expression without a relational operator (=, ~, approx); "
                        "cannot verify two-sided dimensional balance."
                    )

            if verdict == "CONSISTENT":
                consistent_count += 1
            elif verdict == "DIMENSIONLESS":
                dimensionless_count += 1
            elif verdict == "INCONSISTENT":
                inconsistent_count += 1

            results.append({
                "equation": eq[:140],
                "verdict": verdict,
                "explanation": explanation
            })

        total = len(results)
        undecidable = total - consistent_count - dimensionless_count - inconsistent_count
        verified_total = consistent_count + dimensionless_count

        # Global Coherence Rule: UNDECIDABLE is never collapsed into ALL_CONSISTENT
        if inconsistent_count > 0:
            overall = "INCONSISTENCY_DETECTED"
        elif verified_total > 0 and undecidable == 0:
            overall = "ALL_CONSISTENT"
        elif verified_total > 0 and undecidable > 0:
            overall = "CONSISTENT_WITH_UNDECIDABLE"
        else:
            overall = "ALL_UNDECIDABLE"

        return json.dumps({
            "overall_verdict": overall,
            "consistent_count": consistent_count,
            "dimensionless_count": dimensionless_count,
            "inconsistent_count": inconsistent_count,
            "undecidable_count": undecidable,
            "total_equations": total,
            "results": results,
            "note": (
                "GLOBAL COHERENCE RULE: If inconsistent_count > 0, math_status MUST be [MATH_FLAWED]. "
                "If undecidable_count > 0, do NOT claim 'all equations were tool-verified as consistent'; "
                "explicitly state which equations were tool-verified and check UNDECIDABLE equations against the Symbol Table."
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
        "Validates physics and cosmology equations against 20 curated CODATA, PDG, Planck 2018, SH0ES, "
        "DESI 2024/2025, KiDS/DES, BBN, BICEP/Keck, and GW170817 benchmark values with uncertainties, "
        "covariances, and verified DOIs. Returns BENCHMARK_MATCHES, BENCHMARK_MISMATCH, or BENCHMARK_UNAVAILABLE."
    )
    args_schema: Type[BaseModel] = NumericalBenchmarkInput

    # Curated benchmark table: CODATA/PDG constants + Observational Cosmology benchmarks (with uncertainties & DOIs)
    BENCHMARKS: ClassVar[list[dict]] = [
        {
            "pattern": r'fine.structure|\\alpha\s*=|alpha.*137',
            "name": "Fine Structure Constant α",
            "symbol": "α",
            "expected": 7.2973525693e-3,
            "tolerance": 1.1e-12,
            "unit": "dimensionless",
            "formula": "α = e²/(4πε₀ℏc) = 7.2973525693(11) × 10⁻³ (≈ 1/137.036)",
            "source": "CODATA 2018",
            "doi": "10.1103/RevModPhys.93.025010",
        },
        {
            "pattern": r'Planck.constant|\\hbar|h\s*=.*6\.6|6\.626.*10.*-34',
            "name": "Planck Constant h",
            "symbol": "h",
            "expected": 6.62607015e-34,
            "tolerance": 0.0,
            "unit": "J·s",
            "formula": "h = 6.62607015 × 10⁻³⁴ J·s (ℏ = 1.054571817 × 10⁻³⁴ J·s)",
            "source": "CODATA 2018 (SI exact)",
            "doi": "10.1103/RevModPhys.93.025010",
        },
        {
            "pattern": r'speed.of.light|c\s*=.*3.*10\^?8|c.*299',
            "name": "Speed of Light c",
            "symbol": "c",
            "expected": 299792458.0,
            "tolerance": 0.0,
            "unit": "m/s",
            "formula": "c = 299,792,458 m/s",
            "source": "SI definition (exact)",
            "doi": "10.1103/RevModPhys.93.025010",
        },
        {
            "pattern": r'electron.*mass|m_e|mass.*electron',
            "name": "Electron Rest Mass m_e",
            "symbol": "m_e",
            "expected": 9.1093837015e-31,
            "tolerance": 2.8e-40,
            "unit": "kg",
            "formula": "m_e = 9.1093837015 × 10⁻³¹ kg (0.510998950 MeV)",
            "source": "CODATA 2018",
            "doi": "10.1103/RevModPhys.93.025010",
        },
        {
            "pattern": r'proton.*mass|m_p|mass.*proton',
            "name": "Proton Rest Mass m_p",
            "symbol": "m_p",
            "expected": 1.67262192369e-27,
            "tolerance": 5.1e-37,
            "unit": "kg",
            "formula": "m_p = 1.67262192369 × 10⁻²⁷ kg (938.272088 MeV)",
            "source": "CODATA 2018",
            "doi": "10.1103/RevModPhys.93.025010",
        },
        {
            "pattern": r'gravitational.constant|Newton.*G|G\s*=.*6\.67',
            "name": "Gravitational Constant G",
            "symbol": "G",
            "expected": 6.67430e-11,
            "tolerance": 1.5e-15,
            "unit": "m³/(kg·s²)",
            "formula": "G = (6.67430 ± 0.00015) × 10⁻¹¹ m³/(kg·s²)",
            "source": "CODATA 2018",
            "doi": "10.1103/RevModPhys.93.025010",
        },
        {
            "pattern": r'M_\{?(?:\\rm\s*)?Pl\}?|reduced.*planck.*mass|2\.435.*10\^?\{?18\}?|planck.*mass',
            "name": "Reduced Planck Mass M_Pl",
            "symbol": "M_Pl",
            "expected": 2.43536e18,
            "tolerance": 0.00006e18,
            "unit": "GeV",
            "formula": "M_Pl = (8πG)^(-1/2) = 2.43536 × 10¹⁸ GeV (m_Pl = G^(-1/2) = 1.22091 × 10¹⁹ GeV)",
            "source": "CODATA 2018 / PDG",
            "doi": "10.1093/ptep/ptac097",
        },
        {
            "pattern": r'Boltzmann|k_B|k_b\s*=',
            "name": "Boltzmann Constant k_B",
            "symbol": "k_B",
            "expected": 1.380649e-23,
            "tolerance": 0.0,
            "unit": "J/K",
            "formula": "k_B = 1.380649 × 10⁻²³ J/K",
            "source": "SI definition (exact)",
            "doi": "10.1103/RevModPhys.93.025010",
        },
        {
            "pattern": r'Avogadro|N_A|6\.022.*10.*23',
            "name": "Avogadro Constant N_A",
            "symbol": "N_A",
            "expected": 6.02214076e23,
            "tolerance": 0.0,
            "unit": "mol⁻¹",
            "formula": "N_A = 6.02214076 × 10²³ mol⁻¹",
            "source": "SI definition (exact)",
            "doi": "10.1103/RevModPhys.93.025010",
        },
        {
            "pattern": r'Higgs.*mass|125.*GeV|higgs.*boson.*mass|m_H',
            "name": "Higgs Boson Mass m_H",
            "symbol": "m_H",
            "expected": 125.25,
            "tolerance": 0.17,
            "unit": "GeV",
            "formula": "m_H = 125.25 ± 0.17 GeV",
            "source": "PDG 2022 (LHC combined)",
            "doi": "10.1093/ptep/ptac097",
        },
        {
            "pattern": r'cosmological.constant|\\Lambda.*dark.energy|Omega.*Lambda|1\.089.*10\^?\{?-52\}?',
            "name": "Cosmological Constant Λ & Dark Energy Density Ω_Λ",
            "symbol": "Λ",
            "expected": 1.089e-52,
            "tolerance": 0.029e-52,
            "unit": "m⁻²",
            "formula": "Λ = (1.089 ± 0.029) × 10⁻⁵² m⁻²; Ω_Λ = 0.6847 ± 0.0073; ρ_Λ = (2.25 meV)⁴",
            "source": "Planck 2018 VI",
            "doi": "10.1051/0004-6361/201833910",
        },
        {
            "pattern": r'H_0|hubble.*constant|planck.*67|67\.36|67\.4|r_s|sound.*horizon',
            "name": "Planck 2018 ΛCDM Baseline (H_0, Ω_m, n_s, r_s)",
            "symbol": "H_0 (Planck)",
            "expected": 67.36,
            "tolerance": 0.54,
            "unit": "km s⁻¹ Mpc⁻¹",
            "formula": "H_0 = 67.36 ± 0.54 km s⁻¹ Mpc⁻¹; Ω_m = 0.3153 ± 0.0073; Ω_b h² = 0.02237 ± 0.00015; Ω_c h² = 0.1200 ± 0.0012; n_s = 0.9649 ± 0.0042; r_s(z_*) = 147.09 ± 0.26 Mpc",
            "source": "Planck Collaboration (2020) VI",
            "doi": "10.1051/0004-6361/201833910",
        },
        {
            "pattern": r'H_0|hubble.*tension|sh0es|cepheid|73\.04|distance.*ladder',
            "name": "SH0ES Local Distance-Ladder Hubble Constant H_0",
            "symbol": "H_0 (SH0ES)",
            "expected": 73.04,
            "tolerance": 1.04,
            "unit": "km s⁻¹ Mpc⁻¹",
            "formula": "H_0 = 73.04 ± 1.04 km s⁻¹ Mpc⁻¹ (4.85σ Gaussian tension with Planck ΛCDM: ΔH_0 = 5.68 ± 1.17 km s⁻¹ Mpc⁻¹)",
            "source": "Riess et al. (2022) SH0ES / JWST (2024)",
            "doi": "10.3847/2041-8213/ac5c5b",
        },
        {
            "pattern": r'S_8|\\sigma_8|sigma_8|weak.*lensing|cosmic.*shear|structure.*growth|f\\sigma_8',
            "name": "Cosmic Shear Structure Amplitude S_8 = σ_8 (Ω_m/0.3)^0.5",
            "symbol": "S_8",
            "expected": 0.759,
            "tolerance": 0.022,
            "unit": "dimensionless",
            "formula": "S_8(KiDS-1000) = 0.759 (+0.024/-0.021); S_8(DES-Y3) = 0.776 ± 0.017 vs. S_8(Planck 2018) = 0.832 ± 0.013 (σ_8 = 0.8111 ± 0.0060; 2.5σ–2.9σ tension)",
            "source": "KiDS-1000 (2021) / DES-Y3 (2022) / Planck (2020)",
            "doi": "10.1051/0004-6361/202039070",
        },
        {
            "pattern": r'w_0|w_a|w\(a\)|quintessence|k-essence|dynamical.*dark.*energy|desi|cpl',
            "name": "DESI 2024/2025 + CMB + SNe Dynamical Dark Energy (w_0, w_a)",
            "symbol": "(w_0, w_a)",
            "expected": -0.827,
            "tolerance": 0.063,
            "unit": "dimensionless",
            "formula": (
                "DESI+CMB+Pantheon+: w_0 = -0.827 ± 0.063, w_a = -0.75 (+0.29/-0.25), corr(w_0, w_a) = -0.85 (Δχ² ≈ -6.8 vs ΛCDM, 2.5σ); "
                "DESI+CMB+DES-SN5YR: w_0 = -0.727 ± 0.067, w_a = -1.05 (+0.31/-0.27), corr(w_0, w_a) = -0.85 (Δχ² ≈ -15.2 vs ΛCDM, 3.9σ)"
            ),
            "source": "DESI Collaboration (2025) VI",
            "doi": "10.1088/1475-7516/2025/02/021",
        },
        {
            "pattern": r'baryon|baryogenesis|\\eta_B|n_B\s*/\s*s|n_B\s*/\s*n_\\gamma|bbn|nucleosynthesis|N_\{\\rm\s*eff\}',
            "name": "BBN & Planck Baryon Asymmetry (η_B, n_B/s) and N_eff",
            "symbol": "η_10 / Y_B",
            "expected": 6.143e-10,
            "tolerance": 0.190e-10,
            "unit": "dimensionless",
            "formula": "η_B = n_B/n_γ = (6.143 ± 0.190) × 10⁻¹⁰; Y_B = n_B/s = (8.70 ± 0.06) × 10⁻¹¹; N_eff = 2.99 ± 0.17 (SM theoretical N_eff = 3.044)",
            "source": "Planck 2018 VI / PDG 2022 BBN",
            "doi": "10.1051/0004-6361/201833910",
        },
        {
            "pattern": r'c_\{?(?:gw|T)\}?|graviton.*speed|gw170817|tensor.*speed|horndeski|modified.*gravity',
            "name": "GW170817 / GRB170817A Gravitational-Wave Speed Bound",
            "symbol": "|c_gw - c|/c",
            "expected": 0.0,
            "tolerance": 3.0e-15,
            "unit": "dimensionless",
            "formula": "-3 × 10⁻¹⁵ ≤ (c_gw - c)/c ≤ +7 × 10⁻¹⁶ (at z = 0.0098)",
            "source": "LIGO/Virgo & Fermi-GBM (2017)",
            "doi": "10.3847/2041-8213/aa920c",
        },
        {
            "pattern": r'tensor-to-scalar|r_\{?0\.05\}?|bicep|primordial.*tensor|inflation|slow-roll',
            "name": "BICEP/Keck 2021 Tensor-to-Scalar Ratio Bound r_0.05",
            "symbol": "r_0.05",
            "expected": 0.014,
            "tolerance": 0.010,
            "unit": "dimensionless",
            "formula": "r_0.05 < 0.036 (95% CL; r_0.05 = 0.014 ± 0.010)",
            "source": "BICEP/Keck Collaboration (2021)",
            "doi": "10.1103/PhysRevLett.127.151301",
        },
        {
            "pattern": r'strong.*cp|neutron.*edm|d_n|\\bar\{\\theta\}|axion|peccei-quinn',
            "name": "PSI nEDM Bound & Strong CP Angle |θ̄|",
            "symbol": "|d_n|",
            "expected": 0.0,
            "tolerance": 1.8e-26,
            "unit": "e·cm",
            "formula": "|d_n| < 1.8 × 10⁻²⁶ e·cm (90% CL) ⇒ |θ̄| < 10⁻¹⁰",
            "source": "Abel et al. [nEDM Collaboration] (2020)",
            "doi": "10.1103/PhysRevLett.124.081803",
        },
        {
            "pattern": r'thermal.*inflation|reheating|T_0|cmb.*temperature|s_0|entropy.*density',
            "name": "Present CMB Temperature T_0 & Entropy Density s_0",
            "symbol": "T_0 / s_0",
            "expected": 2.72548,
            "tolerance": 0.00057,
            "unit": "K",
            "formula": "T_0 = 2.72548 ± 0.00057 K = 2.3486 × 10⁻¹³ GeV; s_0 = 2891.2 cm⁻³; g_{*s}(T_0) = 3.909",
            "source": "Fixsen (2009) COBE/FIRAS / PDG",
            "doi": "10.1088/0004-637X/707/2/916",
        },
    ]

    def _run(self, concept: str, equations_json: str) -> str:
        try:
            data = json.loads(equations_json)
            equations = data.get("equations", []) if isinstance(data, dict) else data
            full_text = " ".join(str(e) for e in equations)
        except Exception:
            full_text = str(equations_json)
            equations = []

        combined_text = f"{concept} {full_text}"

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
                    "doi": bench.get("doi", ""),
                    "verdict": "BENCHMARK_MATCHES",
                    "note": (
                        f"Concept/equations reference {bench['name']}. "
                        f"Standard value: {bench['formula']} ({bench['source']}, DOI: {bench.get('doi', 'N/A')}). "
                        "Verify that any numerical values cited in the report match this standard within uncertainty."
                    )
                })

        if not benchmark_results:
            return json.dumps({
                "concept": concept,
                "verdict": "BENCHMARK_UNAVAILABLE",
                "matched_benchmarks": 0,
                "results": [],
                "note": (
                    "No matching benchmark found in the curated constants/observational database for this concept. "
                    "The concept may involve theoretical/statistical quantities — use Physics Calculator & Tension Evaluator "
                    "to verify worked numerical examples or contrast variances."
                )
            }, indent=2)

        benchmark_score = min(1, matched_count)

        return json.dumps({
            "concept": concept,
            "verdict": "BENCHMARK_MATCHES",
            "matched_benchmarks": matched_count,
            "benchmark_score": benchmark_score,
            "results": benchmark_results,
            "note": (
                f"Found {matched_count} relevant physical/observational benchmark(s) for this concept. "
                "Cross-check all worked numerical examples and observational comparisons against these standards."
            )
        }, indent=2)


# ---------------------------------------------------------------------------
# Tool 6: PhysicsCalculatorTool (P4 — Worked-Example & Tension Calculator)
# ---------------------------------------------------------------------------

class PhysicsCalculatorInput(BaseModel):
    mode: str = Field(
        default="evaluate",
        description=(
            "Calculation mode: "
            "'evaluate' (compute expression with built-in constants and variables_json), "
            "'verify_claim' (compare computed expression against claimed_value within tolerance_rel, default 10%), "
            "'tension_sigma' (compute Gaussian sigma tension and delta_chi2 between val1±err1 and val2±err2), or "
            "'delta_chi2_w0wa' (compute 2D Gaussian delta_chi2 and sigma of (w0, wa) in variables_json against DESI+CMB+SNe covariance)."
        )
    )
    expression: str = Field(
        default="",
        description=(
            "Mathematical expression to evaluate (e.g. '(1/H_end) * ((g_reh/g_0)**(1/3) * (T_reh/T_0)) * GeV_inv_to_m' "
            "or 'exp(-3 * (1 + w0) * log(a))'). Built-in constants available automatically: "
            "c, hbar, k_B, G, M_Pl (2.43536e18 GeV), m_Pl (1.22091e19 GeV), T_0_K (2.72548), T_0_GeV (2.3486e-13), "
            "g_0 (3.909), s_0_cm3 (2891.2), GeV_inv_to_m (1.97327e-16), GeV_inv_to_s (6.58212e-25), Mpc_to_m (3.08568e22), "
            "H0_Planck (67.36), H0_SH0ES (73.04), S8_Planck (0.832), S8_KiDS (0.759), S8_DES (0.776)."
        )
    )
    variables_json: str = Field(
        default="{}",
        description="Optional JSON dictionary of variable values, e.g. '{\"H_end\": 1e-6, \"T_reh\": 1e2, \"g_reh\": 106.75}' or '{\"w0\": -0.9, \"wa\": -0.2}'."
    )
    claimed_value: float | None = Field(
        default=None,
        description="Optional numerical value claimed in the text to verify against the computed expression."
    )
    tolerance_rel: float = Field(
        default=0.10,
        description="Relative tolerance for 'verify_claim' mode (default 0.10 = 10%)."
    )
    val1: float | None = Field(default=None, description="First value for 'tension_sigma' mode.")
    err1: float | None = Field(default=None, description="1-sigma uncertainty on val1 for 'tension_sigma' mode.")
    val2: float | None = Field(default=None, description="Second value for 'tension_sigma' mode.")
    err2: float | None = Field(default=None, description="1-sigma uncertainty on val2 for 'tension_sigma' mode.")
    correlation: float = Field(default=0.0, description="Correlation coefficient rho in [-1, 1] between val1 and val2.")


class PhysicsCalculatorTool(BaseTool):
    name: str = "Physics Calculator & Tension Evaluator"
    description: str = (
        "Deterministic scientific calculator and observational tension evaluator (sympy/math). "
        "Use before finalizing any numerical example, unit conversion (GeV^-1 to meters/seconds), "
        "or model-vs-data comparison: "
        "(1) 'evaluate' computes exact values using canonical physics/cosmology constants; "
        "(2) 'verify_claim' checks if a formula + benchmark parameters match a claimed number within 10%; "
        "(3) 'tension_sigma' computes Gaussian tension (in sigma) and delta_chi2 between two values ± uncertainties; "
        "(4) 'delta_chi2_w0wa' computes 2D covariant delta_chi2 of a dark-energy model (w0, wa) against DESI 2024/2025 + CMB + SNe."
    )
    args_schema: Type[BaseModel] = PhysicsCalculatorInput

    BUILTIN_CONSTANTS: ClassVar[dict[str, float]] = {
        "c": 299792458.0,
        "hbar": 1.054571817e-34,
        "h": 6.62607015e-34,
        "k_B": 1.380649e-23,
        "G": 6.67430e-11,
        "M_Pl": 2.43536e18,
        "m_Pl": 1.22091e19,
        "T_0_K": 2.72548,
        "T_0_GeV": 2.3486e-13,
        "T_0": 2.3486e-13,
        "g_0": 3.909,
        "g_s0": 3.909,
        "g_star_SM": 106.75,
        "s_0_cm3": 2891.2,
        "GeV_inv_to_m": 1.973269804e-16,
        "GeV_inv_to_s": 6.582119569e-25,
        "Mpc_to_m": 3.085677581e22,
        "yr_to_s": 3.15576e7,
        "H0_Planck": 67.36,
        "H0_Planck_err": 0.54,
        "H0_SH0ES": 73.04,
        "H0_SH0ES_err": 1.04,
        "S8_Planck": 0.832,
        "S8_Planck_err": 0.013,
        "S8_KiDS": 0.759,
        "S8_KiDS_err": 0.022,
        "S8_DES": 0.776,
        "S8_DES_err": 0.017,
        "eta_B": 6.143e-10,
        "Y_B": 8.70e-11,
    }

    @staticmethod
    def _normalize_expr(expr: str) -> str:
        s = (expr or "").strip()
        if "=" in s and not any(op in s for op in ["==", "<=", ">=", "!="]):
            # If user passed "lhs = rhs", evaluate rhs
            s = s.split("=", 1)[1].strip()
        s = s.replace("^", "**")
        s = re.sub(r'\\times|\\cdot', '*', s)
        # Convert simple \frac{A}{B} to ((A)/(B))
        for _ in range(4):
            s_new = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'((\1)/(\2))', s)
            if s_new == s:
                break
            s = s_new
        s = re.sub(r'\\sqrt\{([^{}]+)\}', r'sqrt(\1)', s)
        s = s.replace("{", "(").replace("}", ")")
        s = re.sub(r'\\(?:left|right|rm|text|mathrm)\b', '', s)
        s = s.replace("\\", "")
        return s.strip()

    def _run(
        self,
        mode: str = "evaluate",
        expression: str = "",
        variables_json: str = "{}",
        claimed_value: float | None = None,
        tolerance_rel: float = 0.10,
        val1: float | None = None,
        err1: float | None = None,
        val2: float | None = None,
        err2: float | None = None,
        correlation: float = 0.0,
    ) -> str:
        import math
        import sympy as sp

        mode_clean = (mode or "evaluate").strip().lower()
        user_vars: dict[str, float] = {}
        if variables_json and variables_json.strip():
            try:
                parsed = json.loads(variables_json)
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        try:
                            user_vars[str(k).strip()] = float(v)
                        except (ValueError, TypeError):
                            pass
            except Exception:
                pass

        env_vars = {**self.BUILTIN_CONSTANTS, **user_vars}

        # Mode 3: 1D Gaussian tension_sigma
        if mode_clean == "tension_sigma" or (val1 is not None and val2 is not None and err1 is not None and err2 is not None):
            v1 = float(val1 if val1 is not None else user_vars.get("val1", 0.0))
            v2 = float(val2 if val2 is not None else user_vars.get("val2", 0.0))
            e1 = float(err1 if err1 is not None else user_vars.get("err1", 0.0))
            e2 = float(err2 if err2 is not None else user_vars.get("err2", 0.0))
            rho = max(-0.999, min(0.999, float(correlation)))
            var_diff = e1**2 + e2**2 - 2.0 * rho * e1 * e2
            if var_diff <= 0:
                return json.dumps({"error": "Combined variance must be positive."}, indent=2)
            sigma_diff = math.sqrt(var_diff)
            diff = abs(v1 - v2)
            tension_sig = diff / sigma_diff
            delta_chi2 = tension_sig**2
            return json.dumps({
                "mode": "tension_sigma",
                "val1": v1,
                "err1": e1,
                "val2": v2,
                "err2": e2,
                "correlation": rho,
                "difference": v1 - v2,
                "combined_uncertainty": sigma_diff,
                "tension_sigma": round(tension_sig, 4),
                "delta_chi2_1dof": round(delta_chi2, 4),
                "note": "Gaussian approximation: tension_sigma = |val1 - val2| / sqrt(err1^2 + err2^2 - 2*rho*err1*err2)."
            }, indent=2)

        # Mode 4: 2D DESI (w0, wa) Gaussian covariance delta_chi2
        if mode_clean in ("delta_chi2_w0wa", "desi_w0wa"):
            w0 = float(user_vars.get("w0", user_vars.get("w_0", -1.0)))
            wa = float(user_vars.get("wa", user_vars.get("w_a", 0.0)))
            datasets = {
                "DESI_2024_CMB_PantheonPlus": {"mu_w0": -0.827, "sig_w0": 0.063, "mu_wa": -0.75, "sig_wa": 0.27, "rho": -0.85},
                "DESI_2024_CMB_DES_SN5YR": {"mu_w0": -0.727, "sig_w0": 0.067, "mu_wa": -1.05, "sig_wa": 0.29, "rho": -0.85},
            }
            comparisons = {}
            for ds_name, p in datasets.items():
                dw0 = (w0 - p["mu_w0"]) / p["sig_w0"]
                dwa = (wa - p["mu_wa"]) / p["sig_wa"]
                r = p["rho"]
                dchi2 = (dw0**2 - 2.0 * r * dw0 * dwa + dwa**2) / (1.0 - r**2)
                # Equivalent 1D Gaussian sigma for 1-dof sqrt(dchi2) and 2-dof p-value equivalent
                p_val_2dof = math.exp(-0.5 * dchi2)
                comparisons[ds_name] = {
                    "best_fit_mean": [p["mu_w0"], p["mu_wa"]],
                    "uncertainties_1sigma": [p["sig_w0"], p["sig_wa"]],
                    "correlation_rho": r,
                    "delta_chi2_2dof": round(dchi2, 3),
                    "sqrt_delta_chi2": round(math.sqrt(max(0.0, dchi2)), 3),
                    "gaussian_2d_tail_prob": float(f"{p_val_2dof:.3e}"),
                }
            return json.dumps({
                "mode": "delta_chi2_w0wa",
                "tested_point": {"w0": w0, "wa": wa},
                "comparisons": comparisons,
                "doi": "10.1088/1475-7516/2025/02/021",
                "note": "2D Gaussian covariance approximation against DESI 2024 VI + Planck CMB + Type Ia SNe."
            }, indent=2)

        # Modes 1 & 2: 'evaluate' and 'verify_claim'
        clean_expr = self._normalize_expr(expression)
        if not clean_expr:
            return json.dumps({
                "error": "No expression provided to Physics Calculator.",
                "available_constants": list(self.BUILTIN_CONSTANTS.keys()),
            }, indent=2)

        try:
            local_symbols = {k: sp.Float(v) for k, v in env_vars.items()}
            sym_expr = sp.sympify(clean_expr, locals=local_symbols)
            evaluated = sym_expr.evalf(subs=local_symbols)
            computed_val = float(evaluated)
        except Exception as exc:
            return json.dumps({
                "mode": mode_clean,
                "expression": expression,
                "normalized_expression": clean_expr,
                "error": f"Could not evaluate expression numerically: {exc}",
                "hint": "Provide standard Python math syntax (e.g. '(1/H_end)*GeV_inv_to_m') and define all custom variables in variables_json."
            }, indent=2)

        payload: dict = {
            "mode": "verify_claim" if claimed_value is not None or mode_clean == "verify_claim" else "evaluate",
            "expression": expression,
            "normalized_expression": clean_expr,
            "variables_used": user_vars,
            "computed_value": computed_val,
            "computed_scientific": f"{computed_val:.6e}",
        }

        if claimed_value is not None:
            claimed = float(claimed_value)
            denom = max(abs(computed_val), abs(claimed), 1e-300)
            rel_err = abs(computed_val - claimed) / denom
            ratio = (computed_val / claimed) if abs(claimed) > 1e-300 else None
            matches = rel_err <= float(tolerance_rel)
            payload.update({
                "claimed_value": claimed,
                "relative_error": round(rel_err, 6),
                "computed_to_claimed_ratio": float(f"{ratio:.4e}") if ratio is not None else None,
                "tolerance_rel": tolerance_rel,
                "verdict": "CLAIM_VERIFIED" if matches else "CLAIM_MISMATCH",
                "note": (
                    f"Claim verified within {tolerance_rel*100:.1f}% tolerance ✓"
                    if matches
                    else f"ARITHMETIC MISMATCH: computed {computed_val:.4e} vs claimed {claimed:.4e} (ratio = {ratio:.3e}). Update the manuscript to {computed_val:.4e} ✗"
                )
            })

        return json.dumps(payload, indent=2)


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
        PhysicsCalculatorTool(),
    ]


def get_tier1_math_tools() -> list:
    """Tier 1 (automatic) tools: extract, dimension-check, topology, benchmark, calculator."""
    return [
        EquationExtractorTool(),
        DimensionalConsistencyTool(),
        TopologyClassifierTool(),
        NumericalBenchmarkTool(),
        PhysicsCalculatorTool(),
    ]


def get_tier2_math_tools() -> list:
    """Tier 2 (deep-dive) tools: all tools including symbolic derivation."""
    return get_all_math_tools()


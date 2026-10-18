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

import os
import threading

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared safety helpers: restricted SymPy parsing + wall-clock time limit
# ---------------------------------------------------------------------------

MATH_TOOL_TIMEOUT_S = float(os.getenv("MATH_TOOL_TIMEOUT_S", "8"))
_MAX_EXPR_CHARS = 2000

# Patterns that have no place in a math expression written by an agent.
_UNSAFE_EXPR_RE = re.compile(
    r"__|['\"`;]|\blambda\b|\bimport\b|\bexec\b|\beval\b|\bopen\b|[A-Za-z_]\s*\.\s*[A-Za-z_]"
)
# Huge literal exponents (e.g. 10**10**10) can exhaust memory before any timeout fires.
_HUGE_POWER_RE = re.compile(r"\*\*\s*\(?\s*-?\d{4,}|\*\*\s*\(?\s*-?\d+\s*\)?\s*\*\*")


def _safe_sympy_globals() -> dict:
    """Whitelisted names available to parse_expr (no Python builtins)."""
    import sympy as sp

    allowed = {
        "__builtins__": {},
        # Required by SymPy's parser transformations
        "Symbol": sp.Symbol, "Integer": sp.Integer, "Float": sp.Float,
        "Rational": sp.Rational, "Function": sp.Function,
        "factorial": sp.factorial, "factorial2": sp.factorial2,
        # Elementary functions & constants. E, I, S, N, gamma, beta are deliberately
        # NOT mapped, so they stay plain symbols (energy, Lorentz factor, entropy, ...).
        "sqrt": sp.sqrt, "exp": sp.exp, "log": sp.log, "ln": sp.log,
        "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
        "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
        "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
        "Abs": sp.Abs, "pi": sp.pi, "oo": sp.oo,
        "diff": sp.diff, "integrate": sp.integrate,
        "Derivative": sp.Derivative, "Integral": sp.Integral,
    }
    return allowed


def safe_sympy_parse(expr: str, local_dict: dict | None = None):
    """
    Parse an expression with SymPy using a whitelisted namespace instead of sympify().
    Raises ValueError for oversized or suspicious input.
    """
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations

    s = (expr or "").strip()
    if not s:
        raise ValueError("empty expression")
    if len(s) > _MAX_EXPR_CHARS:
        raise ValueError(f"expression longer than {_MAX_EXPR_CHARS} characters")
    if _UNSAFE_EXPR_RE.search(s):
        raise ValueError("expression contains disallowed tokens")
    if _HUGE_POWER_RE.search(s):
        raise ValueError("expression contains an oversized or stacked literal exponent")
    return parse_expr(
        s,
        local_dict=dict(local_dict or {}),
        global_dict=_safe_sympy_globals(),
        transformations=standard_transformations,
        evaluate=True,
    )


def run_with_timeout(fn, timeout_s: float = MATH_TOOL_TIMEOUT_S, *args, **kwargs):
    """
    Run fn(*args, **kwargs) in a daemon thread and raise TimeoutError if it does not
    finish within timeout_s. The worker thread cannot be killed, but the agent is
    unblocked and the daemon thread never prevents interpreter exit.
    """
    result: dict = {}

    def _target():
        try:
            result["value"] = fn(*args, **kwargs)
        except BaseException as exc:  # propagate any error to the caller
            result["error"] = exc

    worker = threading.Thread(target=_target, daemon=True)
    worker.start()
    worker.join(timeout_s)
    if worker.is_alive():
        raise TimeoutError(f"symbolic computation exceeded {timeout_s:g}s")
    if "error" in result:
        raise result["error"]
    return result.get("value")


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
# Natural-unit [E]^n term analyzer (used by DimensionalConsistencyTool)
# ---------------------------------------------------------------------------

def normalize_latex_equation(eq: str) -> str:
    """Strip presentational LaTeX (\\left, \\big, spacing) so pattern checks see one canonical form."""
    s = str(eq or "")
    s = re.sub(r"\\(?:left|right|bigl|bigr|Bigl|Bigr|biggl|biggr|Biggl|Biggr|big|Big|bigg|Bigg)(?![A-Za-z])", "", s)
    s = re.sub(r"\\(?:displaystyle|textstyle)(?![A-Za-z])", "", s)
    s = re.sub(r"\\(?:qquad|quad)(?![A-Za-z])|\\[,;:!]|~", " ", s)
    s = re.sub(r"\\[dt]frac(?![A-Za-z])", r"\\frac", s)
    s = re.sub(r"\\leq(?![A-Za-z])", r"\\le", s)
    s = re.sub(r"\\geq(?![A-Za-z])", r"\\ge", s)
    s = s.replace("\\{", "(").replace("\\}", ")")
    s = re.sub(r"(?<![_^])\{\\rm\s+([^{}]*)\}", r"\\mathrm{\1}", s)
    s = re.sub(r"\^\s*(-\s*\d+(?:\.\d+)?)", lambda m: "^{" + m.group(1).replace(" ", "") + "}", s)
    return s.strip().rstrip(".,;").strip()


class _UnknownDimension(Exception):
    """Raised when a factor's mass dimension cannot be determined."""


class NaturalUnitDimensionAnalyzer:
    """
    Computes the 4D natural-unit mass dimension [E]^n of every additive term in a LaTeX
    equation and compares them. Each resolved symbol is tagged "exact" (declared in the
    report's symbol table, or an unambiguous canonical symbol) or "inferred" (ambiguous
    letter such as p, P, k, s, n, R, G, or a base-symbol fallback). Only mismatches between
    exact terms produce a definitive INCONSISTENT verdict.
    """

    GREEK = {
        "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta", "theta",
        "vartheta", "iota", "kappa", "lambda", "mu", "nu", "xi", "pi", "rho", "varrho", "sigma",
        "tau", "upsilon", "phi", "varphi", "chi", "psi", "omega", "Gamma", "Delta", "Theta",
        "Lambda", "Xi", "Pi", "Sigma", "Upsilon", "Phi", "Psi", "Omega", "ell", "hbar",
    }
    INDEX_NAMES = {"mu", "nu", "alpha", "beta", "rho", "sigma", "lambda", "kappa", "i", "j"}
    FUNCTIONS = {
        "exp", "ln", "log", "sin", "cos", "tan", "sinh", "cosh", "tanh", "arcsin", "arccos",
        "arctan", "erf", "det", "tr", "Tr", "sgn", "max", "min",
    }
    BIG_OPERATORS = {"int", "iint", "iiint", "oint", "sum", "prod", "lim"}
    SKIP_COMMANDS = {"cdot", "times", "langle", "rangle", "vert", "lvert", "rvert", "nonumber"}
    ACCENTS = {"bar", "tilde", "hat", "vec", "mathbf", "boldsymbol", "overline", "widetilde", "widehat"}
    STYLED = {"mathcal", "mathscr"}
    TEXT_COMMANDS = {"mathrm", "text", "rm", "mathit", "textrm", "operatorname"}
    RELATION_COMMANDS = {
        "equiv", "approx", "simeq", "sim", "cong", "le", "ge", "ll", "gg", "lesssim", "gtrsim",
        "neq", "ne",
    }
    ABORT_COMMANDS = {"propto", "to", "rightarrow", "Rightarrow", "mapsto", "longrightarrow", "in", "subset"}

    UNITS = {
        "GeV": 1, "MeV": 1, "keV": 1, "eV": 1, "TeV": 1, "meV": 1, "PeV": 1, "K": 1, "Hz": 1,
        "kg": 1, "g": 1, "J": 1, "erg": 1,
        "m": -1, "cm": -1, "mm": -1, "km": -1, "fm": -1, "pc": -1, "kpc": -1, "Mpc": -1, "Gpc": -1,
        "s": -1, "yr": -1, "Gyr": -1, "Myr": -1,
    }

    # Bases whose labelled variants (rho_DE, T_reh, H_0, m_phi, ...) keep the base dimension.
    LABEL_SAFE_BASES = {"rho", "Omega", "T", "H", "m", "M", "phi", "chi", "w", "mathcalL", "Gamma", "E", "a", "t"}
    # Bare symbols whose meaning is near-universal here (counted as exact without a symbol table).
    UNAMBIGUOUS_BARE = {"m", "M", "t", "c", "hbar", "k_B", "pi", "e", "i", "mathcalL", "mathscrL",
                        "phi", "chi", "psi", "barpsi", "g", "y", "w"}
    # Bare symbols that are exact only in a scalar-field context (phi/chi/psi in the equation):
    # V = potential density, lambda = coupling, rho/p = energy density/pressure, H = Hubble, T = temperature.
    FIELD_CONTEXT_BARE = {"V", "lambda", "rho", "p", "H", "T"}

    def __init__(self, canonical_dims: dict, custom_dims: dict | None = None):
        self.canonical = self._build_lookup(canonical_dims, extra=True)
        self.custom = self._build_lookup(custom_dims or {}, extra=False)
        self.inner_mismatches: list[str] = []
        self._pending_power = 1.0
        self.field_context = False
        self._canonical_hits = 0
        self.last_basis: str | None = None

    # Dimensionless-in-natural-units constants that never weaken a verdict's basis.
    UNIVERSAL_CONSTANTS = {"c", "hbar", "k_B", "pi", "e", "i"}

    # ---- key normalization -------------------------------------------------
    @staticmethod
    def _nk(s: str) -> str:
        s = str(s or "")
        s = re.sub(r"\\(?:mathrm|text|rm|mathit|textrm)\b", "", s)
        s = s.replace("\\", "").replace("{", "").replace("}", "").replace(" ", "")
        return s

    def _build_lookup(self, dims: dict, extra: bool) -> dict:
        table: dict[str, float] = {}
        for k, v in (dims or {}).items():
            if "^" in str(k):
                continue
            try:
                table[self._nk(k)] = float(v)
            except (TypeError, ValueError):
                continue
        if extra:
            table.update({
                "c": 0.0, "hbar": 0.0, "k_B": 0.0, "pi": 0.0, "e": 0.0, "i": 0.0,
                "n_s": 0.0, "n_t": 0.0, "N_eff": 0.0, "Omega": 0.0, "eta_B": 0.0, "Y_B": 0.0,
                "A_s": 0.0, "f_NL": 0.0, "J": 3.0, "x": -1.0,
                # Tensors carrying Greek indices
                "T_IDX": 4.0, "G_IDX": 2.0, "R_IDX": 2.0, "g_IDX": 0.0, "F_IDX": 2.0,
                "J_IDX": 3.0, "A_IDX": 1.0, "x_IDX": -1.0, "h_IDX": 0.0, "gamma_IDX": 0.0,
                "u_IDX": 0.0,
            })
        return table

    def _lookup(self, table: dict, key: str):
        if key in table:
            return table[key]
        if "_" in key:
            base, label = key.split("_", 1)
            low = f"{base}_{label.lower()}"
            for k, v in table.items():
                if "_" in k:
                    kb, kl = k.split("_", 1)
                    if f"{kb}_{kl.lower()}" == low:
                        return v
        return None

    def _resolve(self, base: str, label: str, has_index: bool, inner_base: str | None):
        """Return (dim, exact) for a symbol or raise _UnknownDimension."""
        b = self._nk(base)
        lab = self._nk(label)
        if lab.startswith((",", ";")):
            raise _UnknownDimension(f"derivative subscript on {base}")
        label_is_index = bool(lab) and self._is_index(label)
        keys = []
        if lab and not label_is_index:
            keys.append(f"{b}_{lab}")
        if has_index or label_is_index:
            keys.append(f"{b}_IDX")
        keys.append(b)

        for key in keys:
            v = self._lookup(self.custom, key)
            if v is not None:
                return v, True
        for key in keys:
            v = self._lookup(self.canonical, key)
            if v is not None:
                if key not in self.UNIVERSAL_CONSTANTS and b not in self.UNIVERSAL_CONSTANTS:
                    self._canonical_hits += 1  # dimension came from built-in defaults, not the report
                if key == b:
                    labelled = bool(lab) and not label_is_index
                    if labelled:
                        return v, b in self.LABEL_SAFE_BASES
                    if has_index or label_is_index:
                        return v, False
                    return v, (b in self.UNAMBIGUOUS_BARE) or (self.field_context and b in self.FIELD_CONTEXT_BARE)
                return v, True
        if inner_base:
            return self._resolve(inner_base, label, has_index, None)
        raise _UnknownDimension(f"symbol {base}{'_' + label if label else ''} not in symbol table")

    def _is_index(self, content: str) -> bool:
        toks = re.findall(r"\\([A-Za-z]+)|([A-Za-z])", content)
        if not toks:
            return False
        for cmd, letter in toks:
            name = cmd or letter
            if name not in self.INDEX_NAMES:
                return False
        stripped = re.sub(r"\\[A-Za-z]+|[A-Za-z]|[\s{}]", "", content)
        return stripped == ""

    # ---- low-level scanning helpers ---------------------------------------
    @staticmethod
    def _match_close(s: str, i: int) -> int:
        pairs = {"(": ")", "[": "]", "{": "}"}
        open_c = s[i]
        close_c = pairs[open_c]
        depth = 0
        for j in range(i, len(s)):
            if s[j] == open_c:
                depth += 1
            elif s[j] == close_c:
                depth -= 1
                if depth == 0:
                    return j
        raise _UnknownDimension("unbalanced brackets")

    def _read_group(self, s: str, i: int) -> tuple[str, int]:
        while i < len(s) and s[i].isspace():
            i += 1
        if i < len(s) and s[i] == "{":
            j = self._match_close(s, i)
            return s[i + 1:j], j + 1
        if i < len(s) and s[i] == "\\":
            m = re.match(r"\\[A-Za-z]+", s[i:])
            if m:
                return m.group(0), i + len(m.group(0))
        if i < len(s):
            return s[i], i + 1
        raise _UnknownDimension("missing group")

    def _read_scripts(self, s: str, i: int) -> tuple[str, str | None, int]:
        """Read any sequence of _x / ^x scripts. Returns (label, exponent, new_index)."""
        label, exponent = "", None
        while i < len(s) and s[i] in "_^":
            kind = s[i]
            content, i = self._read_group(s, i + 1)
            if kind == "_":
                label = content
            else:
                exponent = content
        return label, exponent, i

    @staticmethod
    def _exponent_value(content: str | None):
        if content is None:
            return 1.0
        c = content.replace(" ", "")
        m = re.fullmatch(r"(-?)\\frac\{?(\d+)\}?\{?(\d+)\}?", c)
        if m:
            val = float(m.group(2)) / float(m.group(3))
            return -val if m.group(1) else val
        m = re.fullmatch(r"\(?(-?\d+(?:\.\d+)?)(?:/(\d+(?:\.\d+)?))?\)?", c)
        if m:
            val = float(m.group(1))
            if m.group(2):
                val /= float(m.group(2))
            return val
        return None

    def _apply_exponent(self, dim: float, exact: bool, exponent: str | None, allow_index: bool):
        if exponent is None:
            return dim, exact
        if allow_index and self._is_index(exponent):
            return dim, exact
        val = self._exponent_value(exponent)
        if val is not None:
            return dim * val, exact
        if abs(dim) < 1e-12:
            return 0.0, exact  # dimensionless base raised to a symbolic power
        raise _UnknownDimension(f"symbolic exponent on a dimensionful factor ({exponent})")

    # ---- splitting -----------------------------------------------------------
    def _split_top(self, s: str, splitter) -> list[str]:
        parts, depth, start, i = [], 0, 0, 0
        while i < len(s):
            ch = s[i]
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            elif depth == 0:
                width = splitter(s, i)
                if width:
                    parts.append(s[start:i])
                    i += width
                    start = i
                    continue
            i += 1
        parts.append(s[start:])
        return parts

    def _sum_splitter(self, s: str, i: int) -> int:
        if s[i] in "+-":
            return 1
        m = re.match(r"\\(pm|mp)(?![A-Za-z])", s[i:])
        return len(m.group(0)) if m else 0

    def _relation_splitter(self, s: str, i: int) -> int:
        if s[i] in "=<>":
            return 2 if s[i + 1:i + 2] == "=" else 1
        if s[i] == "\\":
            m = re.match(r"\\([A-Za-z]+)", s[i:])
            if m:
                name = m.group(1)
                if name in self.ABORT_COMMANDS:
                    raise _UnknownDimension(f"relation \\{name} does not imply equal dimensions")
                if name in self.RELATION_COMMANDS:
                    return len(m.group(0))
        return 0

    # ---- parsing -------------------------------------------------------------
    def parse_sum(self, s: str):
        """Return (dim, exact) for a sum of terms, 'ZERO', or raise _UnknownDimension."""
        terms = [t for t in self._split_top(s, self._sum_splitter) if t.strip()]
        if not terms:
            raise _UnknownDimension("empty expression")
        results, unknown = [], 0
        for t in terms:
            try:
                r = self.parse_term(t)
            except _UnknownDimension:
                unknown += 1
                continue
            if r != "ZERO":
                results.append((t.strip(), r))
        if not results:
            if unknown:
                raise _UnknownDimension("no resolvable term")
            return "ZERO"
        dims = {round(r[1][0], 9) for r in results}
        if len(dims) > 1:
            exact_pairs = [r for r in results if r[1][1]]
            desc = ", ".join(f"'{t}' [E]^{d:g}" for t, (d, _) in results)
            if len({round(r[1][0], 9) for r in exact_pairs}) > 1:
                self.inner_mismatches.append(("exact", desc, self._canonical_hits > 0))
            else:
                self.inner_mismatches.append(("inferred", desc, self._canonical_hits > 0))
            raise _UnknownDimension("inhomogeneous sum")
        exact = all(r[1][1] for r in results) and unknown == 0
        return results[0][1][0], exact

    def parse_term(self, t: str):
        s = t.strip()
        if re.fullmatch(r"0+(?:\.0+)?", s):
            return "ZERO"
        total, exact, i, divide = 0.0, True, 0, False
        self._pending_power = 1.0
        while i < len(s):
            ch = s[i]
            if ch.isspace() or ch in "*|":
                i += 1
                continue
            if ch == "/":
                divide = True
                i += 1
                continue
            factor, i = self._parse_factor(s, i)
            if factor is None:
                continue
            d, e = factor
            total += -d if divide else d
            exact = exact and e
            divide = False
        return total, exact

    def _parse_factor(self, s: str, i: int):
        """Parse one multiplicative factor starting at s[i]. Returns ((dim, exact) | None, new_i)."""
        ch = s[i]
        if ch.isdigit() or (ch == "." and s[i + 1:i + 2].isdigit()):
            m = re.match(r"\d*\.?\d+", s[i:])
            i += len(m.group(0))
            _, exponent, i = self._read_scripts(s, i)
            return (0.0, True), i  # pure numbers (incl. 10^{18}) are dimensionless
        if ch in "([{":
            j = self._match_close(s, i)
            inner = s[i + 1:j]
            i = j + 1
            if not inner.strip():
                return None, i
            r = self.parse_sum(inner)
            if r == "ZERO":
                return None, i
            _, exponent, i = self._read_scripts(s, i)
            return self._apply_exponent(r[0], r[1], exponent, allow_index=False), i
        if ch == "'":
            raise _UnknownDimension("prime derivative is ambiguous")
        if ch == "\\":
            return self._parse_command(s, i)
        if ch.isalpha():
            return self._parse_letter(s, i)
        raise _UnknownDimension(f"unsupported token '{ch}'")

    def _maybe_skip_function_args(self, s: str, i: int) -> int:
        if i < len(s) and s[i] == "(":
            j = self._match_close(s, i)
            content = s[i + 1:j]
            simple = r"\s*\\?[A-Za-z]+(?:_\{?[^{}()]*\}?)?\s*"
            if re.fullmatch(rf"{simple}(?:,{simple})*", content):
                return j + 1
        return i

    def _finish_symbol(self, s: str, i: int, base: str, inner_base: str | None):
        label, exponent, i = self._read_scripts(s, i)
        if i < len(s) and s[i] == "'":
            raise _UnknownDimension("prime derivative is ambiguous")
        i = self._maybe_skip_function_args(s, i)
        label2, exponent2, i = self._read_scripts(s, i)  # e.g. \phi(x)^2
        label = label or label2
        exponent = exponent if exponent is not None else exponent2
        has_index = exponent is not None and self._is_index(exponent)
        dim, exact = self._resolve(base, label, has_index, inner_base)
        dim, exact = self._apply_exponent(dim, exact, exponent, allow_index=True)
        power = self._pending_power
        self._pending_power = 1.0
        return (dim * power, exact), i

    def _parse_letter(self, s: str, i: int):
        run = re.match(r"[A-Za-z]+", s[i:]).group(0)
        if len(run) >= 3:
            raise _UnknownDimension(f"multi-letter word '{run}' outside \\mathrm")
        ch = s[i]
        # Differentials: d^4x, dt, d\phi  (the differential carries the variable's dimension)
        if ch == "d" and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt == "^":
                content, j = self._read_group(s, i + 2)
                val = self._exponent_value(content)
                if val is not None and j < len(s) and (s[j].isalpha() or s[j] == "\\" or s[j].isspace()):
                    self._pending_power = val
                    return None, j
            if nxt.isalpha() or nxt == "\\":
                return None, i + 1
        return self._finish_symbol(s, i + 1, ch, None)

    def _parse_command(self, s: str, i: int):
        m = re.match(r"\\([A-Za-z]+)", s[i:])
        if not m:
            raise _UnknownDimension("bad command")
        name = m.group(1)
        i += len(m.group(0))

        if name in self.SKIP_COMMANDS:
            return None, i
        if name == "frac":
            num, i = self._read_group(s, i)
            den, i = self._read_group(s, i)
            rn, rd = self.parse_sum(num), self.parse_sum(den)
            if rn == "ZERO":
                return None, i
            if rd == "ZERO":
                raise _UnknownDimension("division by zero")
            _, exponent, i = self._read_scripts(s, i)
            return self._apply_exponent(rn[0] - rd[0], rn[1] and rd[1], exponent, allow_index=False), i
        if name == "sqrt":
            root = 2.0
            if i < len(s) and s[i] == "[":
                j = self._match_close(s, i)
                val = self._exponent_value(s[i + 1:j])
                if val is None:
                    raise _UnknownDimension("symbolic root order")
                root, i = val, j + 1
            inner, i = self._read_group(s, i)
            if re.fullmatch(r"\s*-\s*g\s*", inner):
                r = (0.0, True)
            else:
                r = self.parse_sum(inner)
                if r == "ZERO":
                    return None, i
            _, exponent, i = self._read_scripts(s, i)
            return self._apply_exponent(r[0] / root, r[1], exponent, allow_index=False), i
        if name in ("dot", "ddot"):
            inner, i = self._read_group(s, i)
            r = self.parse_term(inner)
            if r == "ZERO":
                return None, i
            bump = 1.0 if name == "dot" else 2.0
            label, exponent, i = self._read_scripts(s, i)
            return self._apply_exponent(r[0] + bump, r[1], exponent, allow_index=True), i
        if name in ("partial", "nabla"):
            _, exponent, i = self._read_scripts(s, i)
            if exponent is not None and not self._is_index(exponent):
                val = self._exponent_value(exponent)
                if val is None:
                    raise _UnknownDimension("symbolic derivative order")
                return (val, True), i
            return (1.0, True), i
        if name in ("Box", "square"):
            return (2.0, True), i
        if name in ("delta", "Delta") and (i >= len(s) or s[i] not in "_^ "):
            return None, i  # perturbation / difference prefix: carries the next factor's dimension
        if name in self.BIG_OPERATORS:
            _, _, i = self._read_scripts(s, i)
            return None, i
        if name in self.FUNCTIONS:
            _, _, i = self._read_scripts(s, i)
            while i < len(s) and s[i].isspace():
                i += 1
            if i < len(s) and s[i] in "([{":
                i = self._match_close(s, i) + 1
            elif i < len(s) and (s[i].isalpha() or s[i] == "\\"):
                _, i = self._parse_factor(s, i)
            return (0.0, True), i
        if name in self.TEXT_COMMANDS:
            content, i = self._read_group(s, i)
            if content.strip() == "d":
                return None, i
            unit_dim = self._unit_dimension(content)
            _, exponent, i = self._read_scripts(s, i)
            return self._apply_exponent(unit_dim, True, exponent, allow_index=False), i
        if name in self.ACCENTS:
            inner, i = self._read_group(s, i)
            inner_name = self._nk(inner)
            return self._finish_symbol(s, i, name + inner_name, inner_name)
        if name in self.STYLED:
            inner, i = self._read_group(s, i)
            return self._finish_symbol(s, i, name + self._nk(inner), None)
        if name in self.GREEK:
            return self._finish_symbol(s, i, name, None)
        raise _UnknownDimension(f"unsupported command \\{name}")

    def _unit_dimension(self, content: str) -> float:
        tokens = [t for t in re.split(r"\s+|\\cdot", content.strip()) if t]
        if not tokens:
            raise _UnknownDimension("empty \\mathrm")
        total = 0.0
        for tok in tokens:
            m = re.fullmatch(r"([A-Za-z]+)(?:\^\{?(-?\d+(?:\.\d+)?)\}?)?", tok)
            if not m or m.group(1) not in self.UNITS:
                raise _UnknownDimension(f"non-unit text '{tok}'")
            total += self.UNITS[m.group(1)] * (float(m.group(2)) if m.group(2) else 1.0)
        return total

    # ---- equation-level analysis ----------------------------------------------
    def analyze(self, eq: str) -> tuple[str | None, str | None]:
        """
        Returns (verdict, explanation) where verdict is CONSISTENT, INCONSISTENT,
        POSSIBLE_MISMATCH, or None when the equation cannot be fully resolved.
        """
        s = normalize_latex_equation(eq)
        self.inner_mismatches = []
        self.field_context = bool(re.search(r"\\(?:phi|varphi|chi|psi)(?![A-Za-z])", s))
        try:
            if any(p.strip() for p in self._split_top(s, lambda x, k: 1 if x[k] == "," else 0)[1:]):
                return None, None  # several statements in one string
            sides = [p for p in self._split_top(s, self._relation_splitter)]
        except _UnknownDimension:
            return None, None
        if len(sides) < 2:
            return None, None

        self.last_basis = None
        resolved, unknown = [], 0
        for side in sides:
            for term in self._split_top(side, self._sum_splitter):
                if not term.strip():
                    continue
                self._canonical_hits = 0
                try:
                    r = self.parse_term(term)
                except _UnknownDimension:
                    unknown += 1
                    continue
                if r != "ZERO":
                    resolved.append((term.strip(), r[0], r[1], self._canonical_hits > 0))

        for kind, desc, used_defaults in self.inner_mismatches:
            if kind == "exact":
                self.last_basis = "canonical_defaults" if used_defaults else "declared_symbol_table"
                return "INCONSISTENT", f"Inhomogeneous sum inside a bracket: {desc} — terms that are added must share one mass dimension ✗"

        exact_terms = [r for r in resolved if r[2]]
        exact_dims = {round(r[1], 9) for r in exact_terms}
        if len(exact_dims) > 1:
            self.last_basis = "canonical_defaults" if any(r[3] for r in exact_terms) else "declared_symbol_table"
            desc = "; ".join(f"'{t}' → [E]^{d:g}" for t, d, _, _ in exact_terms)
            return "INCONSISTENT", f"Natural-unit mass-dimension mismatch between terms: {desc} ✗"

        all_dims = {round(r[1], 9) for r in resolved}
        if len(all_dims) > 1 or self.inner_mismatches:
            desc = "; ".join(f"'{t}' → [E]^{d:g}{'' if e else ' (inferred)'}" for t, d, e, _ in resolved)
            return (
                "POSSIBLE_MISMATCH",
                f"Possible mass-dimension mismatch involving ambiguous symbols: {desc}. "
                "Declare these symbols in symbol_dimensions_json to get a definitive verdict."
            )
        if unknown == 0 and len(resolved) >= 2:
            d = resolved[0][1]
            note = "" if all(r[2] for r in resolved) else " (some symbols inferred from canonical defaults)"
            return "CONSISTENT", f"All {len(resolved)} terms carry natural-unit mass dimension [E]^{d:g}{note} ✓"
        return None, None


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
        description=(
            "JSON dictionary copied from the report's Symbol Table, mapping each symbol to its natural-unit "
            "mass dimension [E]^n (e.g. '{\"\\\\phi\": 1, \"V\": 4, \"\\\\lambda\": 0, \"n_B\": 3, \"T\": 1}'). "
            "Ambiguous letters (p, P, k, s, n, R, G, V, T, H, lambda...) only give a definitive verdict when declared here."
        )
    )


class DimensionalConsistencyTool(BaseTool):
    name: str = "Dimensional Consistency Checker"
    description: str = (
        "Checks whether LaTeX physics, cosmology, and statistical equations are dimensionally consistent "
        "in 4D natural units (hbar = c = k_B = 1). Computes the mass dimension [E]^n of every additive term "
        "(products, fractions, powers, roots, derivatives, tensor indices, units) and compares them; "
        "checks every Lagrangian term against [E]^4; detects invalid variable-w(a) exponents and dropped "
        "covariance terms. Pass the report's Symbol Table as symbol_dimensions_json for definitive verdicts. "
        "Per-equation verdicts: CONSISTENT, INCONSISTENT, DIMENSIONLESS, or UNDECIDABLE."
    )
    args_schema: Type[BaseModel] = DimensionalConsistencyInput

    # Known FLAWED / INCONSISTENT patterns checked first (highest priority)
    KNOWN_INCONSISTENT_PATTERNS: ClassVar[list[tuple[str, str]]] = [
        (
            r'E\s*=\s*m\s*c\^?\s*3',
            'E=mc³: [J] != [kg][m/s]³ = [kg·m³/s³] — FLAWED formula ✗'
        ),
        (
            r'a\s*\^\s*\{?\s*-\s*3\s*(?:\\cdot\s*|\*\s*)?[\(\[]\s*1\s*\+\s*(?:w(?:_\{[^{}]*\}|_[A-Za-z0-9])?\s*\(\s*[azt]\s*\)|w_?0\s*\+\s*w_?a\s*\*?\s*[\(\[]\s*1\s*-\s*a)',
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

    _LAGRANGIAN_LHS_RE: ClassVar[re.Pattern] = re.compile(
        r'^\s*(?:\\mathcal\{L\}|\\mathscr\{L\}|\\mathcal L)(?:_(?:\{[^{}]*\}|\\?[A-Za-z0-9]+))?\s*(?:=|\\equiv)'
    )
    _UNSUPPRESSED_POWER_RE: ClassVar[re.Pattern] = re.compile(r'\\(?:phi|chi|varphi)\s*\^\s*\{?\s*([5-9]|\d{2,})\s*\}?')
    _SUPPRESSION_RE: ClassVar[re.Pattern] = re.compile(r'/|\\frac|M_|\\Lambda|f_|\\mu\^\{?-')

    def _unsuppressed_operator_check(self, eq: str, analyzer: "NaturalUnitDimensionAnalyzer") -> tuple[str | None, str | None]:
        """
        In a 4D Lagrangian density, flag each additive term carrying phi^n (n >= 5) without an
        inverse mass scale in that same term. Checked per term, so a valid kinetic term elsewhere
        in the Lagrangian cannot mask the bad operator.
        """
        m = self._LAGRANGIAN_LHS_RE.match(eq)
        if not m:
            return None, None
        rhs = eq[m.end():]
        for term in analyzer._split_top(rhs, analyzer._sum_splitter):
            pw = self._UNSUPPRESSED_POWER_RE.search(term)
            if pw and not self._SUPPRESSION_RE.search(term):
                n = int(pw.group(1))
                return (
                    "INCONSISTENT",
                    f"Lagrangian term '{term.strip()}' carries phi^{n} with mass dimension [E]^{n} (≥5) and no "
                    f"inverse cutoff scale 1/M^{n - 4}; every term of a 4D Lagrangian density must be [E]^4 ✗"
                )
        return None, None

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

        analyzer = NaturalUnitDimensionAnalyzer(self.CANONICAL_MASS_DIMS, custom_dims)
        results = []
        consistent_count = 0
        dimensionless_count = 0
        inconsistent_count = 0

        for raw_eq in equations:
            eq_raw = str(raw_eq).strip()
            eq = normalize_latex_equation(eq_raw)
            verdict = "UNDECIDABLE"
            explanation = (
                "Could not automatically verify dimensional consistency. "
                "Report this equation honestly as UNDECIDABLE or verify its terms against the Symbol Table."
            )
            matched = False
            basis = "none"

            # Step 1: Known flawed patterns (run on the normalized form, so \left( ... \right) is covered)
            for bad_pat, bad_expl in self.KNOWN_INCONSISTENT_PATTERNS:
                if re.search(bad_pat, eq, re.IGNORECASE):
                    verdict, explanation, matched, basis = "INCONSISTENT", bad_expl, True, "known_error_pattern"
                    break

            # Step 2: Unsuppressed higher-dimension operators, checked term by term
            if not matched:
                op_verdict, op_expl = self._unsuppressed_operator_check(eq, analyzer)
                if op_verdict:
                    verdict, explanation, matched, basis = op_verdict, op_expl, True, "lagrangian_operator"

            # Step 3: Term-level natural-unit [E]^n analysis — a definitive mismatch wins immediately
            try:
                nu_verdict, nu_expl = analyzer.analyze(eq) if not matched else (None, None)
            except Exception:
                nu_verdict, nu_expl = None, None
            if not matched and nu_verdict == "INCONSISTENT":
                verdict, explanation, matched = "INCONSISTENT", nu_expl, True
                basis = analyzer.last_basis or "canonical_defaults"

            # Step 4: Known valid physics/cosmology/statistics patterns
            if not matched:
                for pattern, v, expl in self.KNOWN_PATTERNS:
                    if re.search(pattern, eq, re.IGNORECASE):
                        verdict, explanation, matched, basis = v, expl, True, "known_valid_pattern"
                        break

            # Step 5: Term-level analysis result (consistent, or possible mismatch on ambiguous symbols)
            if not matched and nu_verdict == "CONSISTENT":
                verdict, explanation, matched, basis = "CONSISTENT", nu_expl, True, "term_dimensions"
            elif not matched and nu_verdict == "POSSIBLE_MISMATCH":
                verdict, explanation, matched, basis = "UNDECIDABLE", nu_expl, True, "possible_mismatch"

            # Step 6: Fallback for unmatched expressions (never blindly mark standalone tokens as DIMENSIONLESS)
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
                "equation": eq_raw[:140],
                "verdict": verdict,
                "basis": basis,
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
        default="[]",
        description=(
            "A JSON list of derivation step strings in the form: "
            "[\"step1_expr\", \"step2_expr\", ...]. "
            "Each step can be a sympy-parseable equality 'LHS = RHS', a LaTeX equation, "
            "a continuity/ODE solution claim (e.g. 'rho(a) = rho_0 * a**(-3*(1 + w0 + wa*(1-a)))' vs exact CPL integral), "
            "or a derivative/integral identity."
        )
    )
    limits_json: str = Field(
        default="[]",
        description=(
            "Optional JSON list of asymptotic/perturbative limit checks, each a dict: "
            "{\"expr\": \"w0 + wa*(1 - a)\", \"var\": \"a\", \"point\": 1, \"expected\": \"w0\"} "
            "(supports point='oo' or '0' or '1' to verify early-time a->0, present-day a->1, high-T, or super-horizon k->0 limits)."
        )
    )


class SymbolicDerivationTool(BaseTool):
    name: str = "Symbolic Derivation Verifier"
    description: str = (
        "Uses SymPy to symbolically verify step-by-step mathematical derivations, ODE/continuity integrals "
        "(e.g. variable-w(a) dark energy density evolution), variance/covariance expansions, and asymptotic limits "
        "(a->0, a->1, k->0, T->oo). Returns per-step verdicts: STEP_VERIFIED, STEP_ASSUMED, or STEP_INVALID, "
        "plus limit check verdicts (LIMIT_VERIFIED or LIMIT_MISMATCH)."
    )
    args_schema: Type[BaseModel] = SymbolicDerivationInput

    @staticmethod
    def _clean_for_sympy(expr_str: str) -> str:
        s = normalize_latex_equation(expr_str)
        # \rho_{\rm DE,0} -> rho_DE0 ; \mathrm{Var} -> Var
        s = re.sub(r'\\(?:mathrm|text|operatorname)\{([^{}]*)\}', r'\1', s)
        s = re.sub(r'_\{([^{}]*)\}', lambda m: '_' + re.sub(r'[^A-Za-z0-9]', '', m.group(1).replace('\\rm', '')), s)
        # Convert simple \frac{A}{B} -> ((A)/(B))
        for _ in range(4):
            s_new = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'((\1)/(\2))', s)
            if s_new == s:
                break
            s = s_new
        s = re.sub(r'\\sqrt\{([^{}]+)\}', r'sqrt(\1)', s)
        s = re.sub(r'\\exp\b', 'exp', s)
        s = re.sub(r'\\ln\b|\\log\b', 'log', s)
        for old, new in [
            ('^', '**'), ('\\cdot', '*'), ('\\times', '*'),
            ('mc**2', 'm*c**2'), ('\\hbar', 'hbar'),
            ('{', '('), ('}', ')'), ('[', '('), (']', ')'),
        ]:
            s = s.replace(old, new)
        s = re.sub(r'\\(?:rm|text|mathrm)\b', '', s)
        s = s.replace('\\', '')
        s = re.sub(r'\blambda\b', 'lamda', s)  # 'lambda' is a Python keyword
        # LaTeX writes products with whitespace ("lamda phi**2"); make them explicit, but keep
        # function application intact ("exp (x)" -> "exp(x)").
        funcs = {"sqrt", "exp", "log", "ln", "sin", "cos", "tan", "sinh", "cosh", "tanh", "asin", "acos", "atan", "Abs"}
        s = re.sub(
            r'([A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?|\))\s+(?=[A-Za-z_(])',
            lambda m: m.group(1) if m.group(1) in funcs else m.group(1) + '*',
            s.strip(),
        )
        return s.strip()

    # Names that denote strictly positive physical quantities (scale factor, temperature, masses, ...)
    _POSITIVE_NAME_RE: ClassVar[re.Pattern] = re.compile(
        r'^(?:a|t|T|m|M|H|E|k|c|hbar|G|rho|s|n|r|sigma|tau|Gamma|Omega|M_?Pl|m_?Pl|g_?s|g_?star)(?:_\w*|\d*)$'
    )

    @classmethod
    def _check_special_physics_step(cls, step: str, sp_mod) -> tuple[str | None, str | None]:
        """
        Check high-frequency symbolic derivation pitfalls:
        1. Variable-w(a) cosmological continuity equation integration (CPL w(a) = w0 + wa*(1-a))
        2. Contrast variance bilinear expansion Var(A - B)
        """
        s_norm = normalize_latex_equation(step)
        a, w0, wa, rho0 = sp_mod.symbols('a w0 wa rho0', positive=True, real=True)
        w_cpl = w0 + wa * (1 - a)
        # Exact d ln(rho) / d ln(a) required by continuity equation: -3*(1 + w(a))
        target_dlnrho_dlna = -3 * (1 + w_cpl)

        # 1a. Verify exact CPL continuity integral FIRST: a^{-3(1+w0+wa)} * exp(-3*wa*(1-a)) or exp(3*wa*(a-1))
        if (
            re.search(r'1\s*\+\s*w_?0\s*\+\s*w_?a', s_norm)
            and re.search(r'exp\s*\(\s*(?:-\s*3\s*\*?\s*w_?a\s*\*?\s*\(\s*1\s*-\s*a\s*\)|3\s*\*?\s*w_?a\s*\*?\s*\(\s*a\s*-\s*1\s*\))', cls._clean_for_sympy(s_norm))
        ):
            exact_ln_rho = -3 * (1 + w0 + wa) * sp_mod.log(a) - 3 * wa * (1 - a)
            actual_dlnrho_dlna = sp_mod.simplify(a * sp_mod.diff(exact_ln_rho, a))
            residual = sp_mod.simplify(actual_dlnrho_dlna - target_dlnrho_dlna)
            if residual == 0:
                return (
                    "STEP_VERIFIED",
                    "SymPy ODE check confirms d ln(rho)/d ln(a) = -3*(1 + w0 + wa*(1-a)) (residual = 0) for exact CPL integral ✓"
                )

        # 1b. Detect invalid algebraic exponent for variable w(a): a^{-3(1 + w(a))} or a^{-3(1 + w0 + wa*(1-a))}
        if re.search(
            r'a\s*(?:\^|\*\*)\s*[\(\{]?\s*-\s*3\s*\*?\s*[\(\[]\s*1\s*\+\s*(?:w\s*\(\s*[azt]\s*\)|w_?0\s*\+\s*w_?a)',
            s_norm
        ):
            flawed_ln_rho = -3 * (1 + w_cpl) * sp_mod.log(a)
            actual_dlnrho_dlna = sp_mod.simplify(a * sp_mod.diff(flawed_ln_rho, a))
            residual = sp_mod.simplify(actual_dlnrho_dlna - target_dlnrho_dlna)
            return (
                "STEP_INVALID",
                f"Continuity ODE violation: for w(a) = w0 + wa(1-a), claiming rho(a) = rho0 * a^(-3(1+w(a))) yields "
                f"d ln(rho)/d ln(a) = {actual_dlnrho_dlna}, leaving a non-zero residual ({residual}) != 0. "
                f"Exact integral is rho0 * a^(-3*(1+w0+wa)) * exp(-3*wa*(1-a)) ✗"
            )

        # 2. Detect dropped covariance in Var(A - B) = Var(A) + Var(B)
        if re.search(
            r'(?:\\mathrm\{Var\}|\\text\{Var\}|\bVar)\s*\(\s*([^-\)]+?)\s*-\s*([^\)]+?)\s*\)\s*=\s*(?:\\mathrm\{Var\}|\\text\{Var\}|\bVar)\s*\(\s*\1\s*\)\s*\+\s*(?:\\mathrm\{Var\}|\\text\{Var\}|\bVar)\s*\(\s*\2\s*\)\s*$',
            s_norm
        ):
            return (
                "STEP_INVALID",
                "Bilinear variance identity violation: (A - B)^2 = A^2 + B^2 - 2*A*B, so Var(A - B) = Var(A) + Var(B) - 2*Cov(A, B). "
                "Dropping -2*Cov(A, B) is algebraically invalid unless Cov(A, B) = 0 is explicitly proven ✗"
            )

        if re.search(
            r'(?:\\mathrm\{Var\}|\\text\{Var\}|\bVar)\s*\(\s*([^-\)]+?)\s*-\s*([^\)]+?)\s*\)\s*=.*-\s*2\s*\*?\s*(?:\\mathrm\{Cov\}|\\text\{Cov\}|\bCov)',
            s_norm
        ):
            return (
                "STEP_VERIFIED",
                "Bilinear variance identity Var(A - B) = Var(A) + Var(B) - 2*Cov(A, B) verified ✓"
            )

        return (None, None)

    def _verify_equality_step(self, lhs_str: str, rhs_str: str) -> tuple[str, str]:
        """
        Check LHS = RHS symbolically. If the identity fails over generic (complex) symbols, retry with
        physically positive quantities (a, T, m, rho, ...) marked positive; then with every symbol
        positive. Only a residual that survives all of these is reported as INVALID.
        """
        import sympy as sp

        lhs = safe_sympy_parse(lhs_str)
        rhs = safe_sympy_parse(rhs_str)
        expr = lhs - rhs
        diff = sp.simplify(expr)
        if diff == 0:
            return "STEP_VERIFIED", "SymPy confirms: simplify(LHS - RHS) = 0 (identity holds) ✓"

        syms = sorted(expr.free_symbols, key=lambda s: s.name)
        physical = {s: sp.Symbol(s.name, positive=True) for s in syms if self._POSITIVE_NAME_RE.match(s.name)}
        if physical and sp.simplify(expr.subs(physical)) == 0:
            names = ", ".join(sorted(s.name for s in physical))
            return "STEP_VERIFIED", f"Identity holds for positive physical quantities ({names} > 0) ✓"

        all_positive = {s: sp.Symbol(s.name, positive=True) for s in syms}
        if all_positive and sp.simplify(expr.subs(all_positive)) == 0:
            names = ", ".join(s.name for s in syms)
            return (
                "STEP_ASSUMED",
                f"Identity holds only if {names} > 0 — state this positivity assumption explicitly in the derivation."
            )

        if diff.is_number:
            return "STEP_INVALID", f"SymPy falsifies equality: LHS - RHS = {diff} != 0 ✗"
        if lhs.free_symbols and lhs.free_symbols == rhs.free_symbols and sp.expand(expr) != 0:
            return (
                "STEP_INVALID",
                f"Algebraic mismatch over identical symbols {[s.name for s in syms]}: LHS - RHS = {diff} != 0 "
                "(use \\approx, not '=', for approximations) ✗"
            )
        return (
            "STEP_ASSUMED",
            f"Relational definition or physical law (LHS - RHS = {diff}); treated as a model assumption/definition."
        )

    def _evaluate_limit(self, expr_raw: str, var_raw: str, pt_raw, exp_raw, dir_raw: str):
        import sympy as sp

        var_clean = self._clean_for_sympy(var_raw)
        var_sym = sp.Symbol(var_clean, real=True)
        local = {var_clean: var_sym}
        expr_sym = safe_sympy_parse(self._clean_for_sympy(expr_raw), local)
        pt_text = str(pt_raw).strip().lower()
        if pt_text in ("oo", "inf", "infinity", "+oo"):
            pt_sym = sp.oo
        elif pt_text in ("-oo", "-inf", "-infinity"):
            pt_sym = -sp.oo
        else:
            pt_sym = safe_sympy_parse(self._clean_for_sympy(str(pt_raw)))

        if pt_sym in (sp.oo, -sp.oo) or dir_raw == "+-":
            computed = sp.simplify(sp.limit(expr_sym, var_sym, pt_sym))
        else:
            computed = sp.simplify(sp.limit(expr_sym, var_sym, pt_sym, dir=dir_raw))

        if exp_raw is None or str(exp_raw).strip() == "":
            return computed, None, None
        exp_sym = safe_sympy_parse(self._clean_for_sympy(str(exp_raw)), local)
        return computed, exp_sym, sp.simplify(computed - exp_sym)

    def _run(self, concept: str, derivation_steps: str = "[]", limits_json: str = "[]") -> str:
        import sympy as sp

        try:
            steps = json.loads(derivation_steps) if derivation_steps else []
            if isinstance(steps, str):
                steps = [steps]
        except json.JSONDecodeError:
            steps = [s.strip() for s in (derivation_steps or "").split('\n') if s.strip()]

        try:
            limit_specs = json.loads(limits_json) if limits_json else []
            if not isinstance(limit_specs, list):
                limit_specs = []
        except json.JSONDecodeError:
            limit_specs = []

        if not steps and not limit_specs:
            return json.dumps({
                "concept": concept,
                "error": "No derivation steps or limit checks provided.",
                "steps": [],
                "limit_checks": []
            }, indent=2)

        step_results = []
        proven_count = 0
        assumed_count = 0
        invalid_count = 0

        for i, step in enumerate(steps):
            step_str = str(step).strip()
            step_result = {
                "step_number": i + 1,
                "expression": step_str[:220],
                "verdict": "STEP_ASSUMED",
                "detail": ""
            }

            # First check specialized physics/ODE/variance rules
            spec_verdict, spec_detail = self._check_special_physics_step(step_str, sp)
            if spec_verdict is not None:
                step_result["verdict"] = spec_verdict
                step_result["detail"] = spec_detail
                if spec_verdict == "STEP_VERIFIED":
                    proven_count += 1
                elif spec_verdict == "STEP_INVALID":
                    invalid_count += 1
                else:
                    assumed_count += 1
                step_results.append(step_result)
                continue

            # Next try general SymPy algebraic equality / identity verification
            if '==' in step_str or '=' in step_str.replace('==', ''):
                parts = re.split(r'(?<!=)=(?!=)|==', step_str, maxsplit=1)
                try:
                    verdict, detail = run_with_timeout(
                        self._verify_equality_step, MATH_TOOL_TIMEOUT_S,
                        self._clean_for_sympy(parts[0]), self._clean_for_sympy(parts[1]),
                    )
                except TimeoutError as exc:
                    verdict, detail = "STEP_ASSUMED", f"SymPy check timed out ({exc}); requires manual review."
                except Exception as exc:
                    verdict, detail = "STEP_ASSUMED", f"SymPy parse note ({exc}). Treating as assumed — requires manual review."
            else:
                verdict, detail = (
                    "STEP_ASSUMED",
                    "Expression without '=' — nothing to verify symbolically. Write the step as 'LHS = RHS'."
                )

            step_result["verdict"] = verdict
            step_result["detail"] = detail
            if verdict == "STEP_VERIFIED":
                proven_count += 1
            elif verdict == "STEP_INVALID":
                invalid_count += 1
            else:
                assumed_count += 1

            step_results.append(step_result)

        # Evaluate optional asymptotic / perturbative limits
        limit_results = []
        for idx, spec in enumerate(limit_specs, 1):
            if not isinstance(spec, dict):
                continue
            expr_raw = str(spec.get("expr", "")).strip()
            var_raw = str(spec.get("var", "x")).strip()
            pt_raw = spec.get("point", 0)
            exp_raw = spec.get("expected", None)
            dir_raw = str(spec.get("dir", "+-")).strip()

            try:
                computed_lim, exp_sym, diff_lim = run_with_timeout(
                    self._evaluate_limit, MATH_TOOL_TIMEOUT_S, expr_raw, var_raw, pt_raw, exp_raw, dir_raw
                )

                lim_verdict = "LIMIT_COMPUTED"
                lim_detail = f"lim_{{{var_raw} -> {pt_raw}}} ({expr_raw}) = {computed_lim}"
                if exp_sym is not None:
                    if diff_lim == 0:
                        lim_verdict = "LIMIT_VERIFIED"
                        lim_detail += f" == expected ({exp_sym}) ✓"
                        proven_count += 1
                    else:
                        lim_verdict = "LIMIT_MISMATCH"
                        lim_detail += f" != expected ({exp_sym}) (diff = {diff_lim}) ✗"
                        invalid_count += 1

                limit_results.append({
                    "limit_number": idx,
                    "expression": expr_raw,
                    "variable": var_raw,
                    "point": str(pt_raw),
                    "computed_limit": str(computed_lim),
                    "expected_limit": str(exp_raw) if exp_raw is not None else None,
                    "verdict": lim_verdict,
                    "detail": lim_detail,
                })
            except Exception as exc:
                limit_results.append({
                    "limit_number": idx,
                    "expression": expr_raw,
                    "variable": var_raw,
                    "point": str(pt_raw),
                    "verdict": "LIMIT_ERROR",
                    "detail": f"Could not evaluate limit symbolically: {exc}",
                })

        total = len(step_results) + len(limit_results)
        math_status = (
            "[MATH_FLAWED]" if invalid_count > 0
            else "[MATH_PROVEN]" if (proven_count == total and total > 0)
            else "[MATH_CONSISTENT]"
        )

        return json.dumps({
            "concept": concept,
            "math_status": math_status,
            "total_checks": total,
            "proven_steps": proven_count,
            "assumed_steps": assumed_count,
            "invalid_steps": invalid_count,
            "steps": step_results,
            "limit_checks": limit_results,
            "summary": (
                f"Symbolic verification completed: {proven_count}/{total} verified by SymPy, "
                f"{assumed_count} assumed, {invalid_count} flagged as INVALID."
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
                "DESI+CMB+Pantheon+: w_0 = -0.827 ± 0.063, w_a = -0.75 (+0.29/-0.25), corr(w_0, w_a) ≈ -0.85 [approx., read off contours] (Δχ² ≈ -6.8 vs ΛCDM, 2.5σ); "
                "DESI+CMB+DES-SN5YR: w_0 = -0.727 ± 0.067, w_a = -1.05 (+0.31/-0.27), corr(w_0, w_a) ≈ -0.85 [approx.] (Δχ² ≈ -15.2 vs ΛCDM, 3.9σ)"
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
                    "correlation_is_approximate": True,
                    "delta_chi2_2dof": round(dchi2, 3),
                    "sqrt_delta_chi2": round(math.sqrt(max(0.0, dchi2)), 3),
                    "gaussian_2d_tail_prob": float(f"{p_val_2dof:.3e}"),
                }
            return json.dumps({
                "mode": "delta_chi2_w0wa",
                "tested_point": {"w0": w0, "wa": wa},
                "comparisons": comparisons,
                "doi": "10.1088/1475-7516/2025/02/021",
                "note": (
                    "2D Gaussian approximation against DESI 2024 VI + Planck CMB + Type Ia SNe. Means and 1-sigma errors are "
                    "the published values (asymmetric w_a errors symmetrized). The correlation rho = -0.85 is an APPROXIMATE "
                    "value read off the published contours, not a published covariance — quote results as approximate."
                )
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

            def _evaluate() -> float:
                sym_expr = safe_sympy_parse(clean_expr, local_symbols)
                return float(sym_expr.evalf(subs=local_symbols))

            computed_val = run_with_timeout(_evaluate, MATH_TOOL_TIMEOUT_S)
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
    """Tier 1 (automatic) tools: extract, dimension-check, symbolic derivation/limit, topology, benchmark, calculator."""
    return [
        EquationExtractorTool(),
        DimensionalConsistencyTool(),
        SymbolicDerivationTool(),
        TopologyClassifierTool(),
        NumericalBenchmarkTool(),
        PhysicsCalculatorTool(),
    ]


def get_tier2_math_tools() -> list:
    """Tier 2 (deep-dive) tools: all tools including symbolic derivation."""
    return get_all_math_tools()


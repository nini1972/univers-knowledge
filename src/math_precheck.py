"""
math_precheck.py
================
Deterministic math pre-check that runs in code on a research draft BEFORE the Math Physicist.

It extracts the draft's equations (with the surrounding sentence), reads the draft's own
`Symbol | Meaning | Dimension` table, and runs the Dimensional Consistency Checker directly —
no LLM in the loop. The result is:

  * injected into the Math Physicist's task description (via a callback on the last research
    task), so the agent starts from code-computed verdicts instead of re-deriving them; and
  * passed to the flow's math gate, which blocks approval on high-confidence findings even if
    the Math Physicist's report omits or miscopies them.

Only findings the draft cannot dispute block approval:
  - known error patterns (e.g. rho ∝ a^{-3(1+w(a))}, dropped -2Cov(A,B), m_T^2 ~ g^2 T^2 phi^2),
  - unsuppressed phi^n (n >= 5) Lagrangian terms,
  - term mismatches computed purely from the draft's OWN declared symbol table.
Mismatches that rely on built-in default dimensions are reported as advisory only.
Equations the text itself presents as wrong ("the naive form ... is incorrect") are excluded.
"""
from __future__ import annotations

import json
import re

try:
    from tools.math_tools import DimensionalConsistencyTool
except ImportError:  # pragma: no cover - package-style import
    from src.tools.math_tools import DimensionalConsistencyTool

BLOCKING_BASES = ("known_error_pattern", "lagrangian_operator", "declared_symbol_table")
MAX_EQUATIONS = 40

_RELATION_RE = re.compile(r"(=|\\equiv|\\approx|\\simeq|\\sim|\\propto|<|>|\\le|\\ge|\\ll|\\gg)")
_NEGATION_RE = re.compile(
    r"\b(incorrect(?:ly)?|wrong(?:ly)?|naive(?:ly)?|erroneous(?:ly)?|invalid|not\s+valid|never|"
    r"instead\s+of|rather\s+than|common\s+(?:error|mistake|pitfall)|mistaken(?:ly)?|flawed|"
    r"do\s+not\s+(?:write|use)|don't\s+(?:write|use)|avoid|fails?\s+(?:for|when)|is\s+not\s+correct)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Equation extraction with sentence context
# ---------------------------------------------------------------------------

_SENTENCE_BOUNDARY_RE = re.compile(r"[.!?](?=\s|$)|\n\s*\n|\n\s*[-*]\s")


def _sentence_context(text: str, start: int, end: int) -> str:
    """Return the sentence around an equation (bounded by sentence ends, blank lines or list bullets)."""
    before = text[max(0, start - 240):start]
    boundaries = list(_SENTENCE_BOUNDARY_RE.finditer(before))
    if boundaries:
        before = before[boundaries[-1].end():]
    after = text[end:end + 160]
    first = _SENTENCE_BOUNDARY_RE.search(after)
    if first:
        after = after[:first.start()]
    return f"{before} … {after}"


def extract_equations_with_context(text: str, max_equations: int = MAX_EQUATIONS) -> list[dict]:
    """Extract LaTeX equations ($$..$$, \\[..\\], $..$, \\(..\\)) with their sentence context."""
    text = str(text or "")
    found: list[dict] = []
    seen: set[str] = set()
    masked = text

    def _add(eq: str, start: int, end: int):
        eq = eq.strip()
        if len(eq) <= 2 or eq in seen:
            return
        seen.add(eq)
        context = _sentence_context(text, start, end)
        found.append({
            "equation": eq,
            "context": context.strip(),
            "quoted_as_incorrect": bool(_NEGATION_RE.search(context)),
            "relational": bool(_RELATION_RE.search(eq)),
        })

    # Display math first, then mask it so inline patterns don't re-match inside it.
    for pat in (r"\$\$(.+?)\$\$", r"\\\[(.+?)\\\]"):
        for m in re.finditer(pat, masked, re.DOTALL):
            _add(m.group(1), m.start(), m.end())
        masked = re.sub(pat, lambda m: " " * len(m.group(0)), masked, flags=re.DOTALL)
    for pat in (r"\$([^\$\n]+?)\$", r"\\\((.+?)\\\)"):
        for m in re.finditer(pat, masked):
            _add(m.group(1), m.start(), m.end())

    relational = [e for e in found if e["relational"]]
    return relational[:max_equations]


# ---------------------------------------------------------------------------
# Symbol table parsing
# ---------------------------------------------------------------------------

def _parse_dimension_cell(cell: str, header: str) -> float | None:
    c = cell.replace("$", "").replace("`", "").strip()
    if not c or c in {"-", "—", "–", "n/a", "N/A"}:
        return None
    header_l = header.lower()
    num = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)(?:\s*/\s*(\d+))?\s*", c)
    if num and ("mass" in header_l or "[e]" in header_l or "e^n" in header_l):
        val = float(num.group(1))
        return val / float(num.group(2)) if num.group(2) else val
    if re.search(r"dimensionless|\[\s*E\s*\]\s*\^\s*\{?\s*0\s*\}?", c, re.IGNORECASE):
        return 0.0
    m = re.search(
        r"\[?\s*(?:E|M|GeV|\\mathrm\{GeV\}|\\text\{GeV\})\s*\]?\s*\^\s*\{?\s*\(?\s*(-?\d+(?:\.\d+)?)(?:\s*/\s*(\d+))?\s*\)?\s*\}?",
        c,
    )
    if m:
        val = float(m.group(1))
        return val / float(m.group(2)) if m.group(2) else val
    if re.fullmatch(r"\[?\s*(?:E|M|GeV)\s*\]?", c):
        return 1.0
    return None


def _split_symbols(cell: str) -> list[str]:
    c = cell.replace("$", "").replace("`", "").strip()
    out = []
    for part in re.split(r"\s*(?:,|;|/|\bor\b|\band\b)\s*", c):
        part = re.sub(r"\(.*\)$", "", part.strip())  # V(\phi) -> V
        if part and len(part) <= 40:
            out.append(part)
    return out


def parse_symbol_table(text: str) -> dict[str, float]:
    """Read every markdown table that has a Symbol column and a Dimension column."""
    dims: dict[str, float] = {}
    lines = str(text or "").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{2,}", lines[i + 1].strip()):
            headers = [h.strip() for h in line.strip("|").split("|")]
            sym_col = next((k for k, h in enumerate(headers) if "symbol" in h.lower()), None)
            dim_col = next(
                (k for k, h in enumerate(headers) if re.search(r"dimension|dim\b|\[e\]|units?", h.lower())), None
            )
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if sym_col is not None and dim_col is not None and max(sym_col, dim_col) < len(cells):
                    val = _parse_dimension_cell(cells[dim_col], headers[dim_col])
                    if val is not None:
                        for sym in _split_symbols(cells[sym_col]):
                            dims[sym] = val
                i += 1
            continue
        i += 1
    return dims


# ---------------------------------------------------------------------------
# Pre-check
# ---------------------------------------------------------------------------

def run_math_precheck(research_text: str) -> dict:
    """Run the deterministic pre-check on a research draft. Never raises."""
    try:
        equations = extract_equations_with_context(research_text)
        symbol_table = parse_symbol_table(research_text)
        result = {
            "ran": True,
            "equation_count": len(equations),
            "symbol_table": symbol_table,
            "blocking": [],
            "advisory": [],
            "quoted_as_incorrect": [],
            "undecidable_count": 0,
            "verified_count": 0,
            "error": None,
        }
        if not equations:
            result["blocking_count"] = 0
            return result

        tool_out = json.loads(DimensionalConsistencyTool()._run(
            json.dumps([e["equation"] for e in equations]),
            symbol_dimensions_json=json.dumps(symbol_table) if symbol_table else "",
        ))
        for eq_info, res in zip(equations, tool_out.get("results", [])):
            entry = {
                "equation": eq_info["equation"][:200],
                "verdict": res.get("verdict"),
                "basis": res.get("basis"),
                "explanation": res.get("explanation", ""),
            }
            verdict = res.get("verdict")
            if verdict == "INCONSISTENT":
                if eq_info["quoted_as_incorrect"]:
                    result["quoted_as_incorrect"].append(entry)
                elif res.get("basis") in BLOCKING_BASES:
                    result["blocking"].append(entry)
                else:
                    result["advisory"].append(entry)
            elif verdict == "UNDECIDABLE":
                result["undecidable_count"] += 1
                if res.get("basis") == "possible_mismatch":
                    result["advisory"].append(entry)
            elif verdict in ("CONSISTENT", "DIMENSIONLESS"):
                result["verified_count"] += 1
        result["blocking_count"] = len(result["blocking"])
        return result
    except Exception as exc:  # the pre-check must never break a crew run
        return {"ran": False, "error": str(exc), "blocking": [], "blocking_count": 0,
                "advisory": [], "quoted_as_incorrect": [], "equation_count": 0,
                "undecidable_count": 0, "verified_count": 0, "symbol_table": {}}


def summarize_precheck(precheck: dict) -> dict:
    """Compact numbers for telemetry."""
    precheck = precheck or {}
    return {
        "ran": bool(precheck.get("ran")),
        "equations": precheck.get("equation_count", 0),
        "symbols_declared": len(precheck.get("symbol_table") or {}),
        "blocking": precheck.get("blocking_count", 0),
        "advisory": len(precheck.get("advisory") or []),
        "undecidable": precheck.get("undecidable_count", 0),
        "verified": precheck.get("verified_count", 0),
    }


def format_precheck_for_prompt(precheck: dict) -> str:
    """Render the pre-check as a block appended to the Math Physicist's task description."""
    p = precheck or {}
    if not p.get("ran"):
        return (
            "\n\nAUTOMATED PRE-CHECK: could not run on this draft"
            f"{' (' + p['error'] + ')' if p.get('error') else ''}. Perform the full tool workflow yourself."
        )
    syms = p.get("symbol_table") or {}
    lines = [
        "",
        "",
        "AUTOMATED PRE-CHECK (computed in code on the draft before your review — these verdicts are not opinions):",
        f"- Relational equations extracted: {p.get('equation_count', 0)}; "
        f"symbols read from the draft's Symbol Table: {len(syms)}"
        + (f" ({', '.join(list(syms)[:12])}{'…' if len(syms) > 12 else ''})" if syms else
           " — NO machine-readable Symbol | Meaning | Dimension table found; flag this in your Conventions audit."),
        f"- Tool-verified CONSISTENT/DIMENSIONLESS: {p.get('verified_count', 0)}; UNDECIDABLE: {p.get('undecidable_count', 0)}",
        f"- Code-confirmed INCONSISTENT (blocks approval until corrected): {p.get('blocking_count', 0)}",
    ]
    for k, e in enumerate(p.get("blocking") or [], 1):
        lines.append(f"    {k}. `{e['equation']}` [{e['basis']}] — {e['explanation'][:220]}")
    advisory = p.get("advisory") or []
    if advisory:
        lines.append(f"- Possible mismatches that rely on default symbol meanings (verify against the Symbol Table): {len(advisory)}")
        for k, e in enumerate(advisory[:6], 1):
            lines.append(f"    {k}. `{e['equation']}` — {e['explanation'][:180]}")
    quoted = p.get("quoted_as_incorrect") or []
    if quoted:
        lines.append(f"- Equations the draft itself presents as incorrect (not counted): {len(quoted)}")
    lines.extend([
        "PRE-CHECK INSTRUCTIONS:",
        "- Include every code-confirmed INCONSISTENT equation in your Tool Verdicts INCONSISTENT count and in your "
        "Dimensional Consistency section; never describe these equations as consistent.",
        "- Do not re-run the Equation Extractor / Dimensional Consistency Checker on the same equations just to repeat "
        "these verdicts. Spend your tool calls on what the pre-check could not decide: UNDECIDABLE equations (pass the "
        "Symbol Table), derivations and limits (Symbolic Derivation Verifier), and worked numbers (Physics Calculator).",
    ])
    return "\n".join(lines)


def attach_precheck(research_tasks: list, math_task, on_result=None) -> None:
    """
    Attach a callback to the last research task so that, as soon as the draft(s) exist, the
    pre-check runs and its summary is appended to the Math Physicist's task description
    (CrewAI reads Task.description when the task starts, after earlier callbacks have run).
    `on_result(precheck_dict)` receives the result (e.g. to store it in flow state).
    """
    if not research_tasks or math_task is None:
        return
    last = research_tasks[-1]
    previous_cb = getattr(last, "callback", None)

    def _callback(output):
        try:
            texts = []
            for t in research_tasks[:-1]:
                out = getattr(t, "output", None)
                if out is not None and getattr(out, "raw", None):
                    texts.append(str(out.raw))
            texts.append(str(getattr(output, "raw", output) or ""))
            precheck = run_math_precheck("\n\n".join(texts))
            math_task.description = f"{math_task.description}{format_precheck_for_prompt(precheck)}"
            if on_result:
                on_result(precheck)
        except Exception as exc:  # never break the crew
            print(f"[MATH PRECHECK] Warning: {exc}")
        if previous_cb:
            return previous_cb(output)
        return None

    last.callback = _callback

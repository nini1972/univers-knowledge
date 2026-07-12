"""
Equation Database Logger
========================
Captures extracted mathematical equations and links them to concepts.
Writes to knowledge_base/logs/equations.jsonl for future cross-concept analysis.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path


EQUATIONS_LOG = (
    Path(__file__).resolve().parent.parent
    / "knowledge_base"
    / "logs"
    / "equations.jsonl"
)


def log_equations(
    concept: str,
    level: int,
    equations: list[str],
    math_status: str | None = None,
    math_score: int | None = None,
    math_total: int | None = None,
    source: str = "crew_extraction",
    a2a_proof_report: str | None = None,
) -> None:
    """Append discovered equations to the equation database.

    Args:
        concept: The physics concept name.
        level: Knowledge level (1, 2, or 3).
        equations: List of LaTeX equation strings.
        math_status: The math verification status (e.g., MATH_PROVEN).
        math_score: Numerator of the math score (e.g., 4).
        math_total: Denominator of the math score (e.g., 4).
        source: Where the equations were extracted from.
        a2a_proof_report: Full proof report from the A2A Math Service, if available.
    """
    if not equations:
        return

    EQUATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "concept": concept,
        "level": level,
        "equations": equations,
        "equation_count": len(equations),
        "math_status": math_status,
        "math_score": f"{math_score}/{math_total}" if math_score is not None else None,
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if a2a_proof_report:
        entry["a2a_proof_report"] = a2a_proof_report

    try:
        with open(EQUATIONS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(
            f"[EQ DB] Logged {len(equations)} equation(s) for '{concept}' "
            f"[L{level}, {math_status or 'unknown'}]"
        )
    except Exception as e:
        print(f"[EQ DB] Warning: could not write equation log: {e}")

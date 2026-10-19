import datetime
import json
import os
import re
import sys
import uuid
from pathlib import Path

# Ensure UTF-8 stdout for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = REPO_ROOT / "knowledge_base" / "logs"
ADVISORY_FILE = LOGS_DIR / "advisory_queue.jsonl"
DIRECTIVES_FILE = LOGS_DIR / "professor_directives.jsonl"
OFFICE_HOURS_MD = REPO_ROOT / "knowledge_base" / "PROFESSOR_OFFICE_HOURS.md"


def _ensure_log_dir():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _get_utc_now() -> str:
    try:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()
    except AttributeError:
        return datetime.datetime.utcnow().isoformat() + "Z"


def _generate_id(prefix: str = "adv") -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
    short_uid = uuid.uuid4().hex[:6]
    return f"{prefix}-{ts}-{short_uid}"


def create_advisory_request(
    concept: str,
    level: int,
    initiator: str = "Student Orchestrator",
    question: str = "",
    detailed_rationale: str = "",
    agent_needs: dict = None,
    reason_code: str = "",
) -> str | None:
    """
    Creates an advisory inquiry from an agent to the human operator (Professor).
    Persists to advisory_queue.jsonl and updates PROFESSOR_OFFICE_HOURS.md.
    """
    clean_concept = (concept or "").strip()
    if not clean_concept:
        return None
    _ensure_log_dir()

    clean_question = (question or "").strip()
    if not clean_question:
        clean_question = f"How should the agents proceed regarding '{clean_concept}' given: {detailed_rationale or reason_code}?"

    # Check for existing pending request for this concept to avoid duplicate spam
    if ADVISORY_FILE.exists():
        with open(ADVISORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    if (
                        record.get("concept", "").strip().lower() == clean_concept.lower()
                        and record.get("status") == "pending"
                    ):
                        print(f"[OFFICE HOURS] Advisory request already pending for '{clean_concept}' ({record.get('id')}).")
                        return record.get("id")
                except Exception:
                    pass

    req_id = _generate_id("adv")
    record = {
        "id": req_id,
        "timestamp": _get_utc_now(),
        "concept": clean_concept,
        "level": level,
        "initiator": initiator,
        "reason_code": reason_code,
        "question": clean_question,
        "detailed_rationale": detailed_rationale,
        "agent_needs": agent_needs or {},
        "status": "pending",
        "professor_response": None,
        "answered_at": None,
    }

    with open(ADVISORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\n[OFFICE HOURS] [ADVISORY] New Advisory Request filed: [{req_id}] for '{clean_concept}'")
    print(f"               Question: {clean_question}")
    sync_office_hours_markdown()
    return req_id


def get_pending_requests(level: int = None) -> list[dict]:
    """Retrieves all pending advisory requests, optionally filtered by level."""
    if not ADVISORY_FILE.exists():
        return []

    pending = []
    with open(ADVISORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if record.get("status") == "pending":
                    if level is None or record.get("level") == level:
                        pending.append(record)
            except Exception:
                pass
    return pending


def answer_advisory_request(identifier: str, professor_response: str) -> bool:
    """
    Records the Professor's response to an advisory request by ID or concept name.
    Marks status as 'answered' and updates PROFESSOR_OFFICE_HOURS.md.
    """
    clean_target = (identifier or "").strip().lower()
    clean_response = (professor_response or "").strip()
    if not clean_target or not clean_response or not ADVISORY_FILE.exists():
        return False

    answered_any = False
    temp_records = []
    timestamp = _get_utc_now()

    with open(ADVISORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                matches_id = record.get("id", "").strip().lower() == clean_target
                matches_concept = record.get("concept", "").strip().lower() == clean_target

                if (matches_id or matches_concept) and record.get("status") == "pending":
                    record["status"] = "answered"
                    record["professor_response"] = clean_response
                    record["answered_at"] = timestamp
                    answered_any = True
                    print(f"[OFFICE HOURS] Answered advisory request [{record['id']}] for '{record['concept']}'")
                temp_records.append(record)
            except Exception:
                pass

    if answered_any:
        with open(ADVISORY_FILE, "w", encoding="utf-8") as f:
            for rec in temp_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        sync_office_hours_markdown()
    return answered_any


def add_general_directive(directive_text: str, topic_scope: str = "all") -> str:
    """
    Adds a standing curriculum or epistemic directive from the Professor.
    Persists to professor_directives.jsonl and updates PROFESSOR_OFFICE_HOURS.md.
    """
    clean_directive = (directive_text or "").strip()
    if not clean_directive:
        return ""
    _ensure_log_dir()

    dir_id = _generate_id("dir")
    record = {
        "id": dir_id,
        "timestamp": _get_utc_now(),
        "directive": clean_directive,
        "scope": topic_scope.strip().lower() if topic_scope else "all",
        "active": True,
    }

    with open(DIRECTIVES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"[OFFICE HOURS] [DIRECTIVE] Standing Professor Directive recorded [{dir_id}]: {clean_directive}")
    sync_office_hours_markdown()
    return dir_id


def get_active_directive_for_concept(concept: str, level: int = None) -> str | None:
    """
    Retrieves the most recent answered advisory response or directive for a concept.
    """
    clean_concept = (concept or "").strip().lower()
    if not clean_concept or not ADVISORY_FILE.exists():
        return None

    matched_response = None
    with open(ADVISORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if (
                    record.get("status") == "answered"
                    and record.get("concept", "").strip().lower() == clean_concept
                ):
                    if level is None or record.get("level") == level:
                        matched_response = record.get("professor_response")
            except Exception:
                pass
    return matched_response


def get_next_retryable_advisory(level: int = None, repo_root: Path = None) -> dict | None:
    """
    Finds the oldest answered advisory request for the specified level
    whose concept markdown file does NOT yet exist on disk in knowledge_base/.
    Returns the advisory record dictionary or None if none are awaiting retry.
    """
    if not ADVISORY_FILE.exists():
        return None

    if repo_root is None:
        repo_root = REPO_ROOT

    try:
        from workflow_contracts import is_concept_existing
    except ImportError:
        from src.workflow_contracts import is_concept_existing

    with open(ADVISORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if record.get("status") == "answered":
                    rec_level = record.get("level")
                    if level is not None and rec_level != level:
                        continue
                    concept = record.get("concept", "").strip()
                    if not concept:
                        continue
                    if not is_concept_existing(concept, level=rec_level or level or 1, repo_root=repo_root):
                        return record
            except Exception:
                continue

    return None


def get_all_retryable_advisories(level: int = None, repo_root: Path = None) -> list[dict]:
    """Returns all answered advisories whose concept has not yet been verified."""
    if not ADVISORY_FILE.exists():
        return []

    if repo_root is None:
        repo_root = REPO_ROOT

    try:
        from workflow_contracts import is_concept_existing
    except ImportError:
        from src.workflow_contracts import is_concept_existing

    retryable = []
    with open(ADVISORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if record.get("status") == "answered":
                    rec_level = record.get("level")
                    if level is not None and rec_level != level:
                        continue
                    concept = record.get("concept", "").strip()
                    if not concept:
                        continue
                    if not is_concept_existing(concept, level=rec_level or level or 1, repo_root=repo_root):
                        retryable.append(record)
            except Exception:
                continue
    return retryable


def get_active_general_directives(scope: str = None) -> list[str]:
    """Retrieves all active standing directives from the Professor."""
    if not DIRECTIVES_FILE.exists():
        return []

    directives = []
    with open(DIRECTIVES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if record.get("active", True):
                    rec_scope = record.get("scope", "all")
                    if scope is None or rec_scope in ("all", scope.lower()):
                        directives.append(record.get("directive"))
            except Exception:
                pass
    return directives


def dismiss_request(identifier: str) -> bool:
    """Dismisses an advisory request without answering."""
    clean_target = (identifier or "").strip().lower()
    if not clean_target or not ADVISORY_FILE.exists():
        return False

    dismissed = False
    temp_records = []
    with open(ADVISORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                matches_id = record.get("id", "").strip().lower() == clean_target
                matches_concept = record.get("concept", "").strip().lower() == clean_target
                if (matches_id or matches_concept) and record.get("status") == "pending":
                    record["status"] = "dismissed"
                    dismissed = True
                    print(f"[OFFICE HOURS] Dismissed advisory request [{record['id']}]")
                temp_records.append(record)
            except Exception:
                pass

    if dismissed:
        with open(ADVISORY_FILE, "w", encoding="utf-8") as f:
            for rec in temp_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        sync_office_hours_markdown()
    return dismissed


def sync_office_hours_markdown():
    """
    Renders knowledge_base/PROFESSOR_OFFICE_HOURS.md containing current pending questions,
    active directives, and recent answered consultations.
    """
    pending = []
    answered = []
    if ADVISORY_FILE.exists():
        with open(ADVISORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                    if rec.get("status") == "pending":
                        pending.append(rec)
                    elif rec.get("status") == "answered":
                        answered.append(rec)
                except Exception:
                    pass

    directives = []
    if DIRECTIVES_FILE.exists():
        with open(DIRECTIVES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                    if d.get("active", True):
                        directives.append(d)
                except Exception:
                    pass

    lines = [
        "# 🎓 Professor Office Hours & Advisory Queue",
        "",
        "> This document is the interactive communication bridge between the **Student Orchestrator** and the **Professor (Human Operator)**.",
        "> When autonomous agents encounter fundamental scientific dilemmas or exhausted retries, they file an inquiry here.",
        "> Respond via CLI: `python scripts/consult_professor.py answer <id> \"Your directive here\"`",
        "",
        "---",
        "",
        "## 📜 Active Professor Directives",
        "",
    ]

    if directives:
        for d in directives:
            lines.append(f"- **[{d['id']}]** *(Scope: {d.get('scope', 'all')})*: {d['directive']}")
    else:
        lines.append("*No standing directives currently active. Add one using `python scripts/consult_professor.py directive \"...\"`.*")

    lines.extend([
        "",
        "---",
        "",
        f"## 📬 Pending Student Inquiries ({len(pending)})",
        "",
    ])

    if pending:
        lines.append("| ID | Level | Concept | Initiator | Question |")
        lines.append("|---|---|---|---|---|")
        for p in pending:
            short_q = p.get("question", "").replace("|", "-")
            lines.append(f"| `{p['id']}` | L{p.get('level', 1)} | **{p.get('concept')}** | {p.get('initiator')} | {short_q} |")

        lines.append("")
        lines.append("### Detailed Inquiries")
        lines.append("")
        for p in pending:
            lines.append(f"#### 🔍 Inquiry: `{p['id']}` — {p.get('concept')}")
            lines.append(f"- **Timestamp**: `{p.get('timestamp')}`")
            lines.append(f"- **Level**: Level {p.get('level', 1)}")
            lines.append(f"- **Reason Code**: `{p.get('reason_code', 'unspecified')}`")
            lines.append(f"- **Question**: {p.get('question')}")
            if p.get("detailed_rationale"):
                lines.append(f"- **Scientific Rationale**: {p.get('detailed_rationale')}")
            agent_needs = p.get("agent_needs") or {}
            if agent_needs.get("researcher_needs") or agent_needs.get("math_needs"):
                lines.append("- **Agent Blockers**:")
                for rn in agent_needs.get("researcher_needs", []):
                    lines.append(f"  * Researcher: {rn}")
                for mn in agent_needs.get("math_needs", []):
                    lines.append(f"  * Math Physicist: {mn}")
            lines.append("")
            lines.append(f"> **To answer**: `python scripts/consult_professor.py answer {p['id']} \"Your guidance\"`")
            lines.append("")
    else:
        lines.append("*The advisory queue is currently clear. The Student and underlying agents are operating autonomously.*")

    lines.extend([
        "",
        "---",
        "",
        f"## 📚 Answered Advisory Consultations ({len(answered)})",
        "",
    ])

    if answered:
        for a in reversed(answered[-10:]):  # Show latest 10 answered
            lines.append(f"### ✅ `{a['id']}`: {a.get('concept')}")
            lines.append(f"- **Student Inquired**: {a.get('question')}")
            lines.append(f"- **Professor Directive**: 💬 *\"{a.get('professor_response')}\"*")
            lines.append(f"- **Answered At**: `{a.get('answered_at')}`")
            lines.append("")
    else:
        lines.append("*No consultations answered yet.*")

    OFFICE_HOURS_MD.parent.mkdir(parents=True, exist_ok=True)
    OFFICE_HOURS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


AGENT_WISHLIST_MD = REPO_ROOT / "knowledge_base" / "AGENT_WISHLIST.md"


def _classify_need_themes(needs_list: list[str]) -> dict[str, int]:
    """Classify concrete researcher/math needs into recurring operational themes."""
    from collections import Counter

    theme_rules = [
        ("units_and_dimensions", ["unit", "dimension", "gev", "meter", "si ", "m_pl", "planck mass", "rescal"]),
        ("conventions_and_signs", ["convention", "signature", "sign", "action", "metric", "kinetic", "canonical", "model-dependent"]),
        ("worked_arithmetic_and_benchmarks", ["recompute", "numerical", "calculate", "patch scale", "benchmark", "sound speed", "perturbation", "h_0", "s_8", "desi"]),
        ("citation_provenance", ["citation", "doi", "arxiv", "source", "future-dated", "2026", "duplicate"]),
        ("causal_and_statistical_design", ["estimand", "mediator", "covariance", "variance", "power", "multiplicity", "preregister", "nie", "dag", "null model"]),
    ]
    counts: Counter = Counter()
    for item in needs_list:
        low = item.lower()
        for theme_name, keywords in theme_rules:
            if any(kw in low for kw in keywords):
                counts[theme_name] += 1
    return dict(counts.most_common())


def collect_historical_agent_shortcomings(limit: int = 10, recent_window: int = 100) -> dict:
    """
    Mines evaluation_runs.jsonl and advisory_queue.jsonl to extract real operational
    shortcomings, rejection frequencies (both recent-window and all-time), researcher_needs,
    and math_needs encountered by the agents during autonomous runs.
    """
    from collections import Counter

    eval_file = LOGS_DIR / "evaluation_runs.jsonl"
    rejection_counts = Counter()
    researcher_needs = []
    math_needs = []
    recent_rejections = []
    all_records = []
    total_runs = 0
    approved_runs = 0

    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                    all_records.append(rec)
                    total_runs += 1
                    status = rec.get("status")
                    if status == "approved":
                        approved_runs += 1
                    elif status == "rejected":
                        rc = rec.get("reason_code", "unspecified")
                        rejection_counts[rc] += 1
                        recent_rejections.append({
                            "concept": rec.get("concept"),
                            "reason_code": rc,
                            "rationale": rec.get("detailed_rationale", ""),
                            "timestamp": rec.get("timestamp", ""),
                        })
                    needs = rec.get("agent_needs") or {}
                    for rn in needs.get("researcher_needs") or []:
                        if rn and rn not in researcher_needs:
                            researcher_needs.append(rn)
                    for mn in needs.get("math_needs") or []:
                        if mn and mn not in math_needs:
                            math_needs.append(mn)
                except Exception:
                    pass

    window_records = all_records[-recent_window:] if recent_window > 0 else all_records
    window_approved = 0
    window_rejections: Counter = Counter()
    window_needs_all: list[str] = []
    window_researcher_needs: list[str] = []
    window_math_needs: list[str] = []
    for rec in window_records:
        st = rec.get("status")
        if st == "approved":
            window_approved += 1
        elif st == "rejected":
            window_rejections[rec.get("reason_code", "unspecified")] += 1
        needs = rec.get("agent_needs") or {}
        for rn in needs.get("researcher_needs") or []:
            if rn:
                window_needs_all.append(str(rn))
                window_researcher_needs.append(str(rn))
        for mn in needs.get("math_needs") or []:
            if mn:
                window_needs_all.append(str(mn))
                window_math_needs.append(str(mn))

    return {
        "total_evaluations": total_runs,
        "approved_evaluations": approved_runs,
        "rejection_counts": dict(rejection_counts.most_common()),
        "recent_window_size": len(window_records),
        "recent_window_approved": window_approved,
        "recent_window_rejected": sum(window_rejections.values()),
        "recent_window_rejection_counts": dict(window_rejections.most_common()),
        "recent_need_themes": _classify_need_themes(window_needs_all),
        "recent_researcher_need_themes": _classify_need_themes(window_researcher_needs),
        "recent_math_need_themes": _classify_need_themes(window_math_needs),
        "recent_researcher_needs": researcher_needs[-limit:],
        "recent_math_needs": math_needs[-limit:],
        "recent_rejections": recent_rejections[-limit:],
    }


def _live_tool_names() -> dict[str, list[str] | None]:
    """Read the tool lists actually wired to the agents (None if they cannot be imported)."""
    names: dict[str, list[str] | None] = {"researcher": None, "math": None}
    try:
        try:
            from agents.universe_agents import _build_search_tools
        except ImportError:
            from src.agents.universe_agents import _build_search_tools
        names["researcher"] = [t.name for t in _build_search_tools()]
    except Exception:
        pass
    try:
        try:
            from tools.math_tools import get_tier1_math_tools
        except ImportError:
            from src.tools.math_tools import get_tier1_math_tools
        names["math"] = [t.name for t in get_tier1_math_tools()]
    except Exception:
        pass
    return names


def _source_contains(rel_path: str, needle: str) -> bool:
    try:
        return needle in (REPO_ROOT / rel_path).read_text(encoding="utf-8")
    except Exception:
        return False


def _capability_registry(tools: dict) -> list[dict]:
    """
    Capabilities requested in the agent interviews, each with a code probe that decides
    whether it is actually present. Status is computed, never hand-written.
    """
    researcher = tools.get("researcher") or []
    math = tools.get("math") or []

    def has_tool(pool: list[str], name: str):
        return None if not pool else name in pool

    return [
        {"agent": "researcher", "name": "Physics Calculator & Tension Evaluator (worked examples, sigma / delta-chi2)",
         "themes": ["worked_arithmetic_and_benchmarks"],
         "present": has_tool(researcher, "Physics Calculator & Tension Evaluator")},
        {"agent": "researcher", "name": "Observational Cosmology tracker with values, uncertainties and covariances",
         "themes": ["worked_arithmetic_and_benchmarks", "citation_provenance"],
         "present": has_tool(researcher, "Observational Cosmology & Deep-Space Survey Tracker")},
        {"agent": "researcher", "name": "Conventions & Symbol Table / Validity Domain preamble in the concept template",
         "themes": ["conventions_and_signs", "units_and_dimensions"],
         "present": _source_contains("knowledge_base/templates/concept_template.md", "### Conventions & Symbol Table")},
        {"agent": "researcher", "name": "arXiv full-text section reader (exact conventions and prefactors)",
         "themes": ["conventions_and_signs", "citation_provenance"],
         "present": (None if not researcher else any("full-text" in n.lower() or "full text" in n.lower() for n in researcher))},
        {"agent": "math", "name": "Term-level natural-unit [E]^n dimension checker using the report's symbol table",
         "themes": ["units_and_dimensions"],
         "present": has_tool(math, "Dimensional Consistency Checker") and _source_contains("src/tools/math_tools.py", "class NaturalUnitDimensionAnalyzer")},
        {"agent": "math", "name": "Symbolic re-derivation (continuity/ODE integrals, identities, limits) for the Math Physicist",
         "themes": ["conventions_and_signs", "causal_and_statistical_design"],
         "present": has_tool(math, "Symbolic Derivation Verifier")},
        {"agent": "math", "name": "Benchmark table + claim verification (verify_claim within 10%)",
         "themes": ["worked_arithmetic_and_benchmarks"],
         "present": has_tool(math, "Numerical Benchmark Validator") and has_tool(math, "Physics Calculator & Tension Evaluator")},
        {"agent": "math", "name": "Math gate in the flow (tool-confirmed INCONSISTENT / STEP_INVALID blocks approval)",
         "themes": ["units_and_dimensions"],
         "present": _source_contains("src/universe_flow.py", "apply_math_gate(")},
        {"agent": "math", "name": "Automated pre-check: equations + the draft's own symbol table checked in code before the Math Physicist",
         "themes": ["units_and_dimensions", "conventions_and_signs"],
         "present": _source_contains("src/universe_flow.py", "attach_precheck(")},
        {"agent": "skeptic", "name": "Shared canonical conventions header in every crew task",
         "themes": ["conventions_and_signs"],
         "present": _source_contains("src/conventions.py", "CANONICAL_CONVENTIONS_HEADER")},
        {"agent": "skeptic", "name": "Level 3 causal-design checklist (estimand, DAG, identification, power, multiplicity)",
         "themes": ["causal_and_statistical_design"],
         "present": _source_contains("src/conventions.py", "Target Estimand") and _source_contains("src/conventions.py", "multiplicity")},
        {"agent": "skeptic", "name": "Per-run scorecard (UNDECIDABLE ratio, attempts to approval, timeouts)",
         "themes": [],
         "present": _source_contains("src/advisory_manager.py", "def build_run_" + "scorecard(")},
    ]


def _render_capabilities(registry: list[dict], agent: str, theme_counts: dict) -> list[str]:
    out = []
    for cap in registry:
        if cap["agent"] != agent:
            continue
        mentions = sum(theme_counts.get(t, 0) for t in cap["themes"])
        theme_txt = ", ".join(f"`{t}`" for t in cap["themes"]) or "—"
        if cap["present"] is True:
            mark = "✅ present"
        elif cap["present"] is False:
            mark = "🎯 OPEN"
        else:
            mark = "❔ unknown (agent config not importable)"
        out.append(f"  * {mark} — {cap['name']} · addresses {theme_txt} ({mentions} recent mention(s))")
    return out


def _format_theme_counts(theme_counts: dict) -> str:
    if not theme_counts:
        return "*none logged in this window*"
    return ", ".join(f"`{t}` ×{c}" for t, c in theme_counts.items())


def _freshness_line() -> str:
    ts, source = _last_tooling_change_utc()
    since = _evaluations_since(ts)
    if since["total"] == 0:
        return (f"> ⏱️ **Evaluations since the last tooling change** (`{ts}`, {source}): **0** — "
                "everything below predates the current tools and safeguards.")
    return (f"> ⏱️ **Evaluations since the last tooling change** (`{ts}`, {source}): **{since['total']}** "
            f"(`{since['approved']}` approved, `{since['rejected']}` rejected; reasons: "
            + (", ".join(f"`{k}` ×{v}" for k, v in since["reasons"].items()) or "none") + ")")


def _recent_need_lines(needs: list | None, n: int = 3) -> list[str]:
    needs = list(needs or [])[-n:]
    return [f"  * {x}" for x in needs] if needs else ["  * *none logged*"]


def _build_wishlist_section2(stats: dict) -> list[str]:
    """Section 2 of AGENT_WISHLIST.md, generated from live tool wiring, telemetry and code probes."""
    tools = _live_tool_names()
    registry = _capability_registry(tools)
    window = stats["recent_window_size"]

    def tool_line(key: str) -> str:
        lst = tools.get(key)
        if lst is None:
            return "- **Equipped Tools (live)**: *could not import agent configuration*"
        return "- **Equipped Tools (live)**: " + (", ".join(f"`{n}`" for n in lst) or "*none*")

    lines = [
        "",
        "---",
        "",
        "## 🧞 2. Per-Agent Diagnostics & Capability Status",
        "",
        f"> Generated automatically: tool lists are read from the live agent configuration, need themes from the last "
        f"`{window}` evaluations, and each capability's status from a probe of the code. Nothing in this section is hand-written.",
        "",
        "### 🔭 A. Researcher, Bio-Digital Analyst & Cosmological Architect",
        tool_line("researcher"),
        f"- **Recurring need themes (`researcher_needs`, last {window})**: {_format_theme_counts(stats.get('recent_researcher_need_themes', {}))}",
        "- **Most recent concrete needs**:",
    ]
    lines.extend(_recent_need_lines(stats.get("recent_researcher_needs")))
    lines.append("- **Capabilities**:")
    lines.extend(_render_capabilities(registry, "researcher", stats.get("recent_researcher_need_themes", {})))

    lines.extend([
        "",
        "### 🧮 B. Mathematical Physics Verifier",
        tool_line("math"),
        f"- **Recurring need themes (`math_needs`, last {window})**: {_format_theme_counts(stats.get('recent_math_need_themes', {}))}",
        "- **Most recent concrete needs**:",
    ])
    lines.extend(_recent_need_lines(stats.get("recent_math_needs")))
    lines.append("- **Capabilities**:")
    lines.extend(_render_capabilities(registry, "math", stats.get("recent_math_need_themes", {})))

    rejections = stats.get("recent_window_rejection_counts", {})
    lines.extend([
        "",
        "### ⚖️ C. Scientific Skeptic & Student",
        "- **Equipped Tools**: none by design — both receive the Math Physicist's tool-verified report in context.",
        f"- **Rejection root causes (last {window})**: "
        + (", ".join(f"`{rc}` ×{c}" for rc, c in rejections.items()) if rejections else "*none*"),
        "- **Capabilities**:",
    ])
    lines.extend(_render_capabilities(registry, "skeptic", stats.get("recent_need_themes", {})))
    return lines


def generate_agent_wishlist_markdown(live_responses: dict | None = None) -> str:
    """
    Generates a comprehensive Agent Shortcomings & Wishlist report combining empirical
    run telemetry/logs with structured per-agent wishlists (and optional live LLM interviews),
    saving it to knowledge_base/AGENT_WISHLIST.md.
    """
    stats = collect_historical_agent_shortcomings(limit=8, recent_window=100)
    now_str = _get_utc_now()

    # Preserve existing live interview section when refreshing telemetry without --live
    preserved_live_section = ""
    if not live_responses and AGENT_WISHLIST_MD.exists():
        try:
            existing_md = AGENT_WISHLIST_MD.read_text(encoding="utf-8")
            marker = "## 🎙️ 3. Live Agent Interview Transcripts"
            idx = existing_md.find(marker)
            if idx != -1:
                preserved_live_section = existing_md[idx:].strip()
        except Exception:
            pass

    lines = [
        "# 🛠️ Autonomous Agent Shortcomings & Capability Wishlist",
        "",
        f"> **Last Updated**: `{now_str}`",
        "> **How to Query Agents Directly**:",
        "> - Generate/refresh this wishlist: `python scripts/consult_professor.py wishlist` (add `--live` to interview live LLMs)",
        "> - Ask any agent a direct question: `python scripts/consult_professor.py ask <agent_role> \"Your question\"`",
        ">   *(Available roles: `student`, `researcher`, `math`, `skeptic`, `cosmological_architect`, `bio_digital_analyst`, `visualizer`, `archivist`)*",
        "",
        "---",
        "",
        "## 📊 1. Empirical Telemetry: Where Agents Struggle in Production",
        "",
        _freshness_line(),
        "",
        f"### Recent Window Scorecard (Last `{stats['recent_window_size']}` Evaluations)",
        f"- **Evaluations in Window**: `{stats['recent_window_size']}` (`{stats['recent_window_approved']}` approved, `{stats['recent_window_rejected']}` rejected)",
        "- **Recent Rejection Breakdown by Root Cause**:",
    ]

    for rc, cnt in stats["recent_window_rejection_counts"].items():
        lines.append(f"  * `{rc}`: **{cnt}** occurrence(s)")

    if stats.get("recent_need_themes"):
        lines.append("- **Recurring Need Themes in Recent Window (`agent_needs`)**:")
        for theme, cnt in stats["recent_need_themes"].items():
            lines.append(f"  * `{theme}`: **{cnt}** mention(s)")

    lines.extend([
        "",
        "### All-Time Cumulative Totals (Historical Baseline)",
        f"- **Total Logged Evaluations**: `{stats['total_evaluations']}` (`{stats['approved_evaluations']}` approved)",
        "- **All-Time Rejection Breakdown by Root Cause**:",
    ])

    for rc, cnt in stats["rejection_counts"].items():
        lines.append(f"  * `{rc}`: **{cnt}** occurrence(s)")

    lines.extend([
        "",
        "### Recent Concrete Shortcomings Logged for the **Researcher**:",
    ])
    for rn in stats["recent_researcher_needs"]:
        lines.append(f"- {rn}")

    lines.extend([
        "",
        "### Recent Concrete Shortcomings Logged for the **Math Physicist**:",
    ])
    for mn in stats["recent_math_needs"]:
        lines.append(f"- {mn}")

    # Section 2 is generated from live tool wiring, recent telemetry and code probes.
    lines.extend(_build_wishlist_section2(stats))

    if live_responses:
        lines.extend([
            "",
            "---",
            "",
            "## 🎙️ 3. Live Agent Interview Transcripts",
            "",
        ])
        for role_key, resp_text in live_responses.items():
            lines.append(f"### 💬 `{role_key}` Live Response")
            lines.append(resp_text.strip())
            lines.append("")
    elif preserved_live_section:
        lines.extend([
            "",
            "---",
            "",
            preserved_live_section,
        ])

    content = "\n".join(lines) + "\n"
    AGENT_WISHLIST_MD.parent.mkdir(parents=True, exist_ok=True)
    AGENT_WISHLIST_MD.write_text(content, encoding="utf-8")
    return content


# Fallback used when git history is unavailable (e.g. the shallow checkout in GitHub Actions).
# Bump this whenever agent tools, tasks, the math gate or the pre-check change.
LAST_TOOLING_CHANGE_FALLBACK_UTC = "2026-10-19T06:20:00+00:00"
_TOOLING_PATHS = [
    "src/tools", "src/agents", "src/tasks", "src/universe_flow.py", "src/workflow_contracts.py",
    "src/math_precheck.py", "src/conventions.py",
]


def _last_tooling_change_utc() -> tuple[str, str]:
    """Return (ISO timestamp, source) of the most recent change to agent tooling."""
    import subprocess

    def _git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=10)

    try:
        found = _git("log", "-1", "--format=%H %cI", "--", *_TOOLING_PATHS).stdout.strip()
        if found:
            sha, ts = found.split(" ", 1)
            # In a shallow clone the boundary commit has no parent, so git cannot tell what it changed.
            if _git("rev-parse", "--verify", "--quiet", f"{sha}^").returncode == 0:
                return ts, "from git history"
    except Exception:
        pass
    return LAST_TOOLING_CHANGE_FALLBACK_UTC, "from LAST_TOOLING_CHANGE_FALLBACK_UTC"


def _evaluations_since(iso_ts: str) -> dict:
    """Count evaluations logged after iso_ts (approved / rejected / reason codes)."""
    from collections import Counter
    from datetime import datetime, timezone

    def _parse(ts: str):
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            return None

    cutoff = _parse(iso_ts)
    out = {"total": 0, "approved": 0, "rejected": 0, "reasons": {}}
    eval_file = LOGS_DIR / "evaluation_runs.jsonl"
    if cutoff is None or not eval_file.exists():
        return out
    reasons: Counter = Counter()
    with open(eval_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            ts = _parse(rec.get("timestamp", ""))
            if ts is None or ts <= cutoff:
                continue
            out["total"] += 1
            if rec.get("status") == "approved":
                out["approved"] += 1
            elif rec.get("status") == "rejected":
                out["rejected"] += 1
                reasons[rec.get("reason_code", "unspecified")] += 1
    out["reasons"] = dict(reasons.most_common())
    return out


def _describe_tools(tools: list) -> list[str]:
    """'Tool name — first sentence of its description' for each tool."""
    lines = []
    for t in tools:
        name = getattr(t, "name", str(t))
        desc = " ".join(str(getattr(t, "description", "") or "").split())
        # CrewAI prefixes descriptions with the tool signature; keep the human part only.
        desc = re.sub(r"^Tool Name:.*?Tool Description:\s*", "", desc)
        first = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", desc, maxsplit=1)[0] if desc else ""
        lines.append(f"{name} — {first[:200]}" if first else name)
    return lines


def ask_agent_directly(agent_role: str, question: str) -> str:
    """
    Instantiates a live agent from UniverseAgents, injects its recent operational
    shortcomings and equipped tools as context, and runs a direct 1-on-1 question/answer task.
    """
    from crewai import Crew, Task, Process
    try:
        from agents.universe_agents import UniverseAgents
    except ImportError:
        from src.agents.universe_agents import UniverseAgents

    ua = UniverseAgents()
    role_map = {
        "student": ua.student_agent,
        "researcher": ua.researcher_agent,
        "math": ua.math_physicist_agent,
        "skeptic": ua.skeptic_agent,
        "cosmological_architect": ua.cosmological_architect_agent,
        "bio_digital_analyst": ua.bio_digital_analyst_agent,
        "visualizer": ua.visualizer_agent,
        "archivist": ua.archivist_agent,
        "peer_reviewer": ua.peer_reviewer_agent,
    }

    key = agent_role.strip().lower()
    if key not in role_map:
        raise ValueError(f"Unknown agent role '{agent_role}'. Valid roles: {', '.join(role_map.keys())}")

    agent = role_map[key]()
    # Disable delegation during direct 1-on-1 interview for fast, focused response
    agent.allow_delegation = False
    prompt = build_interview_prompt(agent.role, agent.tools or [], question)

    # Temporarily detach tools for meta-wishlist introspection unless the user asked to run a search
    if any(w in question.lower() for w in ["wishlist", "shortcoming", "bottleneck", "struggle", "need", "improve", "missing"]):
        agent.tools = []

    task = Task(
        description=prompt,
        expected_output="A candid, technically specific first-person response addressing the Professor's question.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
    return str(crew.kickoff()).strip()


def build_interview_prompt(role: str, tools: list, question: str) -> str:
    """Interview prompt: tool descriptions, safeguards present/open, telemetry freshness, telemetry, question."""
    tool_lines = _describe_tools(tools)
    stats = collect_historical_agent_shortcomings(limit=5, recent_window=100)
    change_ts, change_source = _last_tooling_change_utc()
    since = _evaluations_since(change_ts)
    registry = _capability_registry(_live_tool_names())
    present = [c["name"] for c in registry if c["present"] is True]
    still_open = [c["name"] for c in registry if c["present"] is False]

    if since["total"] == 0:
        freshness = (
            f"IMPORTANT: 0 production evaluations have run since the last tooling change ({change_ts}, {change_source}). "
            "ALL telemetry below predates your current tools and safeguards. For each recurring failure, say whether "
            "your current tools/safeguards already address it, and focus your wishlist on what is still NOT covered."
        )
    else:
        freshness = (
            f"Since the last tooling change ({change_ts}, {change_source}): {since['total']} evaluations — "
            f"{since['approved']} approved, {since['rejected']} rejected; rejection reasons {json.dumps(since['reasons'])}. "
            "Weight these post-change results most heavily."
        )

    return (
        f"The Human Operator (Professor) is speaking to you directly in a 1-on-1 diagnostic session.\n"
        f"Your Role: {role}\n"
        f"Your Currently Equipped Tools (what each does):\n"
        + ("\n".join(f"  - {line}" for line in tool_lines) if tool_lines else "  - None (pure reasoning)")
        + "\n"
        f"Pipeline safeguards ALREADY IN PLACE (do not request these again unless you explain what is still missing):\n"
        + "\n".join(f"  - {name}" for name in present)
        + "\n"
        f"Known OPEN items: {', '.join(still_open) if still_open else 'none'}\n"
        f"Note: approval/rejection decisions are made by the Student Orchestrator, and the flow's math gate blocks "
        f"approval on code-confirmed math flaws.\n\n"
        f"{freshness}\n\n"
        f"Recent Operational Telemetry (Last {stats['recent_window_size']} Evaluations):\n"
        f"- Recent Window Approvals / Rejections: {stats['recent_window_approved']} approved, {stats['recent_window_rejected']} rejected\n"
        f"- Recent Window Rejection Reasons (Last {stats['recent_window_size']} runs): {json.dumps(stats['recent_window_rejection_counts'])}\n"
        f"- Recurring Need Themes in Recent Window: {json.dumps(stats['recent_need_themes'])}\n"
        f"- All-Time Historical Rejection Totals (older runs included): {json.dumps(stats['rejection_counts'])}\n"
        f"- Recent Researcher Needs: {json.dumps(stats['recent_researcher_needs'])}\n"
        f"- Recent Math Physicist Needs: {json.dumps(stats['recent_math_needs'])}\n\n"
        f"PROFESSOR'S QUESTION TO YOU:\n\"{question}\"\n\n"
        f"Respond candidly in first person as {role}. Base your diagnosis primarily on post-change results when "
        f"they exist, otherwise on the Recent Window, rather than legacy all-time totals. "
        f"Do NOT invoke external tools unless specifically asked to search for a topic; "
        f"focus on giving a clear, concrete, technically specific answer about your workflow, shortcomings, and tool/data wishlist."
    )


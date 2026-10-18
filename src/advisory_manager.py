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
        for mn in needs.get("math_needs") or []:
            if mn:
                window_needs_all.append(str(mn))

    return {
        "total_evaluations": total_runs,
        "approved_evaluations": approved_runs,
        "rejection_counts": dict(rejection_counts.most_common()),
        "recent_window_size": len(window_records),
        "recent_window_approved": window_approved,
        "recent_window_rejected": sum(window_rejections.values()),
        "recent_window_rejection_counts": dict(window_rejections.most_common()),
        "recent_need_themes": _classify_need_themes(window_needs_all),
        "recent_researcher_needs": researcher_needs[-limit:],
        "recent_math_needs": math_needs[-limit:],
        "recent_rejections": recent_rejections[-limit:],
    }


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

    lines.extend([
        "",
        "---",
        "",
        "## 🧞 2. Per-Agent Diagnostic Shortcomings & Wishlist",
        "",
        "### 🔭 A. Fundamental Physics Researcher & Cosmological Architect",
        "- **Equipped Tools**: `ArXiv Preprint Search`, `OpenAlex Scholarly Graph Search`, `Europe PMC Literature Search`, `Pre-Flight Citation Verifier`, `Observational Cosmology & Deep-Space Survey Tracker`, `Physics Calculator & Tension Evaluator`.",
        "- **Shortcomings Encountered During Tasks**:",
        "  1. **Abstract-Only Visibility on Long Derivations**: arXiv and OpenAlex return abstracts (~300–400 words) rather than full-text equation appendices, forcing the Researcher to reconstruct intermediate normalization factors (e.g., identical-particle $1/32\\pi$ vs $1/16\\pi$ phase space or conventions in Thomson scattering opacity $\\dot{\\kappa}$) from memory.",
        "  2. **Observational vs. Textbook Tension**: Standard training priors favor textbook $\\Lambda\\text{CDM}$ and minimal slow-roll inflation, whereas modern deep-space observations (JWST $z > 10\\text{–}14$ luminous galaxies & over-massive black holes, HST/JWST $H_0 \\approx 73\\text{ km s}^{-1}\\text{ Mpc}^{-1}$ vs Planck $67.4$, DESI dynamical dark energy $w_0 w_a\\text{CDM}$, and $S_8$ cosmic shear) often contradict baseline theory.",
        "  3. **Worked-Example Arithmetic Drift**: When adapting a formula to new benchmark parameters on retry, LLM mental arithmetic can slip by factors of $10^2\\text{–}10^3$ without a calculator tool.",
        "- **Agent Wishlist**:",
        "  * ✅ **[IMPLEMENTED]** `Observational Cosmology & Deep-Space Survey Tracker` tool providing direct access to JWST, Hubble (HST), DESI, Euclid, Planck, and NANOGrav observational tensions, verified DOIs, central values $\\pm 1\\sigma$, covariances, and $\\Delta\\chi^2$ benchmarks.",
        "  * ✅ **[IMPLEMENTED]** Structured `### Conventions & Symbol Table` and `### Validity Domain & Claim Scope` (`[GENERAL]` vs `[MODEL-DEPENDENT: ...]`) preamble inside `## 3. Mathematical Framework`.",
        "  * ✅ **[IMPLEMENTED]** **`Physics Calculator & Tension Evaluator` Tool (`PhysicsCalculatorTool`)** so worked numerical examples (e.g., Affleck-Dine baryon yield $n_B/s$, Hubble horizon expansion $\\lambda_{\\rm phys}(t_0)$ in meters, 1D Gaussian tension $\\sigma$, and 2D covariant $\\Delta\\chi^2$ for $(w_0, w_a)$) are computed in Python *before* the draft is submitted to the Math Physicist.",
        "  * 🎯 **[WISHLIST #1]** **arXiv Full-Text Section Extractor (HTML/LaTeX source snippet reader)** to pull exact Lagrangian conventions and coefficient definitions from primary papers when abstracts omit prefactors.",
        "",
        "### 🧮 B. Mathematical Physics Verifier (`z-ai/glm-5.3-flash`)",
        "- **Equipped Tools**: `Equation Extractor`, `Dimensional Consistency Checker`, `Topology Classifier`, `Numerical Benchmark Validator`, `Physics Calculator & Tension Evaluator`.",
        "- **Shortcomings Encountered During Tasks**:",
        "  1. **Context & Tool-Argument Token Bloat in Multi-Agent Debates**: Passing 50,000–75,000 characters of raw prose into `Equation Extractor` and `Topology Classifier` previously caused 180s OpenRouter timeouts.",
        "  2. **Natural-Units ($\\hbar = c = k_B = 1$) vs. SI Ambiguity**: In high-energy and cosmological formulas (e.g., one-pion-exchange potential, curvature-current baryogenesis $\\mathcal{L}_{\\rm int} = (\\partial_\\mu R) J_B^\\mu / M_*^2$, or comoving vs. physical number densities), dimensional consistency depends on declared mass dimensions $[\\phi] = E^1, [R] = E^2, [J^\\mu] = E^3$.",
        "- **Agent Wishlist**:",
        "  * ✅ **[IMPLEMENTED]** Concise equation-only extraction (<4,000 chars) and 25-equation relational prioritization to eliminate 180s tool-call timeouts.",
        "  * ✅ **[IMPLEMENTED]** Global Coherence Rule in Math Verification Report and `DimensionalConsistencyTool` (`CONSISTENT_WITH_UNDECIDABLE` vs `ALL_CONSISTENT`).",
        "  * ✅ **[IMPLEMENTED]** **Natural-Unit Mass-Dimension Evaluator (`[E]^n` checker)** alongside SI unit checking in `DimensionalConsistencyTool`, explicitly checking Lagrangian terms against $[\\mathcal{L}] = [E]^4$ in 4D spacetime and catching known algebraic/dimensional errors (e.g., $a^{-3(1+w(a))}$, $m_T^2 \\sim g^2 T^2 \\phi^2$, dropped $-2\\,\\mathrm{Cov}(A,B)$).",
        "  * ✅ **[IMPLEMENTED]** **20-Benchmark CODATA/PDG/Cosmology Table & `Physics Calculator & Tension Evaluator`** verifying numerical claims within 10% tolerance (`verify_claim`) and evaluating $\\Delta\\chi^2$ / $\\sigma$ tensions.",
        "  * 🎯 **[WISHLIST #1]** **Symbolic Re-Derivation & Perturbative Limit Evaluator (`SymPy` checker)**: A tool that symbolically checks continuity/ODE integrals (such as variable-$w(a)$ integration) and evaluates asymptotic limits ($a \\to 0$, $T \\gg m$, $k \\ll aH$).",
        "",
        "### ⚖️ C. Scientific Skeptic & Student Orchestrator",
        "- **Equipped Tools**: `Peer Review Critique Resolver`.",
        "- **Shortcomings Encountered During Tasks**:",
        "  1. **Convention Conflicts Across Multi-Attempt Retries**: When Researcher A and Researcher B in Level 2 use slightly different Fourier, metric signature $(-,+,+,+)$ vs $(+,-,-,-)$, or reduced vs. Planck mass ($M_{\\rm Pl} = 2.435\\times 10^{18}\\text{ GeV}$ vs $m_{\\rm Pl} = 1.22\\times 10^{19}\\text{ GeV}$) conventions, the synthesis can mix both.",
        "- **Agent Wishlist**:",
        "  * ✅ **[IMPLEMENTED]** **Shared Canonical Convention Header (`src/conventions.py`)** injected at the start of every Level 1/2/3 crew run and micro-revision (fixing reduced Planck mass $M_{\\rm Pl} = (8\\pi G)^{-1/2} = 2.435\\times 10^{18}\\text{ GeV}$, metric signature $(-,+,+,+)$, $g_{*s}(T)$ anchors, and Level 3 causal estimand/covariance requirements).",
    ])

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
    tool_names = [getattr(t, "name", str(t)) for t in (agent.tools or [])]
    stats = collect_historical_agent_shortcomings(limit=5, recent_window=100)

    prompt = (
        f"The Human Operator (Professor) is speaking to you directly in a 1-on-1 diagnostic session.\n"
        f"Your Role: {agent.role}\n"
        f"Your Currently Equipped Tools: {', '.join(tool_names) if tool_names else 'None (pure reasoning)'}\n"
        f"Recent Operational Telemetry (Last {stats['recent_window_size']} Evaluations — Current Production State):\n"
        f"- Recent Window Approvals / Rejections: {stats['recent_window_approved']} approved, {stats['recent_window_rejected']} rejected\n"
        f"- Recent Window Rejection Reasons (Last {stats['recent_window_size']} runs): {json.dumps(stats['recent_window_rejection_counts'])}\n"
        f"- Recurring Need Themes in Recent Window: {json.dumps(stats['recent_need_themes'])}\n"
        f"- All-Time Historical Rejection Totals (older runs included): {json.dumps(stats['rejection_counts'])}\n"
        f"- Recent Researcher Needs: {json.dumps(stats['recent_researcher_needs'])}\n"
        f"- Recent Math Physicist Needs: {json.dumps(stats['recent_math_needs'])}\n\n"
        f"PROFESSOR'S QUESTION TO YOU:\n\"{question}\"\n\n"
        f"Respond candidly in first person as {agent.role}. Base your diagnosis primarily on the Recent Window (last {stats['recent_window_size']} evaluations) telemetry rather than legacy all-time totals. "
        f"Do NOT invoke external tools unless specifically asked to search for a topic; "
        f"focus on giving a clear, concrete, technically specific answer about your workflow, shortcomings, and tool/data wishlist."
    )

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


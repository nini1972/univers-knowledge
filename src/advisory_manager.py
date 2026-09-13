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

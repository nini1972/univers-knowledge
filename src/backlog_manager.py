import os
import json
import re
import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = REPO_ROOT / "knowledge_base" / "logs"
BACKLOG_FILE = LOGS_DIR / "research_backlog.jsonl"
FOLLOWUPS_FILE = LOGS_DIR / "concept_followups.jsonl"


def _ensure_log_dir():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _get_utc_now():
    try:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()
    except AttributeError:
        return datetime.datetime.utcnow().isoformat() + "Z"


def is_question_text(text: str) -> bool:
    t = (text or "").strip()
    return t.endswith("?") or bool(
        re.match(r"^(what|how|can|which|are|is|does|why|to what extent|could|would)\b", t, re.IGNORECASE)
    )


def add_followup_questions(parent_concept: str, level: int, questions: list[str]):
    """Appends deep-dive evaluation follow-up questions to concept_followups.jsonl."""
    if not questions:
        return
    _ensure_log_dir()

    timestamp = _get_utc_now()
    existing = set()
    if FOLLOWUPS_FILE.exists():
        with open(FOLLOWUPS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        existing.add(data.get("question", "").strip().lower())
                    except Exception:
                        pass

    with open(FOLLOWUPS_FILE, "a", encoding="utf-8") as f:
        for q in questions:
            q_clean = q.strip()
            if not q_clean or q_clean.lower() in existing:
                continue

            entry = {
                "question": q_clean,
                "parent_concept": parent_concept,
                "level": level,
                "status": "pending",
                "category": "deep_dive",
                "timestamp": timestamp,
                "resolved_at": None,
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            print(f"[FOLLOWUP] Recorded research follow-up for '{parent_concept}': '{q_clean}'")


def add_to_backlog(parent_concept: str, level: int, questions: list[str]):
    """Backward-compatible wrapper: routes follow-up questions to concept_followups.jsonl."""
    add_followup_questions(parent_concept=parent_concept, level=level, questions=questions)


def add_curriculum_candidate(concept_name: str, level: int = 1, description: str = "", source: str = "curriculum_plan"):
    """Adds a genuine candidate concept to the curriculum research backlog."""
    clean_name = (concept_name or "").strip()
    if not clean_name:
        return
    _ensure_log_dir()

    timestamp = _get_utc_now()
    existing = set()
    if BACKLOG_FILE.exists():
        with open(BACKLOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        name = data.get("concept") or data.get("question") or ""
                        existing.add(name.strip().lower())
                    except Exception:
                        pass

    if clean_name.lower() in existing:
        return

    entry = {
        "concept": clean_name,
        "level": level,
        "description": description.strip(),
        "source": source,
        "status": "pending",
        "timestamp": timestamp,
        "resolved_at": None,
    }
    with open(BACKLOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[CURRICULUM BACKLOG] Added candidate topic: '{clean_name}' (Level {level})")


def get_next_backlog_item(level: int = None) -> dict | None:
    """Returns the oldest pending curriculum candidate item, strictly filtered by level."""
    if not BACKLOG_FILE.exists():
        return None

    with open(BACKLOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get("status") == "pending":
                    item_level = data.get("level")
                    if level is not None and item_level != level:
                        continue

                    concept_text = data.get("concept") or data.get("question") or ""
                    # Guard against lingering multi-sentence questions
                    if is_question_text(concept_text) and len(concept_text) > 80:
                        continue

                    # Standardize return dictionary
                    return {
                        "concept": concept_text,
                        "question": concept_text,
                        "level": item_level,
                        "description": data.get("description", ""),
                        "source": data.get("source", "curriculum"),
                        "timestamp": data.get("timestamp"),
                    }
            except Exception:
                pass
    return None


def get_candidate_curriculum_digest(level: int = None, limit: int = 5) -> str:
    """Returns a formatted digest of pending curriculum topics to guide the Student during topic selection."""
    if not BACKLOG_FILE.exists():
        return ""

    candidates = []
    with open(BACKLOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get("status") == "pending":
                    if level is None or data.get("level") == level:
                        name = (data.get("concept") or data.get("question") or "").strip()
                        if name and not is_question_text(name):
                            candidates.append(name)
                        if len(candidates) >= limit:
                            break
            except Exception:
                pass

    if not candidates:
        return ""
    return "\n".join(f"- {c}" for c in candidates)


def resolve_backlog_item(identifier: str):
    """Marks a backlog concept or follow-up question as resolved in both registries."""
    target = (identifier or "").strip().lower()
    if not target:
        return

    timestamp = _get_utc_now()

    def _resolve_in_file(filepath: Path):
        if not filepath.exists():
            return False
        resolved_any = False
        temp_entries = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    name = (data.get("concept") or data.get("question") or "").strip().lower()
                    if name == target and data.get("status") == "pending":
                        data["status"] = "resolved"
                        data["resolved_at"] = timestamp
                        resolved_any = True
                        print(f"[BACKLOG] Resolved: '{name}' in {filepath.name}")
                    temp_entries.append(data)
                except Exception:
                    pass

        if resolved_any:
            with open(filepath, "w", encoding="utf-8") as f:
                for entry in temp_entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return resolved_any

    _resolve_in_file(BACKLOG_FILE)
    _resolve_in_file(FOLLOWUPS_FILE)

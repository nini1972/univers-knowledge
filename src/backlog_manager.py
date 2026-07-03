import os
import json
import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKLOG_FILE = REPO_ROOT / "knowledge_base" / "logs" / "research_backlog.jsonl"

def _ensure_log_dir():
    BACKLOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def add_to_backlog(parent_concept: str, level: int, questions: list[str]):
    """Appends pending follow-up questions to the research backlog JSONL file."""
    if not questions:
        return
    _ensure_log_dir()
    
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    
    # Read existing questions to avoid duplicates
    existing = set()
    if BACKLOG_FILE.exists():
        with open(BACKLOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        existing.add(data["question"].strip().lower())
                    except Exception:
                        pass

    with open(BACKLOG_FILE, "a", encoding="utf-8") as f:
        for q in questions:
            q_clean = q.strip()
            if not q_clean or q_clean.lower() in existing:
                continue
            
            entry = {
                "question": q_clean,
                "parent_concept": parent_concept,
                "level": level,
                "status": "pending",
                "timestamp": timestamp,
                "resolved_at": None
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            print(f"[BACKLOG] Added pending research point: '{q_clean}' (Parent: {parent_concept})")

def get_next_backlog_item(level: int = None) -> dict:
    """Returns the oldest pending backlog item, optionally filtered by level."""
    if not BACKLOG_FILE.exists():
        return None
        
    with open(BACKLOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get("status") == "pending":
                    if level is None or data.get("level") == level:
                        return data
            except Exception:
                pass
    return None

def resolve_backlog_item(question: str):
    """Marks a backlog question as resolved."""
    if not BACKLOG_FILE.exists():
        return

    resolved_any = False
    temp_entries = []
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    
    with open(BACKLOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get("question").strip().lower() == question.strip().lower() and data.get("status") == "pending":
                    data["status"] = "resolved"
                    data["resolved_at"] = timestamp
                    resolved_any = True
                    print(f"[BACKLOG] Resolved backlog research point: '{data['question']}'")
                temp_entries.append(data)
            except Exception:
                pass
                
    if resolved_any:
        with open(BACKLOG_FILE, "w", encoding="utf-8") as f:
            for entry in temp_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

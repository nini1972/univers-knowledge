import json
import os
from datetime import datetime
from collections import Counter
from pathlib import Path

# Resolve workspace root (repo root)
REPO_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = REPO_ROOT / "knowledge_base" / "logs"

def _ensure_logs_dir():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

def log_evaluation_outcome(concept: str, status: str, reason_code: str, score: int = None, total_score: int = None, follow_up_questions: list = None, attempt: int = 1):
    """
    Appends an evaluation outcome to knowledge_base/logs/evaluation_runs.jsonl.
    """
    _ensure_logs_dir()
    log_file = LOGS_DIR / "evaluation_runs.jsonl"

    # Try to determine the attempt number dynamically if not provided or if we can read prior history
    if attempt == 1 and log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Count prior entries for this exact concept in this session/run if possible,
                # or just count overall attempts.
                attempts_found = sum(1 for line in lines if json.loads(line).get("concept") == concept)
                attempt = attempts_found + 1
        except Exception:
            pass

    record = {
        "concept": concept,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "attempt": attempt,
        "status": status,
        "reason_code": reason_code,
        "score": score,
        "total_score": total_score,
        "follow_up_questions": follow_up_questions or []
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def get_top_failure_patterns(limit: int = 3) -> list:
    """
    Reads prior run evaluations and identifies top recurring reason codes for rejections.
    Returns a list of dicts with count and description.
    """
    log_file = LOGS_DIR / "evaluation_runs.jsonl"
    if not log_file.exists():
        return []

    rejections = []
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("status") == "rejected":
                    rejections.append(record.get("reason_code", "unspecified"))
    except Exception:
        return []

    counts = Counter(rejections)
    top_reasons = counts.most_common(limit)

    friendly_messages = {
        "insufficient_sources": "citing fewer than 3 independent scientific sources",
        "lack_of_math_rigor": "insufficient mathematical grounding or missing LaTeX formulas",
        "insufficient_skeptic_score": "failing to meet the strict 5-point Skeptic verification checklist criteria",
        "lack_of_experimental_confirmation": "absence of direct empirical evidence without theoretical disclaimers",
        "parse_error": "failing to format the student evaluation strictly as machine-parseable JSON",
    }

    patterns = []
    for reason, count in top_reasons:
        desc = friendly_messages.get(reason, f"rejections categorized under '{reason}'")
        patterns.append(f"Avoid {desc} (encountered {count} time(s) previously)")

    return patterns


def log_telemetry_event(stage: str, event_type: str, duration_seconds: float = None, metadata: dict = None):
    """
    Appends a telemetry record to knowledge_base/logs/telemetry.jsonl.
    """
    _ensure_logs_dir()
    telemetry_file = LOGS_DIR / "telemetry.jsonl"

    record = {
        "stage": stage,
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "duration_seconds": duration_seconds,
        "metadata": metadata or {}
    }

    with open(telemetry_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def get_last_missing_prerequisite(index_content: str) -> str:
    """
    Reads telemetry.jsonl to find if the last Level 2 topic selection was blocked by a missing prerequisite.
    Only returns the missing prerequisite if it is not already present in the index.
    """
    telemetry_file = LOGS_DIR / "telemetry.jsonl"
    if not telemetry_file.exists():
        return None

    try:
        with open(telemetry_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Search backwards from the latest line
        for line in reversed(lines):
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("stage") == "topic_selection_level2" and record.get("event_type") == "end":
                metadata = record.get("metadata", {})
                if metadata.get("status") == "blocked_by_prerequisite":
                    missing = metadata.get("missing_prerequisite")
                    if missing and missing.lower() not in index_content.lower():
                        return missing
    except Exception as e:
        print(f"Warning: Failed to parse telemetry for prerequisites: {e}")

    return None


def log_rejected_concept(
    concept: str,
    level: int,
    reason_code: str,
    total_attempts: int,
    follow_up_questions: list = None,
    math_score=None,
    math_status: str = None,
    last_skeptic_score: int = None,
    last_skeptic_total: int = None,
):
    """
    Appends a permanently-rejected concept record to knowledge_base/logs/rejected_concepts.jsonl.
    Called when a concept exhausts all retries and is NOT saved to the knowledge base.

    Fields:
      - concept:              Name of the concept that was rejected.
      - level:                Pipeline level (1 or 2).
      - reason_code:          Final rejection reason from the Student.
      - total_attempts:       How many research/evaluation attempts were made.
      - follow_up_questions:  Questions the Student suggested for improvement.
      - math_score:           Math Physicist score (int or None).
      - math_status:          Math Physicist status string (e.g. MATH_CONSISTENT).
      - last_skeptic_score:   Skeptic score on the final attempt.
      - last_skeptic_total:   Skeptic total on the final attempt.
    """
    _ensure_logs_dir()
    log_file = LOGS_DIR / "rejected_concepts.jsonl"

    record = {
        "concept": concept,
        "level": level,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_attempts": total_attempts,
        "final_reason_code": reason_code,
        "follow_up_questions": follow_up_questions or [],
        "math_score": math_score,
        "math_status": math_status,
        "last_skeptic_score": last_skeptic_score,
        "last_skeptic_total": last_skeptic_total,
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=True) + "\n")

    print(
        f"[REJECTED LOG] '{concept}' recorded to rejected_concepts.jsonl "
        f"(attempts={total_attempts}, reason={reason_code}, math={math_score}, math_status={math_status})"
    )

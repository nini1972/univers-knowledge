import json
import os
from datetime import datetime, timezone
from collections import Counter
from pathlib import Path

# Resolve workspace root (repo root)
REPO_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = REPO_ROOT / "knowledge_base" / "logs"

def _ensure_logs_dir():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

def _get_utc_now():
    try:
        return datetime.now(timezone.utc).isoformat()
    except AttributeError:
        return datetime.utcnow().isoformat() + "Z"


def log_evaluation_outcome(
    concept: str,
    status: str,
    reason_code: str,
    score: int = None,
    total_score: int = None,
    follow_up_questions: list = None,
    attempt: int = 1,
    epistemic_status: str = "[THEORETICAL]",
    confidence_score: float = None,
    detailed_rationale: str = None,
    agent_needs: dict = None,
):
    """
    Appends an enriched evaluation outcome to knowledge_base/logs/evaluation_runs.jsonl.
    """
    _ensure_logs_dir()
    log_file = LOGS_DIR / "evaluation_runs.jsonl"

    if attempt == 1 and log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                attempts_found = sum(1 for line in lines if json.loads(line).get("concept") == concept)
                attempt = attempts_found + 1
        except Exception:
            pass

    record = {
        "concept": concept,
        "timestamp": _get_utc_now(),
        "attempt": attempt,
        "status": status,
        "reason_code": reason_code,
        "epistemic_status": epistemic_status,
        "confidence_score": confidence_score,
        "detailed_rationale": detailed_rationale,
        "agent_needs": agent_needs or {},
        "score": score,
        "total_score": total_score,
        "follow_up_questions": follow_up_questions or []
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def get_top_failure_patterns(limit: int = 3) -> list:
    """
    Reads prior run evaluations and identifies top recurring reason codes for rejections.
    Returns a list of strings with actionable guidance for the agents.
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
        "insufficient_independent_sources": "citing fewer than 3 independent scientific sources",
        "lack_of_math_rigor": "insufficient mathematical grounding or missing LaTeX formulas",
        "mathematical_flaw_or_inconsistency": "mathematical errors, unit mismatches, or dimensional inconsistencies",
        "insufficient_skeptic_score": "failing to meet the strict Skeptic verification checklist criteria",
        "ontological_category_error": "unifying incompatible physical or mathematical structures without rigorous mapping",
        "unfalsifiable_or_unmeasurable_scale": "predicting unmeasurable effect sizes without an empirical test protocol",
        "missing_empirical_anchoring": "asserting theoretical conjectures as proven physical facts without experimental constraints",
        "logical_fallacy_or_speculation": "unsubstantiated metaphysical speculation lacking physicalist grounding",
        "missing_critical_comparisons": "omitting core mathematical and empirical comparisons between competing theories",
        "lack_of_experimental_confirmation": "absence of direct empirical evidence without theoretical disclaimers",
        "parse_error": "failing to format the student evaluation strictly as machine-parseable JSON",
        "missing_math_equations": "failing to include formal LaTeX equations or mathematical models",
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
    epistemic_status: str = None,
    detailed_rationale: str = None,
    agent_needs: dict = None,
):
    """
    Appends a permanently-rejected concept record to knowledge_base/logs/rejected_concepts.jsonl.
    Called when a concept exhausts all retries and is NOT saved to the knowledge base.
    """
    _ensure_logs_dir()
    log_file = LOGS_DIR / "rejected_concepts.jsonl"

    record = {
        "concept": concept,
        "level": level,
        "timestamp": _get_utc_now(),
        "total_attempts": total_attempts,
        "final_reason_code": reason_code,
        "epistemic_status": epistemic_status,
        "detailed_rationale": detailed_rationale,
        "agent_needs": agent_needs or {},
        "follow_up_questions": follow_up_questions or [],
        "math_score": math_score,
        "math_status": math_status,
        "last_skeptic_score": last_skeptic_score,
        "last_skeptic_total": last_skeptic_total,
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(
        f"[REJECTED LOG] '{concept}' recorded to rejected_concepts.jsonl "
        f"(attempts={total_attempts}, reason={reason_code}, math={math_score}, math_status={math_status})"
    )

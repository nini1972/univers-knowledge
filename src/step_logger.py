"""Agent step callback utility.

Creates a JSONL log of every intermediate reasoning step produced by CrewAI
agents (Thought / Action / Observation / Final Answer).  Each run appends to
``logs/agent_steps.jsonl`` in the repository root so you can review what
agents were "thinking" after execution.

Usage::

    from step_logger import make_step_callback
    callback = make_step_callback("evaluation_crew")
    Crew(..., step_callback=callback)
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def make_step_callback(crew_label: str = "crew") -> Any:
    """Return a step_callback function that appends reasoning steps to a JSONL log.

    Args:
        crew_label: A short human-readable label for the crew, used to
                    distinguish entries from different crews in the log.

    Returns:
        A callable suitable for passing as ``Crew(step_callback=...)``.
    """
    repo_root = Path(__file__).resolve().parent.parent
    log_dir = repo_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "agent_steps.jsonl"

    def _callback(step_output: Any) -> None:
        entry = {
            "ts": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "crew": crew_label,
            "step": str(step_output),
        }
        try:
            with open(log_file, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as exc:
            # Never let logging failures break a run
            print(f"WARNING: step_logger could not write to {log_file}: {exc}")

    return _callback

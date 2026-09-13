"""
Backlog Triage and Migration Utility for Univers Knowledge Builder.

Analyzes knowledge_base/logs/research_backlog.jsonl, categorizing items into:
  1. TOPIC_FOLLOWUP: Legitimate deep-dive questions attached to an established concept.
  2. RECURSIVE_CHAIN: Sub-questions born from earlier questions (loop bug).
  3. ERRATUM_CITATION: Requests for citation or source fixes.
  4. RESOLVED: Previously resolved historical records.
  5. CURRICULUM_CONCEPT: Genuine concise physics topics.

Migrates follow-up questions to knowledge_base/logs/concept_followups.jsonl and
cleans research_backlog.jsonl to only contain true curriculum candidate topics.
"""

import argparse
import datetime
import json
import re
import shutil
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = REPO_ROOT / "knowledge_base" / "logs"
BACKLOG_FILE = LOGS_DIR / "research_backlog.jsonl"
FOLLOWUPS_FILE = LOGS_DIR / "concept_followups.jsonl"


def is_question_text(text: str) -> bool:
    t = text.strip()
    return t.endswith("?") or bool(
        re.match(r"^(what|how|can|which|are|is|does|why|to what extent|could|would)\b", t, re.IGNORECASE)
    )


def is_citation_erratum(text: str) -> bool:
    return bool(
        re.search(r"(bibliographic citation|correct.*citation|listed as arxiv)", text, re.IGNORECASE)
    )


def classify_item(item: dict) -> str:
    status = item.get("status")
    question = item.get("question", "").strip()
    parent = item.get("parent_concept", "").strip()

    if status == "resolved":
        return "RESOLVED"
    if is_citation_erratum(question):
        return "ERRATUM_CITATION"
    if is_question_text(parent):
        return "RECURSIVE_CHAIN"
    if is_question_text(question):
        return "TOPIC_FOLLOWUP"
    return "CURRICULUM_CONCEPT"


def run_triage(dry_run: bool = True):
    print("=" * 60)
    print(f"Backlog Triage & Migration {'[DRY RUN]' if dry_run else '[APPLYING CHANGES]'}")
    print("=" * 60)

    if not BACKLOG_FILE.exists():
        print(f"Error: Backlog file not found at {BACKLOG_FILE}")
        return

    # 1. Backup
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_file = LOGS_DIR / f"research_backlog.backup_{ts}.jsonl"
    if not dry_run:
        shutil.copy2(BACKLOG_FILE, backup_file)
        print(f"[*] Immutable backup created: {backup_file.name}")

    # 2. Read and Classify
    all_items = []
    with open(BACKLOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    all_items.append(json.loads(line))
                except Exception as exc:
                    print(f"Warning: Failed to parse line: {exc}")

    counts = Counter()
    level_counts = Counter()
    followups_to_save = []
    curriculum_candidates = []

    for item in all_items:
        category = classify_item(item)
        counts[category] += 1
        level = item.get("level", 1)
        level_counts[(level, category)] += 1

        if category in ("TOPIC_FOLLOWUP", "RECURSIVE_CHAIN", "ERRATUM_CITATION", "RESOLVED"):
            followup_entry = {
                "question": item.get("question", "").strip(),
                "parent_concept": item.get("parent_concept", "").strip(),
                "level": level,
                "status": "archived" if category in ("RECURSIVE_CHAIN", "ERRATUM_CITATION") else item.get("status", "pending"),
                "category": category.lower(),
                "timestamp": item.get("timestamp"),
                "resolved_at": item.get("resolved_at"),
            }
            followups_to_save.append(followup_entry)
        else:
            curriculum_candidates.append(item)

    print(f"\nTotal Records Analyzed: {len(all_items)}")
    print("-" * 40)
    for cat, c in counts.most_common():
        print(f"  {cat:<25}: {c}")

    print("\nBreakdown by Level and Category:")
    print("-" * 40)
    for (lvl, cat), c in sorted(level_counts.items()):
        print(f"  Level {lvl} - {cat:<22}: {c}")

    print(f"\nAction Summary:")
    print(f"  -> Moving to concept_followups.jsonl : {len(followups_to_save)} records")
    print(f"  -> Retaining in research_backlog.jsonl: {len(curriculum_candidates)} records")

    if dry_run:
        print("\n[DRY RUN] No files were modified. Run with --apply to commit changes.")
        return

    # 3. Write concept_followups.jsonl
    with open(FOLLOWUPS_FILE, "w", encoding="utf-8") as f:
        for entry in followups_to_save:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"\n[+] Successfully written {len(followups_to_save)} records to {FOLLOWUPS_FILE.name}")

    # 4. Write cleaned research_backlog.jsonl
    with open(BACKLOG_FILE, "w", encoding="utf-8") as f:
        for entry in curriculum_candidates:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[+] Successfully refreshed {BACKLOG_FILE.name} with {len(curriculum_candidates)} active curriculum items.")
    print("\nBacklog triage complete! The Student topic selection pipeline is now unclogged.")


def main():
    parser = argparse.ArgumentParser(description="Triage and clean research_backlog.jsonl")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    args = parser.parse_args()
    run_triage(dry_run=not args.apply)


if __name__ == "__main__":
    main()

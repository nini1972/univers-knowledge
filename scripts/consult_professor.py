"""
Professor Office Hours CLI — Univers Knowledge Builder

Interactive command-line tool for the Professor (human operator) to:
  - Review pending scientific and curriculum inquiries from the Student and specialist agents.
  - Answer inquiries to provide binding guidance for subsequent runs.
  - Issue standing directives for curriculum or epistemic thresholds.
  - Review answered consultation history.

Usage:
  python scripts/consult_professor.py [list]
  python scripts/consult_professor.py answer <id> "<your directive>"
  python scripts/consult_professor.py directive "<standing directive>" [--scope <all|level_1|level_2|level_3>]
  python scripts/consult_professor.py dismiss <id>
  python scripts/consult_professor.py history
"""

import argparse
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure src/ is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

try:
    import advisory_manager
except ImportError:
    from src import advisory_manager


def cmd_list(args):
    pending = advisory_manager.get_pending_requests(level=args.level)
    directives = advisory_manager.get_active_general_directives()

    print("=" * 70)
    print("🎓 PROFESSOR OFFICE HOURS — ADVISORY QUEUE")
    print("=" * 70)

    if directives:
        print("\n📜 Active Standing Directives:")
        for idx, d in enumerate(directives, 1):
            print(f"  {idx}. {d}")

    if not pending:
        print("\n✨ The advisory queue is clear! All agents are operating smoothly.")
        print("   No pending inquiries require your guidance.\n")
        return

    print(f"\n📬 Pending Inquiries from Student & Agents ({len(pending)}):")
    print("-" * 70)
    for p in pending:
        print(f"\n🆔 [{p['id']}] Level {p.get('level', 1)} | Concept: '{p.get('concept')}'")
        print(f"   Initiator: {p.get('initiator', 'Student')}")
        print(f"   Reason:    {p.get('reason_code', 'unspecified')}")
        print(f"   Question:  {p.get('question')}")
        if p.get("detailed_rationale"):
            print(f"   Rationale: {p.get('detailed_rationale')}")
        needs = p.get("agent_needs") or {}
        if needs.get("researcher_needs") or needs.get("math_needs"):
            print("   Agent Needs:")
            for rn in needs.get("researcher_needs", []):
                print(f"     - Researcher: {rn}")
            for mn in needs.get("math_needs", []):
                print(f"     - Math Physicist: {mn}")
        print(f"   👉 To answer: python scripts/consult_professor.py answer {p['id']} \"<guidance>\"")
    print("\n" + "=" * 70 + "\n")


def cmd_answer(args):
    target = args.id_or_concept
    response = args.response
    success = advisory_manager.answer_advisory_request(target, response)
    if success:
        print(f"✅ Successfully answered advisory inquiry '{target}'.")
        print(f"   Directive: \"{response}\"")
        print(f"   The Student and agents will ingest this directive on the next run.")
    else:
        print(f"❌ Error: Could not find a pending advisory request matching '{target}'.")


def cmd_directive(args):
    dir_id = advisory_manager.add_general_directive(args.text, topic_scope=args.scope)
    if dir_id:
        print(f"✅ Standing directive [{dir_id}] recorded for scope '{args.scope}':")
        print(f"   \"{args.text}\"")


def cmd_dismiss(args):
    target = args.id_or_concept
    success = advisory_manager.dismiss_request(target)
    if success:
        print(f"✅ Dismissed advisory inquiry '{target}'.")
    else:
        print(f"❌ Error: Could not find a pending advisory request matching '{target}'.")


def cmd_history(args):
    import json
    advisory_file = REPO_ROOT / "knowledge_base" / "logs" / "advisory_queue.jsonl"
    if not advisory_file.exists():
        print("No advisory history exists yet.")
        return

    print("=" * 70)
    print("📚 CONSULTATION HISTORY")
    print("=" * 70)
    count = 0
    with open(advisory_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("status") == "answered":
                count += 1
                print(f"\n[{rec['id']}] Concept: {rec.get('concept')} (L{rec.get('level', 1)})")
                print(f"  Question:  {rec.get('question')}")
                print(f"  Directive: \"{rec.get('professor_response')}\"")
                print(f"  Answered:  {rec.get('answered_at')}")

    if count == 0:
        print("\nNo answered consultations yet.")
    else:
        print(f"\nTotal answered consultations: {count}\n")


def cmd_sync(args):
    advisory_manager.sync_office_hours_markdown()
    print("✅ Successfully synchronized knowledge_base/PROFESSOR_OFFICE_HOURS.md")


def main():
    parser = argparse.ArgumentParser(description="Professor Office Hours CLI — Univers Knowledge Builder")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list
    list_parser = subparsers.add_parser("list", help="List pending advisory inquiries")
    list_parser.add_argument("--level", type=int, default=None, help="Filter by level (1, 2, or 3)")

    # answer
    ans_parser = subparsers.add_parser("answer", help="Answer a pending advisory inquiry")
    ans_parser.add_argument("id_or_concept", help="ID (e.g. adv-20260913-a1b2) or concept name")
    ans_parser.add_argument("response", help="The Professor directive or guidance text")

    # directive
    dir_parser = subparsers.add_parser("directive", help="Set a standing global directive")
    dir_parser.add_argument("text", help="The directive instruction")
    dir_parser.add_argument("--scope", default="all", help="Scope: all, level_1, level_2, level_3")

    # dismiss
    dis_parser = subparsers.add_parser("dismiss", help="Dismiss an advisory inquiry")
    dis_parser.add_argument("id_or_concept", help="ID or concept name to dismiss")

    # history
    subparsers.add_parser("history", help="View answered consultation history")

    # sync
    subparsers.add_parser("sync", help="Synchronize PROFESSOR_OFFICE_HOURS.md")

    args = parser.parse_args()

    if not args.command or args.command == "list":
        cmd_list(args if hasattr(args, "level") else argparse.Namespace(level=None))
    elif args.command == "answer":
        cmd_answer(args)
    elif args.command == "directive":
        cmd_directive(args)
    elif args.command == "dismiss":
        cmd_dismiss(args)
    elif args.command == "history":
        cmd_history(args)
    elif args.command == "sync":
        cmd_sync(args)


if __name__ == "__main__":
    main()

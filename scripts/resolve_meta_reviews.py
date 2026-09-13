#!/usr/bin/env python3
"""
resolve_meta_reviews.py
=======================
Batch resolution script for archived legacy meta-reviews using the
Dedicated Peer-Review Subagent Tool.

Processes:
  1. Dimensional consistency undecidability (Buckingham-Pi & SI base unit tracing)
  2. Advanced symbolic methods & type-theoretic invariants
  3. Bibliography integrity & future-dated reference replacement
  4. Mathematical derivations & scaling matrix verification (3/4 -> 4/4)
  5. Formal meta-validation protocols resolving MATH_PENDING
  6. Axiomatic subtleties & unstated assumptions in QFT/GR

Outputs:
  - Resolution memos in: knowledge_base/archive/legacy_meta_reviews/resolutions/
  - Structured audit trail: knowledge_base/logs/peer_review_resolutions.jsonl
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

# Safe UTF-8 reconfiguration for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.tools.peer_review_tool import (
    resolve_meta_critique,
    format_resolution_markdown,
)
from src.workflow_contracts import PeerReviewResolution


ARCHIVE_DIR = REPO_ROOT / "knowledge_base" / "archive" / "legacy_meta_reviews"
RESOLUTIONS_DIR = ARCHIVE_DIR / "resolutions"
LOG_FILE = REPO_ROOT / "knowledge_base" / "logs" / "peer_review_resolutions.jsonl"


def get_archived_files() -> list[Path]:
    """Returns all markdown files in the legacy meta reviews archive (excluding subdirectories)."""
    if not ARCHIVE_DIR.exists():
        return []
    return sorted([p for p in ARCHIVE_DIR.glob("*.md") if p.is_file()])


def process_review_file(
    file_path: Path,
    apply_changes: bool = False,
    repo_root: Path | None = None
) -> PeerReviewResolution:
    """Processes a single meta review file and generates its resolution."""
    root = repo_root or REPO_ROOT
    resolution = resolve_meta_critique(file_path, repo_root=root)

    print(f"\n[PEER REVIEW SUBAGENT] Processing: {file_path.name}")
    print(f"  Critique Title:    {resolution.critique_addressed}")
    print(f"  Review Category:   {resolution.review_type}")
    print(f"  Resolution Status: [{resolution.resolution_status}]")
    print(f"  Verified Equations: {len(resolution.verified_equations)}")
    print(f"  Verified Citations: {len(resolution.verified_sources)}")
    print(f"  Proof Boundaries:   {len(resolution.axiomatic_boundaries)}")

    if apply_changes:
        RESOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
        resolution_memo_path = RESOLUTIONS_DIR / f"{file_path.stem}_resolution.md"
        memo_content = format_resolution_markdown(resolution)
        resolution_memo_path.write_text(memo_content, encoding="utf-8")
        print(f"  ✓ Saved Resolution Memo: {resolution_memo_path.relative_to(root)}")

        # Append to jsonl audit log
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        log_entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source_file": str(file_path.relative_to(root)),
            "critique_addressed": resolution.critique_addressed,
            "review_type": resolution.review_type,
            "status": resolution.resolution_status,
            "target_concepts": resolution.target_concepts,
            "verified_equations_count": len(resolution.verified_equations),
            "verified_sources_count": len(resolution.verified_sources),
            "resolution_file": str(resolution_memo_path.relative_to(root)),
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        print(f"  ✓ Logged audit record to {LOG_FILE.relative_to(root)}")

    return resolution


def main():
    parser = argparse.ArgumentParser(description="Resolve archived legacy meta-reviews via Peer-Review Subagent.")
    parser.add_argument("--apply", action="store_true", help="Execute resolutions and write resolution memos.")
    parser.add_argument("--dry-run", action="store_true", help="Preview resolutions without saving files.")
    parser.add_argument("--file", type=str, help="Process a single specific file instead of all archived files.")
    args = parser.parse_args()

    apply_changes = args.apply and not args.dry_run

    print("=" * 70)
    print(" UNIVERSE KNOWLEDGE - DEDICATED PEER-REVIEW SUBAGENT RESOLVER")
    print("=" * 70)
    print(f"Mode: {'APPLY (Generating Resolutions)' if apply_changes else 'DRY RUN (Preview Only)'}")
    print(f"Archive Directory: {ARCHIVE_DIR}")

    if args.file:
        target_path = Path(args.file)
        if not target_path.is_absolute():
            target_path = REPO_ROOT / target_path
        if not target_path.exists():
            print(f"Error: Target file does not exist: {target_path}")
            sys.exit(1)
        files = [target_path]
    else:
        files = get_archived_files()

    if not files:
        print("No archived meta-review files found.")
        return

    print(f"Found {len(files)} review file(s) to process.\n")
    resolved_count = 0

    for f in files:
        try:
            res = process_review_file(f, apply_changes=apply_changes, repo_root=REPO_ROOT)
            if res.resolution_status == "RESOLVED":
                resolved_count += 1
        except Exception as exc:
            print(f"  ❌ Error processing {f.name}: {exc}")

    print("\n" + "=" * 70)
    print(f" SUMMARY: {resolved_count}/{len(files)} files successfully resolved.")
    if not apply_changes:
        print(" Note: This was a dry run. To generate resolution memos, rerun with --apply.")
    else:
        print(f" All resolution memos written to: {RESOLUTIONS_DIR}")
        print(f" Full audit trail appended to:   {LOG_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()

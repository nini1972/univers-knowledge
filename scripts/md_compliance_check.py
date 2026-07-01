"""
md_compliance_check.py
----------------------
Audits all knowledge base markdown files for structural compliance:
  - YAML frontmatter: title, level, status, math_status, math_score
  - Required sections: 1-7 (mandatory), 8-9 (math engine, soft check)

Usage:
    uv run python scripts/md_compliance_check.py
    uv run python scripts/md_compliance_check.py --level 1
    uv run python scripts/md_compliance_check.py --verbose
    uv run python scripts/md_compliance_check.py --fail-on-soft
"""
import re
import sys
import argparse
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
KB_DIR = REPO_ROOT / "knowledge_base"

LEVELS = {
    "1": KB_DIR / "level_1_fundamental_physics",
    "2": KB_DIR / "level_2_advanced_frameworks",
    "3": KB_DIR / "level_3_speculative_models",
}

REQUIRED_YAML_KEYS = ["title:", "level:", "status:", "sources:"]
SOFT_YAML_KEYS     = ["math_status:", "math_score:"]

REQUIRED_SECTIONS = [
    "## 1.", "## 2.", "## 3.", "## 4.",
    "## 5.", "## 6.", "## 7.",
]
SOFT_SECTIONS = ["## 8.", "## 9."]

VALID_MATH_STATUSES = {
    "MATH_PROVEN", "MATH_CONSISTENT", "MATH_TOPOLOGICAL",
    "MATH_CONJECTURED", "MATH_FLAWED", "MATH_PENDING",
}

# ── Checker ───────────────────────────────────────────────────────────────────

def check_file(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    errors   = []   # hard failures
    warnings = []   # soft / expected-to-improve

    # 1. Frontmatter presence
    fm_match = re.search(r"^---\s*\n([\s\S]*?)\n---", text)
    if not fm_match:
        errors.append("MISSING YAML frontmatter block")
        fm_text = ""
    else:
        fm_text = fm_match.group(1).lower()

        # 2. Required YAML keys
        for key in REQUIRED_YAML_KEYS:
            if key not in fm_text:
                errors.append(f"YAML missing required key: {key}")

        # 3. Soft YAML keys (math fields)
        for key in SOFT_YAML_KEYS:
            if key not in fm_text:
                warnings.append(f"YAML missing math field: {key}")
            elif key == "math_status:":
                # Validate the value is a known status
                m = re.search(r"math_status:\s*[\"']?\[?(\w+)\]?[\"']?", fm_match.group(1), re.IGNORECASE)
                if m:
                    val = m.group(1).upper()
                    if val not in VALID_MATH_STATUSES:
                        warnings.append(f"math_status has unknown value: {val}")

    # 4. Top-level heading
    if not re.search(r"^#\s+.+", text, re.MULTILINE):
        errors.append("MISSING top-level heading (# Title)")

    # 5. Required sections
    for s in REQUIRED_SECTIONS:
        if s not in text:
            errors.append(f"MISSING required section: {s}...")

    # 6. Soft sections (math)
    for s in SOFT_SECTIONS:
        if s not in text:
            warnings.append(f"Math section not present: {s}... (added by enrichment pipeline)")

    return errors, warnings


# ── Report ────────────────────────────────────────────────────────────────────

def run(level_filter=None, verbose=False, fail_on_soft=False):
    total = 0
    fully_compliant = 0
    soft_only = 0
    hard_failures = 0
    math_ok = 0

    math_status_counts = {}
    hard_fail_files = []
    soft_warn_files = []

    levels_to_check = {k: v for k, v in LEVELS.items()
                       if level_filter is None or k == level_filter}

    for level_id, folder in sorted(levels_to_check.items()):
        if not folder.exists():
            continue
        md_files = sorted(folder.glob("*.md"))
        if not md_files:
            continue

        print(f"\n{'='*60}")
        print(f"  Level {level_id}: {folder.name}  ({len(md_files)} docs)")
        print(f"{'='*60}")

        for f in md_files:
            total += 1
            errors, warnings = check_file(f)

            # Collect math_status
            text = f.read_text(encoding="utf-8", errors="ignore")
            ms_match = re.search(r"math_status:\s*[\"']?\[?(\w+)\]?[\"']?", text, re.IGNORECASE)
            ms_val = ms_match.group(1).upper() if ms_match else "MISSING"
            math_status_counts[ms_val] = math_status_counts.get(ms_val, 0) + 1
            if ms_val in ("MATH_PROVEN", "MATH_CONSISTENT", "MATH_TOPOLOGICAL"):
                math_ok += 1

            if errors:
                hard_failures += 1
                hard_fail_files.append((f.name, errors, warnings))
                icon = "FAIL"
            elif warnings:
                soft_only += 1
                soft_warn_files.append((f.name, warnings))
                icon = "WARN"
            else:
                fully_compliant += 1
                icon = "OK  "

            if verbose or errors:
                print(f"  [{icon}] {f.stem}")
                for e in errors:
                    print(f"         ERROR: {e}")
                for w in warnings:
                    print(f"         warn : {w}")
            elif icon == "WARN" and verbose:
                print(f"  [{icon}] {f.stem}")
                for w in warnings:
                    print(f"         warn : {w}")
            else:
                if not verbose:
                    if icon != "OK  ":
                        print(f"  [{icon}] {f.stem}")

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  COMPLIANCE SUMMARY")
    print(f"{'='*60}")
    print(f"  Total docs checked : {total}")
    print(f"  Fully compliant    : {fully_compliant}  (all fields + math sections present)")
    print(f"  Soft warnings only : {soft_only}  (missing math fields/sections only)")
    print(f"  Hard failures      : {hard_failures}  (missing required structure)")
    print(f"  Math OK (3 statuses): {math_ok}  (PROVEN + CONSISTENT + TOPOLOGICAL)")
    print()
    print(f"  Math Status Breakdown:")
    for status, count in sorted(math_status_counts.items(), key=lambda x: -x[1]):
        bar = "#" * count
        print(f"    {status:<22} {count:>3}  {bar}")

    if hard_fail_files:
        print(f"\n  HARD FAILURES ({len(hard_fail_files)} files):")
        for fname, errs, warns in hard_fail_files:
            print(f"    - {fname}")
            for e in errs:
                print(f"        ERROR: {e}")

    print(f"\n  Tip: run with --verbose to see all files")
    print(f"  Tip: run with --level 1 to check one level only")
    print()

    exit_code = 0
    if hard_failures > 0:
        exit_code = 1
    if fail_on_soft and soft_only > 0:
        exit_code = 2
    return exit_code


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit knowledge base MD compliance")
    parser.add_argument("--level", choices=["1", "2", "3"], default=None,
                        help="Only check a specific level")
    parser.add_argument("--verbose", action="store_true",
                        help="Show all files including OK ones")
    parser.add_argument("--fail-on-soft", action="store_true",
                        help="Exit with code 2 if any soft warnings found")
    args = parser.parse_args()

    code = run(
        level_filter=args.level,
        verbose=args.verbose,
        fail_on_soft=args.fail_on_soft,
    )
    sys.exit(code)

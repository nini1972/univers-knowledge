import re
import subprocess
import sys
from pathlib import PurePosixPath

BLOCKED_PATH_PATTERNS = (
    re.compile(r"^\.env(?:\.|$)"),
    re.compile(r"(^|/)__pycache__(/|$)"),
    re.compile(r"\.py[co]$"),
)

# Focused patterns for common secret formats.
SECRET_PATTERNS = (
    re.compile(r"OPENAI_API_KEY\s*=\s*sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(result.stderr.strip() or "Git command failed.")
        sys.exit(2)
    return result.stdout


def get_staged_files() -> list[str]:
    raw = run_git("diff", "--cached", "--name-only", "-z")
    if not raw:
        return []
    parts = raw.split("\0")
    return [p.replace("\\", "/") for p in parts if p]


def has_blocked_path(path: str) -> bool:
    normalized = str(PurePosixPath(path))
    return any(pattern.search(normalized) for pattern in BLOCKED_PATH_PATTERNS)


def get_staged_added_lines() -> list[str]:
    diff = run_git("diff", "--cached", "--no-color", "-U0")
    added = []
    for line in diff.splitlines():
        if line.startswith("+++"):
            continue
        if line.startswith("+"):
            added.append(line[1:])
    return added


def main() -> int:
    staged_files = get_staged_files()

    blocked_files = [p for p in staged_files if has_blocked_path(p)]
    if blocked_files:
        print("Commit blocked: forbidden files are staged:")
        for path in blocked_files:
            print(f"  - {path}")
        print("\nRemove them from the commit and try again.")
        return 1

    added_lines = get_staged_added_lines()
    for line in added_lines:
        if any(pattern.search(line) for pattern in SECRET_PATTERNS):
            print("Commit blocked: potential secret detected in staged changes.")
            print("Review staged diff and remove or rotate secret values before commit.")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

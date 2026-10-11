import sys
import os
from pathlib import Path

# Ensure virtual environment site-packages are loaded for AppLocker/policy compliance
VENV_SITE_PACKAGES = Path(__file__).resolve().parent.parent / ".venv" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists():
    import site
    site.addsitedir(str(VENV_SITE_PACKAGES))
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Ensure UTF-8 output encoding across environments
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv

try:
    from universe_flow import UniverseFlow, update_index_file as _flow_update_index
except ImportError:
    from src.universe_flow import UniverseFlow, update_index_file as _flow_update_index


def read_index(filepath: str) -> str:
    """Read the current knowledge base index content."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Index not found. Start with basic physics."


def update_index_file(index_path: str, concept_name: str = "", level_folder: str = "", filename: str = ""):
    """Backward-compatible helper to synchronize the index file and OKF graph."""
    repo_root = Path(__file__).resolve().parent.parent
    _flow_update_index(index_path, repo_root)


def run_level1_flow(next_concept: str = None, dry_run: bool = None):
    """Core Level 1 learning, research, verification, and documentation workflow delegated to UniverseFlow."""
    load_dotenv()
    if dry_run is None:
        dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

    flow = UniverseFlow()
    inputs = {
        "level": 1,
        "dry_run": dry_run,
    }
    if next_concept:
        inputs["concept"] = next_concept

    return flow.kickoff(inputs=inputs)


def main():
    """Main CLI entrypoint for Level 1 Autonomous Student Execution."""
    import argparse
    load_dotenv()

    parser = argparse.ArgumentParser(description="Level 1 Fundamental Physics Orchestrator")
    parser.add_argument("--concept", type=str, default="", help="Specific concept to research (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Execute in dry-run mode without external LLM calls")
    args, _ = parser.parse_known_args()

    dry_run = args.dry_run or os.getenv("DRY_RUN", "false").lower() == "true"
    concept = args.concept or None

    run_level1_flow(next_concept=concept, dry_run=dry_run)


if __name__ == "__main__":
    main()

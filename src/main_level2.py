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
    from universe_flow import UniverseFlow, _extract_level2_selection, update_index_file as _flow_update_index
except ImportError:
    from src.universe_flow import UniverseFlow, _extract_level2_selection, update_index_file as _flow_update_index


def update_index_file(index_path: str, concept_name: str = "", level_folder: str = "", filename: str = ""):
    """Backward-compatible helper to synchronize the index file and OKF graph."""
    repo_root = Path(__file__).resolve().parent.parent
    _flow_update_index(index_path, repo_root)


def run_level2_flow(concept: str = None, dry_run: bool = None):
    """Core Level 2 Advanced Frameworks debate workflow delegated to UniverseFlow."""
    load_dotenv()
    if "OPENROUTER_MODEL_MATH" not in os.environ and "OPENROUTER_MODEL_RESEARCHER" in os.environ:
        os.environ["OPENROUTER_MODEL_MATH"] = os.environ["OPENROUTER_MODEL_RESEARCHER"]

    if dry_run is None:
        dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

    flow = UniverseFlow()
    inputs = {
        "level": 2,
        "dry_run": dry_run,
    }
    if concept:
        inputs["concept"] = concept

    return flow.kickoff(inputs=inputs)


def main():
    """Main CLI entrypoint for Level 2 Advanced Frameworks Execution."""
    import argparse
    load_dotenv()

    parser = argparse.ArgumentParser(description="Level 2 Advanced Frameworks Orchestrator")
    parser.add_argument("--concept", type=str, default="", help="Specific debate concept to research (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Execute in dry-run mode without external LLM calls")
    args, _ = parser.parse_known_args()

    dry_run = args.dry_run or os.getenv("DRY_RUN", "false").lower() == "true"
    concept = args.concept or None

    run_level2_flow(concept=concept, dry_run=dry_run)


if __name__ == "__main__":
    main()

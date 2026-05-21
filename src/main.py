import os
import re
import json
from pathlib import Path
from dotenv import load_dotenv
from crewai import Crew, Process

from agents.universe_agents import UniverseAgents
from tasks.universe_tasks import UniverseTasks
try:
    from workflow_contracts import (
        parse_student_decision,
        normalize_markdown_output,
        validate_concept_markdown,
    )
except ImportError:
    from src.workflow_contracts import (
        parse_student_decision,
        normalize_markdown_output,
        validate_concept_markdown,
    )
try:
    from index_utils import index_heading_for_level, prune_stale_index_links, sanitize_index_file
except ImportError:
    from src.index_utils import index_heading_for_level, prune_stale_index_links, sanitize_index_file

def read_index(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Index not found. Start with basic physics."

def sanitize_filename(name):
    # Convert "The Standard Model!" to "the_standard_model.md"
    s = re.sub(r'[^a-zA-Z0-9\s]', '', name).strip().replace(' ', '_').lower()
    return f"{s}.md"


def update_index_file(index_path: str, concept_name: str, level_folder: str, filename: str):
    """Deterministically merge new concept into index without LLM rewriting."""
    repo_root = Path(__file__).resolve().parent.parent
    idx = repo_root / index_path
    if not idx.exists():
        idx.parent.mkdir(parents=True, exist_ok=True)
        idx.write_text("# Knowledge Base Index\n\n", encoding="utf-8")

    lines = idx.read_text(encoding="utf-8").splitlines()
    lines = prune_stale_index_links(lines, repo_root)

    heading = index_heading_for_level(level_folder, "## Level 1: Fundamental Physics")
    link_rel = f"{level_folder}/{filename}"
    entry = f"- [{concept_name}]({link_rel})"

    if any(entry == line.strip() for line in lines):
        idx.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return

    if heading not in lines:
        if lines and lines[-1].strip() != "":
            lines.append("")
        lines.extend([heading, "", entry])
        idx.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return

    h_idx = lines.index(heading)
    insert_at = h_idx + 1
    while insert_at < len(lines) and not lines[insert_at].startswith("## "):
        insert_at += 1

    section_lines = lines[h_idx + 1:insert_at]
    if section_lines and section_lines[0].strip() != "":
        lines.insert(h_idx + 1, "")
        insert_at += 1
    lines.insert(insert_at, entry)

    idx.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main():
    load_dotenv()
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    index_path = "knowledge_base/_index.md"
    current_index = sanitize_index_file(index_path, Path(__file__).resolve().parent.parent)

    # Initialize Agents
    agents = UniverseAgents()

    # Use a dedicated student instance for the topic-selection crew so its
    # executor state does not bleed into the main research crew below.
    topic_student = agents.student_agent()

    researcher = agents.researcher_agent()
    skeptic = agents.skeptic_agent()
    archivist = agents.archivist_agent()
    has_genmedia_credentials = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    visualizer = agents.visualizer_agent() if has_genmedia_credentials else None
    if not has_genmedia_credentials:
        print("WARNING: GOOGLE_APPLICATION_CREDENTIALS is not set; skipping visual generation task.")

    # Initialize Tasks
    tasks = UniverseTasks()
    
    print("--- STEP 1: Determine Next Topic ---")
    topic_task = tasks.determine_next_topic_task(topic_student, current_index)
    topic_crew = Crew(agents=[topic_student], tasks=[topic_task], verbose=True)
    
    if dry_run:
        # Keep local dry-runs deterministic and API-free when needed.
        next_concept = "Quantum Entanglement"
    else:
        # Run the Student first to decide what to learn in this cycle.
        next_concept = topic_crew.kickoff()
    
    next_concept = str(next_concept).strip()
    print(f"Target Concept Selected: {next_concept}")
    
    # We dynamically create the output paths based on the Student's decision
    filename = sanitize_filename(next_concept)
    # For now, default to level 1. A more advanced Student could decide the level dynamically.
    level_folder = "level_1_fundamental_physics" 
    output_location = f"knowledge_base/{level_folder}/{filename}"

    # Never overwrite existing concept files during automated runs.
    repo_root = Path(__file__).resolve().parent.parent
    if (repo_root / output_location).exists():
        print(f"Concept file already exists, skipping write: {output_location}")
        return

    print("--- STEP 2: Research & Verification ---")

    # Fresh student instance for the research crew — avoids the
    # "Executor is already running" RuntimeError caused by reusing the
    # same agent object that was already used in topic_crew above.
    research_student = agents.student_agent()

    research_task = tasks.research_concept_task(researcher, next_concept)
    verify_task = tasks.verify_research_task(skeptic, next_concept)
    evaluate_task = tasks.student_evaluation_task(research_student, next_concept)

    evaluation_crew = Crew(
        agents=[research_student, researcher, skeptic],
        tasks=[research_task, verify_task, evaluate_task],
        process=Process.sequential,
        verbose=True
    )
    
    if dry_run:
        evaluation_output = json.dumps({
            "status": "approved",
            "reason_code": "dry_run",
            "summary_for_archivist": f"Dry-run approved summary for {next_concept}.",
            "follow_up_questions": []
        })
    else:
        evaluation_output = str(evaluation_crew.kickoff()).strip()

    decision = parse_student_decision(evaluation_output)
    if decision["status"] != "approved":
        print(
            "Concept rejected by Student decision contract. "
            f"reason_code={decision['reason_code']} follow_up_questions={decision['follow_up_questions']}"
        )
        return

    print("--- STEP 3: Documentation & Validation ---")

    visual_task = tasks.generate_visual_concept_task(visualizer, next_concept) if visualizer else None
    document_task = tasks.document_knowledge_task(
        archivist,
        output_location,
        include_visual=bool(visual_task),
        approved_summary=decision["summary_for_archivist"],
    )

    final_agents = [archivist]
    final_tasks = []
    if visualizer and visual_task:
        final_agents.insert(0, visualizer)
        final_tasks.append(visual_task)
    final_tasks.append(document_task)

    final_crew = Crew(
        agents=final_agents,
        tasks=final_tasks,
        process=Process.sequential,
        verbose=True
    )

    if dry_run:
        print("DRY_RUN enabled. Skipping final_crew.kickoff().")
        return

    document_output = normalize_markdown_output(str(final_crew.kickoff()).strip())
    valid, validation_errors = validate_concept_markdown(document_output)
    if not valid:
        print("ERROR: Document validation failed; file/index update was blocked.")
        for err in validation_errors:
            print(f" - {err}")
        return

    output_file = repo_root / output_location
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(document_output.rstrip() + "\n", encoding="utf-8")
    update_index_file(index_path, next_concept, level_folder, filename)
    print(f"Workflow complete: wrote validated document to {output_location}")

if __name__ == "__main__":
    main()

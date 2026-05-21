import os
import re
from pathlib import Path
from dotenv import load_dotenv
from crewai import Crew, Process

from agents.universe_agents import UniverseAgents
from tasks.universe_tasks import UniverseTasks
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
    student = agents.student_agent()
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
    topic_task = tasks.determine_next_topic_task(student, current_index)
    topic_crew = Crew(agents=[student], tasks=[topic_task], verbose=True)
    
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

    print("--- STEP 2: Research & Verification Loop ---")
    
    research_task = tasks.research_concept_task(researcher, next_concept)
    verify_task = tasks.verify_research_task(skeptic, next_concept)
    evaluate_task = tasks.student_evaluation_task(student, next_concept)
    visual_task = tasks.generate_visual_concept_task(visualizer, next_concept) if visualizer else None
    document_task = tasks.document_knowledge_task(
        archivist,
        output_location,
        include_visual=bool(visual_task)
    )

    crew_agents = [student, researcher, skeptic, archivist]
    crew_tasks = [research_task, verify_task, evaluate_task]
    if visualizer and visual_task:
        crew_agents.append(visualizer)
        crew_tasks.append(visual_task)
    crew_tasks.append(document_task)

    # Instantiate the Crew
    universe_crew = Crew(
        agents=crew_agents,
        tasks=crew_tasks,
        process=Process.sequential,
        verbose=True
    )
    
    # Execute the core workflow
    if dry_run:
        print("DRY_RUN enabled. Skipping universe_crew.kickoff().")
    else:
        result = universe_crew.kickoff()
        update_index_file(index_path, next_concept, level_folder, filename)
        print("Workflow complete:", result)

if __name__ == "__main__":
    main()

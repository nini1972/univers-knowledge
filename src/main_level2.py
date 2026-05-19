import os
import re
from pathlib import Path
from dotenv import load_dotenv
from crewai import Crew, Process

from agents.universe_agents import UniverseAgents
from tasks.universe_tasks import UniverseTasks


def _index_heading_for_level(level_folder: str) -> str:
    mapping = {
        "level_1_fundamental_physics": "## Level 1: Fundamental Physics",
        "level_2_advanced_frameworks": "## Level 2: Advanced Frameworks",
    }
    return mapping.get(level_folder, "## Level 2: Advanced Frameworks")


def _prune_stale_index_links(index_lines, repo_root: Path):
    out = []
    for line in index_lines:
        match = re.search(r"\[[^\]]+\]\(([^)]+\.md)\)", line)
        if match and line.lstrip().startswith("-"):
            target = repo_root / "knowledge_base" / match.group(1)
            if not target.exists():
                continue
        out.append(line)
    return out


def sanitize_index_file(index_path: str):
    repo_root = Path(__file__).resolve().parent.parent
    idx = repo_root / index_path
    if not idx.exists():
        return
    lines = idx.read_text(encoding="utf-8").splitlines()
    lines = _prune_stale_index_links(lines, repo_root)
    idx.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _ensure_index_file(idx: Path):
    if idx.exists():
        return
    idx.parent.mkdir(parents=True, exist_ok=True)
    idx.write_text("# Knowledge Base Index\n\n", encoding="utf-8")


def _append_entry_under_new_heading(lines, heading: str, entry: str):
    if lines and lines[-1].strip() != "":
        lines.append("")
    lines.extend([heading, "", entry])
    return lines


def _insert_entry_under_existing_heading(lines, heading: str, entry: str):
    h_idx = lines.index(heading)
    insert_at = h_idx + 1
    while insert_at < len(lines) and not lines[insert_at].startswith("## "):
        insert_at += 1

    section_lines = lines[h_idx + 1:insert_at]
    if section_lines and section_lines[0].strip() != "":
        lines.insert(h_idx + 1, "")
        insert_at += 1
    lines.insert(insert_at, entry)
    return lines


def update_index_file(index_path: str, concept_name: str, level_folder: str, filename: str):
    repo_root = Path(__file__).resolve().parent.parent
    idx = repo_root / index_path
    _ensure_index_file(idx)

    lines = idx.read_text(encoding="utf-8").splitlines()
    lines = _prune_stale_index_links(lines, repo_root)

    heading = _index_heading_for_level(level_folder)
    link_rel = f"{level_folder}/{filename}"
    entry = f"- [{concept_name}]({link_rel})"

    if not any(entry == line.strip() for line in lines):
        if heading in lines:
            lines = _insert_entry_under_existing_heading(lines, heading, entry)
        else:
            lines = _append_entry_under_new_heading(lines, heading, entry)

    idx.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

def main():
    load_dotenv()
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    index_path = "knowledge_base/_index.md"
    sanitize_index_file(index_path)

    # Initialize Agents
    agents = UniverseAgents()
    student = agents.student_agent()
    researcher = agents.researcher_agent()
    skeptic = agents.skeptic_agent()
    visualizer = agents.visualizer_agent()
    archivist = agents.archivist_agent()

    # Initialize Tasks
    tasks = UniverseTasks()
    
    theory_a = "String Theory"
    theory_b = "Loop Quantum Gravity"
    concept_name = "Quantum Gravity Debate"
    level_folder = "level_2_advanced_frameworks"
    filename = "quantum_gravity_debate.md"
    output_location = "knowledge_base/level_2_advanced_frameworks/quantum_gravity_debate.md"

    repo_root = Path(__file__).resolve().parent.parent
    if (repo_root / output_location).exists():
        print(f"Concept file already exists, skipping write: {output_location}")
        return
    
    # 1. Research both approaches
    research_task_a = tasks.research_concept_task(researcher, theory_a)
    research_task_b = tasks.research_concept_task(researcher, theory_b)
    
    # 2. Skeptic debates them
    debate_task = tasks.debate_theories_task(skeptic, theory_a, theory_b)
    
    # 3. Student evaluates the debate
    evaluate_task = tasks.student_evaluation_task(student, f"The debate between {theory_a} and {theory_b}")
    
    # 4. Visualizer creates a prompt to illustrate the competing concepts
    visual_task = tasks.generate_visual_concept_task(visualizer, "Quantum Gravity Approaches")

    # 5. Archivist formats the final theoretical document
    document_task = tasks.document_knowledge_task(archivist, output_location)

    # Instantiate the Crew
    advanced_crew = Crew(
        agents=[researcher, skeptic, student, visualizer, archivist],
        tasks=[
            research_task_a, 
            research_task_b, 
            debate_task, 
            evaluate_task, 
            visual_task,
            document_task
        ],
        process=Process.sequential,
        verbose=True
    )

    print("Phase 3: Level 2 Advanced Frameworks Orchestration Ready.")
    print(f"Beginning debate on: {theory_a} vs {theory_b}")
    
    # Execute the workflow
    if dry_run:
        print("DRY_RUN enabled. Skipping advanced_crew.kickoff().")
    else:
        result = advanced_crew.kickoff()
        update_index_file(index_path, concept_name, level_folder, filename)
        print("Workflow complete:", result)

if __name__ == "__main__":
    main()

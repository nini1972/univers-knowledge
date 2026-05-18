import os
import re
from dotenv import load_dotenv
from crewai import Crew, Process

from agents.universe_agents import UniverseAgents
from tasks.universe_tasks import UniverseTasks

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

def main():
    load_dotenv()
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    index_path = "../knowledge_base/_index.md"
    current_index = read_index(index_path)

    # Initialize Agents
    agents = UniverseAgents()
    student = agents.student_agent()
    researcher = agents.researcher_agent()
    skeptic = agents.skeptic_agent()
    visualizer = agents.visualizer_agent()
    archivist = agents.archivist_agent()

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
    output_location = f"../knowledge_base/{level_folder}/{filename}"

    print("--- STEP 2: Research & Verification Loop ---")
    
    research_task = tasks.research_concept_task(researcher, next_concept)
    verify_task = tasks.verify_research_task(skeptic, next_concept)
    evaluate_task = tasks.student_evaluation_task(student, next_concept)
    visual_task = tasks.generate_visual_concept_task(visualizer, next_concept)
    document_task = tasks.document_knowledge_task(archivist, output_location)
    update_index_task = tasks.update_index_task(archivist, index_path, next_concept, level_folder)

    # Instantiate the Crew
    universe_crew = Crew(
        agents=[student, researcher, skeptic, visualizer, archivist],
        tasks=[
            research_task, 
            verify_task, 
            evaluate_task, 
            visual_task,
            document_task, 
            update_index_task
        ],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute the core workflow
    if dry_run:
        print("DRY_RUN enabled. Skipping universe_crew.kickoff().")
    else:
        result = universe_crew.kickoff()
        print("Workflow complete:", result)

if __name__ == "__main__":
    main()

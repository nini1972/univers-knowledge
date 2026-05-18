import os
from dotenv import load_dotenv
from crewai import Crew, Process

from agents.universe_agents import UniverseAgents
from tasks.universe_tasks import UniverseTasks

def main():
    load_dotenv()
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

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
    output_location = "../knowledge_base/level_2_advanced_frameworks/quantum_gravity_debate.md"
    
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
        print("Workflow complete:", result)

if __name__ == "__main__":
    main()

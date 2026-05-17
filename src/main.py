import os
from dotenv import load_dotenv
from crewai import Crew, Process

from agents.universe_agents import UniverseAgents
from tasks.universe_tasks import UniverseTasks

def main():
    load_dotenv()

    # Initialize Agents
    agents = UniverseAgents()
    student = agents.student_agent()
    researcher = agents.researcher_agent()
    skeptic = agents.skeptic_agent()
    archivist = agents.archivist_agent()

    # Initialize Tasks
    tasks = UniverseTasks()
    
    # We can pass an initial concept here to kick off the learning process
    initial_concept = "The Standard Model of Elementary Particles"
    output_location = "../knowledge_base/level_1_fundamental_physics/standard_model.md"
    
    research_task = tasks.research_concept_task(researcher, initial_concept)
    verify_task = tasks.verify_research_task(skeptic, initial_concept)
    evaluate_task = tasks.student_evaluation_task(student, initial_concept)
    document_task = tasks.document_knowledge_task(archivist, output_location)

    # Instantiate the Crew
    universe_crew = Crew(
        agents=[student, researcher, skeptic, archivist],
        tasks=[research_task, verify_task, evaluate_task, document_task],
        process=Process.sequential,
        verbose=True
    )

    print("Initialize Student Agent logic completed.")
    print(f"Beginning research on: {initial_concept}")
    
    # Execute the workflow
    # WARNING: Need OPENAI_API_KEY or LLM endpoint configured to run this.
    # result = universe_crew.kickoff()
    # print("Workflow complete:", result)

if __name__ == "__main__":
    main()

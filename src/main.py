import sys
import os
from pathlib import Path
# Ensure virtual environment site-packages are loaded for AppLocker/policy compliance
VENV_SITE_PACKAGES = Path(__file__).resolve().parent.parent / ".venv" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists():
    import site
    site.addsitedir(str(VENV_SITE_PACKAGES))

import re
import json
from dotenv import load_dotenv
from crewai import Crew, Process

from agents.universe_agents import UniverseAgents
from tasks.universe_tasks import UniverseTasks
try:
    from workflow_contracts import (
        parse_student_decision,
        normalize_markdown_output,
        validate_concept_markdown,
        parse_skeptic_checklist_score,
    )
except ImportError:
    from src.workflow_contracts import (
        parse_student_decision,
        normalize_markdown_output,
        validate_concept_markdown,
        parse_skeptic_checklist_score,
    )
try:
    from index_utils import index_heading_for_level, prune_stale_index_links, sanitize_index_file
except ImportError:
    from src.index_utils import index_heading_for_level, prune_stale_index_links, sanitize_index_file

try:
    from evaluation_logger import (
        log_evaluation_outcome,
        get_top_failure_patterns,
        log_telemetry_event,
        get_last_missing_prerequisite,
    )
except ImportError:
    from src.evaluation_logger import (
        log_evaluation_outcome,
        get_top_failure_patterns,
        log_telemetry_event,
        get_last_missing_prerequisite,
    )

import time


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
    """Deterministically synchronize the entire index to match current files on disk."""
    repo_root = Path(__file__).resolve().parent.parent
    try:
        from index_utils import synchronize_index
    except ImportError:
        from src.index_utils import synchronize_index
    synchronize_index(index_path, repo_root)


def run_level1_flow(next_concept: str):
    """Core Level 1 learning, research, verification, and documentation workflow."""
    load_dotenv()
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    index_path = "knowledge_base/_index.md"
    repo_root = Path(__file__).resolve().parent.parent

    # Initialize Agents
    agents = UniverseAgents()
    researcher = agents.researcher_agent()
    skeptic = agents.skeptic_agent()
    archivist = agents.archivist_agent()
    has_genmedia_credentials = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    visualizer = agents.visualizer_agent() if has_genmedia_credentials else None
    if not has_genmedia_credentials:
        print("WARNING: GOOGLE_APPLICATION_CREDENTIALS is not set; skipping visual generation task.")

    # Initialize Tasks
    tasks = UniverseTasks()

    # Retrieve pre-run failure guidance patterns (Issue 7)
    patterns = get_top_failure_patterns()
    pattern_guidance = ""
    if patterns:
        pattern_guidance = "\n\nCRITICAL HISTORICAL FAILURE GUIDANCE:\n" + "\n".join(f"- {p}" for p in patterns)

    # We dynamically create the output paths based on the Student's decision
    filename = sanitize_filename(next_concept)
    level_folder = "level_1_fundamental_physics" 
    output_location = f"knowledge_base/{level_folder}/{filename}"

    if (repo_root / output_location).exists():
        print(f"Concept file already exists, skipping write: {output_location}")
        return

    print("--- STEP 2: Research & Verification ---")
    step2_start = time.time()
    log_telemetry_event("research_evaluation", "start", metadata={"concept": next_concept})

    max_retries = 2
    retries = 0
    follow_up_context = ""
    decision = {
        "status": "rejected",
        "reason_code": "missing_evaluation",
        "summary_for_archivist": "",
        "follow_up_questions": ["No evaluation decision was produced."]
    }
    rejected = False

    while True:
        attempt_start = time.time()
        log_telemetry_event(
            "research_evaluation_attempt", 
            "start", 
            metadata={"concept": next_concept, "attempt": retries + 1}
        )

        research_student = agents.student_agent()
        research_concept_prompt = next_concept
        if follow_up_context:
            research_concept_prompt = f"{next_concept}\nFollow-up context from prior rejection:\n{follow_up_context}"

        research_task = tasks.research_concept_task(researcher, research_concept_prompt)
        verify_task = tasks.verify_research_task(skeptic, next_concept, context=[research_task])
        evaluate_task = tasks.student_evaluation_task(research_student, next_concept, context=[research_task, verify_task])
        if pattern_guidance:
            evaluate_task.description += pattern_guidance

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
            skeptic_output = "Verification Score: 5/5"
        else:
            evaluation_output = str(evaluation_crew.kickoff()).strip()
            skeptic_output = ""
            if hasattr(verify_task, 'output') and verify_task.output:
                skeptic_output = str(verify_task.output.raw)

        decision = parse_student_decision(evaluation_output)
        rejected = decision["status"] != "approved"
        
        # Parse skeptic checklist score (Issue 9)
        score, total_score = parse_skeptic_checklist_score(skeptic_output)
        if score is None and skeptic_output:
            # Fallback parsing on raw output text just in case
            score, total_score = parse_skeptic_checklist_score(evaluation_output)
        
        # Log evaluation outcome (Issue 6)
        log_evaluation_outcome(
            concept=next_concept,
            status=decision["status"],
            reason_code=decision["reason_code"],
            score=score,
            total_score=total_score,
            follow_up_questions=decision["follow_up_questions"],
            attempt=retries + 1
        )

        log_telemetry_event(
            "research_evaluation_attempt", 
            "end", 
            duration_seconds=time.time() - attempt_start, 
            metadata={
                "status": decision["status"],
                "reason_code": decision["reason_code"],
                "score": score,
                "total_score": total_score,
                "attempt": retries + 1
            }
        )

        if not rejected:
            break
        if retries >= max_retries:
            print(
                "WARNING: Evaluation rejected after "
                f"{max_retries} retries (reason_code={decision['reason_code']}). "
                "Skipping document generation."
            )
            break

        retries += 1
        follow_up_context = json.dumps(
            {
                "reason_code": decision["reason_code"],
                "follow_up_questions": decision["follow_up_questions"],
            },
            ensure_ascii=True,
        )
        print(f"Evaluation rejected. Retrying research with follow-up context (attempt {retries}/{max_retries}).")

    log_telemetry_event(
        "research_evaluation", 
        "end", 
        duration_seconds=time.time() - step2_start, 
        metadata={
            "final_status": decision["status"],
            "total_attempts": retries + 1
        }
    )

    if rejected and retries >= max_retries:
        return

    print("--- STEP 3: Documentation & Validation ---")
    step3_start = time.time()
    log_telemetry_event("documentation_validation", "start", metadata={"concept": next_concept, "output_location": output_location})

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
        log_telemetry_event(
            "documentation_validation", 
            "end", 
            duration_seconds=time.time() - step3_start, 
            metadata={"status": "skipped_dry_run"}
        )
        return

    document_output = normalize_markdown_output(str(final_crew.kickoff()).strip())
    valid, validation_errors = validate_concept_markdown(document_output)
    if not valid:
        print("ERROR: Document validation failed; file/index update was blocked.")
        for err in validation_errors:
            print(f" - {err}")
        log_telemetry_event(
            "documentation_validation", 
            "end", 
            duration_seconds=time.time() - step3_start, 
            metadata={"status": "failed_validation", "errors": validation_errors}
        )
        return

    output_file = repo_root / output_location
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(document_output.rstrip() + "\n", encoding="utf-8")
    update_index_file(index_path, next_concept, level_folder, filename)
    print(f"Workflow complete: wrote validated document to {output_location}")
    log_telemetry_event(
        "documentation_validation", 
        "end", 
        duration_seconds=time.time() - step3_start, 
        metadata={"status": "success", "output_location": output_location}
    )

    try:
        print("--- STEP 4: Skeptic Sandbox Debate (Caveman & Oracle Integration) ---")
        sandbox_script = Path(__file__).resolve().parent / "skeptic_sandbox.py"
        import subprocess
        import sys
        subprocess.run([sys.executable, str(sandbox_script), next_concept], check=True)
    except Exception as e:
        print(f"Warning: Failed to run Skeptic Sandbox debate: {e}")



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

    # Initialize Tasks
    tasks = UniverseTasks()
    
    print("--- STEP 1: Determine Next Topic ---")
    step1_start = time.time()
    log_telemetry_event("topic_selection", "start", metadata={"index_path": index_path})

    # Retrieve pre-run failure guidance patterns (Issue 7)
    patterns = get_top_failure_patterns()
    pattern_guidance = ""
    if patterns:
        pattern_guidance = "\n\nCRITICAL HISTORICAL FAILURE GUIDANCE:\n" + "\n".join(f"- {p}" for p in patterns)

    topic_task = tasks.determine_next_topic_task(topic_student, current_index)
    if pattern_guidance:
        topic_task.description += pattern_guidance

    topic_crew = Crew(agents=[topic_student], tasks=[topic_task], verbose=True)
    
    missing_prereq = get_last_missing_prerequisite(current_index)
    if missing_prereq:
        print(f"[CLOSED-LOOP FEEDBACK] Prioritizing missing Level 2 prerequisite: '{missing_prereq}'")
        next_concept = missing_prereq
    elif dry_run:
        next_concept = "Quantum Entanglement"
    else:
        next_concept = topic_crew.kickoff()
    
    next_concept = str(next_concept).strip()
    print(f"Target Concept Selected: {next_concept}")
    log_telemetry_event(
        "topic_selection", 
        "end", 
        duration_seconds=time.time() - step1_start, 
        metadata={"selected_concept": next_concept}
    )
    
    # Run the Level 1 flow
    run_level1_flow(next_concept)


if __name__ == "__main__":
    main()

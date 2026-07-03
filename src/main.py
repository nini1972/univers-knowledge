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
try:
    from step_logger import make_step_callback
except ImportError:
    from src.step_logger import make_step_callback

from agents.universe_agents import UniverseAgents
from tasks.universe_tasks import UniverseTasks
try:
    from workflow_contracts import (
        parse_student_decision,
        normalize_markdown_output,
        validate_concept_markdown,
        parse_skeptic_checklist_score,
        parse_math_score,
        parse_math_status,
    )
except ImportError:
    from src.workflow_contracts import (
        parse_student_decision,
        normalize_markdown_output,
        validate_concept_markdown,
        parse_skeptic_checklist_score,
        parse_math_score,
        parse_math_status,
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
        log_rejected_concept,
    )
except ImportError:
    from src.evaluation_logger import (
        log_evaluation_outcome,
        get_top_failure_patterns,
        log_telemetry_event,
        get_last_missing_prerequisite,
        log_rejected_concept,
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
    math_physicist = agents.math_physicist_agent()
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
        # ── NEW: Tier 1 Math Verification ────────────────────────────────────
        math_task = tasks.math_verification_task(math_physicist, next_concept, context=[research_task])
        # ── Skeptic now receives both research and math verification reports ──
        verify_task = tasks.verify_research_task(skeptic, next_concept, context=[research_task, math_task])
        evaluate_task = tasks.student_evaluation_task(research_student, next_concept, context=[research_task, math_task, verify_task])
        if pattern_guidance:
            evaluate_task.description += pattern_guidance

        evaluation_crew = Crew(
            agents=[research_student, researcher, math_physicist, skeptic],
            tasks=[research_task, math_task, verify_task, evaluate_task],
            process=Process.sequential,
            verbose=True,
            step_callback=make_step_callback("evaluation_crew"),
        )

        if dry_run:
            evaluation_output = json.dumps({
                "status": "approved",
                "reason_code": "dry_run",
                "summary_for_archivist": f"Dry-run approved summary for {next_concept}.",
                "follow_up_questions": []
            })
            skeptic_output = "Verification Score: 6/6"
            math_output = "**Math Score:** 4/4\n[MATH_PROVEN]"
        else:
            evaluation_output = str(evaluation_crew.kickoff()).strip()
            skeptic_output = ""
            math_output = ""
            if hasattr(verify_task, 'output') and verify_task.output:
                skeptic_output = str(verify_task.output.raw)
            if hasattr(math_task, 'output') and math_task.output:
                math_output = str(math_task.output.raw)

        decision = parse_student_decision(evaluation_output)
        rejected = decision["status"] != "approved"

        # Parse skeptic checklist score (Issue 9)
        score, total_score = parse_skeptic_checklist_score(skeptic_output)
        if score is None and skeptic_output:
            # Fallback parsing on raw output text just in case
            score, total_score = parse_skeptic_checklist_score(evaluation_output)

        # Parse math verification score and status (Math Engine)
        math_score, math_total = parse_math_score(math_output)
        math_status_val = parse_math_status(math_output)
        if math_score is not None:
            print(f"[MATH] Score: {math_score}/{math_total} | Status: [{math_status_val}]")

        # Force a retry if no equations are found on the first attempt
        if math_status_val == "MATH_PENDING" and retries == 0:
            print(f"[MATH RETRY TRIGGER] '{next_concept}' is MATH_PENDING on attempt 1. Forcing retry with math search prompt.")
            rejected = True
            decision = {
                "status": "rejected",
                "reason_code": "missing_math_equations",
                "summary_for_archivist": "",
                "follow_up_questions": [
                    "The Math Physicist found no LaTeX equations in the research report. "
                    "Please search specifically for the mathematical formulas, equations, or "
                    "formal mathematical models associated with this concept and format them "
                    "in standard LaTeX notation (e.g. using $...$ or $$...$$)."
                ]
            }


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
                "math_score": math_score,
                "math_status": math_status_val,
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
            log_rejected_concept(
                concept=next_concept,
                level=1,
                reason_code=decision["reason_code"],
                total_attempts=retries + 1,
                follow_up_questions=decision.get("follow_up_questions", []),
                math_score=math_score,
                math_status=math_status_val,
                last_skeptic_score=score,
                last_skeptic_total=total_score,
            )
            try:
                import backlog_manager
            except ImportError:
                from src import backlog_manager
            backlog_manager.add_to_backlog(next_concept, level=1, questions=decision.get("follow_up_questions", []))
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
        math_status=math_status_val,
        math_score=math_score,
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
        verbose=True,
        step_callback=make_step_callback("final_crew"),
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

    try:
        import backlog_manager
    except ImportError:
        from src import backlog_manager
    backlog_manager.resolve_backlog_item(next_concept)
    backlog_manager.add_to_backlog(next_concept, level=1, questions=decision.get("follow_up_questions", []))

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

    topic_crew = Crew(agents=[topic_student], tasks=[topic_task], verbose=True, step_callback=make_step_callback("topic_crew"))

    try:
        import backlog_manager
    except ImportError:
        from src import backlog_manager
    backlog_item = backlog_manager.get_next_backlog_item()

    missing_prereq = get_last_missing_prerequisite(current_index)
    if backlog_item:
        print(f"[CLOSED-LOOP FEEDBACK] Prioritizing backlog research point: '{backlog_item['question']}'")
        next_concept = backlog_item['question']
    elif missing_prereq:
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

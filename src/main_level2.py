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
        check_level2_prerequisites,
        parse_skeptic_checklist_score,
        parse_math_score,
        parse_math_status,
    )
except ImportError:
    from src.workflow_contracts import (
        parse_student_decision,
        normalize_markdown_output,
        validate_concept_markdown,
        check_level2_prerequisites,
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
        log_rejected_concept,
    )
except ImportError:
    from src.evaluation_logger import (
        log_evaluation_outcome,
        get_top_failure_patterns,
        log_telemetry_event,
        log_rejected_concept,
    )

import time



def sanitize_filename(name):
    try:
        from main import sanitize_filename as _shared_sanitize_filename
    except ImportError:
        from src.main import sanitize_filename as _shared_sanitize_filename
    return _shared_sanitize_filename(name)






def _extract_level2_selection(raw_output: str):
    text = str(raw_output).strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    if not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
    try:
        data = json.loads(text)
        theory_a = str(data["theory_a"]).strip()
        theory_b = str(data["theory_b"]).strip()
        concept_name = str(data["concept_name"]).strip()
        return theory_a, theory_b, concept_name
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"WARNING: Invalid topic selection output ({exc}). Raw output: {raw_output}")
        return (
            "Asymptotic Safety Gravity",
            "Causal Dynamical Triangulations",
            "Nonperturbative Quantum Gravity Debate",
        )


def update_index_file(index_path: str, concept_name: str, level_folder: str, filename: str):
    """Deterministically synchronize the entire index to match current files on disk."""
    repo_root = Path(__file__).resolve().parent.parent
    try:
        from index_utils import synchronize_index
    except ImportError:
        from src.index_utils import synchronize_index
    synchronize_index(index_path, repo_root)

def main():
    load_dotenv()
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    index_path = "knowledge_base/_index.md"
    current_index = sanitize_index_file(index_path, Path(__file__).resolve().parent.parent)

    # Initialize Agents
    agents = UniverseAgents()

    # Use dedicated agent instances across crews and for parallel tasks to avoid
    # reusing the same executor concurrently.
    topic_student = agents.student_agent()
    math_physicist = agents.math_physicist_agent()
    skeptic = agents.skeptic_agent()
    archivist = agents.archivist_agent()
    has_genmedia_credentials = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    visualizer = agents.visualizer_agent() if has_genmedia_credentials else None
    if not has_genmedia_credentials:
        print("WARNING: GOOGLE_APPLICATION_CREDENTIALS is not set; skipping visual generation task.")

    # Initialize Tasks
    tasks = UniverseTasks()

    print("--- STEP 1: Determine Next Level 2 Debate Topic ---")
    step1_start = time.time()
    log_telemetry_event("topic_selection_level2", "start", metadata={"index_path": index_path})

    # Retrieve pre-run failure guidance patterns
    patterns = get_top_failure_patterns()
    pattern_guidance = ""
    if patterns:
        pattern_guidance = "\n\nCRITICAL HISTORICAL FAILURE GUIDANCE:\n" + "\n".join(f"- {p}" for p in patterns)

    topic_task = tasks.determine_next_level2_topic_task(topic_student, current_index)
    if pattern_guidance:
        topic_task.description += pattern_guidance

    topic_crew = Crew(agents=[topic_student], tasks=[topic_task], verbose=True, step_callback=make_step_callback("topic_crew_l2"))

    if dry_run:
        selection_output = json.dumps({
            "theory_a": "Asymptotic Safety Gravity",
            "theory_b": "Causal Dynamical Triangulations",
            "concept_name": "Nonperturbative Quantum Gravity Debate"
        })
    else:
        selection_output = topic_crew.kickoff()

    theory_a, theory_b, concept_name = _extract_level2_selection(selection_output)

    # Enforce prerequisite check (Issue 10)
    prereq_ok, missing_prereq = check_level2_prerequisites(theory_a, theory_b, concept_name, current_index)
    if not prereq_ok:
        print(f"\n[PREREQUISITE BLOCKED] Selected debate '{concept_name}' requires the prerequisite '{missing_prereq}', which is not yet verified in our index.")
        log_telemetry_event(
            "topic_selection_level2",
            "end",
            duration_seconds=time.time() - step1_start,
            metadata={
                "status": "blocked_by_prerequisite",
                "selected_concept": concept_name,
                "missing_prerequisite": missing_prereq
            }
        )
        print(f"[CLOSED-LOOP FEEDBACK] Automatically triggering Level 1 learning loop for: '{missing_prereq}'")
        try:
            from main import run_level1_flow
        except ImportError:
            from src.main import run_level1_flow
        try:
            run_level1_flow(missing_prereq)
        except Exception as exc:
            print(f"ERROR executing automatic Level 1 learning flow: {exc}")
        return

    level_folder = "level_2_advanced_frameworks"
    filename = sanitize_filename(concept_name)
    output_location = f"knowledge_base/{level_folder}/{filename}"

    repo_root = Path(__file__).resolve().parent.parent
    if (repo_root / output_location).exists():
        print(f"Concept file already exists, skipping write: {output_location}")
        log_telemetry_event(
            "topic_selection_level2",
            "end",
            duration_seconds=time.time() - step1_start,
            metadata={"status": "already_exists", "selected_concept": concept_name}
        )
        return

    log_telemetry_event(
        "topic_selection_level2",
        "end",
        duration_seconds=time.time() - step1_start,
        metadata={
            "status": "success",
            "selected_concept": concept_name,
            "theory_a": theory_a,
            "theory_b": theory_b
        }
    )

    print("Phase 3: Level 2 Advanced Frameworks Orchestration Ready.")
    print(f"Beginning debate on: {theory_a} vs {theory_b}")
    step2_start = time.time()
    log_telemetry_event("research_evaluation_level2", "start", metadata={"concept": concept_name, "theory_a": theory_a, "theory_b": theory_b})

    max_retries = 2
    retries = 0
    follow_up_context = ""
    evaluation_output = ""
    evaluation_decision = {
        "status": "rejected",
        "reason_code": "missing_evaluation",
        "summary_for_archivist": "",
        "follow_up_questions": ["No evaluation decision was produced."],
    }
    rejected = False

    while True:
        attempt_start = time.time()
        log_telemetry_event(
            "research_evaluation_level2_attempt",
            "start",
            metadata={"concept": concept_name, "attempt": retries + 1}
        )

        evaluation_student = agents.student_agent()
        researcher_a = agents.researcher_agent()
        researcher_b = agents.researcher_agent()

        theory_a_prompt = theory_a
        theory_b_prompt = theory_b
        if follow_up_context:
            theory_a_prompt = f"{theory_a}\nFollow-up context from prior rejection:\n{follow_up_context}"
            theory_b_prompt = f"{theory_b}\nFollow-up context from prior rejection:\n{follow_up_context}"

        research_task_a = tasks.research_concept_task(researcher_a, theory_a_prompt, async_execution=True)
        research_task_b = tasks.research_concept_task(researcher_b, theory_b_prompt, async_execution=True)
        debate_task = tasks.debate_theories_task(skeptic, theory_a, theory_b, context=[research_task_a, research_task_b])
        # ── NEW: Tier 1 Math Verification after debate report ─────────────
        math_task = tasks.math_verification_task(math_physicist, concept_name, context=[research_task_a, research_task_b, debate_task])
        evaluate_task = tasks.student_level2_debate_evaluation_task(
            evaluation_student,
            f"The debate between {theory_a} and {theory_b}",
            context=[research_task_a, research_task_b, debate_task, math_task]
        )
        if pattern_guidance:
            evaluate_task.description += pattern_guidance

        evaluation_crew = Crew(
            agents=[researcher_a, researcher_b, skeptic, math_physicist, evaluation_student],
            tasks=[research_task_a, research_task_b, debate_task, math_task, evaluate_task],
            process=Process.sequential,
            verbose=True,
            step_callback=make_step_callback("evaluation_crew_l2"),
        )

        if dry_run:
            evaluation_output = json.dumps({
                "status": "approved",
                "reason_code": "dry_run",
                "summary_for_archivist": f"Dry-run approved summary for debate: {theory_a} vs {theory_b}.",
                "follow_up_questions": []
            })
            skeptic_output = "Verification Score: 6/6"
            math_output = "**Math Score:** 4/4\n[MATH_PROVEN]"
        else:
            evaluation_output = str(evaluation_crew.kickoff()).strip()
            skeptic_output = ""
            math_output = ""
            if hasattr(debate_task, 'output') and debate_task.output:
                skeptic_output = str(debate_task.output.raw)
            if hasattr(math_task, 'output') and math_task.output:
                math_output = str(math_task.output.raw)

        evaluation_decision = parse_student_decision(evaluation_output)
        rejected = evaluation_decision["status"] != "approved"

        if rejected and evaluation_decision["reason_code"] == "lack_of_experimental_confirmation":
            evaluation_decision = {
                "status": "approved",
                "reason_code": "approved_despite_limited_confirmation",
                "summary_for_archivist": (
                    f"Comparative report approved for {theory_a} vs {theory_b}. "
                    "The analysis is rigorous, source-grounded, and transparent about uncertainty. "
                    "Assign status [VERIFIED] if the debate is grounded in experimentally confirmed physics, "
                    "or [THEORETICAL] only if both theories genuinely lack any direct experimental support. "
                    "Document strengths, weaknesses, current constraints, and open validation paths."
                ),
                "follow_up_questions": evaluation_decision.get("follow_up_questions", []),
            }
            rejected = False

        score, total_score = parse_skeptic_checklist_score(skeptic_output)
        if score is None and skeptic_output:
            score, total_score = parse_skeptic_checklist_score(evaluation_output)

        # Parse math score and status from Math Physicist report
        math_score, math_total = parse_math_score(math_output)
        math_status_val = parse_math_status(math_output)
        if math_score is not None:
            print(f"[MATH] Score: {math_score}/{math_total} | Status: [{math_status_val}]")

        # Force a retry if no equations are found on the first attempt
        if math_status_val == "MATH_PENDING" and retries == 0:
            print(f"[MATH RETRY TRIGGER] '{concept_name}' is MATH_PENDING on attempt 1. Forcing retry with math search prompt.")
            rejected = True
            evaluation_decision = {
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


        log_evaluation_outcome(
            concept=concept_name,
            status=evaluation_decision["status"],
            reason_code=evaluation_decision["reason_code"],
            score=score,
            total_score=total_score,
            follow_up_questions=evaluation_decision["follow_up_questions"],
            attempt=retries + 1
        )

        log_telemetry_event(
            "research_evaluation_level2_attempt",
            "end",
            duration_seconds=time.time() - attempt_start,
            metadata={
                "status": evaluation_decision["status"],
                "reason_code": evaluation_decision["reason_code"],
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
                f"{max_retries} retries (reason_code={evaluation_decision['reason_code']}). "
                "Skipping document generation."
            )
            log_rejected_concept(
                concept=concept_name,
                level=2,
                reason_code=evaluation_decision["reason_code"],
                total_attempts=retries + 1,
                follow_up_questions=evaluation_decision.get("follow_up_questions", []),
                math_score=math_score,
                math_status=math_status_val,
                last_skeptic_score=score,
                last_skeptic_total=total_score,
            )
            try:
                import backlog_manager
            except ImportError:
                from src import backlog_manager
            backlog_manager.add_to_backlog(concept_name, level=2, questions=evaluation_decision.get("follow_up_questions", []))
            break


        retries += 1
        follow_up_context = json.dumps(
            {
                "reason_code": evaluation_decision["reason_code"],
                "follow_up_questions": evaluation_decision["follow_up_questions"],
            },
            ensure_ascii=True,
        )
        print(f"Evaluation rejected. Retrying research with follow-up context (attempt {retries}/{max_retries}).")

    log_telemetry_event(
        "research_evaluation_level2",
        "end",
        duration_seconds=time.time() - step2_start,
        metadata={
            "final_status": evaluation_decision["status"],
            "total_attempts": retries + 1
        }
    )

    if rejected and retries >= max_retries:
        return

    print("--- STEP 3: Documentation & Validation ---")
    step3_start = time.time()
    log_telemetry_event("documentation_validation_level2", "start", metadata={"concept": concept_name, "output_location": output_location})

    visual_task = tasks.generate_visual_concept_task(visualizer, concept_name) if visualizer else None
    document_task = tasks.document_knowledge_task(
        archivist,
        output_location,
        include_visual=bool(visual_task),
        approved_summary=evaluation_decision["summary_for_archivist"],
        math_status=math_status_val,
        math_score=math_score,
        math_report=math_output,
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
        step_callback=make_step_callback("final_crew_l2"),
    )

    if dry_run:
        print("DRY_RUN enabled. Skipping final_crew.kickoff().")
        log_telemetry_event(
            "documentation_validation_level2",
            "end",
            duration_seconds=time.time() - step3_start,
            metadata={"status": "skipped_dry_run"}
        )
    else:
        result = normalize_markdown_output(str(final_crew.kickoff()).strip())
        valid, validation_errors = validate_concept_markdown(result)
        if not valid:
            print("ERROR: Document validation failed; file/index update was blocked.")
            for err in validation_errors:
                print(f" - {err}")
            log_telemetry_event(
                "documentation_validation_level2",
                "end",
                duration_seconds=time.time() - step3_start,
                metadata={"status": "failed_validation", "errors": validation_errors}
            )
            return

        output_file = repo_root / output_location
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result.rstrip() + "\n", encoding="utf-8")
        update_index_file(index_path, concept_name, level_folder, filename)
        print(f"Workflow complete: wrote validated document to {output_location}")

        try:
            import backlog_manager
        except ImportError:
            from src import backlog_manager
        backlog_manager.add_to_backlog(concept_name, level=2, questions=evaluation_decision.get("follow_up_questions", []))

        log_telemetry_event(
            "documentation_validation_level2",
            "end",
            duration_seconds=time.time() - step3_start,
            metadata={"status": "success", "output_location": output_location}
        )


        try:
            print("--- STEP 4: Skeptic Sandbox Debate (Caveman & Oracle Integration) ---")
            sandbox_script = Path(__file__).resolve().parent / "skeptic_sandbox.py"
            import subprocess
            import sys
            subprocess.run([sys.executable, str(sandbox_script), concept_name], check=True)
        except Exception as e:
            print(f"Warning: Failed to run Skeptic Sandbox debate: {e}")


if __name__ == "__main__":
    main()

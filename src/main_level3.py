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
import time
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
        is_concept_existing,
        sanitize_filename,
    )
except ImportError:
    from src.workflow_contracts import (
        parse_student_decision,
        normalize_markdown_output,
        validate_concept_markdown,
        parse_skeptic_checklist_score,
        parse_math_score,
        parse_math_status,
        is_concept_existing,
        sanitize_filename,
    )

try:
    from index_utils import sanitize_index_file, generate_clean_topic_digest
except ImportError:
    from src.index_utils import sanitize_index_file, generate_clean_topic_digest

try:
    from a2a_math_client import extract_equations_from_report
except ImportError:
    from src.a2a_math_client import extract_equations_from_report

try:
    from equation_logger import log_equations
except ImportError:
    from src.equation_logger import log_equations

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





def _extract_level3_selection(raw_output: str):
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
        focus_area = str(data.get("focus_area", "Emergence and Physicalist Consciousness")).strip()
        concept_name = str(data["concept_name"]).strip()
        return focus_area, concept_name
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"WARNING: Invalid Level 3 topic selection output ({exc}). Raw output: {raw_output}")
        return (
            "Integrated Information Theory vs Physicalist Emergence",
            "Thermodynamic Limits of Neural Information Processing",
        )


def update_index_file(index_path: str, concept_name: str, level_folder: str, filename: str):
    """Deterministically synchronize the entire index to match current files on disk and rebuild OKF graph.json."""
    repo_root = Path(__file__).resolve().parent.parent
    try:
        from index_utils import synchronize_index
    except ImportError:
        from src.index_utils import synchronize_index
    synchronize_index(index_path, repo_root)

    try:
        import subprocess
        indexer_script = repo_root / "scripts" / "okf_indexer.py"
        if indexer_script.exists():
            subprocess.run([sys.executable, str(indexer_script), "--build", "--repo-root", str(repo_root)], check=False)
    except Exception as exc:
        print(f"Warning: Failed to auto-rebuild OKF graph.json: {exc}")

    try:
        try:
            from equation_archaeologist import EquationArchaeologist
        except ImportError:
            from src.equation_archaeologist import EquationArchaeologist
        EquationArchaeologist(repo_root).run()
    except Exception as exc:
        print(f"Warning: Failed to run Equation Archaeologist: {exc}")


def main():
    load_dotenv()
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    index_path = "knowledge_base/_index.md"
    current_index = sanitize_index_file(index_path, Path(__file__).resolve().parent.parent)

    # Initialize Agents
    agents = UniverseAgents()
    topic_student = agents.student_agent()
    bio_digital_analyst = agents.bio_digital_analyst_agent()
    cosmological_architect = agents.cosmological_architect_agent()
    math_physicist = agents.math_physicist_agent()
    skeptic = agents.skeptic_agent()
    archivist = agents.archivist_agent()
    has_genmedia_credentials = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    visualizer = agents.visualizer_agent() if has_genmedia_credentials else None
    if not has_genmedia_credentials:
        print("WARNING: GOOGLE_APPLICATION_CREDENTIALS is not set; skipping visual generation task.")

    # Initialize Tasks
    tasks = UniverseTasks()

    print("--- STEP 1: Determine Next Level 3 Topic (Emergence & Intelligence) ---")
    step1_start = time.time()
    log_telemetry_event("topic_selection_level3", "start", metadata={"index_path": index_path})

    patterns = get_top_failure_patterns()
    pattern_guidance = ""
    if patterns:
        pattern_guidance = "\n\nCRITICAL HISTORICAL FAILURE GUIDANCE:\n" + "\n".join(f"- {p}" for p in patterns)

    max_topic_attempts = 4
    excluded_concepts = []
    focus_area, concept_name = None, None
    output_location = None
    level_folder = "level_3_emergence_and_intelligence"
    repo_root = Path(__file__).resolve().parent.parent
    topic_digest = generate_clean_topic_digest(repo_root=repo_root)

    for attempt in range(1, max_topic_attempts + 1):
        topic_student = agents.student_agent()
        topic_task = tasks.determine_next_level3_topic_task(topic_student, topic_digest)

        exclusion_prompt = ""
        if excluded_concepts:
            exclusion_prompt = "\n\nCRITICAL DEDUPLICATION RULE:\nDo NOT select any of the following already-existing concepts:\n" + "\n".join(f"- {c}" for c in excluded_concepts)

        if pattern_guidance or exclusion_prompt:
            topic_task.description += (pattern_guidance + exclusion_prompt)

        topic_crew = Crew(agents=[topic_student], tasks=[topic_task], verbose=True, step_callback=make_step_callback(f"topic_crew_l3_att{attempt}"))

        if dry_run:
            selection_output = json.dumps({
                "focus_area": "Integrated Information Theory & Neural Thermodynamics",
                "concept_name": f"Thermodynamic Limits of Neural Information Processing {attempt}"
            })
        else:
            selection_output = topic_crew.kickoff()

        focus_area, concept_name = _extract_level3_selection(selection_output)
        filename = sanitize_filename(concept_name)
        output_location = f"knowledge_base/{level_folder}/{filename}"

        if (repo_root / output_location).exists() or is_concept_existing(concept_name, level=3, repo_root=repo_root):
            print(f"[TOPIC SELECTION RETRY] Attempt {attempt}/{max_topic_attempts}: Selected Level 3 concept '{concept_name}' already exists. Retrying...")
            excluded_concepts.append(concept_name)
            log_telemetry_event(
                "topic_selection_level3_retry",
                "attempt_duplicate",
                metadata={"attempt": attempt, "concept": concept_name}
            )
            continue
        else:
            print(f"[TOPIC SELECTION SUCCESS] Selected valid new Level 3 topic on attempt {attempt}: '{concept_name}'")
            break

    if not concept_name or (repo_root / output_location).exists() or is_concept_existing(concept_name, level=3, repo_root=repo_root):
        print(f"ERROR: Unable to select a non-existing Level 3 topic after {max_topic_attempts} attempts.")
        log_telemetry_event(
            "topic_selection_level3",
            "end",
            duration_seconds=time.time() - step1_start,
            metadata={"status": "max_retries_exceeded", "excluded_count": len(excluded_concepts)}
        )
        return

    log_telemetry_event(
        "topic_selection_level3",
        "end",
        duration_seconds=time.time() - step1_start,
        metadata={
            "status": "success",
            "selected_concept": concept_name,
            "focus_area": focus_area
        }
    )

    print("Phase 4: Level 3 Emergence and Intelligence Research Ready.")
    print(f"Beginning research on Level 3 topic: {concept_name} (Focus Area: {focus_area})")
    step2_start = time.time()
    log_telemetry_event("research_evaluation_level3", "start", metadata={"concept": concept_name, "focus_area": focus_area})

    max_retries = 2
    retries = 0
    follow_up_context = ""
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
            "research_evaluation_level3_attempt",
            "start",
            metadata={"concept": concept_name, "attempt": retries + 1}
        )

        evaluation_student = agents.student_agent()

        research_prompt = concept_name
        if follow_up_context:
            research_prompt = f"{concept_name}\nFollow-up context from prior rejection:\n{follow_up_context}"

        research_task_a = tasks.research_concept_task(bio_digital_analyst, research_prompt, async_execution=True)
        research_task_b = tasks.research_concept_task(cosmological_architect, research_prompt, async_execution=True)
        math_task = tasks.math_verification_task(math_physicist, concept_name, context=[research_task_a, research_task_b])
        verify_task = tasks.verify_research_task(skeptic, concept_name, context=[research_task_a, research_task_b, math_task])
        evaluate_task = tasks.student_level3_evaluation_task(
            evaluation_student,
            concept_name,
            context=[research_task_a, research_task_b, math_task, verify_task]
        )
        if pattern_guidance:
            evaluate_task.description += pattern_guidance

        evaluation_crew = Crew(
            agents=[bio_digital_analyst, cosmological_architect, math_physicist, skeptic, evaluation_student],
            tasks=[research_task_a, research_task_b, math_task, verify_task, evaluate_task],
            process=Process.sequential,
            verbose=True,
            step_callback=make_step_callback("evaluation_crew_l3"),
        )

        if dry_run:
            evaluation_output = json.dumps({
                "status": "approved",
                "reason_code": "dry_run",
                "summary_for_archivist": f"Dry-run approved summary for Level 3 concept: {concept_name}.",
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

        evaluation_decision = parse_student_decision(evaluation_output)
        rejected = evaluation_decision["status"] != "approved"

        score, total_score = parse_skeptic_checklist_score(skeptic_output)
        if score is None and skeptic_output:
            score, total_score = parse_skeptic_checklist_score(evaluation_output)

        math_score, math_total = parse_math_score(math_output)
        math_status_val = parse_math_status(math_output)
        if math_score is not None:
            print(f"[MATH] Score: {math_score}/{math_total} | Status: [{math_status_val}]")

        try:
            all_crew_text_for_eqs = "\n".join(filter(None, [math_output, skeptic_output, evaluation_output]))
            discovered_equations = extract_equations_from_report(all_crew_text_for_eqs)
            log_equations(
                concept=concept_name,
                level=3,
                equations=discovered_equations,
                math_status=math_status_val,
                math_score=math_score,
                math_total=math_total,
            )
        except Exception as eq_err:
            print(f"[EQ DB] Warning: {eq_err}")

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
            "research_evaluation_level3_attempt",
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
                level=3,
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
            backlog_manager.add_to_backlog(concept_name, level=3, questions=evaluation_decision.get("follow_up_questions", []))
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
        "research_evaluation_level3",
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
    log_telemetry_event("documentation_validation_level3", "start", metadata={"concept": concept_name, "output_location": output_location})

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
        step_callback=make_step_callback("final_crew_l3"),
    )

    if dry_run:
        print("DRY_RUN enabled. Skipping final_crew.kickoff().")
        log_telemetry_event(
            "documentation_validation_level3",
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
                "documentation_validation_level3",
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
        backlog_manager.add_to_backlog(concept_name, level=3, questions=evaluation_decision.get("follow_up_questions", []))

        log_telemetry_event(
            "documentation_validation_level3",
            "end",
            duration_seconds=time.time() - step3_start,
            metadata={"status": "success", "output_location": output_location}
        )

        try:
            print("--- STEP 4: Skeptic Sandbox Debate (Caveman & Oracle Integration) ---")
            sandbox_script = Path(__file__).resolve().parent / "skeptic_sandbox.py"
            import subprocess
            subprocess.run([sys.executable, str(sandbox_script), concept_name], check=True)
        except Exception as e:
            print(f"Warning: Failed to run Skeptic Sandbox debate: {e}")


if __name__ == "__main__":
    main()

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
        check_level2_prerequisites,
    )
except ImportError:
    from src.workflow_contracts import (
        parse_student_decision,
        normalize_markdown_output,
        validate_concept_markdown,
        check_level2_prerequisites,
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
    )
except ImportError:
    from src.evaluation_logger import (
        log_evaluation_outcome,
        get_top_failure_patterns,
        log_telemetry_event,
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
    lines = prune_stale_index_links(lines, repo_root)

    heading = index_heading_for_level(level_folder, "## Level 2: Advanced Frameworks")
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
    current_index = sanitize_index_file(index_path, Path(__file__).resolve().parent.parent)

    # Initialize Agents
    agents = UniverseAgents()

    # Use dedicated agent instances across crews and for parallel tasks to avoid
    # reusing the same executor concurrently.
    topic_student = agents.student_agent()
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

    topic_crew = Crew(agents=[topic_student], tasks=[topic_task], verbose=True)

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
        print(f"Please run the Level 1 learning loop first (e.g., 'python main.py') to study and index '{missing_prereq}' first.\n")
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
        evaluate_task = tasks.student_level2_debate_evaluation_task(
            evaluation_student,
            f"The debate between {theory_a} and {theory_b}",
            context=[research_task_a, research_task_b, debate_task]
        )
        if pattern_guidance:
            evaluate_task.description += pattern_guidance

        evaluation_crew = Crew(
            agents=[researcher_a, researcher_b, skeptic, evaluation_student],
            tasks=[research_task_a, research_task_b, debate_task, evaluate_task],
            process=Process.sequential,
            verbose=True
        )

        if dry_run:
            evaluation_output = json.dumps({
                "status": "approved",
                "reason_code": "dry_run",
                "summary_for_archivist": f"Dry-run approved summary for debate: {theory_a} vs {theory_b}.",
                "follow_up_questions": []
            })
            skeptic_output = "Verification Score: 5/5"
        else:
            evaluation_output = str(evaluation_crew.kickoff()).strip()
            skeptic_output = ""
            if hasattr(debate_task, 'output') and debate_task.output:
                skeptic_output = str(debate_task.output.raw)

        evaluation_decision = parse_student_decision(evaluation_output)
        rejected = evaluation_decision["status"] != "approved"

        if rejected and evaluation_decision["reason_code"] == "lack_of_experimental_confirmation":
            evaluation_decision = {
                "status": "approved",
                "reason_code": "theoretical_without_direct_confirmation",
                "summary_for_archivist": (
                    f"[THEORETICAL] Comparative report approved for {theory_a} vs {theory_b}. "
                    "The analysis is rigorous, source-grounded, and transparent about uncertainty, "
                    "but lacks direct experimental confirmation at this stage. "
                    "Document strengths, weaknesses, current constraints, and open validation paths."
                ),
                "follow_up_questions": evaluation_decision.get("follow_up_questions", []),
            }
            rejected = False

        score, total_score = parse_skeptic_checklist_score(skeptic_output)
        if score is None and skeptic_output:
            score, total_score = parse_skeptic_checklist_score(evaluation_output)

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
        approved_summary=evaluation_decision["summary_for_archivist"]
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
        log_telemetry_event(
            "documentation_validation_level2", 
            "end", 
            duration_seconds=time.time() - step3_start, 
            metadata={"status": "success", "output_location": output_location}
        )

if __name__ == "__main__":
    main()


import sys
import os
from pathlib import Path

# Ensure virtual environment site-packages are loaded for AppLocker/policy compliance
VENV_SITE_PACKAGES = Path(__file__).resolve().parent.parent / ".venv" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists():
    import site
    site.addsitedir(str(VENV_SITE_PACKAGES))
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Ensure UTF-8 output encoding across environments
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import re
import json
import time
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from crewai import Crew, Process
from crewai.flow.flow import Flow, start, listen, router

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
        apply_math_gate,
        is_concept_existing,
        sanitize_filename,
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
        apply_math_gate,
        is_concept_existing,
        sanitize_filename,
    )

try:
    from index_utils import (
        index_heading_for_level,
        prune_stale_index_links,
        sanitize_index_file,
        generate_clean_topic_digest,
        synchronize_index,
    )
except ImportError:
    from src.index_utils import (
        index_heading_for_level,
        prune_stale_index_links,
        sanitize_index_file,
        generate_clean_topic_digest,
        synchronize_index,
    )

try:
    from a2a_math_client import call_a2a_math_service, extract_equations_from_report
except ImportError:
    from src.a2a_math_client import call_a2a_math_service, extract_equations_from_report

try:
    from equation_logger import log_equations
except ImportError:
    from src.equation_logger import log_equations

try:
    from math_precheck import attach_precheck, run_math_precheck, summarize_precheck
except ImportError:
    from src.math_precheck import attach_precheck, run_math_precheck, summarize_precheck

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

try:
    from advisory_manager import (
        create_advisory_request,
        get_active_directive_for_concept,
        get_active_general_directives,
        get_next_retryable_advisory,
    )
except ImportError:
    from src.advisory_manager import (
        create_advisory_request,
        get_active_directive_for_concept,
        get_active_general_directives,
        get_next_retryable_advisory,
    )

try:
    import backlog_manager
except ImportError:
    from src import backlog_manager


# ─────────────────────────────────────────────────────────────────────────────
# State Schema
# ─────────────────────────────────────────────────────────────────────────────

class UniverseState(BaseModel):
    """Structured Pydantic state tracking the entire lifecycle of a knowledge run."""
    level: int = 1
    dry_run: bool = False
    concept: str = ""
    topic_metadata: Dict[str, Any] = Field(default_factory=dict)
    output_location: str = ""
    level_folder: str = ""
    filename: str = ""

    # Attempt & Micro-Revision counters
    attempt: int = 1
    max_attempts: int = 2
    micro_revisions_count: int = 0
    max_micro_revisions: int = 1

    # Stage outputs
    research_output: str = ""
    math_output: str = ""
    skeptic_output: str = ""
    evaluation_output: str = ""

    # Verifications & Scores
    math_status: str = "MATH_PENDING"
    math_score: Optional[int] = None
    math_total: Optional[int] = None
    skeptic_score: Optional[int] = None
    skeptic_total: Optional[int] = None
    math_precheck: Dict[str, Any] = Field(default_factory=dict)

    # Decision & Routing
    decision: Dict[str, Any] = Field(default_factory=dict)
    decision_status: str = "pending"
    reason_code: str = ""
    follow_up_context: str = ""

    # Finalization
    document_output: str = ""
    validation_passed: bool = False
    completed: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Helper Utilities
# ─────────────────────────────────────────────────────────────────────────────

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


def _resolve_level2_theories(concept: str, topic_metadata: dict | None = None) -> tuple[str, str]:
    """Ensure Level 2 concepts always resolve into distinct (theory_a, theory_b) strings."""
    meta = topic_metadata or {}
    th_a = str(meta.get("theory_a") or "").strip()
    th_b = str(meta.get("theory_b") or "").strip()
    if th_a and th_b and th_a != th_b:
        return th_a, th_b

    parts = re.split(r"\s+(?:vs\.?|versus)\s+", str(concept).strip(), maxsplit=1, flags=re.IGNORECASE)
    if len(parts) == 2 and parts[0].strip() and parts[1].strip():
        left, right = parts[0].strip(), parts[1].strip()
        in_match = re.search(r"(\s+in\s+.+)$", right, flags=re.IGNORECASE)
        if in_match and " in " not in left.lower():
            left = f"{left}{in_match.group(1)}"
        return left, right

    return str(concept).strip(), str(concept).strip()


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


def update_index_file(index_path: str, repo_root: Path):
    """Deterministically synchronize the entire index to match current files on disk and rebuild OKF graph.json."""
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
        archaeologist = EquationArchaeologist(repo_root=repo_root)
        archaeologist.scan_and_index()
    except Exception as exc:
        print(f"Warning: Failed to auto-index equations: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# UniverseFlow
# ─────────────────────────────────────────────────────────────────────────────

class UniverseFlow(Flow[UniverseState]):
    """
    Modern unified event-driven CrewAI Flow orchestrating Level 1, Level 2, and Level 3 knowledge generation.
    Features:
    - Structured Pydantic state machine.
    - Automatic step-level checkpointing to disk for crash recovery (Issue C).
    - In-place micro-revision routing without discarding research drafts (Issue D).
    - Unified single-orchestrator architecture eliminating 1,500+ lines of triplication (Issue B).
    """
    _skip_auto_memory = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo_root = Path(__file__).resolve().parent.parent
        self.checkpoints_dir = self.repo_root / "knowledge_base" / "logs" / "checkpoints"
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.agents = UniverseAgents()
        self.tasks = UniverseTasks()
        self.index_path = "knowledge_base/_index.md"

    def _save_checkpoint(self, stage: str):
        """Save an atomic JSON snapshot of the current state for resilience and debuggability."""
        try:
            safe_concept = sanitize_filename(self.state.concept or "in_flight")
            checkpoint_file = self.checkpoints_dir / f"level_{self.state.level}_{safe_concept}.json"
            snapshot = {
                "stage": stage,
                "timestamp": time.time(),
                "state": self.state.model_dump(),
            }
            checkpoint_file.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as exc:
            print(f"[CHECKPOINT WARNING] Failed to persist checkpoint for stage '{stage}': {exc}")

    def _kickoff_with_salvage(self, crew: Crew, crew_tasks: list, label: str) -> str:
        """
        Run a crew. If it dies on an empty LLM response ("None or empty") after some tasks finished
        (typically the research drafts), re-run ONLY the unfinished tasks once in a fresh crew. The
        finished tasks keep their outputs, and CrewAI reads context from Task.output, so the retried
        tasks still see the drafts. Any other error, or a second failure, is raised to the caller.
        """
        try:
            return str(crew.kickoff()).strip()
        except Exception as err:
            if "none or empty" not in str(err).lower():
                raise
            finished = [t for t in crew_tasks if getattr(t, "output", None)]
            remaining = [t for t in crew_tasks if not getattr(t, "output", None)]
            if not finished or not remaining:
                raise
            print(
                f"[FLOW CREW RETRY] {label}: empty LLM response after {len(finished)} finished task(s); "
                f"re-running the remaining {len(remaining)} task(s) once with the existing drafts."
            )
            log_telemetry_event("crew_empty_response_retry", "start", metadata={
                "label": label, "finished_tasks": len(finished), "remaining_tasks": len(remaining),
            })
            agents, seen = [], set()
            for t in remaining:
                if t.agent is not None and id(t.agent) not in seen:
                    seen.add(id(t.agent))
                    agents.append(t.agent)
            retry_crew = Crew(
                agents=agents,
                tasks=remaining,
                process=Process.sequential,
                verbose=True,
                step_callback=make_step_callback(f"{label}_retry"),
            )
            result = str(retry_crew.kickoff()).strip()
            log_telemetry_event("crew_empty_response_retry", "end", metadata={"label": label, "recovered": True})
            return result

    # ── STEP 1: Topic Selection ──────────────────────────────────────────────

    @start()
    def select_topic(self):
        """Deterministically select or confirm the next learning topic based on level and curriculum."""
        load_dotenv()
        step1_start = time.time()
        log_telemetry_event(f"topic_selection_level{self.state.level}", "start", metadata={"level": self.state.level})

        level = self.state.level
        if level == 1:
            self.state.level_folder = "level_1_fundamental_physics"
        elif level == 2:
            self.state.level_folder = "level_2_advanced_frameworks"
        else:
            self.state.level_folder = "level_3_emergence_and_intelligence"

        # If a concept was passed directly in inputs, respect it immediately
        if self.state.concept:
            if level == 2:
                th_a, th_b = _resolve_level2_theories(self.state.concept, self.state.topic_metadata)
                self.state.topic_metadata = {**self.state.topic_metadata, "theory_a": th_a, "theory_b": th_b}
            self.state.filename = sanitize_filename(self.state.concept)
            self.state.output_location = f"knowledge_base/{self.state.level_folder}/{self.state.filename}"
            print(f"[FLOW TOPIC] Using pre-selected Level {level} concept: '{self.state.concept}'")
            self._save_checkpoint("topic_selected")
            return

        current_index = sanitize_index_file(self.index_path, self.repo_root)
        topic_digest = generate_clean_topic_digest(repo_root=self.repo_root)
        patterns = get_top_failure_patterns()
        pattern_guidance = ""
        if patterns:
            pattern_guidance = "\n\nCRITICAL HISTORICAL FAILURE GUIDANCE:\n" + "\n".join(f"- {p}" for p in patterns)

        standing_directives = get_active_general_directives(f"level_{level}")
        directives_prompt = ""
        if standing_directives:
            directives_prompt = "\n\nPROFESSOR STANDING DIRECTIVES:\n" + "\n".join(f"- {d}" for d in standing_directives)

        # ── Level 1 Logic ──
        if level == 1:
            missing_prereq = get_last_missing_prerequisite(current_index)
            retryable_advisory = get_next_retryable_advisory(level=1, repo_root=self.repo_root)
            backlog_item = backlog_manager.get_next_backlog_item(level=1)

            if missing_prereq:
                print(f"[CLOSED-LOOP FEEDBACK] Prioritizing missing Level 2 prerequisite: '{missing_prereq}'")
                self.state.concept = missing_prereq
            elif retryable_advisory:
                candidate = retryable_advisory.get("concept")
                print(f"[OFFICE HOURS CLOSED-LOOP] Prioritizing answered advisory retry for Level 1: '{candidate}'")
                self.state.concept = candidate
            elif backlog_item:
                candidate = backlog_item.get("concept") or backlog_item.get("question")
                print(f"[CLOSED-LOOP FEEDBACK] Prioritizing curriculum candidate: '{candidate}'")
                self.state.concept = candidate
            elif self.state.dry_run:
                self.state.concept = "Quantum Entanglement"
            else:
                max_topic_attempts = 4
                excluded_concepts = []
                topic_student = self.agents.student_agent()
                for att in range(1, max_topic_attempts + 1):
                    topic_task = self.tasks.determine_next_topic_task(topic_student, topic_digest)
                    exclusion_prompt = ""
                    if excluded_concepts:
                        exclusion_prompt = "\n\nCRITICAL DEDUPLICATION RULE:\nDo NOT select any of the following:\n" + "\n".join(f"- {c}" for c in excluded_concepts)
                    topic_task.description += (pattern_guidance + directives_prompt + exclusion_prompt)

                    topic_crew = Crew(agents=[topic_student], tasks=[topic_task], verbose=True, step_callback=make_step_callback(f"topic_crew_l1_att{att}"))
                    candidate = str(topic_crew.kickoff()).strip()
                    cand_filename = sanitize_filename(candidate)
                    target_loc = f"knowledge_base/{self.state.level_folder}/{cand_filename}"

                    if (self.repo_root / target_loc).exists() or is_concept_existing(candidate, level=1, repo_root=self.repo_root):
                        print(f"[TOPIC SELECTION RETRY] Attempt {att}/{max_topic_attempts}: '{candidate}' already exists. Retrying...")
                        excluded_concepts.append(candidate)
                        continue
                    else:
                        self.state.concept = candidate
                        break

                if not self.state.concept:
                    self.state.concept = "Quantum Decoherence"

        # ── Level 2 Logic ──
        elif level == 2:
            retryable_advisory = get_next_retryable_advisory(level=2, repo_root=self.repo_root)
            if retryable_advisory:
                candidate = retryable_advisory.get("concept")
                print(f"[OFFICE HOURS CLOSED-LOOP] Prioritizing answered advisory retry for Level 2: '{candidate}'")
                self.state.concept = candidate
                th_a, th_b = _resolve_level2_theories(candidate, self.state.topic_metadata)
                self.state.topic_metadata = {"theory_a": th_a, "theory_b": th_b}
            elif self.state.dry_run:
                self.state.concept = "Asymptotic Safety vs Causal Dynamical Triangulations"
                self.state.topic_metadata = {"theory_a": "Asymptotic Safety Gravity", "theory_b": "Causal Dynamical Triangulations"}
            else:
                max_topic_attempts = 4
                excluded_concepts = []
                topic_student = self.agents.student_agent()
                for att in range(1, max_topic_attempts + 1):
                    topic_task = self.tasks.determine_next_level2_topic_task(topic_student, topic_digest)
                    exclusion_prompt = ""
                    if excluded_concepts:
                        exclusion_prompt = "\n\nCRITICAL DEDUPLICATION RULE:\nDo NOT select any of the following:\n" + "\n".join(f"- {c}" for c in excluded_concepts)
                    topic_task.description += (pattern_guidance + directives_prompt + exclusion_prompt)

                    topic_crew = Crew(agents=[topic_student], tasks=[topic_task], verbose=True, step_callback=make_step_callback(f"topic_crew_l2_att{att}"))
                    sel_output = topic_crew.kickoff()
                    th_a, th_b, cand_concept = _extract_level2_selection(sel_output)
                    cand_filename = sanitize_filename(cand_concept)
                    target_loc = f"knowledge_base/{self.state.level_folder}/{cand_filename}"

                    if (self.repo_root / target_loc).exists() or is_concept_existing(cand_concept, level=2, repo_root=self.repo_root):
                        print(f"[TOPIC SELECTION RETRY] Attempt {att}/{max_topic_attempts}: '{cand_concept}' already exists. Retrying...")
                        excluded_concepts.append(cand_concept)
                        continue
                    else:
                        self.state.concept = cand_concept
                        self.state.topic_metadata = {"theory_a": th_a, "theory_b": th_b}
                        break

                if not self.state.concept:
                    self.state.concept = "Loop Quantum Gravity vs String Theory"
                    self.state.topic_metadata = {"theory_a": "Loop Quantum Gravity", "theory_b": "String Theory"}

        # ── Level 3 Logic ──
        else:
            retryable_advisory = get_next_retryable_advisory(level=3, repo_root=self.repo_root)
            if retryable_advisory:
                candidate = retryable_advisory.get("concept")
                print(f"[OFFICE HOURS CLOSED-LOOP] Prioritizing answered advisory retry for Level 3: '{candidate}'")
                self.state.concept = candidate
            elif self.state.dry_run:
                self.state.concept = "Thermodynamic Limits of Neural Information Processing"
                self.state.topic_metadata = {"focus_area": "Integrated Information Theory & Neural Thermodynamics"}
            else:
                max_topic_attempts = 4
                excluded_concepts = []
                topic_student = self.agents.student_agent()
                for att in range(1, max_topic_attempts + 1):
                    topic_task = self.tasks.determine_next_level3_topic_task(topic_student, topic_digest)
                    exclusion_prompt = ""
                    if excluded_concepts:
                        exclusion_prompt = "\n\nCRITICAL DEDUPLICATION RULE:\nDo NOT select any of the following:\n" + "\n".join(f"- {c}" for c in excluded_concepts)
                    topic_task.description += (pattern_guidance + directives_prompt + exclusion_prompt)

                    topic_crew = Crew(agents=[topic_student], tasks=[topic_task], verbose=True, step_callback=make_step_callback(f"topic_crew_l3_att{att}"))
                    sel_output = topic_crew.kickoff()
                    f_area, cand_concept = _extract_level3_selection(sel_output)
                    cand_filename = sanitize_filename(cand_concept)
                    target_loc = f"knowledge_base/{self.state.level_folder}/{cand_filename}"

                    if (self.repo_root / target_loc).exists() or is_concept_existing(cand_concept, level=3, repo_root=self.repo_root):
                        print(f"[TOPIC SELECTION RETRY] Attempt {att}/{max_topic_attempts}: '{cand_concept}' already exists. Retrying...")
                        excluded_concepts.append(cand_concept)
                        continue
                    else:
                        self.state.concept = cand_concept
                        self.state.topic_metadata = {"focus_area": f_area}
                        break

                if not self.state.concept:
                    self.state.concept = "Thermodynamic Limits of Neural Information Processing"
                    self.state.topic_metadata = {"focus_area": "Thermodynamics of Computation"}

        self.state.filename = sanitize_filename(self.state.concept)
        self.state.output_location = f"knowledge_base/{self.state.level_folder}/{self.state.filename}"

        print(f"[FLOW TOPIC] Selected Level {level} Topic: '{self.state.concept}' -> {self.state.output_location}")
        log_telemetry_event(
            f"topic_selection_level{level}",
            "end",
            duration_seconds=time.time() - step1_start,
            metadata={"selected_concept": self.state.concept, "output_location": self.state.output_location}
        )
        self._save_checkpoint("topic_selected")

    # ── STEP 2: Research & Verification Crew ─────────────────────────────────

    @listen(select_topic)
    def conduct_research_and_verify(self):
        """Execute the multi-agent research, mathematical verification, skeptic audit, and student evaluation."""
        attempt_start = time.time()
        print(f"\n--- STEP 2: Research & Evaluation (Level {self.state.level}, Attempt {self.state.attempt}/{self.state.max_attempts}) ---")
        log_telemetry_event(
            f"research_evaluation_level{self.state.level}_attempt",
            "start",
            metadata={"concept": self.state.concept, "attempt": self.state.attempt}
        )

        level = self.state.level
        concept = self.state.concept

        # Directives & Guidance
        concept_directive = get_active_directive_for_concept(concept, level=level)
        general_directives = get_active_general_directives(f"level_{level}")
        directive_lines = []
        if concept_directive:
            directive_lines.append(f"- DIRECTIVE FOR '{concept}': {concept_directive}")
        if general_directives:
            directive_lines.extend(f"- STANDING DIRECTIVE: {d}" for d in general_directives)

        professor_guidance = ""
        if directive_lines:
            professor_guidance = "\n\nPROFESSOR DIRECTIVES & GUIDANCE:\n" + "\n".join(directive_lines)

        patterns = get_top_failure_patterns()
        pattern_guidance = ""
        if patterns:
            pattern_guidance = "\n\nCRITICAL HISTORICAL FAILURE GUIDANCE:\n" + "\n".join(f"- {p}" for p in patterns)

        # Build agents
        evaluation_student = self.agents.student_agent()
        math_physicist = self.agents.math_physicist_agent()
        skeptic = self.agents.skeptic_agent()

        research_prompt = concept
        if self.state.follow_up_context:
            research_prompt = f"{concept}\nFollow-up context from prior evaluation:\n{self.state.follow_up_context}"

        crew_agents = []
        crew_tasks = []

        if level == 1:
            researcher = self.agents.researcher_agent()
            research_task = self.tasks.research_concept_task(researcher, research_prompt, level=1)
            math_task = self.tasks.math_verification_task(math_physicist, concept, context=[research_task])
            verify_task = self.tasks.verify_research_task(skeptic, concept, context=[research_task, math_task])
            evaluate_task = self.tasks.student_evaluation_task(evaluation_student, concept, context=[research_task, math_task, verify_task])

            if pattern_guidance:
                evaluate_task.description += pattern_guidance
            if professor_guidance:
                research_task.description += professor_guidance
                math_task.description += professor_guidance
                evaluate_task.description += professor_guidance

            crew_agents = [evaluation_student, researcher, math_physicist, skeptic]
            crew_tasks = [research_task, math_task, verify_task, evaluate_task]

        elif level == 2:
            th_a, th_b = _resolve_level2_theories(concept, self.state.topic_metadata)
            self.state.topic_metadata = {**self.state.topic_metadata, "theory_a": th_a, "theory_b": th_b}
            researcher_a = self.agents.researcher_agent()
            researcher_b = self.agents.researcher_agent()

            th_a_prompt = f"{th_a}\nFollow-up context:\n{self.state.follow_up_context}" if self.state.follow_up_context else th_a
            th_b_prompt = f"{th_b}\nFollow-up context:\n{self.state.follow_up_context}" if self.state.follow_up_context else th_b

            research_task_a = self.tasks.research_concept_task(researcher_a, th_a_prompt, level=2)
            research_task_b = self.tasks.research_concept_task(researcher_b, th_b_prompt, level=2)
            math_task = self.tasks.math_verification_task(math_physicist, concept, context=[research_task_a, research_task_b])
            debate_task = self.tasks.debate_theories_task(skeptic, th_a, th_b, context=[research_task_a, research_task_b, math_task])
            evaluate_task = self.tasks.student_level2_debate_evaluation_task(evaluation_student, f"The debate between {th_a} and {th_b}", context=[research_task_a, research_task_b, math_task, debate_task])
            skeptic_task = debate_task

            if pattern_guidance:
                evaluate_task.description += pattern_guidance
            if professor_guidance:
                research_task_a.description += professor_guidance
                research_task_b.description += professor_guidance
                math_task.description += professor_guidance
                debate_task.description += professor_guidance
                evaluate_task.description += professor_guidance

            crew_agents = [researcher_a, researcher_b, math_physicist, skeptic, evaluation_student]
            crew_tasks = [research_task_a, research_task_b, math_task, debate_task, evaluate_task]

        else: # Level 3
            bio_digital_analyst = self.agents.bio_digital_analyst_agent()
            cosmological_architect = self.agents.cosmological_architect_agent()

            research_task_a = self.tasks.research_concept_task(bio_digital_analyst, research_prompt, level=3)
            research_task_b = self.tasks.research_concept_task(cosmological_architect, research_prompt, level=3)
            math_task = self.tasks.math_verification_task(math_physicist, concept, context=[research_task_a, research_task_b])
            verify_task = self.tasks.verify_research_task(skeptic, concept, context=[research_task_a, research_task_b, math_task])
            evaluate_task = self.tasks.student_level3_evaluation_task(evaluation_student, concept, context=[research_task_a, research_task_b, math_task, verify_task])
            skeptic_task = verify_task

            if pattern_guidance:
                evaluate_task.description += pattern_guidance
            if professor_guidance:
                research_task_a.description += professor_guidance
                research_task_b.description += professor_guidance
                math_task.description += professor_guidance
                verify_task.description += professor_guidance
                evaluate_task.description += professor_guidance

            crew_agents = [bio_digital_analyst, cosmological_architect, math_physicist, skeptic, evaluation_student]
            crew_tasks = [research_task_a, research_task_b, math_task, verify_task, evaluate_task]

        if level == 1:
            skeptic_task = verify_task

        # Deterministic math pre-check: runs in code as soon as the draft(s) exist and is appended
        # to the Math Physicist's task; the result is also kept for the math gate.
        self.state.math_precheck = {}
        research_tasks = crew_tasks[:crew_tasks.index(math_task)]
        attach_precheck(research_tasks, math_task, on_result=lambda pre: setattr(self.state, "math_precheck", pre))

        eval_crew = Crew(
            agents=crew_agents,
            tasks=crew_tasks,
            process=Process.sequential,
            verbose=True,
            step_callback=make_step_callback(f"eval_crew_l{level}_att{self.state.attempt}"),
        )

        a2a_proof = None
        if self.state.dry_run:
            self.state.evaluation_output = json.dumps({
                "status": "approved",
                "reason_code": "dry_run",
                "epistemic_status": "[THEORETICAL]",
                "confidence_score": 0.95,
                "summary_for_archivist": f"Dry-run approved summary for Level {level}: {concept}.",
                "follow_up_questions": []
            })
            self.state.research_output = f"Research report for {concept}.\nSources:\n- Author A (2024), https://doi.org/10.1234/test"
            self.state.skeptic_output = "Verification Score: 6/6"
            self.state.math_output = "**Math Score:** 4/4\n[MATH_PROVEN]"
        else:
            try:
                self.state.evaluation_output = self._kickoff_with_salvage(
                    eval_crew, crew_tasks, f"eval_crew_l{level}_att{self.state.attempt}"
                )
            except Exception as kickoff_err:
                print(f"[FLOW CREW ERROR] Evaluation crew kickoff failed: {kickoff_err}")
                self.state.evaluation_output = json.dumps({
                    "status": "rejected",
                    "reason_code": "crew_kickoff_error",
                    "summary_for_archivist": "",
                    "follow_up_questions": [f"Execution failed with error: {str(kickoff_err)[:200]}"]
                })

            # Harvest outputs from task objects
            research_pieces = []
            skeptic_raw = ""
            math_raw = ""
            for t in crew_tasks:
                if hasattr(t, "output") and t.output:
                    out_text = str(t.output.raw)
                    if t == math_task:
                        math_raw = out_text
                    elif t == skeptic_task:  # verify_task or debate_task
                        skeptic_raw = out_text
                    elif t != evaluate_task:
                        research_pieces.append(out_text)

            self.state.research_output = "\n\n".join(research_pieces) if research_pieces else self.state.research_output
            self.state.math_output = math_raw
            self.state.skeptic_output = skeptic_raw

            # A2A Math Service & Equation extraction
            try:
                all_crew_text = "\n".join(filter(None, [self.state.math_output, self.state.skeptic_output, self.state.evaluation_output]))
                a2a_equations = extract_equations_from_report(all_crew_text)
                a2a_result = call_a2a_math_service(concept, a2a_equations)
                if a2a_result:
                    a2a_proof = (a2a_result.get("result") or {}).get("proof_report")
            except Exception as a2a_err:
                print(f"[A2A INTEGRATION] Warning: {a2a_err}")

        # Parse metrics
        self.state.decision = parse_student_decision(self.state.evaluation_output)
        self.state.decision_status = self.state.decision.get("status", "rejected")
        self.state.reason_code = self.state.decision.get("reason_code", "unknown")

        self.state.skeptic_score, self.state.skeptic_total = parse_skeptic_checklist_score(self.state.skeptic_output)
        if self.state.skeptic_score is None:
            self.state.skeptic_score, self.state.skeptic_total = parse_skeptic_checklist_score(self.state.evaluation_output)

        self.state.math_score, self.state.math_total = parse_math_score(self.state.math_output)
        self.state.math_status = parse_math_status(self.state.math_output)

        # Code-run pre-check (normally produced by the research-task callback; recomputed if it didn't fire)
        if not self.state.math_precheck and self.state.research_output:
            self.state.math_precheck = run_math_precheck(self.state.research_output)

        # Math gate: a tool-confirmed flaw in the math report or the pre-check blocks Student approval
        self.state.decision, math_gate = apply_math_gate(
            self.state.decision, self.state.math_output, self.state.math_precheck
        )
        if math_gate.get("overrode_approval"):
            print(f"[MATH GATE] Student approval overridden: {'; '.join(math_gate['reasons'])}")
            self.state.decision_status = self.state.decision.get("status", "rejected")
            self.state.reason_code = self.state.decision.get("reason_code", "mathematical_flaw_or_inconsistency")
        elif math_gate.get("coherence_violation"):
            print(f"[MATH GATE] Coherence warning: {'; '.join(math_gate['reasons'])}")

        # Log equations
        try:
            all_text_eqs = "\n".join(filter(None, [self.state.math_output, self.state.skeptic_output, self.state.evaluation_output]))
            discovered_eqs = extract_equations_from_report(all_text_eqs)
            log_equations(
                concept=concept,
                level=level,
                equations=discovered_eqs,
                math_status=self.state.math_status,
                math_score=self.state.math_score,
                math_total=self.state.math_total,
                a2a_proof_report=a2a_proof,
            )
        except Exception as eq_err:
            print(f"[EQ DB] Warning: {eq_err}")

        # Telemetry
        log_telemetry_event(
            f"research_evaluation_level{level}_attempt",
            "end",
            duration_seconds=time.time() - attempt_start,
            metadata={
                "status": self.state.decision_status,
                "reason_code": self.state.reason_code,
                "score": self.state.skeptic_score,
                "total_score": self.state.skeptic_total,
                "math_score": self.state.math_score,
                "math_status": self.state.math_status,
                "math_tool_verdicts": math_gate.get("tool_verdicts", {}),
                "math_precheck": summarize_precheck(self.state.math_precheck),
                "math_gate_blocked": bool(math_gate.get("overrode_approval")),
                "math_coherence_violation": bool(math_gate.get("coherence_violation")),
                "attempt": self.state.attempt,
            }
        )

        self._save_checkpoint(f"evaluated_attempt_{self.state.attempt}")

    # ── STEP 3: Router & Branching ───────────────────────────────────────────

    @router(conduct_research_and_verify)
    def evaluate_route(self):
        """Intelligently route execution between approval, micro-revision, retry, or escalation."""
        status = self.state.decision_status
        reason_code = self.state.reason_code
        print(f"\n[FLOW ROUTER] Evaluating decision: status='{status}', reason='{reason_code}'")

        if status == "approved":
            return "approved"

        # Log rejection outcome
        log_evaluation_outcome(
            concept=self.state.concept,
            status=status,
            reason_code=reason_code,
            score=self.state.skeptic_score,
            total_score=self.state.skeptic_total,
            follow_up_questions=self.state.decision.get("follow_up_questions", []),
            attempt=self.state.attempt,
            epistemic_status=self.state.decision.get("epistemic_status", "[THEORETICAL]"),
            confidence_score=self.state.decision.get("confidence_score"),
            detailed_rationale=self.state.decision.get("detailed_rationale"),
            agent_needs=self.state.decision.get("agent_needs"),
        )

        # Check eligibility for in-place micro-revision (Issue D)
        # Micro-revision is triggered when research has solid substance but localized flaws:
        # e.g., skeptic score >= 4/6 OR specific math/equation errors that can be patched in-place.
        can_micro_revise = (
            self.state.micro_revisions_count < self.state.max_micro_revisions and
            (
                (self.state.skeptic_score is not None and self.state.skeptic_score >= 4) or
                reason_code in [
                    "mathematical_flaw_or_inconsistency",
                    "missing_math_equations",
                    "insufficient_skeptic_score",
                    "missing_critical_comparisons",
                ]
            )
        )

        if can_micro_revise:
            print(f"[FLOW ROUTER] -> Micro-Revision selected: In-place agent deliberation on localized defects.")
            return "micro_revision"

        if self.state.attempt < self.state.max_attempts:
            print(f"[FLOW ROUTER] -> Full Retry selected: Re-running research attempt {self.state.attempt + 1}/{self.state.max_attempts}.")
            return "full_retry"

        print(f"[FLOW ROUTER] -> Escalate selected: Max attempts exceeded.")
        return "escalate"

    # ── BRANCH 4A: Targeted Micro-Revision ───────────────────────────────────

    @listen("micro_revision")
    def execute_micro_revision(self):
        """Execute in-place targeted micro-revision on the existing draft, preserving valid sections."""
        self.state.micro_revisions_count += 1
        rev_num = self.state.micro_revisions_count
        print(f"\n--- MICRO-REVISION {rev_num}/{self.state.max_micro_revisions}: In-Place Diagnostic Patching ---")
        log_telemetry_event("micro_revision", "start", metadata={"concept": self.state.concept, "revision": rev_num})

        if self.state.dry_run:
            self.state.decision["status"] = "approved"
            self.state.decision_status = "approved"
            self.state.decision["summary_for_archivist"] = f"Approved via dry-run micro-revision for {self.state.concept}."
            print("[MICRO-REVISION] Dry-run micro-revision applied successfully.")
            return

        # Use researcher agent to perform targeted revision on the draft
        lead_agent = self.agents.bio_digital_analyst_agent() if self.state.level == 3 else self.agents.researcher_agent()
        math_agent = self.agents.math_physicist_agent()
        skeptic_agent = self.agents.skeptic_agent()
        student_agent = self.agents.student_agent()

        rev_task = self.tasks.targeted_micro_revision_task(
            agent=lead_agent,
            concept=self.state.concept,
            original_draft=self.state.research_output,
            feedback_dict=self.state.decision,
            level=self.state.level,
        )
        math_task = self.tasks.math_verification_task(math_agent, self.state.concept, context=[rev_task])
        verify_task = self.tasks.verify_research_task(skeptic_agent, self.state.concept, context=[rev_task, math_task])

        if self.state.level == 1:
            eval_task = self.tasks.student_evaluation_task(student_agent, self.state.concept, context=[rev_task, math_task, verify_task])
        elif self.state.level == 2:
            th_a, th_b = _resolve_level2_theories(self.state.concept, self.state.topic_metadata)
            eval_task = self.tasks.student_level2_debate_evaluation_task(student_agent, f"The debate between {th_a} and {th_b}", context=[rev_task, math_task, verify_task])
        else:
            eval_task = self.tasks.student_level3_evaluation_task(student_agent, self.state.concept, context=[rev_task, math_task, verify_task])

        concept_directive = get_active_directive_for_concept(self.state.concept, level=self.state.level)
        general_directives = get_active_general_directives(f"level_{self.state.level}")
        directive_lines = []
        if concept_directive:
            directive_lines.append(f"- DIRECTIVE FOR '{self.state.concept}': {concept_directive}")
        if general_directives:
            directive_lines.extend(f"- STANDING DIRECTIVE: {d}" for d in general_directives)
        if directive_lines:
            prof_guidance = "\n\nPROFESSOR DIRECTIVES & GUIDANCE:\n" + "\n".join(directive_lines)
            rev_task.description += prof_guidance
            math_task.description += prof_guidance
            verify_task.description += prof_guidance
            eval_task.description += prof_guidance

        self.state.math_precheck = {}
        attach_precheck([rev_task], math_task, on_result=lambda pre: setattr(self.state, "math_precheck", pre))

        micro_crew = Crew(
            agents=[lead_agent, math_agent, skeptic_agent, student_agent],
            tasks=[rev_task, math_task, verify_task, eval_task],
            process=Process.sequential,
            verbose=True,
            step_callback=make_step_callback(f"micro_crew_rev{rev_num}"),
        )

        try:
            eval_out = self._kickoff_with_salvage(
                micro_crew, [rev_task, math_task, verify_task, eval_task], f"micro_crew_rev{rev_num}"
            )
            if hasattr(rev_task, "output") and rev_task.output:
                self.state.research_output = str(rev_task.output.raw)
            if hasattr(math_task, "output") and math_task.output:
                self.state.math_output = str(math_task.output.raw)
            if hasattr(verify_task, "output") and verify_task.output:
                self.state.skeptic_output = str(verify_task.output.raw)

            self.state.decision = parse_student_decision(eval_out)
            self.state.decision_status = self.state.decision.get("status", "rejected")
            self.state.reason_code = self.state.decision.get("reason_code", "unknown")

            self.state.math_score, self.state.math_total = parse_math_score(self.state.math_output)
            self.state.math_status = parse_math_status(self.state.math_output)
            self.state.skeptic_score, self.state.skeptic_total = parse_skeptic_checklist_score(self.state.skeptic_output)

            if not self.state.math_precheck and self.state.research_output:
                self.state.math_precheck = run_math_precheck(self.state.research_output)
            self.state.decision, math_gate = apply_math_gate(
                self.state.decision, self.state.math_output, self.state.math_precheck
            )
            if math_gate.get("overrode_approval"):
                print(f"[MATH GATE] Micro-revision approval overridden: {'; '.join(math_gate['reasons'])}")
                self.state.decision_status = self.state.decision.get("status", "rejected")
                self.state.reason_code = self.state.decision.get("reason_code", "mathematical_flaw_or_inconsistency")

            print(f"[MICRO-REVISION RESULT] Status: {self.state.decision_status} (Math: {self.state.math_status}, Skeptic: {self.state.skeptic_score}/{self.state.skeptic_total})")
        except Exception as exc:
            print(f"[MICRO-REVISION ERROR] Failed: {exc}")

        log_telemetry_event("micro_revision", "end", metadata={
            "status": self.state.decision_status,
            "revision": rev_num,
            "math_precheck": summarize_precheck(self.state.math_precheck),
        })
        self._save_checkpoint(f"micro_revision_{rev_num}")

    @router(execute_micro_revision)
    def route_post_micro_revision(self):
        """Route following micro-revision."""
        if self.state.decision_status == "approved":
            return "approved"
        if self.state.attempt < self.state.max_attempts:
            return "full_retry"
        return "escalate"

    # ── BRANCH 4B: Full Retry ────────────────────────────────────────────────

    @listen("full_retry")
    def execute_full_retry(self):
        """Prepare feedback context and execute next full research attempt."""
        self.state.attempt += 1
        agent_needs = self.state.decision.get("agent_needs", {})
        self.state.follow_up_context = json.dumps(
            {
                "reason_code": self.state.reason_code,
                "detailed_rationale": self.state.decision.get("detailed_rationale", ""),
                "agent_needs": agent_needs,
                "follow_up_questions": self.state.decision.get("follow_up_questions", []),
            },
            ensure_ascii=False,
            indent=2,
        )
        print(f"[FULL RETRY] Retrying full research with diagnostic context (attempt {self.state.attempt}/{self.state.max_attempts}).")
        # Run research & verify directly for the new attempt
        self.conduct_research_and_verify()

    @router(execute_full_retry)
    def route_post_full_retry(self):
        """Route following full retry."""
        if self.state.decision_status == "approved":
            return "approved"
        # If still rejected after retry, allow one micro-revision if eligible or escalate
        if self.state.micro_revisions_count < self.state.max_micro_revisions and self.state.skeptic_score and self.state.skeptic_score >= 4:
            return "micro_revision"
        return "escalate"

    # ── BRANCH 4C: Escalation ────────────────────────────────────────────────

    @listen("escalate")
    def execute_escalation(self):
        """Handle persistent rejections by logging tickets and updating the backlog."""
        print(f"\n[ESCALATION] Concept '{self.state.concept}' rejected after {self.state.attempt} attempts (reason: {self.state.reason_code}).")
        agent_needs = self.state.decision.get("agent_needs", {})

        log_rejected_concept(
            concept=self.state.concept,
            level=self.state.level,
            reason_code=self.state.reason_code,
            total_attempts=self.state.attempt,
            follow_up_questions=self.state.decision.get("follow_up_questions", []),
            math_score=self.state.math_score,
            math_status=self.state.math_status,
            last_skeptic_score=self.state.skeptic_score,
            last_skeptic_total=self.state.skeptic_total,
            epistemic_status=self.state.decision.get("epistemic_status"),
            detailed_rationale=self.state.decision.get("detailed_rationale"),
            agent_needs=agent_needs,
        )

        backlog_manager.add_to_backlog(self.state.concept, level=self.state.level, questions=self.state.decision.get("follow_up_questions", []))

        # File an advisory ticket for Professor Office Hours
        default_q = f"Concept '{self.state.concept}' was rejected after {self.state.attempt} attempts ({self.state.reason_code}). How should the agents proceed?"
        create_advisory_request(
            concept=self.state.concept,
            level=self.state.level,
            initiator="UniverseFlow Orchestrator",
            question=agent_needs.get("professor_question") or default_q,
            detailed_rationale=self.state.decision.get("detailed_rationale", ""),
            agent_needs=agent_needs,
            reason_code=self.state.reason_code,
        )

        self._save_checkpoint("escalated")

    # ── BRANCH 4D: Approval & Persistence ────────────────────────────────────

    @listen("approved")
    def persist_and_index(self):
        """Generate final documentation, validate markdown compliance, persist to disk, and synchronize index."""
        step3_start = time.time()
        print(f"\n--- STEP 3: Documentation, Validation & Persistence ---")
        log_telemetry_event(f"documentation_validation_level{self.state.level}", "start", metadata={"concept": self.state.concept, "output_location": self.state.output_location})

        archivist = self.agents.archivist_agent()
        visualizer = self.agents.visualizer_agent()

        visual_task = self.tasks.generate_visual_concept_task(visualizer, self.state.concept) if visualizer else None
        document_task = self.tasks.document_knowledge_task(
            archivist,
            self.state.output_location,
            include_visual=bool(visual_task),
            approved_summary=self.state.decision.get("summary_for_archivist", f"Approved knowledge summary for {self.state.concept}."),
            math_status=self.state.math_status,
            math_score=self.state.math_score,
            math_report=self.state.math_output,
            research_report=self.state.research_output,
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
            step_callback=make_step_callback(f"final_crew_l{self.state.level}"),
        )

        if self.state.dry_run:
            print("DRY_RUN enabled. Skipping final_crew.kickoff() and disk persistence.")
            log_telemetry_event(
                f"documentation_validation_level{self.state.level}",
                "end",
                duration_seconds=time.time() - step3_start,
                metadata={"status": "skipped_dry_run"}
            )
            self._save_checkpoint("completed_dry_run")
            return

        try:
            doc_output = normalize_markdown_output(str(final_crew.kickoff()).strip())
        except Exception as final_err:
            print(f"[ARCHIVIST ERROR] Final crew kickoff failed: {final_err}")
            log_telemetry_event(f"documentation_validation_level{self.state.level}", "end", duration_seconds=time.time() - step3_start, metadata={"status": "error", "error": str(final_err)[:200]})
            return

        valid, validation_errors = validate_concept_markdown(doc_output)
        if not valid:
            print("ERROR: Document validation failed; disk write blocked.")
            for err in validation_errors:
                print(f" - {err}")
            log_telemetry_event(f"documentation_validation_level{self.state.level}", "end", duration_seconds=time.time() - step3_start, metadata={"status": "failed_validation", "errors": validation_errors})
            return

        # Write to disk
        output_file = self.repo_root / self.state.output_location
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(doc_output.rstrip() + "\n", encoding="utf-8")
        self.state.document_output = doc_output
        self.state.validation_passed = True
        self.state.completed = True

        print(f"[FLOW PERSISTENCE] Successfully wrote validated document to: {self.state.output_location}")

        # Update index and OKF graph
        update_index_file(self.index_path, self.repo_root)

        # Backlog resolution
        backlog_manager.resolve_backlog_item(self.state.concept)
        backlog_manager.add_to_backlog(self.state.concept, level=self.state.level, questions=self.state.decision.get("follow_up_questions", []))

        log_telemetry_event(
            f"documentation_validation_level{self.state.level}",
            "end",
            duration_seconds=time.time() - step3_start,
            metadata={"status": "success", "output_location": self.state.output_location}
        )

        # Step 4: Skeptic Sandbox Debate
        try:
            print("--- STEP 4: Skeptic Sandbox Debate (Caveman & Oracle Integration) ---")
            sandbox_script = self.repo_root / "src" / "skeptic_sandbox.py"
            if sandbox_script.exists():
                import subprocess
                subprocess.run([sys.executable, str(sandbox_script), self.state.concept], check=False)
        except Exception as sb_err:
            print(f"[SANDBOX WARNING] Skeptic Sandbox debate failed: {sb_err}")

        self._save_checkpoint("completed")


# ── Standalone CLI Runner ────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Universe Knowledge Unified CrewAI Flow")
    parser.add_argument("--level", type=int, default=1, choices=[1, 2, 3], help="Curriculum level (1, 2, or 3)")
    parser.add_argument("--concept", type=str, default="", help="Specific concept to research (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode without external LLM calls")
    args = parser.parse_args()

    dry_run = args.dry_run or os.getenv("DRY_RUN", "false").lower() == "true"
    flow = UniverseFlow()
    flow.kickoff(inputs={
        "level": args.level,
        "concept": args.concept,
        "dry_run": dry_run,
    })


if __name__ == "__main__":
    main()

import json
import re
from typing import Literal, Optional
from pydantic import BaseModel, Field


DEFAULT_REJECTION = {
    "status": "rejected",
    "reason_code": "parse_error",
    "epistemic_status": "[THEORETICAL]",
    "confidence_score": 0.0,
    "summary_for_archivist": "",
    "detailed_rationale": "Failed to parse a structured JSON evaluation output from the Student Orchestrator.",
    "agent_needs": {
        "researcher_needs": ["Re-run research report with strict adherence to required sections."],
        "math_needs": ["Ensure equations are formatted in standard LaTeX."],
        "human_advisor_needed": False,
    },
    "follow_up_questions": [
        "Reformat the student evaluation as strict JSON following the required schema."
    ],
}


def _extract_json_blob(raw_output: str):
    text = str(raw_output).strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    if text.startswith("{") and text.endswith("}"):
        return text

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return None


def _normalize_status(raw_status: str):
    status = str(raw_status).strip().lower()
    if status in {"approved", "approve", "pass", "passed"}:
        return "approved"
    if status in {"rejected", "reject", "fail", "failed", "needs_follow_up"}:
        return "rejected"
    return None


def _normalize_reason_code(raw_reason: str):
    reason = re.sub(r"[^a-z0-9_]+", "_", str(raw_reason).strip().lower())
    reason = re.sub(r"_+", "_", reason).strip("_")
    return reason or "unspecified"


def _normalize_epistemic_status(raw: str, default: str = "[THEORETICAL]") -> str:
    s = str(raw or "").strip().upper()
    if not s:
        return default
    if not s.startswith("[") and not s.endswith("]"):
        s = f"[{s}]"
    if s in {"[VERIFIED]", "[THEORETICAL]", "[CONJECTURED]", "[HYPOTHETICAL]"}:
        return s
    return default


def _normalize_confidence_score(raw: any, default: float = 0.5) -> float:
    try:
        val = float(raw)
        return max(0.0, min(1.0, round(val, 2)))
    except (ValueError, TypeError):
        return default


def _normalize_agent_needs(raw: any) -> dict:
    if not isinstance(raw, dict):
        return {
            "researcher_needs": [],
            "math_needs": [],
            "human_advisor_needed": False,
        }
    researcher_needs = raw.get("researcher_needs", [])
    if isinstance(researcher_needs, str):
        researcher_needs = [researcher_needs.strip()] if researcher_needs.strip() else []
    elif isinstance(researcher_needs, list):
        researcher_needs = [str(x).strip() for x in researcher_needs if str(x).strip()]
    else:
        researcher_needs = []

    math_needs = raw.get("math_needs", [])
    if isinstance(math_needs, str):
        math_needs = [math_needs.strip()] if math_needs.strip() else []
    elif isinstance(math_needs, list):
        math_needs = [str(x).strip() for x in math_needs if str(x).strip()]
    else:
        math_needs = []

    human_needed = bool(raw.get("human_advisor_needed", False))
    prof_q = str(raw.get("professor_question", "")).strip()
    return {
        "researcher_needs": researcher_needs,
        "math_needs": math_needs,
        "human_advisor_needed": human_needed,
        "professor_question": prof_q,
    }


def parse_student_decision(raw_output: str):
    blob = _extract_json_blob(raw_output)
    if not blob:
        return {**DEFAULT_REJECTION}

    try:
        data = json.loads(blob)
    except json.JSONDecodeError:
        try:
            # LLMs frequently output raw LaTeX like \mid, \(, \arg, \phi in JSON strings without escaping.
            # Replace single backslashes that are not valid JSON escape sequences with double backslashes.
            repaired_blob = re.sub(r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', blob)
            data = json.loads(repaired_blob)
        except Exception:
            return {**DEFAULT_REJECTION}

    status = _normalize_status(data.get("status", ""))
    if not status:
        return {**DEFAULT_REJECTION, "reason_code": "invalid_status"}

    summary = str(
        data.get("summary_for_archivist")
        or data.get("approved_summary")
        or data.get("summary")
        or ""
    ).strip()

    follow_up_raw = data.get("follow_up_questions", [])
    if isinstance(follow_up_raw, str):
        follow_up_questions = [follow_up_raw.strip()] if follow_up_raw.strip() else []
    elif isinstance(follow_up_raw, list):
        follow_up_questions = [str(item).strip() for item in follow_up_raw if str(item).strip()]
    else:
        follow_up_questions = []

    epistemic_status = _normalize_epistemic_status(
        data.get("epistemic_status") or data.get("status_classification"),
        default="[VERIFIED]" if status == "approved" else "[THEORETICAL]"
    )
    confidence_score = _normalize_confidence_score(
        data.get("confidence_score"),
        default=0.9 if status == "approved" else 0.4
    )
    detailed_rationale = str(
        data.get("detailed_rationale")
        or data.get("rationale")
        or data.get("reason_description")
        or ""
    ).strip()
    if not detailed_rationale:
        detailed_rationale = summary if status == "approved" else f"Rejected due to {data.get('reason_code', 'unspecified')}."

    agent_needs = _normalize_agent_needs(data.get("agent_needs"))

    decision = {
        "status": status,
        "reason_code": _normalize_reason_code(data.get("reason_code", "unspecified")),
        "epistemic_status": epistemic_status,
        "confidence_score": confidence_score,
        "summary_for_archivist": summary,
        "detailed_rationale": detailed_rationale,
        "agent_needs": agent_needs,
        "follow_up_questions": follow_up_questions,
    }

    if decision["status"] == "approved" and not decision["summary_for_archivist"]:
        decision["summary_for_archivist"] = "Approved. Document the validated concept with citations and verification notes."

    if decision["status"] == "rejected" and not decision["follow_up_questions"]:
        decision["follow_up_questions"] = [
            "Clarify missing evidence, contradictions, and required citations before re-evaluation."
        ]

    return decision


def normalize_markdown_output(raw_output: str):
    text = str(raw_output).strip()

    # Extract content inside markdown code block if present (discards external preamble/postamble)
    fence_match = re.search(r"```(?:markdown|md)?\s*\n([\s\S]*?)\n```", text, re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()
    elif text.startswith("```"):
        text = re.sub(r"^```(?:markdown|md)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    # Step 1: Extract and isolate YAML frontmatter if present
    frontmatter = ""
    # Find first --- and its closing ---
    first_dash = text.find("---")
    if first_dash != -1:
        second_dash = text.find("---", first_dash + 3)
        if second_dash != -1:
            frontmatter = text[first_dash:second_dash + 3].strip()
            # The body is everything after the closing ---
            body_text = text[second_dash + 3:].strip()
        else:
            body_text = text
    else:
        body_text = text

    # Step 2: Extract top-level title `# Title`
    title = ""
    title_match = re.search(r"^#\s+(.+)$", body_text, re.MULTILINE)
    if title_match:
        title = title_match.group(0).strip()
        body_text = body_text.replace(title, "", 1).strip()
    else:
        # Try to extract from frontmatter if available
        if frontmatter:
            title_fm = re.search(r"title:\s*\"?([^\n\"]+)\"?", frontmatter, re.IGNORECASE)
            if title_fm:
                title = f"# {title_fm.group(1).strip()}"
            else:
                title = "# Fundamental Physics Concept"
        else:
            title = "# Fundamental Physics Concept"

    # Step 3: Standardize headings line-by-line in body_text
    heading_patterns = [
        (1, r"^#*\s*(?:\d+\.?\s*)?Overview.*$", "## 1. Overview"),
        (2, r"^#*\s*(?:\d+\.?\s*)?(?:Detailed\s+)?Explanation.*$", "## 2. Detailed Explanation"),
        (3, r"^#*\s*(?:\d+\.?\s*)?(?:Mathematical\s+)?Framework.*$", "## 3. Mathematical Framework"),
        (4, r"^#*\s*(?:\d+\.?\s*)?(?:Skeptical\s+Perspectives|Alternative\s+Hypotheses|Skeptical\s+Perspectives\s*&\s*Alternative\s+Hypotheses).*$", "## 4. Skeptical Perspectives & Alternative Hypotheses"),
        (5, r"^#*\s*(?:\d+\.?\s*)?(?:Verification\s*&\s*Skeptic's\s*Notes|Verification\s+Notes|Skeptic's\s*Notes).*$", "## 5. Verification & Skeptic's Notes"),
        (6, r"^#*\s*(?:\d+\.?\s*)?(?:Visual\s+Representation|Visual\s+Grounding|Visualization).*$", "## 6. Visual Representation"),
        (7, r"^#*\s*(?:\d+\.?\s*)?Related\s+Concepts.*$", "## 7. Related Concepts"),
        (8, r"^#*\s*(?:\d+\.?\s*)?(?:Mathematical\s+)?Derivation.*$", "## 8. Mathematical Derivation"),
        (9, r"^#*\s*(?:\d+\.?\s*)?(?:Mathematical\s+)?Integrity.*Report.*$", "## 9. Mathematical Integrity Report")
    ]

    lines = body_text.splitlines()
    for idx, line in enumerate(lines):
        line_stripped = line.strip()
        for h_id, pattern, standard_heading in heading_patterns:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                lines[idx] = standard_heading
                break
    body_text = "\n".join(lines)

    # Step 4: Parse contents for each section
    REQUIRED_HEADINGS = [
        "## 1. Overview",
        "## 2. Detailed Explanation",
        "## 3. Mathematical Framework",
        "## 4. Skeptical Perspectives & Alternative Hypotheses",
        "## 5. Verification & Skeptic's Notes",
        "## 6. Visual Representation",
        "## 7. Related Concepts"
    ]

    # Detect optional headings dynamically (e.g. ## 8. ... and ## 9. ...)
    detected_optional_headings = []
    for match in re.finditer(r'^##\s+([89]\..*)$', body_text, re.MULTILINE):
        heading_text = match.group(0).strip()
        pos = match.start()
        detected_optional_headings.append((pos, heading_text))

    all_headings = []
    # Add required headings that exist in the text
    for heading in REQUIRED_HEADINGS:
        pos = body_text.find(heading)
        if pos != -1:
            all_headings.append((pos, heading))

    # Add detected optional headings
    all_headings.extend(detected_optional_headings)

    # Sort by character index to preserve relative ordering in original text
    all_headings.sort(key=lambda x: x[0])

    section_contents = {}
    for i in range(len(all_headings)):
        pos, heading = all_headings[i]
        start_idx = pos + len(heading)
        if i + 1 < len(all_headings):
            end_idx = all_headings[i+1][0]
            content = body_text[start_idx:end_idx].strip()
        else:
            content = body_text[start_idx:].strip()
        section_contents[heading] = content

    # Step 5: Assign default placeholders for any missing headings
    default_placeholders = {
        "## 1. Overview": "*(Overview content pending validation.)*",
        "## 2. Detailed Explanation": "*(Detailed explanation pending research.)*",
        "## 3. Mathematical Framework": "*(No mathematical framework compiled.)*",
        "## 4. Skeptical Perspectives & Alternative Hypotheses": "*(No alternative hypotheses compiled.)*",
        "## 5. Verification & Skeptic's Notes": "*(Verification notes pending peer review.)*",
        "## 6. Visual Representation": "*(No visual representation compiled.)*",
        "## 7. Related Concepts": "*(No related concepts linked.)*"
    }

    # Step 6: Reconstruct the document body in perfect order
    reconstructed_body = []
    for heading in REQUIRED_HEADINGS:
        content = section_contents.get(heading, "").strip()
        if not content:
            content = default_placeholders[heading]
        reconstructed_body.append(heading)
        reconstructed_body.append(content)
        reconstructed_body.append("") # Spacer line

    # Reconstruct any optional/custom headings (like ## 8. and ## 9.)
    for _, heading in all_headings:
        if heading not in REQUIRED_HEADINGS:
            content = section_contents.get(heading, "").strip()
            reconstructed_body.append(heading)
            reconstructed_body.append(content)
            reconstructed_body.append("") # Spacer line

    # Step 7: Parse, repair and guarantee all required keys in frontmatter
    default_fm_keys = {
        "title": f'"{title.replace("#", "").strip()}"',
        "level": "1",
        "status": '"[THEORETICAL]"',
        "sources": '  - "Standard scientific consensus"'
    }

    parsed_keys = {}
    sources_lines = []
    in_sources = False

    if frontmatter:
        # Reparse inner keys of existing frontmatter block
        # Split into lines and clean
        fm_lines = [line.strip() for line in frontmatter.splitlines() if line.strip()]
        if fm_lines and fm_lines[0] == "---":
            fm_lines = fm_lines[1:]
        if fm_lines and fm_lines[-1] == "---":
            fm_lines = fm_lines[:-1]

        for line in fm_lines:
            if line.startswith("-") and in_sources:
                sources_lines.append(line)
                continue

            if ":" in line:
                parts = line.split(":", 1)
                key = parts[0].strip().lower()
                val = parts[1].strip()

                if key == "sources":
                    in_sources = True
                    if val:  # single line source, e.g. sources: [A, B]
                        sources_lines.append(f"  - {val}")
                    continue

                in_sources = False
                parsed_keys[key] = val

        if "title" in parsed_keys:
            default_fm_keys["title"] = parsed_keys["title"]
        if "level" in parsed_keys:
            default_fm_keys["level"] = parsed_keys["level"]
        if "status" in parsed_keys:
            default_fm_keys["status"] = parsed_keys["status"]

    # Reconstruct perfectly
    repaired_lines = []
    repaired_lines.append("title: " + default_fm_keys["title"])
    repaired_lines.append("level: " + str(default_fm_keys["level"]))
    repaired_lines.append("status: " + default_fm_keys["status"])

    # Reconstruct math fields if they exist in parsed_keys
    if "math_status" in parsed_keys:
        val = parsed_keys["math_status"].strip()
        if not (val.startswith('"') and val.endswith('"')):
            val = f'"{val}"'
        repaired_lines.append("math_status: " + val)
    if "math_score" in parsed_keys:
        val = parsed_keys["math_score"].strip()
        if not (val.startswith('"') and val.endswith('"')):
            val = f'"{val}"'
        repaired_lines.append("math_score: " + val)

    repaired_lines.append("sources:")
    if sources_lines:
        for s in sources_lines:
            s_clean = s.strip().lstrip("-").strip()
            if not ((s_clean.startswith('"') and s_clean.endswith('"')) or (s_clean.startswith("'") and s_clean.endswith("'"))):
                if ": " in s_clean or s_clean.startswith("[") or s_clean.startswith("{"):
                    escaped = s_clean.replace('"', '\\"')
                    s_clean = f'"{escaped}"'
            repaired_lines.append(f"  - {s_clean}")
    else:
        repaired_lines.append(default_fm_keys["sources"])

    frontmatter = "---\n" + "\n".join(repaired_lines) + "\n---"

    final_doc = f"{frontmatter}\n\n{title}\n\n" + "\n".join(reconstructed_body)
    return final_doc.strip()



def validate_concept_markdown(markdown_text: str):
    errors = []
    warnings = []
    text = str(markdown_text or "").strip()
    if not text:
        return False, ["Document is empty."]

    frontmatter_match = re.search(r"^---\s*\n([\s\S]*?)\n---\s*", text)
    if not frontmatter_match:
        errors.append("Missing YAML frontmatter block.")
    else:
        frontmatter = frontmatter_match.group(1).lower()
        for key in ["title:", "level:", "status:", "sources:"]:
            if key not in frontmatter:
                errors.append(f"Frontmatter missing required key: {key}")
        # Soft check for new math fields (warning, not blocking)
        for math_key in ["math_status:", "math_score:"]:
            if math_key not in frontmatter:
                warnings.append(f"Frontmatter missing math field: {math_key} (will be added by math enrichment pipeline)")

    required_sections = [
        "## 1. Overview",
        "## 2. Detailed Explanation",
        "## 3. Mathematical Framework",
        "## 4. Skeptical Perspectives & Alternative Hypotheses",
        "## 5. Verification & Skeptic's Notes",
        "## 6. Visual Representation",
        "## 7. Related Concepts",
    ]
    for heading in required_sections:
        if heading not in text:
            errors.append(f"Missing required section heading: {heading}")

    # Soft check for math sections (sections 8 & 9 are added by enrichment pipeline)
    for math_section in ["## 8. Mathematical Derivation", "## 9. Mathematical Integrity Report"]:
        if math_section not in text:
            warnings.append(f"Math section not yet present: {math_section} (added by math_enrichment.py)")

    if not re.search(r"^#\s+.+", text, re.MULTILINE):
        errors.append("Missing top-level title heading (e.g., '# Concept Name').")

    # Log warnings to console (non-blocking)
    for w in warnings:
        print(f"  [MATH WARN] {w}")

    return len(errors) == 0, errors



def parse_skeptic_checklist_score(skeptic_output: str):
    """
    Parses the skeptic's output to find the verification score or calculate it from the checkboxes.
    Returns (score, total) or (None, None).
    """
    text = str(skeptic_output or "")

    # 1. Try to find an explicit "Verification Score: X/Y" or "Score: X/Y"
    score_match = re.search(r"Verification\s*Score:\s*(\d+)\s*/\s*(\d+)", text, re.IGNORECASE)
    if not score_match:
        score_match = re.search(r"Score:\s*(\d+)\s*/\s*(\d+)", text, re.IGNORECASE)

    if score_match:
        return int(score_match.group(1)), int(score_match.group(2))

    # 2. Fallback: Parse markdown checkboxes like `- [x]` or `- [ ]`
    checkboxes = re.findall(r"-\s*\[([ xX])\]\s", text)
    if checkboxes:
        checked = sum(1 for cb in checkboxes if cb.lower() == 'x')
        total = len(checkboxes)
        return checked, total

    return None, None


def check_level2_prerequisites(theory_a: str, theory_b: str, concept_name: str, index_content: str):
    """
    Checks if prerequisites for selected Level 2 topics exist in the current index.
    Returns (True, None) if prerequisites are met.
    Otherwise returns (False, fallback_concept) suggesting a missing prerequisite to learn first.
    """
    prerequisites = {
        "gravity": ["General Relativity", "Quantum Mechanics"],
        "quantum": ["Quantum Mechanics"],
        "string": ["Quantum Mechanics", "General Relativity"],
        "supersymmetry": ["Quantum Mechanics"],
        "cosmology": ["General Relativity"],
    }

    index_lower = index_content.lower()
    combined_text = f"{theory_a} {theory_b} {concept_name}".lower()

    for keyword, prereqs in prerequisites.items():
        if keyword in combined_text:
            for prereq in prereqs:
                if prereq.lower() not in index_lower:
                    return False, prereq

    return True, None


def parse_math_score(math_output: str):
    """
    Parses the Math Physicist's verification report to extract the Math Score (X/4).
    Returns (score: int | None, total: int | None).

    Handles formats like:
      - "Math Score: 3/4"
      - "**Math Score:** 3/4"
      - "Score: 3/4"
    """
    text = str(math_output or "")

    # Strip markdown bold asterisks before matching for robustness
    stripped = text.replace("**", "").replace("*", "")

    # Primary: Match "Math Score: X/Y" (after stripping)
    match = re.search(r'Math\s*Score\s*:\s*(\d+)\s*/\s*(\d+)', stripped, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))

    # Secondary: generic score format anchored to denominator 4 (after stripping)
    match = re.search(r'Score\s*:\s*(\d+)\s*/\s*4', stripped, re.IGNORECASE)
    if match:
        return int(match.group(1)), 4

    return None, None


def parse_math_status(math_output: str) -> str:
    """
    Parses the Math Physicist's report to extract the assigned math_status label.
    Returns one of: MATH_PROVEN, MATH_CONSISTENT, MATH_CONJECTURED, MATH_TOPOLOGICAL,
                    MATH_FLAWED, MATH_PENDING, or MATH_UNKNOWN (if not found).
    """
    text = str(math_output or "")
    valid_statuses = [
        "MATH_PROVEN", "MATH_CONSISTENT", "MATH_CONJECTURED",
        "MATH_TOPOLOGICAL", "MATH_FLAWED", "MATH_PENDING",
    ]
    for status in valid_statuses:
        # Match [MATH_PROVEN] or MATH_PROVEN
        if re.search(rf"\[?{re.escape(status)}\]?", text, re.IGNORECASE):
            return status
    return "MATH_UNKNOWN"


def sanitize_filename(name: str, max_len: int = 180) -> str:
    """Sanitizes a concept name into a valid markdown filename, capped at max_len characters."""
    s = re.sub(r'[^a-zA-Z0-9\s]', '', str(name)).strip().replace(' ', '_').lower()
    if len(s) > max_len:
        s = s[:max_len].rstrip('_')
    return f"{s}.md"


def is_concept_existing(concept_name: str, level: int = 2, repo_root=None, max_len: int = 180) -> bool:
    """
    Checks whether a concept file or OKF node ID already exists on disk, in graph.json, or in _index.md.
    """
    if not concept_name or not str(concept_name).strip():
        return False

    raw_s = re.sub(r'[^a-zA-Z0-9\s]', '', str(concept_name)).strip().replace(' ', '_').lower()
    s = raw_s[:max_len].rstrip('_') if len(raw_s) > max_len else raw_s
    filename = f"{s}.md"

    if repo_root is None:
        from pathlib import Path
        repo_root = Path(__file__).resolve().parent.parent

    # Check OKF graph.json manifest first
    graph_path = repo_root / "knowledge_base" / "graph.json"
    if graph_path.exists():
        try:
            with open(graph_path, "r", encoding="utf-8") as f:
                graph_data = json.load(f)
                for node in graph_data.get("nodes", []):
                    if node.get("id") in [s, raw_s] or node.get("path", "").endswith(filename):
                        return True
        except Exception:
            pass

    # Check disk file
    if level == 1:
        level_folder = "level_1_fundamental_physics"
    elif level == 3:
        level_folder = "level_3_emergence_and_intelligence"
    else:
        level_folder = "level_2_advanced_frameworks"

    filepath = repo_root / "knowledge_base" / level_folder / filename
    if filepath.exists():
        return True

    # Check _index.md fallback
    index_path = repo_root / "knowledge_base" / "_index.md"
    if index_path.exists():
        try:
            index_text = index_path.read_text(encoding="utf-8").lower()
            if filename in index_text or s in index_text or raw_s in index_text:
                return True
        except Exception:
            pass

    return False


class PeerReviewRequest(BaseModel):
    """Input contract for requesting a peer-review or critique resolution."""
    critique_text_or_path: str = Field(
        ...,
        description="Text of the critique/objection or path to an archived/pending review file."
    )
    target_concept: Optional[str] = Field(
        None,
        description="Name or slug of the target physics concept being critiqued."
    )
    review_type: Literal[
        "auto",
        "dimensional_analysis",
        "bibliography_verification",
        "derivation_proof",
        "axiomatic_assumptions"
    ] = Field(
        default="auto",
        description="Category of peer review to perform."
    )
    context_markdown: Optional[str] = Field(
        None,
        description="Optional current markdown text of the concept being critiqued."
    )


class PeerReviewResolution(BaseModel):
    """Output contract containing structured resolution of a peer-review critique."""
    resolution_status: Literal["RESOLVED", "PARTIALLY_RESOLVED", "CONJECTURAL_LIMIT"] = Field(
        ...,
        description="Overall resolution verdict."
    )
    review_type: str = Field(
        ...,
        description="Determined or requested review category."
    )
    critique_addressed: str = Field(
        ...,
        description="Summary of the specific critique or objection addressed."
    )
    target_concepts: list[str] = Field(
        default_factory=list,
        description="Target or related canonical concepts."
    )
    technical_resolution: str = Field(
        ...,
        description="Detailed mathematical, dimensional, or bibliographic resolution."
    )
    verified_equations: list[str] = Field(
        default_factory=list,
        description="List of equations verified or derived."
    )
    verified_sources: list[str] = Field(
        default_factory=list,
        description="Verified peer-reviewed sources or replacements."
    )
    axiomatic_boundaries: list[str] = Field(
        default_factory=list,
        description="Documented assumptions, limits, or proof boundaries."
    )
    suggested_patch_markdown: str = Field(
        ...,
        description="Markdown snippet that can be integrated into the knowledge base."
    )


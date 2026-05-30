import json
import re


DEFAULT_REJECTION = {
    "status": "rejected",
    "reason_code": "parse_error",
    "summary_for_archivist": "",
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


def parse_student_decision(raw_output: str):
    blob = _extract_json_blob(raw_output)
    if not blob:
        return {**DEFAULT_REJECTION}

    try:
        data = json.loads(blob)
    except json.JSONDecodeError:
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

    decision = {
        "status": status,
        "reason_code": _normalize_reason_code(data.get("reason_code", "unspecified")),
        "summary_for_archivist": summary,
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
        (7, r"^#*\s*(?:\d+\.?\s*)?Related\s+Concepts.*$", "## 7. Related Concepts")
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

    section_contents = {}
    heading_positions = []
    for heading in REQUIRED_HEADINGS:
        pos = body_text.find(heading)
        if pos != -1:
            heading_positions.append((pos, heading))

    # Sort by character index
    heading_positions.sort()

    for i in range(len(heading_positions)):
        pos, heading = heading_positions[i]
        start_idx = pos + len(heading)
        if i + 1 < len(heading_positions):
            end_idx = heading_positions[i+1][0]
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

    # Step 7: Parse, repair and guarantee all required keys in frontmatter
    if not frontmatter:
        clean_title = title.replace("#", "").strip()
        frontmatter = (
            f"---\n"
            f"title: \"{clean_title}\"\n"
            f"level: 1\n"
            f"status: \"[THEORETICAL]\"\n"
            f"sources:\n"
            f"  - \"Standard scientific consensus\"\n"
            f"---"
        )
    else:
        # Reparse inner keys of existing frontmatter block
        fm_inner_match = re.search(r"^---\s*\n([\s\S]*?)\n---", frontmatter)
        if fm_inner_match:
            fm_inner = fm_inner_match.group(1)
            fm_keys = {}
            for line in fm_inner.splitlines():
                if ":" in line:
                    parts = line.split(":", 1)
                    fm_keys[parts[0].strip().lower()] = parts[1].strip()

            repaired_lines = []
            
            # 1. Title
            if "title" in fm_keys:
                repaired_lines.append(f"title: {fm_keys['title']}")
            else:
                clean_title = title.replace("#", "").strip()
                repaired_lines.append(f"title: \"{clean_title}\"")
            
            # 2. Level
            if "level" in fm_keys:
                repaired_lines.append(f"level: {fm_keys['level']}")
            else:
                repaired_lines.append("level: 1")
            
            # 3. Status
            if "status" in fm_keys:
                repaired_lines.append(f"status: {fm_keys['status']}")
            else:
                repaired_lines.append("status: \"[THEORETICAL]\"")
            
            # 4. Sources
            if "sources" in fm_keys:
                sources_match = re.search(r"sources:[\s\S]*", fm_inner, re.IGNORECASE)
                if sources_match:
                    repaired_lines.append(sources_match.group(0).strip())
                else:
                    repaired_lines.append("sources:\n  - \"Standard scientific consensus\"")
            else:
                repaired_lines.append("sources:\n  - \"Standard scientific consensus\"")
                
            frontmatter = "---\n" + "\n".join(repaired_lines) + "\n---"

    final_doc = f"{frontmatter}\n\n{title}\n\n" + "\n".join(reconstructed_body)
    return final_doc.strip()


def validate_concept_markdown(markdown_text: str):
    errors = []
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

    if not re.search(r"^#\s+.+", text, re.MULTILINE):
        errors.append("Missing top-level title heading (e.g., '# Concept Name').")

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

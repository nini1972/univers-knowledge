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
    if text.startswith("```"):
        text = re.sub(r"^```(?:markdown|md)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    return text


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
        "## 4. Verification & Skeptic's Notes",
        "## 5. Visual Representation",
        "## 6. Related Concepts",
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

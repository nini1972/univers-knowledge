import unittest

from src.workflow_contracts import parse_student_decision, validate_concept_markdown, normalize_markdown_output


VALID_MARKDOWN = """---
title: "Supersymmetry"
level: 2
status: "[THEORETICAL]"
sources:
  - arXiv:hep-ph/9709356
  - CERN report
  - Review article
---

# Supersymmetry

## 1. Overview
Overview text.

## 2. Detailed Explanation
Detailed explanation text.

## 3. Mathematical Framework
$E=mc^2$

## 4. Verification & Skeptic's Notes
Verification notes.

## 5. Visual Representation
[VISUAL_PENDING: pending generation]

## 6. Related Concepts
- [Standard Model]
"""


class TestWorkflowContracts(unittest.TestCase):
    def test_parse_student_decision_approved_payload(self):
        raw = """
        {
          "status": "approved",
          "reason_code": "rigorous_theoretical_report",
          "summary_for_archivist": "[THEORETICAL] Approved with clear limitations.",
          "follow_up_questions": []
        }
        """
        decision = parse_student_decision(raw)
        self.assertEqual(decision["status"], "approved")
        self.assertEqual(decision["reason_code"], "rigorous_theoretical_report")
        self.assertIn("[THEORETICAL]", decision["summary_for_archivist"])

    def test_parse_student_decision_rejected_payload(self):
        raw = """
        {
          "status": "rejected",
          "reason_code": "insufficient_sources",
          "summary_for_archivist": "",
          "follow_up_questions": ["Add one more independent peer-reviewed source."]
        }
        """
        decision = parse_student_decision(raw)
        self.assertEqual(decision["status"], "rejected")
        self.assertEqual(decision["reason_code"], "insufficient_sources")
        self.assertGreaterEqual(len(decision["follow_up_questions"]), 1)

    def test_parse_student_decision_malformed_falls_back_safely(self):
        decision = parse_student_decision("APPROVED: looks good to me")
        self.assertEqual(decision["status"], "rejected")
        self.assertEqual(decision["reason_code"], "parse_error")
        self.assertGreaterEqual(len(decision["follow_up_questions"]), 1)

    def test_status_drives_gate_not_keywords(self):
        raw = """
        {
          "status": "approved",
          "reason_code": "contains_word_fail_but_is_approved",
          "summary_for_archivist": "This text says fail in prose, but status is approved.",
          "follow_up_questions": []
        }
        """
        decision = parse_student_decision(raw)
        rejected = decision["status"] != "approved"
        self.assertFalse(rejected)

    def test_validate_concept_markdown_accepts_valid_document(self):
        valid, errors = validate_concept_markdown(VALID_MARKDOWN)
        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_validate_concept_markdown_rejects_missing_section(self):
        invalid_doc = VALID_MARKDOWN.replace("## 4. Verification & Skeptic's Notes\nVerification notes.\n\n", "")
        valid, errors = validate_concept_markdown(invalid_doc)
        self.assertFalse(valid)
        self.assertTrue(any("## 4. Verification & Skeptic's Notes" in err for err in errors))

    def test_validate_concept_markdown_rejects_missing_frontmatter(self):
        invalid_doc = VALID_MARKDOWN.split("---\n", 2)[-1]
        valid, errors = validate_concept_markdown(invalid_doc)
        self.assertFalse(valid)
        self.assertTrue(any("Missing YAML frontmatter block" in err for err in errors))

    def test_normalize_markdown_output_strips_fences(self):
        raw = """```markdown
# Title
## 1. Overview
content
```"""
        normalized = normalize_markdown_output(raw)
        self.assertFalse(normalized.startswith("```"))
        self.assertIn("# Title", normalized)


if __name__ == "__main__":
    unittest.main()

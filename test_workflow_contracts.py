import unittest
from pathlib import Path

from src.workflow_contracts import (
    parse_student_decision,
    validate_concept_markdown,
    normalize_markdown_output,
    parse_skeptic_checklist_score,
)



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

## 4. Skeptical Perspectives & Alternative Hypotheses
Skeptical perspectives text.

## 5. Verification & Skeptic's Notes
Verification notes.

## 6. Visual Representation
[VISUAL_PENDING: pending generation]

## 7. Related Concepts
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
        invalid_doc = VALID_MARKDOWN.replace("## 5. Verification & Skeptic's Notes\nVerification notes.\n\n", "")
        valid, errors = validate_concept_markdown(invalid_doc)
        self.assertFalse(valid)
        self.assertTrue(any("## 5. Verification & Skeptic's Notes" in err for err in errors))

    def test_validate_concept_markdown_rejects_missing_frontmatter(self):
        invalid_doc = VALID_MARKDOWN.split("---\n", 2)[-1]
        valid, errors = validate_concept_markdown(invalid_doc)
        self.assertFalse(valid)
        self.assertTrue(any("Missing YAML frontmatter block" in err for err in errors))

    def test_normalize_markdown_output_strips_fences_and_preambles(self):
        raw = """Here is your report:
```markdown
---
title: "Quantum Gravity"
level: 2
status: "[THEORETICAL]"
sources:
  - CERN Report
---

# Quantum Gravity
## 1. Overview
Some overview content.
```
I hope this helps!"""
        normalized = normalize_markdown_output(raw)
        self.assertFalse(normalized.startswith("Here is your"))
        self.assertTrue(normalized.startswith("---"))
        self.assertNotIn("I hope this helps!", normalized)
        self.assertIn("# Quantum Gravity", normalized)
        self.assertIn("## 1. Overview", normalized)

    def test_normalize_markdown_standardizes_mismatched_headings(self):
        raw = """---
title: "Dark Matter"
level: 1
status: "[THEORETICAL]"
sources:
  - arXiv:1234.5678
---
# Dark Matter

### 1. overview
Intro here.

## Explanation
Some details.

## 3. Mathematical Framework
$F=ma$

## 4. Alternative hypotheses
Alternative details.

## Skeptic's Notes
Verification info.

## 6. Visualization
A drawing prompt.

## Related Concepts
- [Link]
"""
        normalized = normalize_markdown_output(raw)
        valid, errors = validate_concept_markdown(normalized)
        self.assertTrue(valid, f"Validation failed with errors: {errors}")
        self.assertIn("## 1. Overview", normalized)
        self.assertIn("## 2. Detailed Explanation", normalized)
        self.assertIn("## 3. Mathematical Framework", normalized)
        self.assertIn("## 4. Skeptical Perspectives & Alternative Hypotheses", normalized)
        self.assertIn("## 5. Verification & Skeptic's Notes", normalized)
        self.assertIn("## 6. Visual Representation", normalized)
        self.assertIn("## 7. Related Concepts", normalized)

    def test_normalize_markdown_inserts_missing_headings_with_placeholders(self):
        raw = """---
title: "Standard Model"
level: 1
status: "[VERIFIED]"
sources:
  - CERN website
---
# Standard Model

## 1. Overview
Over.

## 2. Detailed Explanation
Explanation.
"""
        normalized = normalize_markdown_output(raw)
        valid, errors = validate_concept_markdown(normalized)
        self.assertTrue(valid, f"Validation failed with errors: {errors}")
        self.assertIn("## 3. Mathematical Framework", normalized)
        self.assertIn("*(No mathematical framework compiled.)*", normalized)
        self.assertIn("## 7. Related Concepts", normalized)
        self.assertIn("*(No related concepts linked.)*", normalized)

    def test_normalize_markdown_repairs_missing_frontmatter(self):
        raw = """# Electromagnetism

## 1. Overview
The electromagnetic force is one of the four fundamental forces.
"""
        normalized = normalize_markdown_output(raw)
        valid, errors = validate_concept_markdown(normalized)
        self.assertTrue(valid, f"Validation failed with errors: {errors}")
        self.assertTrue(normalized.startswith("---"))
        self.assertIn('title: "Electromagnetism"', normalized)
        self.assertIn('status: "[THEORETICAL]"', normalized)


    def test_parse_skeptic_checklist_score_explicit(self):
        text = "Some critique here.\nVerification Score: 4/5\nOther notes."
        score, total = parse_skeptic_checklist_score(text)
        self.assertEqual(score, 4)
        self.assertEqual(total, 5)

    def test_parse_skeptic_checklist_score_checkbox_fallback(self):
        text = """
        Checklist:
        - [x] Criterion 1
        - [x] Criterion 2
        - [ ] Criterion 3
        - [x] Criterion 4
        """
        score, total = parse_skeptic_checklist_score(text)
        self.assertEqual(score, 3)
        self.assertEqual(total, 4)

    def test_check_level2_prerequisites_blocks_when_missing(self):
        from src.workflow_contracts import check_level2_prerequisites
        index_content = "# Knowledge Base Index\n\n## Level 1\n- [Standard Model](level_1/standard_model.md)"
        theory_a = "String Theory"
        theory_b = "Loop Quantum Gravity"
        concept_name = "Quantum Gravity Debate"
        
        prereq_ok, missing = check_level2_prerequisites(theory_a, theory_b, concept_name, index_content)
        self.assertFalse(prereq_ok)
        self.assertEqual(missing, "General Relativity")

    def test_check_level2_prerequisites_allows_when_present(self):
        from src.workflow_contracts import check_level2_prerequisites
        index_content = "# Knowledge Base Index\n\n## Level 1\n- [General Relativity](level_1/gr.md)\n- [Quantum Mechanics](level_1/qm.md)"
        theory_a = "String Theory"
        theory_b = "Loop Quantum Gravity"
        concept_name = "Quantum Gravity Debate"
        
        prereq_ok, missing = check_level2_prerequisites(theory_a, theory_b, concept_name, index_content)
        self.assertTrue(prereq_ok)
        self.assertIsNone(missing)

    def test_normalize_markdown_repairs_complex_frontmatter(self):
        raw = """---
sources:
  - arXiv:1234.5678
  - http://example.com
title: "Electromagnetism"
level: 1
status: "[VERIFIED]"
---
# Electromagnetism

## 1. Overview
The electromagnetic force is one of the four fundamental forces.
"""
        normalized = normalize_markdown_output(raw)
        valid, errors = validate_concept_markdown(normalized)
        self.assertTrue(valid, f"Validation failed with errors: {errors}")
        self.assertTrue(normalized.startswith("---"))
        self.assertIn('title: "Electromagnetism"', normalized)
        self.assertIn('level: 1', normalized)
        self.assertIn('status: "[VERIFIED]"', normalized)
        self.assertIn('  - arXiv:1234.5678', normalized)
        self.assertIn('  - http://example.com', normalized)

    def test_is_concept_existing_returns_true_for_existing_file(self):
        from src.workflow_contracts import is_concept_existing
        concept_name = "Asymmetric Dark Matter vs WIMP Baryogenesis in Explaining Matter-Antimatter Asymmetry"
        self.assertTrue(is_concept_existing(concept_name, level=2))

    def test_is_concept_existing_returns_false_for_new_file(self):
        from src.workflow_contracts import is_concept_existing
        concept_name = "Nonexistent Theoretical Framework 99999"
        self.assertFalse(is_concept_existing(concept_name, level=2))

    def test_is_concept_existing_level3(self):
        from src.workflow_contracts import is_concept_existing
        concept_name = "Nonexistent Level 3 Emergence Topic 99999"
        self.assertFalse(is_concept_existing(concept_name, level=3))

    def test_okf_indexer_smart_edges(self):
        from pathlib import Path
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
        try:
            from okf_indexer import scan_okf_bundle
        except ImportError:
            import importlib.util
            spec = importlib.util.spec_from_file_location("okf_indexer", Path(__file__).resolve().parent / "scripts" / "okf_indexer.py")
            okf_indexer = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(okf_indexer)
            scan_okf_bundle = okf_indexer.scan_okf_bundle

        repo_root = Path(__file__).resolve().parent
        graph_data, errors, warnings = scan_okf_bundle(repo_root)
        self.assertGreater(graph_data["stats"]["total_edges"], 0, "Smart Edge Resolver should find directed edges")
        self.assertEqual(len(errors), 0, f"OKF Indexer produced schema errors: {errors}")

    def test_equation_archaeologist(self):
        from pathlib import Path
        try:
            from equation_archaeologist import EquationArchaeologist
        except ImportError:
            from src.equation_archaeologist import EquationArchaeologist

        repo_root = Path(__file__).resolve().parent
        archaeologist = EquationArchaeologist(repo_root)
        catalog = archaeologist.run()

        self.assertGreater(catalog["stats"]["total_entries"], 0, "Should load logged equation entries")
        self.assertGreater(catalog["stats"]["total_equations"], 0, "Should count logged equations")
        self.assertGreater(len(catalog["bridges"]), 0, "Should find cross-concept equation bridges")
        self.assertTrue((repo_root / "knowledge_base" / "equation_index.json").exists())
        self.assertTrue((repo_root / "knowledge_base" / "equation_taxonomy_and_bridges.md").exists())

    def test_clean_topic_digest(self):
        """Verifies that generate_clean_topic_digest creates a compact, Mermaid-free summary."""
        try:
            from index_utils import generate_clean_topic_digest
        except ImportError:
            from src.index_utils import generate_clean_topic_digest

        repo_root = Path(__file__).resolve().parent
        digest = generate_clean_topic_digest(repo_root=repo_root)

        self.assertIn("# Knowledge Base Summary", digest)
        self.assertIn("## Level 1: Fundamental Physics", digest)
        self.assertNotIn("graph TD", digest, "Digest must not contain raw Mermaid graph code")
        self.assertNotIn("classDef", digest, "Digest must not contain raw Mermaid CSS classes")
        self.assertGreater(len(digest), 100, "Digest should contain topics from database")

    def test_sanitize_long_filename(self):
        """Verifies that sanitize_filename caps filenames under Linux NAME_MAX limit."""
        try:
            from workflow_contracts import sanitize_filename
        except ImportError:
            from src.workflow_contracts import sanitize_filename

        ultra_long_name = "How can the proposed comparison between nearby steady astrophysical sources and the diffuse neutrino population be statistically quantified to yield an unambiguous test given that the current statistics for nearby neutrino sources like NGC 1068 remain low"
        filename = sanitize_filename(ultra_long_name)
        self.assertLessEqual(len(filename), 184)
        self.assertTrue(filename.endswith(".md"))


if __name__ == "__main__":
    unittest.main()




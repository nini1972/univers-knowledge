import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class TestAdvisoryManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.logs_dir = Path(self.temp_dir) / "knowledge_base" / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.advisory_file = self.logs_dir / "advisory_queue.jsonl"
        self.directives_file = self.logs_dir / "professor_directives.jsonl"
        self.office_hours_md = Path(self.temp_dir) / "knowledge_base" / "PROFESSOR_OFFICE_HOURS.md"

        self.patcher_repo = patch("src.advisory_manager.REPO_ROOT", Path(self.temp_dir))
        self.patcher_logs = patch("src.advisory_manager.LOGS_DIR", self.logs_dir)
        self.patcher_advisory = patch("src.advisory_manager.ADVISORY_FILE", self.advisory_file)
        self.patcher_directives = patch("src.advisory_manager.DIRECTIVES_FILE", self.directives_file)
        self.patcher_md = patch("src.advisory_manager.OFFICE_HOURS_MD", self.office_hours_md)

        self.patcher_repo.start()
        self.patcher_logs.start()
        self.patcher_advisory.start()
        self.patcher_directives.start()
        self.patcher_md.start()

        import src.advisory_manager as am
        self.am = am

    def tearDown(self):
        self.patcher_md.stop()
        self.patcher_directives.stop()
        self.patcher_advisory.stop()
        self.patcher_logs.stop()
        self.patcher_repo.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_advisory_request(self):
        req_id = self.am.create_advisory_request(
            concept="Quantum Decoherence in Biological Systems",
            level=3,
            initiator="Student Orchestrator",
            question="Is decoherence timescale consistent with neural microtubules?",
            detailed_rationale="Debated in Penrose-Hameroff Orch-OR model.",
            agent_needs={"researcher_needs": ["Empirical decoherence times"]},
            reason_code="unfalsifiable_or_unmeasurable_scale",
        )
        self.assertIsNotNone(req_id)
        self.assertTrue(req_id.startswith("adv-"))
        self.assertTrue(self.advisory_file.exists())
        self.assertTrue(self.office_hours_md.exists())

        with open(self.advisory_file, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], req_id)
        self.assertEqual(records[0]["concept"], "Quantum Decoherence in Biological Systems")
        self.assertEqual(records[0]["level"], 3)
        self.assertEqual(records[0]["status"], "pending")
        self.assertEqual(records[0]["agent_needs"]["researcher_needs"], ["Empirical decoherence times"])

    def test_create_advisory_request_deduplication(self):
        id1 = self.am.create_advisory_request(
            concept="Black Hole Firewall Paradox",
            level=1,
            question="Does firewall violate equivalence principle?",
        )
        # Attempt to file duplicate pending request for same concept
        id2 = self.am.create_advisory_request(
            concept="black hole firewall paradox",
            level=1,
            question="Another question on the same topic.",
        )
        self.assertEqual(id1, id2)

        with open(self.advisory_file, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
        self.assertEqual(len(records), 1)

    def test_create_advisory_request_empty_concept(self):
        req_id = self.am.create_advisory_request(concept="   ", level=1)
        self.assertIsNone(req_id)
        self.assertFalse(self.advisory_file.exists())

    def test_get_pending_requests_and_level_filter(self):
        self.am.create_advisory_request("Higgs Mechanism", level=1, question="Clarify Goldstone bosons")
        self.am.create_advisory_request("Asymptotic Safety vs Loop Quantum Gravity", level=2, question="Which renormalization group flow is reliable?")
        self.am.create_advisory_request("Integrated Information Theory", level=3, question="Phi calculability bounds")

        all_pending = self.am.get_pending_requests()
        self.assertEqual(len(all_pending), 3)

        l1_pending = self.am.get_pending_requests(level=1)
        self.assertEqual(len(l1_pending), 1)
        self.assertEqual(l1_pending[0]["concept"], "Higgs Mechanism")

        l2_pending = self.am.get_pending_requests(level=2)
        self.assertEqual(len(l2_pending), 1)
        self.assertEqual(l2_pending[0]["concept"], "Asymptotic Safety vs Loop Quantum Gravity")

        l3_pending = self.am.get_pending_requests(level=3)
        self.assertEqual(len(l3_pending), 1)
        self.assertEqual(l3_pending[0]["concept"], "Integrated Information Theory")

    def test_answer_advisory_request_by_id(self):
        req_id = self.am.create_advisory_request("Superconductivity", level=1, question="BCS vs Ginzburg-Landau")
        success = self.am.answer_advisory_request(req_id, "Prioritize BCS microscopic theory first, then connect to GL parameter.")
        self.assertTrue(success)

        # Confirm pending is now empty
        pending = self.am.get_pending_requests()
        self.assertEqual(len(pending), 0)

        # Confirm directive for concept returns professor's answer
        directive = self.am.get_active_directive_for_concept("Superconductivity", level=1)
        self.assertIn("Prioritize BCS microscopic theory", directive)

    def test_answer_advisory_request_by_concept_name(self):
        self.am.create_advisory_request("Bose-Einstein Condensation", level=1, question="Critical temperature formulation")
        success = self.am.answer_advisory_request("bose-einstein condensation", "Use the standard non-interacting gas formula for Tc.")
        self.assertTrue(success)

        directive = self.am.get_active_directive_for_concept("Bose-Einstein Condensation")
        self.assertEqual(directive, "Use the standard non-interacting gas formula for Tc.")

    def test_add_and_get_general_directives(self):
        dir1 = self.am.add_general_directive("All papers must include experimental verification limits.", topic_scope="all")
        dir2 = self.am.add_general_directive("Emphasize non-perturbative calculations.", topic_scope="level_2")

        self.assertTrue(self.directives_file.exists())
        self.assertTrue(dir1.startswith("dir-"))
        self.assertTrue(dir2.startswith("dir-"))

        all_dirs = self.am.get_active_general_directives()
        self.assertEqual(len(all_dirs), 2)

        l1_dirs = self.am.get_active_general_directives(scope="level_1")
        self.assertEqual(len(l1_dirs), 1)
        self.assertIn("experimental verification limits", l1_dirs[0])

        l2_dirs = self.am.get_active_general_directives(scope="level_2")
        self.assertEqual(len(l2_dirs), 2)

    def test_dismiss_request(self):
        req_id = self.am.create_advisory_request("Tachyon Condensation", level=1, question="Is this relevant?")
        dismissed = self.am.dismiss_request(req_id)
        self.assertTrue(dismissed)

        pending = self.am.get_pending_requests()
        self.assertEqual(len(pending), 0)

        # Dismissed request should not provide a concept directive
        self.assertIsNone(self.am.get_active_directive_for_concept("Tachyon Condensation"))

    def test_sync_office_hours_markdown(self):
        self.am.add_general_directive("Ensure all equations are in standard LaTeX notation.", topic_scope="all")
        req_id = self.am.create_advisory_request(
            concept="Cosmic Inflation",
            level=1,
            question="Which slow-roll parameters should be verified?",
            detailed_rationale="Multiple models exist (Starobinsky, chaotic).",
            agent_needs={"researcher_needs": ["Planck 2018 bounds"], "math_needs": ["Slow-roll epsilon and eta"]},
            reason_code="missing_empirical_anchoring",
        )
        self.am.answer_advisory_request(req_id, "Use Starobinsky R^2 inflation and constrain with Planck 2018 r < 0.06.")

        # Create a second pending one
        self.am.create_advisory_request(
            concept="Neutrino Oscillations",
            level=1,
            question="PMNS matrix conventions to use?",
        )

        md_content = self.office_hours_md.read_text(encoding="utf-8")
        self.assertIn("# 🎓 Professor Office Hours & Advisory Queue", md_content)
        self.assertIn("Ensure all equations are in standard LaTeX notation", md_content)
        self.assertIn("Neutrino Oscillations", md_content)
        self.assertIn("Cosmic Inflation", md_content)
        self.assertIn("Starobinsky R^2 inflation", md_content)


if __name__ == "__main__":
    unittest.main()

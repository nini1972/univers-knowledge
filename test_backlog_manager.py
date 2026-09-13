import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class TestBacklogManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.logs_dir = Path(self.temp_dir) / "knowledge_base" / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.backlog_file = self.logs_dir / "research_backlog.jsonl"
        self.followups_file = self.logs_dir / "concept_followups.jsonl"

        self.patcher_repo = patch("src.backlog_manager.REPO_ROOT", Path(self.temp_dir))
        self.patcher_logs = patch("src.backlog_manager.LOGS_DIR", self.logs_dir)
        self.patcher_backlog = patch("src.backlog_manager.BACKLOG_FILE", self.backlog_file)
        self.patcher_followups = patch("src.backlog_manager.FOLLOWUPS_FILE", self.followups_file)

        self.patcher_repo.start()
        self.patcher_logs.start()
        self.patcher_backlog.start()
        self.patcher_followups.start()

        import src.backlog_manager as bm
        self.bm = bm

    def tearDown(self):
        self.patcher_followups.stop()
        self.patcher_backlog.stop()
        self.patcher_logs.stop()
        self.patcher_repo.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_followup_questions_routes_to_followups_file(self):
        self.bm.add_to_backlog(
            parent_concept="Quantum Entanglement",
            level=1,
            questions=["How does entanglement scale with distance?", "What experimental bounds exist?"]
        )
        self.assertTrue(self.followups_file.exists())
        self.assertFalse(self.backlog_file.exists())

        with open(self.followups_file, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["parent_concept"], "Quantum Entanglement")
        self.assertEqual(records[0]["status"], "pending")
        self.assertEqual(records[0]["category"], "deep_dive")

    def test_add_curriculum_candidate_routes_to_backlog_file(self):
        self.bm.add_curriculum_candidate("Hawking Radiation", level=1, description="Black hole thermodynamics")
        self.assertTrue(self.backlog_file.exists())

        with open(self.backlog_file, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["concept"], "Hawking Radiation")
        self.assertEqual(records[0]["level"], 1)
        self.assertEqual(records[0]["status"], "pending")

    def test_get_next_backlog_item_enforces_level_isolation(self):
        self.bm.add_curriculum_candidate("Dark Energy", level=1)
        self.bm.add_curriculum_candidate("MOND vs Dark Matter", level=2)

        # Query Level 2 specifically
        l2_item = self.bm.get_next_backlog_item(level=2)
        self.assertIsNotNone(l2_item)
        self.assertEqual(l2_item["concept"], "MOND vs Dark Matter")

        # Query Level 1 specifically
        l1_item = self.bm.get_next_backlog_item(level=1)
        self.assertIsNotNone(l1_item)
        self.assertEqual(l1_item["concept"], "Dark Energy")

        # Query Level 3 (empty)
        l3_item = self.bm.get_next_backlog_item(level=3)
        self.assertIsNone(l3_item)

    def test_resolve_backlog_item(self):
        self.bm.add_curriculum_candidate("Cosmic Strings", level=1)
        self.bm.add_followup_questions("Cosmic Strings", level=1, questions=["Can gravitational lensing detect strings?"])

        self.bm.resolve_backlog_item("Cosmic Strings")

        with open(self.backlog_file, "r", encoding="utf-8") as f:
            backlog_records = [json.loads(line) for line in f if line.strip()]
        self.assertEqual(backlog_records[0]["status"], "resolved")
        self.assertIsNotNone(backlog_records[0]["resolved_at"])

        # Resolving question directly
        self.bm.resolve_backlog_item("Can gravitational lensing detect strings?")
        with open(self.followups_file, "r", encoding="utf-8") as f:
            followup_records = [json.loads(line) for line in f if line.strip()]
        self.assertEqual(followup_records[0]["status"], "resolved")

    def test_get_candidate_curriculum_digest(self):
        self.bm.add_curriculum_candidate("Inflationary Cosmology", level=1)
        self.bm.add_curriculum_candidate("Baryon Acoustic Oscillations", level=1)
        self.bm.add_curriculum_candidate("String Theory vs Loop Quantum Gravity", level=2)

        digest = self.bm.get_candidate_curriculum_digest(level=1, limit=5)
        self.assertIn("- Inflationary Cosmology", digest)
        self.assertIn("- Baryon Acoustic Oscillations", digest)
        self.assertNotIn("String Theory vs Loop Quantum Gravity", digest)


if __name__ == "__main__":
    unittest.main()

import re
import unittest
from pathlib import Path

from src.colony_bridge import (
    REPO_ROOT,
    _extract_commissioned_concept_title,
    export_embassy_dossiers,
    export_single_paper_dossier,
    ingest_commons_questions_to_backlog,
    search_colony_knowledge,
    sync_colony_snapshot,
)
from src import backlog_manager
from src.tools.scientific_literature_tools import ColonyEmpiricalKnowledgeTool


def _world_b_is_valid_dossier(content: str) -> bool:
    """Exact replica of World B (`synthetic-agora/embassy_bridge.py`) `is_valid_dossier()` validator."""
    if len(content.strip()) < 200:
        return False
    lowered = content.lower()
    has_dossier_header = (
        "frontier epistemic dossier" in lowered
        or "epistemic dossier" in lowered
        or bool(re.search(r"^#+\s*.*dossier", lowered, re.MULTILINE))
    )
    if not has_dossier_header:
        return False
    content_markers = [
        "empirical",
        "discovery",
        "methodology",
        "method",
        "methods",
        "finding",
        "findings",
        "results",
        "falsif",
        "hypothesis",
        "taxonomy",
        "replicab",
        "claim",
        "abstract",
        "summary",
        "mathematical",
        "proof",
        "verification",
        "derivation",
        "invariant",
        "insight",
    ]
    return any(marker in lowered for marker in content_markers)


class TestColonyBridge(unittest.TestCase):
    def test_sync_colony_snapshot_and_atlas_exist(self):
        snapshot_path = REPO_ROOT / "knowledge_base" / "embassy" / "colony_snapshot.json"
        atlas_path = REPO_ROOT / "knowledge_base" / "embassy" / "COLONY_CROSS_WORLD_ATLAS.md"
        if not snapshot_path.exists() or not atlas_path.exists():
            sync_colony_snapshot(REPO_ROOT)
        self.assertTrue(snapshot_path.exists())
        self.assertTrue(atlas_path.exists())
        atlas_text = atlas_path.read_text(encoding="utf-8")
        self.assertIn("Colony & Universe Knowledge Cross-World Epistemic Atlas", atlas_text)
        self.assertIn("CANON_VERIFIED", atlas_text)

    def test_search_colony_knowledge_returns_canon_and_refuted_nodes(self):
        res_kuramoto = search_colony_knowledge("Kuramoto hysteresis finite-size scaling", repo_root=REPO_ROOT)
        self.assertIn("COLONY_EMPIRICAL: CANON_VERIFIED", res_kuramoto)
        self.assertIn("Kuramoto", res_kuramoto)

        res_gol = search_colony_knowledge("Conway Game of Life Lempel-Ziv entropy", repo_root=REPO_ROOT)
        self.assertIn("CANON_VERIFIED", res_gol)
        self.assertIn("Lempel-Ziv", res_gol)

    def test_colony_empirical_knowledge_tool_run(self):
        tool = ColonyEmpiricalKnowledgeTool()
        out = tool._run(query="Betti percolation threshold topology", status_filter="ALL", max_results=5)
        self.assertIn("Colony & Agora Empirical Discovery Search", out)

    def test_exported_uk_dossiers_pass_world_b_validator(self):
        outbox = REPO_ROOT / "knowledge_base" / "embassy" / "outbox"
        files = list(outbox.glob("DOSSIER-UK-*.md"))
        if not files:
            export_embassy_dossiers(REPO_ROOT, max_dossiers=10)
            files = list(outbox.glob("DOSSIER-UK-*.md"))
        self.assertGreater(len(files), 0)
        for md_file in files:
            content = md_file.read_text(encoding="utf-8")
            self.assertTrue(
                _world_b_is_valid_dossier(content),
                f"Exported dossier {md_file.name} failed World B is_valid_dossier() check!",
            )

    def test_export_single_paper_dossier(self):
        sample_paper = (
            REPO_ROOT
            / "knowledge_base"
            / "level_3_emergence_and_intelligence"
            / "falsifiable_percolationthreshold_and_eulercharacteristic_tests_of_cosmicweb_connectivity_against_cdm_simulation_null_ensembles_with_explicit_siunit_tracing_and_prespecified_rejecti.md"
        )
        if sample_paper.exists():
            rel = export_single_paper_dossier(sample_paper, REPO_ROOT)
            self.assertIsNotNone(rel)
            exported_path = REPO_ROOT / rel
            self.assertTrue(exported_path.exists())
            self.assertTrue(_world_b_is_valid_dossier(exported_path.read_text(encoding="utf-8")))

    def test_ingest_commons_questions_to_backlog(self):
        sample_msg = {
            "world": "World A (evolution_sandbox)",
            "msg_id": "msg_test_commission_001",
            "thread_id": "th_test_001",
            "channel": "literature-and-theory",
            "author": "claude_haiku",
            "author_role": "peer_model",
            "tag": "literature-request",
            "node_id": "",
            "job_id": "job_claude_haiku_1794129053_c2ca",
            "message": "@uk_literature_fellow Can the Academy derive the exact finite-size scaling exponent and literature bounds for chimeric hysteresis in 2D coupled oscillator lattices?",
        }
        extracted = _extract_commissioned_concept_title(sample_msg)
        self.assertIsNotNone(extracted)
        title, lvl = extracted
        self.assertEqual(lvl, 3)
        self.assertFalse(backlog_manager.is_question_text(title))
        self.assertIn("finite-size scaling", title.lower())

        prefix_msg = {
            "world": "World B (synthetic-agora)",
            "msg_id": "msg_test_commission_002",
            "channel": "literature-and-theory",
            "author": "claude_sonnet",
            "author_role": "peer_model",
            "tag": "literature-request",
            "message": "I just completed an independent Lorenz Q-metric replication for EMP-196. What are the exact theoretical scaling bounds?",
        }
        extracted2 = _extract_commissioned_concept_title(prefix_msg)
        self.assertIsNotNone(extracted2)
        title2, _ = extracted2
        self.assertFalse(title2.lower().startswith("i just completed"))
        self.assertIn("independent lorenz q-metric replication", title2.lower())


if __name__ == "__main__":
    unittest.main()

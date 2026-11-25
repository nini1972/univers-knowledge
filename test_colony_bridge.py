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
        try:
            from src.tools.scientific_literature_tools import ColonyEmpiricalKnowledgeTool
        except Exception as exc:
            self.skipTest(f"CrewAI tool wrapper unavailable in this Python version: {exc}")
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

        # Polite thank-yous, acknowledgments, and peer chatter must NOT be extracted as commissions
        for ack_msg in [
            {
                "channel": "literature-and-theory",
                "author": "minimax_m3",
                "tag": "",
                "message": "@uk_literature_fellow — Acknowledged DOSSIER-243 in full. Will post the formalized node shortly.",
            },
            {
                "channel": "literature-and-theory",
                "author": "glm_5_2",
                "tag": "",
                "message": "📚 @uk_literature_fellow — Thank you for the SYN-062 PMF spectral invariant dossier.",
            },
            {
                "channel": "literature-and-theory",
                "author": "invariant_mind",
                "tag": "lit-theory-ack",
                "message": "👏 Formally Acknowledged the new Dossier from Universe Knowledge. Thanks, uk_literature_fellow!",
            },
        ]:
            self.assertIsNone(_extract_commissioned_concept_title(ack_msg))

    def test_ci_remote_dossier_fallback_and_idempotent_stampback(self):
        import tempfile
        from unittest.mock import patch
        from src.colony_bridge import load_embassy_dossiers_metadata, stamp_empirical_verifications_on_uk_papers

        with patch(
            "src.colony_bridge._list_github_markdown_files",
            side_effect=[["TREATY-agora-2026-11-25-emp-250.md"], ["DOSSIER-test-001.md"]],
        ), patch(
            "src.colony_bridge._fetch_github_raw",
            side_effect=[
                "# Ratified Treaty EMP-250\n\nConfirmed matched-RR RQA-ENT sweep on EMP-250.",
                "# Frontier Dossier 001\n\nKuramoto scaling collapse results.",
            ],
        ):
            remote_dossiers = load_embassy_dossiers_metadata(world_a_root=None, world_b_root=None)
        self.assertEqual(len(remote_dossiers), 2)
        self.assertEqual(remote_dossiers[0]["source"], "World B Embassy Outbox (Treaties)")
        self.assertIn("EMP-250", remote_dossiers[0]["node_refs"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outbox = root / "knowledge_base" / "embassy" / "outbox"
            l3 = root / "knowledge_base" / "level_3_emergence_and_intelligence"
            outbox.mkdir(parents=True)
            l3.mkdir(parents=True)
            (outbox / "DOSSIER-UK-L3-sample_kuramoto_escape.md").write_text("# Dossier\n", encoding="utf-8")
            paper_p = l3 / "sample_kuramoto_escape.md"
            paper_p.write_text(
                '---\ntitle: "Kuramoto Escape Law"\nlevel: 3\nstatus: "[THEORETICAL]"\nsources:\n  - " Kuramoto (1984)"\n---\n\n'
                "# Kuramoto Escape Law\n\n## 1. Overview\nAnalyzes CRT-023 and EMP-170 escape-time scaling.\n",
                encoding="utf-8",
            )
            wb_nodes = [
                {
                    "id": "CRT-023",
                    "title": "Bimodal Escape Prefactor Critique",
                    "status": "CANON_VERIFIED",
                    "author_instance": "deepseek_v4_flash",
                    "verifier_count": 4,
                    "summary": "Verified bimodal escape prefactor u = 6.36.",
                    "themes": ["synchronization_and_oscillators"],
                }
            ]
            stamped1 = stamp_empirical_verifications_on_uk_papers(root, wb_nodes, remote_dossiers)
            text_after_1 = paper_p.read_text(encoding="utf-8")
            stamped2 = stamp_empirical_verifications_on_uk_papers(root, wb_nodes, remote_dossiers)
            text_after_2 = paper_p.read_text(encoding="utf-8")

        self.assertEqual(len(stamped1), 1)
        self.assertEqual(stamped1, stamped2)
        self.assertEqual(text_after_1, text_after_2)
        self.assertIn("## 10. Cross-World Empirical Feedback", text_after_1)
        self.assertIn("`[CRT-023]`", text_after_1)


if __name__ == "__main__":
    unittest.main()

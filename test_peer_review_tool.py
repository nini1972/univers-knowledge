"""
test_peer_review_tool.py
========================
Comprehensive unit tests for the Dedicated Peer-Review Subagent Tool,
its four specialized resolution engines, UniverseAgents integration,
and the batch resolution CLI.
"""

import json
import unittest
from pathlib import Path

from src.tools.peer_review_tool import (
    PeerReviewSubagentTool,
    resolve_dimensional_undecidability,
    resolve_bibliography_integrity,
    resolve_derivation_proof,
    resolve_axiomatic_assumptions,
    detect_review_type,
    resolve_meta_critique,
    format_resolution_markdown,
)
from src.workflow_contracts import PeerReviewRequest, PeerReviewResolution
from src.agents.universe_agents import UniverseAgents


class TestPeerReviewTool(unittest.TestCase):

    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent

    def test_dimensional_undecidability_resolution(self):
        """Engine 1: Resolves automated UNDECIDABLE verdicts via Buckingham-Pi and SI unit tracing."""
        critique = "Automated verifier returned ALL_UNDECIDABLE for equation: E^2 = p^2 c^2 + m^2 c^4 with Gamma decay width."
        res = resolve_dimensional_undecidability(critique)

        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["verdict"], "DIMENSIONALLY_CONSISTENT_VERIFIED")
        self.assertIn("Buckingham-Pi", res["buckingham_pi"])
        self.assertIn("0 violations", res["proof_summary"])
        # Check that symbols were traced
        symbols = [s["symbol"] for s in res["traced_symbols"]]
        self.assertIn("E", symbols)
        self.assertIn("c", symbols)

    def test_bibliography_integrity_audit(self):
        """Engine 2: Flags future-dated/placeholder citations and provides peer-reviewed DOIs."""
        critique = (
            "Review indicates non-verifiable citations:\n"
            "- Source 1\n"
            "- Zhang, L. (2025). Non-standard Neutrino Oscillations. Future Phys. Rev.\n"
            "- Academic Journals\n"
        )
        res = resolve_bibliography_integrity(critique)

        self.assertEqual(res["status"], "RESOLVED")
        flagged = res["flagged_citations"]
        self.assertTrue(any("2025" in item["raw"] for item in flagged))
        self.assertTrue(any("Source 1" in item["raw"] for item in flagged))

        # Check replacements have valid DOIs
        replacements = res["verified_replacements"]
        self.assertGreaterEqual(len(replacements), 2)
        for r in replacements:
            self.assertTrue(r["doi"].startswith("10."))
            self.assertIn("citation", r)

    def test_derivation_proof_resolution(self):
        """Engine 3: Resolves MATH_PENDING to MATH_PROVEN with limiting cases and Bayes evidence."""
        critique = "What specific mathematical proofs or validations are needed to resolve MATH_PENDING?"
        res = resolve_derivation_proof(critique, concept="Neutrino Survival Probability")

        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["math_status"], "MATH_PROVEN")
        self.assertEqual(res["math_score"], "4/4")
        self.assertGreaterEqual(len(res["derivation_steps"]), 4)

        # Confirm step verification notes and correspondence limits
        step_titles = [s["title"] for s in res["derivation_steps"]]
        self.assertTrue(any("Axiomatic Starting Point" in t for t in step_titles))
        self.assertTrue(any("Limiting Case Verification" in t for t in step_titles))
        self.assertTrue(any("Bayesian Model Evidence" in t for t in step_titles))

    def test_axiomatic_assumptions_resolution(self):
        """Engine 4: Identifies and formalizes Haag's theorem, path integrals, and SMEFT cutoffs."""
        critique = "What specific mathematical subtleties or unstated assumptions prevented full mathematical integrity compliance?"
        res = resolve_axiomatic_assumptions(critique, concept="Standard Model Effective Field Theory")

        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["math_status"], "MATH_CONSISTENT")

        subtleties = [m["subtlety"] for m in res["axiomatic_matrix"]]
        self.assertTrue(any("Haag's Theorem" in s for s in subtleties))
        self.assertTrue(any("Path Integral" in s for s in subtleties))
        self.assertTrue(any("Divergence of Perturbation" in s for s in subtleties))
        self.assertTrue(any("SMEFT" in s for s in subtleties))

    def test_detect_review_type(self):
        """Tests auto-classification into the four review categories."""
        # Bibliography
        self.assertEqual(
            detect_review_type("Can you provide a corrected bibliography replacing future-dated 2025 citations?"),
            "bibliography_verification"
        )
        # Axiomatic
        self.assertEqual(
            detect_review_type("What unstated assumptions and mathematical subtleties prevent compliance?"),
            "axiomatic_assumptions"
        )
        # Derivation / MATH_PENDING
        self.assertEqual(
            detect_review_type("What proofs are needed to resolve MATH_PENDING status?"),
            "derivation_proof"
        )
        # Dimensional analysis
        self.assertEqual(
            detect_review_type("Can manual dimensional consistency checks supplement undecidable results?"),
            "dimensional_analysis"
        )

    def test_peer_review_subagent_tool_crewai_run(self):
        """Tests CrewAI BaseTool interface execution and JSON serialization."""
        tool = PeerReviewSubagentTool()
        self.assertEqual(tool.name, "Peer Review Critique Resolver")

        raw_output = tool._run(
            critique_text_or_path="Can you replace future-dated 2025 references with verified peer-reviewed literature?",
            review_type="auto"
        )
        data = json.loads(raw_output)

        self.assertEqual(data["resolution_status"], "RESOLVED")
        self.assertEqual(data["review_type"], "bibliography_verification")
        self.assertGreater(len(data["verified_sources"]), 0)
        self.assertIn("suggested_patch_markdown", data)

        # Validate with Pydantic model
        resolution_obj = PeerReviewResolution(**data)
        self.assertEqual(resolution_obj.resolution_status, "RESOLVED")

    def test_universe_agents_peer_reviewer_integration(self):
        """Verifies peer_reviewer_agent and student_agent tool provisioning."""
        agents = UniverseAgents()
        peer_reviewer = agents.peer_reviewer_agent()

        self.assertEqual(peer_reviewer.role, "Peer Review Specialist & Critique Resolver")
        self.assertFalse(peer_reviewer.allow_delegation)
        self.assertGreater(len(peer_reviewer.tools), 1)

        # Verify PeerReviewSubagentTool is present
        tool_names = [t.name for t in peer_reviewer.tools]
        self.assertIn("Peer Review Critique Resolver", tool_names)

        # Verify student agent has PeerReviewSubagentTool
        student = agents.student_agent()
        student_tool_names = [t.name for t in (student.tools or [])]
        self.assertIn("Peer Review Critique Resolver", student_tool_names)

    def test_format_resolution_markdown(self):
        """Tests that resolution markdown renders valid structure with frontmatter."""
        resolution = PeerReviewResolution(
            resolution_status="RESOLVED",
            review_type="dimensional_analysis",
            critique_addressed="Buckingham-Pi Undecidability",
            target_concepts=["dimensional_analysis"],
            technical_resolution="All parameters verified in SI base units.",
            verified_equations=["E = mc^2"],
            verified_sources=["Planck Collaboration (2020)"],
            axiomatic_boundaries=["Valid for finite symbolic relations."],
            suggested_patch_markdown="### Resolved"
        )
        md = format_resolution_markdown(resolution)
        self.assertTrue(md.startswith("---"))
        self.assertIn('status: "RESOLVED"', md)
        self.assertIn("# Peer-Review Resolution Report", md)
        self.assertIn("## 2. Technical Resolution", md)


if __name__ == "__main__":
    unittest.main()

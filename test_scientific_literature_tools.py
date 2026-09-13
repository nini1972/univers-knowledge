"""
test_scientific_literature_tools.py
===================================
Comprehensive unit tests for open scientific literature tools:
  - ArxivSearchTool
  - OpenAlexSearchTool
  - EuropePmcSearchTool
  - CitationAuditTool
  - Agent search tool provisioning in UniverseAgents
"""

import unittest
from unittest.mock import patch, MagicMock

from src.tools.scientific_literature_tools import (
    ArxivSearchTool,
    OpenAlexSearchTool,
    EuropePmcSearchTool,
    CitationAuditTool,
    reconstruct_abstract,
)
from src.agents.universe_agents import _build_search_tools, UniverseAgents


class TestScientificLiteratureTools(unittest.TestCase):

    def test_reconstruct_abstract(self):
        """Tests that inverted index dictionaries reconstruct into ordered text."""
        inverted_index = {
            "We": [0],
            "measure": [1],
            "the": [2, 6],
            "neutrino": [3],
            "mass": [4],
            "in": [5],
            "laboratory.": [7]
        }
        reconstructed = reconstruct_abstract(inverted_index)
        self.assertEqual(reconstructed, "We measure the neutrino mass in the laboratory.")

        # Test empty or None
        self.assertEqual(reconstruct_abstract(None), "")
        self.assertEqual(reconstruct_abstract({}), "")

    def test_tool_definitions(self):
        """Tests tool metadata and schemas."""
        arxiv = ArxivSearchTool()
        self.assertEqual(arxiv.name, "ArXiv Preprint Search")

        openalex = OpenAlexSearchTool()
        self.assertEqual(openalex.name, "OpenAlex Scholarly Graph Search")

        pmc = EuropePmcSearchTool()
        self.assertEqual(pmc.name, "Europe PMC Literature Search")

        audit = CitationAuditTool()
        self.assertEqual(audit.name, "Pre-Flight Citation Verifier")

    def test_citation_audit_clean_report(self):
        """Tests that a clean report with valid DOIs passes the citation audit."""
        report = """# Neutrino Oscillations and Decay

## 1. Overview
Neutrino decay is bounded by cosmological observations.

## Sources
- Esteban, I., et al. (2020). NuFIT 5.0. JHEP. 10.1007/JHEP09(2020)178
- Aghanim, N., et al. (2020). Planck 2018. A&A. 10.1051/0004-6361/201833910
- Workman, R. L., et al. (2022). Review of Particle Physics. 10.1093/ptep/ptac097
"""
        audit_tool = CitationAuditTool()
        result = audit_tool._run(report)

        self.assertIn("CITATION AUDIT PASSED", result)
        self.assertIn("Verified Authentic DOIs", result)
        self.assertNotIn("FUTURE_DATED_HALLUCINATION", result)
        self.assertNotIn("PLACEHOLDER_CITATION", result)

    def test_citation_audit_flags_issues(self):
        """Tests that future-dated years and placeholders are flagged with recommendations."""
        bad_report = """# Speculative Quantum Cosmology

## Sources
- Source 1
- Academic Journals
- Li, X. (2025). Non-standard gravity. Future Physics.
- 10.9999/nonexistent_fake_doi_12345
"""
        audit_tool = CitationAuditTool()
        result = audit_tool._run(bad_report)

        self.assertIn("CITATION AUDIT ACTION REQUIRED", result)
        self.assertIn("PLACEHOLDER_CITATION", result)
        self.assertIn("FUTURE_DATED_HALLUCINATION", result)
        self.assertIn("Recommended Verified Peer-Reviewed Replacements", result)

    def test_openalex_live_search(self):
        """Live integration test: OpenAlex search returns verified peer-reviewed records."""
        tool = OpenAlexSearchTool()
        output = tool._run("neutrino oscillations", max_results=2)

        self.assertIn("OpenAlex Scholarly Results", output)
        self.assertIn("Year:", output)
        self.assertIn("Citations:", output)

    def test_openalex_cited_by_mode(self):
        """Live integration test: OpenAlex cited_by mode traverses citation graph."""
        tool = OpenAlexSearchTool()
        # Seminal paper DOI: 10.1103/physrevd.25.774
        output = tool._run("10.1103/physrevd.25.774", mode="cited_by", max_results=2)

        self.assertIn("OpenAlex Scholarly Results", output)
        self.assertIn("Mode: `cited_by`", output)

    def test_europe_pmc_live_search(self):
        """Live integration test: Europe PMC queries open-access biophysics/emergence literature."""
        tool = EuropePmcSearchTool()
        output = tool._run("quantum biology", max_results=2)

        self.assertIn("Europe PMC Literature Results", output)
        self.assertIn("Year:", output)

    def test_arxiv_fallback_resilience(self):
        """Tests that ArxivSearchTool falls back gracefully if direct server is rate-limited."""
        tool = ArxivSearchTool()
        # Should return formatted markdown (either via direct arXiv or via OpenAlex mirror)
        output = tool._run("neutrino decay", max_results=2)
        self.assertIn("ArXiv", output)
        self.assertTrue("arXiv ID:" in output or "Preprint" in output)

    def test_build_search_tools_provisioning(self):
        """Tests that search tools are ALWAYS provisioned, even without commercial API keys."""
        # Test with no API keys in environment
        with patch.dict("os.environ", {}, clear=True):
            tools = _build_search_tools()
            tool_names = [t.name for t in tools]

            self.assertIn("ArXiv Preprint Search", tool_names)
            self.assertIn("OpenAlex Scholarly Graph Search", tool_names)
            self.assertIn("Europe PMC Literature Search", tool_names)
            self.assertIn("Pre-Flight Citation Verifier", tool_names)
            self.assertGreaterEqual(len(tools), 4)

    def test_researcher_agent_has_all_literature_tools(self):
        """Tests that UniverseAgents().researcher_agent() is equipped with literature tools."""
        agents = UniverseAgents()
        researcher = agents.researcher_agent()

        tool_names = [t.name for t in researcher.tools]
        self.assertIn("ArXiv Preprint Search", tool_names)
        self.assertIn("OpenAlex Scholarly Graph Search", tool_names)
        self.assertIn("Europe PMC Literature Search", tool_names)
        self.assertIn("Pre-Flight Citation Verifier", tool_names)


if __name__ == "__main__":
    unittest.main()

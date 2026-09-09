import importlib
import sys
import types
import unittest
from unittest.mock import patch


def _load_module():
    fake_crewai = types.SimpleNamespace(Agent=object, LLM=object)
    with patch.dict(sys.modules, {"crewai": fake_crewai}):
        sys.modules.pop("src.agents.universe_agents", None)
        return importlib.import_module("src.agents.universe_agents")


class TestUniverseAgentsOpenRouterModels(unittest.TestCase):
    def test_normalize_openrouter_model_strips_provider_prefix(self):
        module = _load_module()
        self.assertEqual(
            module._normalize_openrouter_model("openrouter/openai/gpt-4o-mini"),
            "openai/gpt-4o-mini",
        )

    def test_resolve_openrouter_model_falls_back_when_catalog_missing_model(self):
        module = _load_module()
        module._OPENROUTER_MODEL_INDEX = None

        with patch.dict(
            module.os.environ,
            {"OPENROUTER_MODEL_RESEARCHER": "openrouter/nonexistent/model"},
            clear=False,
        ):
            with patch.object(
                module,
                "_fetch_openrouter_model_index",
                return_value={"openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet"},
            ):
                resolved = module._resolve_openrouter_model("test-key", "researcher")

        self.assertEqual(resolved, "openai/gpt-4o-mini")

    def test_resolve_openrouter_model_keeps_valid_non_tool_model(self):
        module = _load_module()
        module._OPENROUTER_MODEL_INDEX = None

        with patch.dict(
            module.os.environ,
            {"OPENROUTER_MODEL_ARCHIVIST": "openrouter/anthropic/claude-3.5-sonnet"},
            clear=False,
        ):
            with patch.object(
                module,
                "_fetch_openrouter_model_index",
                return_value={"anthropic/claude-3.5-sonnet", "openai/gpt-4o-mini"},
            ):
                resolved = module._resolve_openrouter_model("test-key", "archivist")

        self.assertEqual(resolved, "anthropic/claude-3.5-sonnet")


if __name__ == "__main__":
    unittest.main()

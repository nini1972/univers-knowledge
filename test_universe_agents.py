import importlib
import sys
import types
import unittest
from unittest.mock import patch


class MockLLM:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def _load_module():
    fake_crewai = types.SimpleNamespace(Agent=object, LLM=MockLLM)
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
                return_value={module._OPENROUTER_FALLBACK_MODEL, "anthropic/claude-3.5-sonnet"},
            ):
                resolved = module._resolve_openrouter_model("test-key", "researcher")

        self.assertEqual(resolved, module._OPENROUTER_FALLBACK_MODEL)

    def test_resolve_openrouter_model_preserves_glm_flash_for_researcher(self):
        module = _load_module()
        module._OPENROUTER_MODEL_INDEX = None

        with patch.dict(
            module.os.environ,
            {"OPENROUTER_MODEL_RESEARCHER": "~z-ai/glm-flash-latest"},
            clear=False,
        ):
            with patch.object(
                module,
                "_fetch_openrouter_model_index",
                return_value={"~z-ai/glm-flash-latest", module._OPENROUTER_FALLBACK_MODEL},
            ):
                resolved = module._resolve_openrouter_model("test-key", "researcher")

        self.assertEqual(resolved, "~z-ai/glm-flash-latest")

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

    def test_get_llm_configures_timeout_and_low_reasoning_for_researcher(self):
        module = _load_module()
        module._OPENROUTER_MODEL_INDEX = None

        with patch.dict(
            module.os.environ,
            {
                "OPENROUTER_API_KEY": "test-key",
                "OPENROUTER_MODEL_RESEARCHER": "~z-ai/glm-flash-latest",
            },
            clear=False,
        ):
            with patch.object(
                module,
                "_fetch_openrouter_model_index",
                return_value={"~z-ai/glm-flash-latest"},
            ):
                llm = module._get_llm("researcher")

        self.assertIsNotNone(llm)
        self.assertEqual(llm.kwargs.get("timeout"), 180.0)
        self.assertEqual(llm.kwargs.get("reasoning_effort"), "low")
        self.assertEqual(llm.kwargs.get("model"), "openrouter/~z-ai/glm-flash-latest")

    def test_get_llm_custom_reasoning_effort_override(self):
        module = _load_module()
        module._OPENROUTER_MODEL_INDEX = None

        with patch.dict(
            module.os.environ,
            {
                "OPENROUTER_API_KEY": "test-key",
                "OPENROUTER_MODEL_RESEARCHER": "~z-ai/glm-flash-latest",
                "OPENROUTER_REASONING_EFFORT_RESEARCHER": "high",
            },
            clear=False,
        ):
            with patch.object(
                module,
                "_fetch_openrouter_model_index",
                return_value={"~z-ai/glm-flash-latest"},
            ):
                llm = module._get_llm("researcher")

        self.assertIsNotNone(llm)
        self.assertEqual(llm.kwargs.get("reasoning_effort"), "high")

    def test_get_llm_non_tool_role_omits_reasoning_effort_by_default(self):
        module = _load_module()
        module._OPENROUTER_MODEL_INDEX = None

        with patch.dict(
            module.os.environ,
            {
                "OPENROUTER_API_KEY": "test-key",
                "OPENROUTER_MODEL_ARCHIVIST": "openai/gpt-4o-mini",
            },
            clear=False,
        ):
            with patch.object(
                module,
                "_fetch_openrouter_model_index",
                return_value={"openai/gpt-4o-mini"},
            ):
                llm = module._get_llm("archivist")

        self.assertIsNotNone(llm)
        self.assertNotIn("reasoning_effort", llm.kwargs)


if __name__ == "__main__":
    unittest.main()

import importlib
import logging
from pathlib import Path
import sys
import tempfile
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
        self.assertNotIn("additional_params", llm.kwargs)

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

    def test_approximate_token_warning_logged_only_once_in_process(self):
        module = _load_module()

        class _ListHandler(logging.Handler):
            def __init__(self):
                super().__init__()
                self.records = []

            def emit(self, record):
                self.records.append(record.getMessage())

        test_logger = logging.getLogger("test.crewai.base_llm.inproc")
        test_logger.handlers.clear()
        test_logger.filters.clear()
        test_logger.propagate = False
        test_logger.setLevel(logging.WARNING)
        handler = _ListHandler()
        test_logger.addHandler(handler)
        test_logger.addFilter(module._ApproximateTokenWarningOnceFilter())

        for model_name in ("openrouter/model-a", "openrouter/model-a", "openrouter/model-b", "openrouter/model-b", "openrouter/model-c"):
            test_logger.warning(
                "Using an approximate input token count for model %r: assuming one token per four characters because a native token count is unavailable.",
                model_name,
            )
        test_logger.warning("Function 'foo' not found in available functions")
        test_logger.warning("Function 'bar' not found in available functions")

        approx_msgs = [m for m in handler.records if "Using an approximate input token count" in m]
        other_msgs = [m for m in handler.records if "Using an approximate input token count" not in m]
        self.assertEqual(len(approx_msgs), 1)
        self.assertEqual(len(other_msgs), 2)
        self.assertEqual(len(handler.records), 3)

    def test_approximate_token_warning_logged_once_across_processes_via_runner_temp(self):
        module = _load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            sentinel = Path(tmpdir) / ".uk_crewai_approx_token_warned"
            filter_proc_1 = module._ApproximateTokenWarningOnceFilter(sentinel_path=sentinel)
            filter_proc_2 = module._ApproximateTokenWarningOnceFilter(sentinel_path=sentinel)

            rec1 = logging.LogRecord(
                "crewai.llms.base_llm",
                logging.WARNING,
                "",
                0,
                "Using an approximate input token count for model %r: assuming one token per four characters because a native token count is unavailable.",
                ("openrouter/z-ai/glm-5.3-flash",),
                None,
            )
            rec2 = logging.LogRecord(
                "crewai.llms.base_llm",
                logging.WARNING,
                "",
                0,
                "Using an approximate input token count for model %r: assuming one token per four characters because a native token count is unavailable.",
                ("openrouter/openai/gpt-luna",),
                None,
            )
            rec_unrelated = logging.LogRecord(
                "crewai.llms.base_llm",
                logging.WARNING,
                "",
                0,
                "Unrelated CrewAI warning",
                (),
                None,
            )

            self.assertTrue(filter_proc_1.filter(rec1))
            self.assertFalse(filter_proc_1.filter(rec2))
            self.assertTrue(sentinel.exists())
            self.assertFalse(filter_proc_2.filter(rec2))
            self.assertTrue(filter_proc_2.filter(rec_unrelated))

    def test_install_crewai_log_filters_is_idempotent(self):
        module = _load_module()
        target_logger = logging.getLogger("crewai.llms.base_llm")
        original_filters = list(target_logger.filters)
        try:
            target_logger.filters.clear()
            with patch.dict(module.os.environ, {"RUNNER_TEMP": ""}, clear=False):
                module._install_crewai_log_filters()
                module._install_crewai_log_filters()
                installed = [
                    f for f in target_logger.filters
                    if getattr(f, "_uk_approx_token_once_filter", False)
                ]
                self.assertEqual(len(installed), 1)
        finally:
            target_logger.filters[:] = original_filters


if __name__ == "__main__":
    unittest.main()

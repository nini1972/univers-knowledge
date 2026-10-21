"""Regression tests for the math verification tools, the flow's math gate and the generated wishlist."""
import json
import time
import unittest

from src.tools.math_tools import (
    DimensionalConsistencyTool,
    NumericalBenchmarkTool,
    PhysicsCalculatorTool,
    SymbolicDerivationTool,
    get_tier1_math_tools,
    run_with_timeout,
    safe_sympy_parse,
)
from src.workflow_contracts import apply_math_gate, evaluate_math_gate, parse_math_status


def _dims(equations, table=None):
    out = DimensionalConsistencyTool()._run(
        json.dumps(equations), symbol_dimensions_json=json.dumps(table) if table else ""
    )
    return json.loads(out)


def _verdicts(equations, table=None):
    return [r["verdict"] for r in _dims(equations, table)["results"]]


class TestDimensionalConsistency(unittest.TestCase):
    def test_variable_w_exponent_caught_in_any_bracket_style(self):
        for eq in (
            r"\rho_{\rm DE}(a) = \rho_{\rm DE,0} a^{-3(1+w(a))}",
            r"\rho_{\rm DE} \propto a^{-3\left(1+w(a)\right)}",
            r"\rho = \rho_0 a^{-3\cdot(1 + w_{\rm DE}(a))}",
        ):
            self.assertEqual(_verdicts([eq]), ["INCONSISTENT"], eq)

    def test_exact_cpl_integral_not_flagged(self):
        eq = r"\rho_{\rm DE}(a) = \rho_{\rm DE,0}\, a^{-3(1+w_0+w_a)} e^{-3w_a(1-a)}"
        self.assertNotEqual(_verdicts([eq]), ["INCONSISTENT"])

    def test_unsuppressed_operator_not_masked_by_valid_kinetic_term(self):
        eq = r"\mathcal{L} = \frac{1}{2}(\partial\phi)^2 - g\phi^5"
        self.assertEqual(_verdicts([eq]), ["INCONSISTENT"])

    def test_suppressed_operator_allowed(self):
        eq = r"\mathcal{L} = -\frac{1}{2}\partial_\mu\phi\partial^\mu\phi - \frac{\lambda}{4}\phi^4 - \frac{c_6}{\Lambda^2}\phi^6"
        self.assertNotEqual(_verdicts([eq]), ["INCONSISTENT"])

    def test_potential_with_wrong_term_is_flagged_not_failed(self):
        # A mismatch computed from symbol dimensions is a review flag, never a definitive verdict.
        self.assertEqual(_verdicts([r"V(\phi) = \lambda \phi^4 + m^2 \phi^3"]), ["DIMENSION_FLAG"])

    def test_symbol_table_turns_possible_mismatch_into_flag(self):
        self.assertEqual(_verdicts([r"n_B = T^4"]), ["UNDECIDABLE"])
        self.assertEqual(_verdicts([r"n_B = T^4"], {"n_B": 3, "T": 1}), ["DIMENSION_FLAG"])

    def test_thermal_mass_and_variance_patterns(self):
        verdicts = _verdicts([
            r"m_T^2 \sim g^2 T^2 \phi^2",
            r"\mathrm{Var}(A - B) = \mathrm{Var}(A) + \mathrm{Var}(B)",
        ])
        self.assertEqual(verdicts, ["INCONSISTENT", "INCONSISTENT"])

    def test_standard_equations_never_flagged(self):
        standard = [
            r"E = mc^2",
            r"E^2 = p^2c^2 + m^2c^4",
            r"H^2 = \frac{8\pi G}{3}\rho",
            r"H^2 = \frac{\rho}{3M_{\rm Pl}^2}",
            r"\dot{\rho} + 3H(\rho + p) = 0",
            r"\ddot{\phi} + 3H\dot{\phi} + \frac{dV}{d\phi} = 0",
            r"G_{\mu\nu} = 8\pi G T_{\mu\nu}",
            r"m_T^2 = g^2 T^2",
            r"V_T = \frac{1}{2} g^2 T^2 \phi^2",
            r"s = \frac{2\pi^2}{45} g_{*s} T^3",
            r"H_0 = 67.4\,\mathrm{km\,s^{-1}\,Mpc^{-1}}",
            r"M_{\rm Pl} = 2.435 \times 10^{18}\,\mathrm{GeV}",
            r"\mathcal{L}_{\rm int} = \frac{1}{M_*^2} (\partial_\mu R) J_B^\mu",
            r"\mathcal{L} = \bar{\psi}(i\gamma^\mu\partial_\mu - m)\psi",
            r"V(\phi) = \frac{\lambda}{4}(\phi^2 - v^2)^2",
            r"H = \frac{p^2}{2m} + V(x)",
            r"S = \int d^4x \sqrt{-g}\,\mathcal{L}",
            r"\Delta x \Delta p \geq \hbar/2",
            r"T_{\rm reh} \sim \sqrt{\Gamma M_{\rm Pl}}",
            r"\mathrm{Var}(A - B) = \mathrm{Var}(A) + \mathrm{Var}(B) - 2\mathrm{Cov}(A,B)",
        ]
        for eq, verdict in zip(standard, _verdicts(standard)):
            self.assertNotIn(verdict, ("INCONSISTENT", "DIMENSION_FLAG"), eq)

    def test_global_coherence_rule(self):
        out = _dims([r"E = m c^2", r"\nabla_\mu T^{\mu\nu} = 0"])
        self.assertEqual(out["overall_verdict"], "CONSISTENT_WITH_UNDECIDABLE")
        out = _dims([r"E = m c^2", r"n_B = T^4"], {"n_B": 3, "T": 1})
        self.assertEqual(out["overall_verdict"], "NEEDS_REVIEW")
        out = _dims([r"E = m c^2", r"\rho = \rho_0 a^{-3(1+w(a))}"])
        self.assertEqual(out["overall_verdict"], "INCONSISTENCY_DETECTED")


class TestRun106175419435Regressions(unittest.TestCase):
    """Exact equations that produced false INCONSISTENT / STEP_INVALID verdicts in the 2026-10-19 nightly run."""

    TABLE = {"\\phi": 1, "X": 4, "V": 4, "\\rho": 4, "G": 1, "K": 4, "\\sigma_1": 0, "\\sigma_2": 0, "v_1": 0, "v_2": 0}

    def test_chi_squared_statistics_are_dimensionless(self):
        for eq in (
            r"\Delta\chi^2_{1\,dof} = 23.49",
            r"\Delta\chi^2_{1\,dof} = 16.60",
            r"\Delta\chi^2 \equiv \sigma_{tension}^{\,2}",
            r"\Delta\chi^2 \approx 23.5",
        ):
            self.assertEqual(_verdicts([eq], self.TABLE), ["DIMENSIONLESS"], eq)

    def test_horndeski_g_is_not_newtons_constant(self):
        for eq in (
            r"\mathcal{L}_{KGB} = G(\phi,X)\,\Box\phi - K(\phi,X)",
            r"L = G^{\mu\nu}\partial_\mu\phi\,\partial_\nu\phi - K(\phi,X)",
            r"G^{\mu\nu} \equiv G(\phi,X)\,\partial^\mu\phi\,\partial^\nu\phi / \sqrt{X}",
        ):
            self.assertNotIn(_verdicts([eq], self.TABLE)[0], ("INCONSISTENT", "DIMENSION_FLAG"), eq)
            self.assertNotEqual(_verdicts([eq])[0], "INCONSISTENT", eq)

    def test_symbol_reuse_is_a_flag_not_a_failure(self):
        # rho is declared as energy density but used here as a correlation coefficient.
        eq = r"\sigma_{tension} = \frac{|v_1-v_2|}{\sqrt{\sigma_1^2+\sigma_2^2-2\rho\,\sigma_1\sigma_2}}"
        self.assertEqual(_verdicts([eq], self.TABLE), ["DIMENSION_FLAG"])

    def test_correct_cpl_integral_with_e_power_and_inequality_statement(self):
        tool = SymbolicDerivationTool()
        steps = json.loads(tool._run("CPL", json.dumps([
            r"\rho(a) = \rho_{\phi,0}\,a^{-3(1+w_0+w_a)}\,e^{3w_a(a-1)}",
            r"a^{-3(1+w(a))} \neq \rho(a)/\rho_{\phi,0}\quad \text{for } w_a \neq 0",
        ])))["steps"]
        self.assertEqual(steps[0]["verdict"], "STEP_VERIFIED", steps[0])
        self.assertEqual(steps[1]["verdict"], "STEP_ASSUMED", steps[1])

    def test_symbol_table_cells_with_definitions(self):
        from src.math_precheck import parse_symbol_table

        table = parse_symbol_table(
            "| Symbol | Meaning | Dimension |\n|---|---|---|\n"
            "| $w \\equiv p/\\rho$ | equation of state | dimensionless |\n"
            "| $H \\equiv \\dot a/a$ | Hubble rate | $[E]^1$ |\n"
            "| $m_\\phi = \\sqrt{V''}$ | field mass | $[E]^1$ |\n"
            "| **$G^{\\mu\\nu} \\equiv G(\\phi, X)\\, \\partial^\\mu\\phi\\, \\partial^\\nu\\phi$** | braiding tensor | $[E]^0$ |\n"
        )
        self.assertEqual(table.get("w"), 0.0)
        self.assertEqual(table.get("H"), 1.0)
        self.assertEqual(table.get("m_\\phi"), 1.0)
        self.assertIn("G^{\\mu\\nu}", table)
        self.assertFalse(any("equiv" in k or "=" in k for k in table), table)


class TestRuns1066_1071Regressions(unittest.TestCase):
    """Exact cases from the 2026-10-20 / 2026-10-21 nightly runs (106630894103, 107105672520)."""

    def _limits(self, limits):
        out = json.loads(SymbolicDerivationTool()._run("test", json.dumps([]), json.dumps(limits)))
        return [r["verdict"] for r in out["limit_checks"]], out

    def test_student_json_with_raw_newlines_and_tabs_is_parsed(self):
        from src.workflow_contracts import parse_student_decision

        for raw in (
            '{"status": "approved", "reason_code": "theoretically_sound_conjecture", '
            '"summary_for_archivist": "Corrections:\n(1) Tag the Page curve.\n(2) Retag lifetime.", '
            '"detailed_rationale": "ok", "follow_up_questions": ["q"]}',
            '{"status": "approved", "reason_code": "theoretically_sound_conjecture", '
            '"summary_for_archivist": "a\tb", "detailed_rationale": "ok", "follow_up_questions": ["q"]}',
            '```json\n{"status": "approved", "reason_code": "theoretically_sound_conjecture",\n'
            '"summary_for_archivist": "(1) \\to fix\n(2) \\mathcal{L}", "detailed_rationale": "ok", '
            '"follow_up_questions": ["q"]}\n```',
        ):
            decision = parse_student_decision(raw)
            self.assertEqual(decision["status"], "approved", (raw, decision))

    def test_hawking_temperature_limit_to_infinity_verified(self):
        verdicts, out = self._limits([
            {"expr": "hbar*c**3/(8*pi*G*k_B*M)", "var": "M", "point": 0, "expected": "oo", "dir": "+"},
        ])
        self.assertEqual(verdicts, ["LIMIT_VERIFIED"], out)

    def test_unevaluable_limits_are_undecidable_not_mismatch(self):
        verdicts, out = self._limits([
            {"expr": "rho_CPL(a)/rho0", "var": "a", "point": 1, "expected": "1"},
            {"expr": "t*Integral(sin(x**x), (x, 0, 1))", "var": "t", "point": 1, "expected": "1"},
        ])
        self.assertEqual(verdicts, ["LIMIT_UNDECIDABLE", "LIMIT_UNDECIDABLE"], out)
        self.assertEqual(out["invalid_steps"], 0, out)

    def test_genuinely_wrong_limit_still_mismatch(self):
        verdicts, out = self._limits([
            {"expr": "1/(1 - b*x0*L/(2*pi))", "var": "L", "point": "oo", "expected": "-2*pi/(b*x0)"},
        ])
        self.assertEqual(verdicts, ["LIMIT_MISMATCH"], out)

    def test_bare_numbers_with_units_in_prose_not_flagged(self):
        eqs = [
            r"M_{\rm GUT} \sim 2\times10^{16}",
            r"T > 100",
            r"\tau_p \sim 10^{31}",
            r"M \approx 1.989\times10^{30}",
            r"T_0 = 2.7255\,\mathrm{K}",
        ]
        for eq, verdict in zip(eqs, _verdicts(eqs)):
            self.assertNotIn(verdict, ("INCONSISTENT", "DIMENSION_FLAG"), eq)

    def test_lindbladian_is_not_a_lagrangian(self):
        for eq in (r"\frac{d\rho}{dt} = \mathcal{L}(\rho)", r"\dot\rho = \mathcal{L}\rho"):
            self.assertNotIn(_verdicts([eq])[0], ("INCONSISTENT", "DIMENSION_FLAG"), eq)

    def test_real_errors_still_caught(self):
        self.assertEqual(_verdicts([r"\mathcal{L} = \frac{1}{2}(\partial\phi)^2 - g\phi^5"]), ["INCONSISTENT"])
        self.assertEqual(_verdicts([r"V(\phi) = \lambda \phi^4 + m^2 \phi^3"]), ["DIMENSION_FLAG"])


class TestSymbolicDerivation(unittest.TestCase):
    def setUp(self):
        self.tool = SymbolicDerivationTool()

    def _run(self, steps, limits=None):
        return json.loads(self.tool._run("test", json.dumps(steps), json.dumps(limits or [])))

    def test_valid_derivation_and_limits(self):
        res = self._run(
            [
                r"\rho(a) = \rho_0 a^{-3(1 + w_0 + w_a)} \exp(-3 w_a (1 - a))",
                "(A - B)**2 = A**2 - 2*A*B + B**2",
                r"\mathrm{Var}(A - B) = \mathrm{Var}(A) + \mathrm{Var}(B) - 2 \mathrm{Cov}(A, B)",
            ],
            [
                {"expr": "w0 + wa*(1 - a)", "var": "a", "point": 1, "expected": "w0"},
                {"expr": "w0 + wa*(1 - a)", "var": "a", "point": 0, "expected": "w0 + wa"},
            ],
        )
        self.assertEqual(res["invalid_steps"], 0, res)
        self.assertEqual(res["math_status"], "[MATH_PROVEN]", res)

    def test_flawed_derivation(self):
        res = self._run(
            [
                r"\rho(a) = \rho_0 a^{-3\left(1 + w(a)\right)}",
                "(A - B)**2 = A**2 + B**2",
                r"\mathrm{Var}(A - B) = \mathrm{Var}(A) + \mathrm{Var}(B)",
            ],
            [{"expr": "w0 + wa*(1 - a)", "var": "a", "point": 0, "expected": "w0"}],
        )
        self.assertEqual(res["invalid_steps"], 4, res)
        self.assertEqual(res["math_status"], "[MATH_FLAWED]")

    def test_positivity_of_physical_quantities(self):
        steps = self._run(["sqrt(a**2) = a", "sqrt(x**2) = x", r"\lambda \phi^2 = \phi^2 \lambda"])["steps"]
        self.assertEqual(steps[0]["verdict"], "STEP_VERIFIED", steps[0])  # scale factor a > 0
        self.assertEqual(steps[1]["verdict"], "STEP_ASSUMED", steps[1])   # needs a stated assumption
        self.assertEqual(steps[2]["verdict"], "STEP_VERIFIED", steps[2])  # \lambda parses (keyword-safe)

    def test_expression_without_equals_is_not_verified(self):
        steps = self._run(["x**2 + 1"])["steps"]
        self.assertEqual(steps[0]["verdict"], "STEP_ASSUMED")

    def test_tier1_wiring(self):
        names = [t.name for t in get_tier1_math_tools()]
        self.assertIn("Symbolic Derivation Verifier", names)
        self.assertIn("Physics Calculator & Tension Evaluator", names)


class TestSafetyHelpers(unittest.TestCase):
    def test_parser_rejects_python_escapes(self):
        for bad in ("__import__('os').system('echo hi')", "x.__class__", "open('f')", "lambda: 1", "10**10**10"):
            with self.assertRaises(ValueError, msg=bad):
                safe_sympy_parse(bad)

    def test_parser_has_no_builtins(self):
        with self.assertRaises(Exception):
            safe_sympy_parse("getattr(x, 'y')")

    def test_parser_keeps_physics_symbols(self):
        expr = safe_sympy_parse("E - m*c**2")
        self.assertEqual({s.name for s in expr.free_symbols}, {"E", "m", "c"})

    def test_timeout(self):
        with self.assertRaises(TimeoutError):
            run_with_timeout(time.sleep, 0.2, 2)


class TestCalculatorAndBenchmarks(unittest.TestCase):
    def setUp(self):
        self.calc = PhysicsCalculatorTool()

    def test_claim_mismatch(self):
        res = json.loads(self.calc._run(
            mode="verify_claim",
            expression="(GeV_inv_to_m / 1e-6) * exp(11.5) * ((106.75 / g_0)**(1/3)) * (1.0 / T_0_GeV)",
            claimed_value=0.3,
        ))
        self.assertEqual(res["verdict"], "CLAIM_MISMATCH")

    def test_h0_tension(self):
        res = json.loads(self.calc._run(mode="tension_sigma", val1=73.04, err1=1.04, val2=67.36, err2=0.54))
        self.assertTrue(4.8 < res["tension_sigma"] < 4.9, res)

    def test_desi_delta_chi2_labelled_approximate(self):
        res = json.loads(self.calc._run(mode="delta_chi2_w0wa", variables_json='{"w0": -1.0, "wa": 0.0}'))
        self.assertGreater(res["comparisons"]["DESI_2024_CMB_DES_SN5YR"]["delta_chi2_2dof"], 10.0)
        self.assertIn("APPROXIMATE", res["note"])

    def test_calculator_rejects_code(self):
        res = json.loads(self.calc._run(mode="evaluate", expression="__import__('os').getcwd()"))
        self.assertIn("error", res)

    def test_benchmark_table_size(self):
        self.assertEqual(len(NumericalBenchmarkTool().BENCHMARKS), 20)


MATH_REPORT_OK = """## Math Verification Report
**Concept:** X
**Math Score:** 4/4
**Math Status:** [MATH_CONSISTENT]
**Tool Verdicts:** INCONSISTENT=0; UNDECIDABLE=2; STEP_INVALID=0; LIMIT_MISMATCH=0; CLAIM_MISMATCH=0
Legend echoed by the model: [MATH_PROVEN] score 4/4 ... [MATH_FLAWED] any INCONSISTENT verdict.
"""

MATH_REPORT_BAD = """## Math Verification Report
**Math Score:** 3/4
**Math Status:** [MATH_CONSISTENT]
**Tool Verdicts:** INCONSISTENT=1; UNDECIDABLE=0; STEP_INVALID=0; LIMIT_MISMATCH=0; CLAIM_MISMATCH=0
All equations are dimensionally consistent.
"""


class TestMathGate(unittest.TestCase):
    def test_status_line_wins_over_echoed_legend(self):
        self.assertEqual(parse_math_status(MATH_REPORT_OK), "MATH_CONSISTENT")

    def test_clean_report_keeps_approval(self):
        decision, gate = apply_math_gate({"status": "approved", "reason_code": "ok"}, MATH_REPORT_OK)
        self.assertEqual(decision["status"], "approved")
        self.assertFalse(gate["block"])
        self.assertEqual(gate["tool_verdicts"]["UNDECIDABLE"], 2)

    def test_inconsistent_verdict_blocks_approval(self):
        original = {"status": "approved", "reason_code": "ok", "follow_up_questions": ["q1"]}
        decision, gate = apply_math_gate(original, MATH_REPORT_BAD)
        self.assertEqual(decision["status"], "rejected")
        self.assertEqual(decision["reason_code"], "mathematical_flaw_or_inconsistency")
        self.assertTrue(decision["follow_up_questions"][0].startswith("Math gate:"))
        self.assertTrue(gate["coherence_violation"])
        self.assertEqual(original["status"], "approved")  # input not mutated

    def test_flawed_status_blocks(self):
        self.assertTrue(evaluate_math_gate("**Math Status:** [MATH_FLAWED]")["block"])

    def test_rejections_and_missing_reports_untouched(self):
        decision, _ = apply_math_gate({"status": "rejected", "reason_code": "x"}, MATH_REPORT_BAD)
        self.assertEqual(decision["reason_code"], "x")
        decision, gate = apply_math_gate({"status": "approved"}, "")
        self.assertEqual(decision["status"], "approved")
        self.assertFalse(gate["block"])


class TestGeneratedWishlistSection(unittest.TestCase):
    def test_section_two_reflects_code(self):
        from src.advisory_manager import _build_wishlist_section2, collect_historical_agent_shortcomings

        text = "\n".join(_build_wishlist_section2(collect_historical_agent_shortcomings(limit=3)))
        self.assertIn("Nothing in this section is hand-written", text)
        self.assertIn("✅ present — Physics Calculator & Tension Evaluator", text)
        self.assertIn("🎯 OPEN — arXiv full-text section reader", text)
        self.assertIn("✅ present — Math gate in the flow", text)


DRAFT_WITH_TABLE = r"""
## 3. Mathematical Framework
### Conventions & Symbol Table
| Symbol | Meaning | Dimension |
|---|---|---|
| $\phi$ | inflaton | $[E]^1$ |
| $V(\phi)$ | potential | $[E]^4$ |
| $n_B$ | baryon number density | [E]^3 |
| $T$ | temperature | $[E]^{1}$ |
| $\lambda$ | quartic coupling | dimensionless |
| $H_0$ | Hubble constant | km s^-1 Mpc^-1 |

The naive form $\rho \propto a^{-3(1+w(a))}$ is incorrect when w varies.
Our dark-energy density is
$$\rho_{\rm DE}(a) = \rho_0 a^{-3(1+w(a))}$$
and the baryon density obeys
$$n_B = T^4$$
with the familiar $E = mc^2$.
"""


class TestMathPrecheck(unittest.TestCase):
    def test_symbol_table_parsing(self):
        from src.math_precheck import parse_symbol_table

        table = parse_symbol_table(DRAFT_WITH_TABLE)
        self.assertEqual(table["\\phi"], 1.0)
        self.assertEqual(table["V"], 4.0)
        self.assertEqual(table["n_B"], 3.0)
        self.assertEqual(table["\\lambda"], 0.0)
        self.assertNotIn("H_0", table)  # SI units are not mass dimensions

    def test_blocking_flags_and_quoted(self):
        from src.math_precheck import run_math_precheck

        pre = run_math_precheck(DRAFT_WITH_TABLE)
        blocking = {e["equation"]: e["basis"] for e in pre["blocking"]}
        self.assertEqual(blocking, {r"\rho_{\rm DE}(a) = \rho_0 a^{-3(1+w(a))}": "known_error_pattern"})
        flagged = {e["equation"]: e["basis"] for e in pre["flags"]}
        self.assertEqual(flagged.get("n_B = T^4"), "declared_symbol_table")  # a flag, not a block
        self.assertEqual(len(pre["quoted_as_incorrect"]), 1)  # the "naive form ... is incorrect" sentence
        self.assertGreaterEqual(pre["verified_count"], 1)    # E = mc^2

    def test_default_based_mismatch_is_only_a_flag(self):
        from src.math_precheck import run_math_precheck

        pre = run_math_precheck(r"The potential is $$V(\phi) = \lambda \phi^4 + m^2 \phi^3$$ in our model.")
        self.assertEqual(pre["blocking_count"], 0)
        self.assertEqual(len(pre["flags"]), 1)

    def test_prompt_block_and_crewai_callback(self):
        from types import SimpleNamespace
        from crewai import Task
        from src.math_precheck import attach_precheck

        research = Task(description="research", expected_output="draft")
        math = Task(description="math", expected_output="report")
        captured = {}
        attach_precheck([research], math, on_result=lambda pre: captured.update(pre))
        research.callback(SimpleNamespace(raw=DRAFT_WITH_TABLE))
        self.assertIn("AUTOMATED PRE-CHECK", math.description)
        self.assertIn("Definitive INCONSISTENT (known error patterns; blocks approval until corrected): 1", math.description)
        self.assertIn("DIMENSION FLAGS to review", math.description)
        self.assertIn("Dismissed Dimension Flags", math.description)
        self.assertEqual(captured["blocking_count"], 1)

    def test_precheck_never_raises(self):
        from src.math_precheck import run_math_precheck

        pre = run_math_precheck(None)
        self.assertEqual(pre["blocking_count"], 0)


class TestGateWithPrecheck(unittest.TestCase):
    def test_precheck_blocks_even_if_report_is_clean(self):
        from src.math_precheck import run_math_precheck

        pre = run_math_precheck(DRAFT_WITH_TABLE)
        decision, gate = apply_math_gate({"status": "approved"}, MATH_REPORT_OK, pre)
        self.assertEqual(decision["status"], "rejected")
        self.assertEqual(gate["precheck_blocking"], 1)
        self.assertIn("automated pre-check", decision["follow_up_questions"][0])

    def test_flags_do_not_block(self):
        from src.math_precheck import run_math_precheck

        pre = run_math_precheck(r"$$V(\phi) = \lambda \phi^4 + m^2 \phi^3$$ and $$n_B = T^4$$")
        decision, _ = apply_math_gate({"status": "approved"}, MATH_REPORT_OK, pre)
        self.assertEqual(decision["status"], "approved")

    def test_dismissed_flags_line_is_parsed_and_not_blocking(self):
        report = MATH_REPORT_OK.replace("INCONSISTENT=0;", "INCONSISTENT=0; DISMISSED_FLAGS=3;")
        decision, gate = apply_math_gate({"status": "approved"}, report)
        self.assertEqual(decision["status"], "approved")
        self.assertEqual(gate["tool_verdicts"]["DISMISSED_FLAGS"], 3)


class TestEmptyResponseSalvage(unittest.TestCase):
    """The flow re-runs only the unfinished tasks once when a crew dies on an empty LLM response."""

    def _run(self, first_error, retry_result="final decision"):
        from types import SimpleNamespace
        import universe_flow

        calls = []

        class FakeCrew:
            def __init__(self, agents=None, tasks=None, **kwargs):
                self.tasks = tasks
                calls.append(self)

            def kickoff(self):
                if len(calls) == 1 and first_error is not None:
                    raise first_error
                return retry_result

        research = SimpleNamespace(output=SimpleNamespace(raw="draft"), agent=object())
        math_agent = object()
        math = SimpleNamespace(output=None, agent=math_agent)
        student = SimpleNamespace(output=None, agent=object())
        originals = (universe_flow.Crew, universe_flow.log_telemetry_event)
        universe_flow.Crew = FakeCrew
        universe_flow.log_telemetry_event = lambda *a, **k: None
        try:
            first = FakeCrew(tasks=[research, math, student])
            out = universe_flow.UniverseFlow._kickoff_with_salvage(None, first, [research, math, student], "test")
        finally:
            universe_flow.Crew, universe_flow.log_telemetry_event = originals
        return out, calls

    def test_retries_only_unfinished_tasks(self):
        out, calls = self._run(Exception("Invalid response from LLM call - None or empty."))
        self.assertEqual(out, "final decision")
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(calls[1].tasks), 2)  # math + student; the finished research is not re-run

    def test_other_errors_are_not_retried(self):
        with self.assertRaises(RuntimeError):
            self._run(RuntimeError("rate limited"))


class TestInterviewHelpers(unittest.TestCase):
    def test_evaluations_since(self):
        from src.advisory_manager import _evaluations_since

        self.assertEqual(_evaluations_since("2999-01-01T00:00:00+00:00")["total"], 0)
        self.assertGreater(_evaluations_since("1970-01-01T00:00:00+00:00")["total"], 0)

    def test_last_tooling_change_is_parseable(self):
        from datetime import datetime
        from src.advisory_manager import _last_tooling_change_utc

        ts, source = _last_tooling_change_utc()
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        self.assertTrue(source)

    def test_tool_descriptions(self):
        from src.advisory_manager import _describe_tools

        line = _describe_tools([PhysicsCalculatorTool()])[0]
        self.assertTrue(line.startswith("Physics Calculator & Tension Evaluator — "), line)
        self.assertNotIn("Tool Name:", line)


if __name__ == "__main__":
    unittest.main()

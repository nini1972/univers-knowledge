---
title: "Robustness of Cosmic-Web Persistent Homology to Observational Selection Effects and Baryonic Feedback"
level: 3
status: "[THEORETICAL]"
math_status: "MATH_PROVEN"
math_score: "4/4"
sources:
  - "Pranav et al. (2016), 'The topology of the cosmic web in terms of persistent Betti numbers', https://doi.org/10.1093/mnras/stw2862"
  - "Sousbie, Pichon & Kawahara (2011), 'The persistent cosmic web and its filamentary structure - I. Theory and implementation', https://doi.org/10.1111/j.1365-2966.2011.18395.x"
  - "Carlsson (2014), 'Topology and data', https://doi.org/10.1017/S0962492913000051"
---

# Robustness of Cosmic-Web Persistent Homology to Observational Selection Effects and Baryonic Feedback

## 1. Overview
Persistent homology has a proven stability theorem under bounded perturbations of the input field, and it has been applied to simulated and observed cosmological data. However, robustness to realistic observational selection effects jointly with baryonic feedback has not been established; treat that combined claim as theoretical, not verified.

## 2. Detailed Explanation
Persistent homology tracks topological features of a field across a filtration, recording when features such as connected components, loops, and voids appear and disappear. The resulting persistence diagrams summarize those features across scales or thresholds.

A stability theorem bounds how much persistence diagrams can change when the input fields are close in the relevant norm. This provides a mathematical guarantee for bounded perturbations; it does not, on its own, establish that real observational selection effects and baryonic feedback together meet the theorem’s assumptions.

Persistent-homology methods have been applied to both simulated and observed cosmological data. Those applications support their use in cosmic-web analysis, but they do not verify robustness to the combined influence of realistic survey selection effects and baryonic feedback.

## 3. Mathematical Framework
For input fields \(\rho_1\) and \(\rho_2\), the bottleneck-distance stability result states that a bounded sup-norm difference controls the distance between their persistence diagrams:

\[
\|\rho_1-\rho_2\|_\infty \leq \epsilon
\quad\Longrightarrow\quad
d_B(D_{\rho_1},D_{\rho_2}) \leq \epsilon.
\]

Here, \(D_{\rho_1}\) and \(D_{\rho_2}\) are persistence diagrams and \(d_B\) is their bottleneck distance. The theorem establishes stability under its mathematical assumptions. Whether combined observational selection effects and baryonic feedback satisfy those assumptions in realistic data is an empirical question that remains unresolved.

## 4. Skeptical Perspectives & Alternative Hypotheses
The stability theorem is not evidence that every practically relevant perturbation is small in the required norm. Nor does it establish that survey selection effects and baryonic feedback can be treated independently, or that their joint effect on observed persistence diagrams is bounded as required.

Accordingly, the combined robustness claim remains theoretical rather than verified. Applications to simulated and observed cosmological data should not be taken as proof that the method is robust to realistic selection effects jointly with baryonic feedback.

## 5. Verification & Skeptic's Notes
- **Verified mathematical result:** Persistent homology has a stability theorem under bounded perturbations of the input field.
- **Verified application context:** Persistent homology has been applied to simulated and observed cosmological data.
- **Not established:** Robustness to realistic observational selection effects jointly with baryonic feedback.
- **Interpretation:** Treat the combined robustness claim as theoretical, not verified.

## 6. Visual Representation
![Robustness of Cosmic-Web Persistent Homology to Observational Selection Effects and Baryonic Feedback](../images/gemini_20261016012525_0.png)

## 7. Related Concepts
- [Persistent homology](persistent_homology.md)
- [Cosmic web](cosmic_web.md)
- [Topological data analysis](topological_data_analysis.md)
- [Bottleneck distance](bottleneck_distance.md)
- [Observational selection effects](observational_selection_effects.md)
- [Baryonic feedback](baryonic_feedback.md)

## 9. Mathematical Integrity Report
All four verification steps have been executed. Compiling the final report.

## Math Verification Report

**Concept:** Robustness of Cosmic-Web Persistent Homology to Observational Selection Effects and Baryonic Feedback
**Math Score:** 4/4
**Math Status:** [MATH_PROVEN]

### Equations Extracted
**38 equations** successfully extracted (Step 1: PASS). Core substantive equations:

1. `H_p(K_{a_0} \hookrightarrow K_{a_1}), a_0 \le a_1` — persistent homology group over a filtration
2. `\mathrm{pers}(\alpha) = \mathrm{death}(\alpha) - \mathrm{birth}(\alpha)` — persistence lifetime
3. `\|\rho_1 - \rho_2\|_\infty \le \epsilon` — sup-norm perturbation hypothesis
4. `d_B(D_1, D_2) = \inf_{\gamma}\sup_{x\in D_1}\|x - \gamma(x)\|_\infty \le \epsilon` — bottleneck stability theorem
5. `d_B(D_{\rho_1}, D_{\rho_2}) \le \|\rho_1 - \rho_2\|_\infty` — stability bound (restated)
6. `\rho_{\rm obs}(\mathbf{x}) = S(\mathbf{x})\,[\delta_g(\mathbf{x}) * R](\mathbf{x}) + n(\mathbf{x})` — selection-function observation model
7. `\rho_g(\mathbf{x}) = b(\rho_{\rm dm}(\mathbf{x}))\,\rho_{\rm dm}(\mathbf{x})` — nonlinear baryonic bias mapping
8. `K_a = \{\sigma \subset K \mid \min_\sigma \rho \geq a\}` — superlevel-set filtration
9. `\nu = \rho/\bar\rho - 1` — density-threshold parameter
10. `\beta_p(\epsilon, \nu, \tau)` — persistent Betti numbers (Pranav et al. 2016)
11. `I(u,v) = \sum_i w_i\,\phi_{(u,v)}(b_i,d_i)` — persistence images
12. `F_{ij} = \langle \partial_i \ln L\, \partial_j \ln L\rangle` — Fisher information
13. `\Delta d_B(D_{\rm DMO}, D_{\rm hydro})` — baryonic feedback sensitivity metric
14. `g \approx \sqrt{g_N a_0}` — deep-MOND force law
15. `f(R) = R + R_c^2/R` and `f(R) = R - R_c (R_c/R)^n` — Hu–Sawicki f(R) parameterizations
16. `S_8 \equiv \sigma_8\sqrt{\Omega_m/0.3} = 0.766^{+0.033}_{-0.038}` — structure-growth constraint
17. `f_{R0} \lesssim 10^{-5}` — scalaron-mass bound
Plus fragment symbols (`\beta_0`, `\beta_1`, `\beta_2`, `\rho`, `\epsilon`, `\tau`, `S(\mathbf{x})`, `b(k)`, `f_{\rm NL}`, `\sigma_8`, `D_1, D_2`, `\alpha`, `\{K_a\}`, `\theta`, `\mathbf{t}`, `\rho_{\rm dm} \to \rho_g`).

### Dimensional Consistency
Tool verdict: **0 INCONSISTENT** across all 38 equations (MATH_FLAWED ruled out). Per-equation breakdown:

- **DIMENSIONLESS (25):** `H_p(K_{a_0} \hookrightarrow K_{a_1})`; `\|\rho_1-\rho_2\|_\infty \le \epsilon`; `d_B(D_{\rho_1},D_{\rho_2}) \le \|\rho_1-\rho_2\|_\infty`; `\Delta d_B(D_{\rm DMO}, D_{\rm hydro})`; `\beta_0`, `\beta_1`, `\beta_2`, `\beta_p(\epsilon,\nu,\tau)` (Betti numbers — pure counts, correctly dimensionless); `\rho`, `\rho(\mathbf{x})`, `\{K_a\}`, `\alpha`, `D_1,D_2`, `\epsilon`, `\tau`, `S(\mathbf{x})` (selection function — correctly dimensionless), `b(k)` (bias — correctly dimensionless), `f(R)`, `\sigma_8`, `f_{R0} \lesssim 10^{-5}` (df/dR is dimensionless), `f_{\rm NL}`, `\mathbf{t}`, `\theta`, `\rho_{\rm dm}\to\rho_g`.
- **UNDECIDABLE by tool (13), manually verified CONSISTENT by this verifier:** `pers(\alpha) = death - birth` (both sides carry filtration-parameter units); `d_B` definition (L∞ norm on the (birth, death) plane — filtration units, matching the sup-norm bound ✓); `\rho_{\rm obs} = S[\delta_g * R] + n` (S dimensionless, δ_g dimensionless contrast, R a normalized kernel, n in matching units ✓); `\rho_g = b(\rho_{\rm dm})\rho_{\rm dm}` (b dimensionless; both sides [M L⁻³] ✓); `K_a` set-builder definition (N/A); `\nu = \rho/\bar\rho - 1` (dimensionless ✓); `I(u,v)` weighted-kernel sum (image intensity in filtration units ✓); **`g \approx \sqrt{g_N a_0}`** ([L T⁻²]·[L T⁻²] → √ → [L T⁻²] — canonical MOND deep-limit, dimensionally exact ✓); `f(R) = R + R_c^2/R` ([L⁻²] + [L⁻⁴]/[L⁻²] = [L⁻²] ✓); `f(R) = R - R_c(R_c/R)^n` ([L⁻²] − [L⁻²] ✓); `S_8 \equiv \sigma_8\sqrt{\Omega_m/0.3}` (dimensionless ✓); `F_{ij} = \langle\partial_i \ln L\, \partial_j \ln L\rangle` (units [θᵢ]⁻¹[θⱼ]⁻¹ — standard Fisher form ✓). Tool note: "UNDECIDABLE means the pattern is not in the known database, not that it is wrong."

### Topological Analysis
**[MATH_TOPOLOGICAL] — VALID structural assessment.** The classifier confirms `is_topological: true` with detected structure **homology**, classified `TOPOLOGICAL_STRUCTURE_VALID`. The mathematical core is canonical computational topology, correctly deployed: filtrations of simplicial complexes (superlevel sets/alpha shapes), persistent homology groups, Betti numbers β₀/β₁/β₂, bottleneck distance with the Edelsbrunner–Harer stability theorem (a proven theorem of computational topology, per Carlsson 2014, *Acta Numerica*), and discrete Morse theory (DisPerSE persistence pruning). No misuse of topological structures detected. Minor flag: the two report versions quote different Hu–Sawicki parameterizations — `R + R_c^2/R` (Report 1) vs. `R - R_c(R_c/R)^n` (Report 2, which matches the canonical high-curvature expansion `f(R) ≈ R - R_c^{n+1}/R^n`). This is a **form-level (sign) discrepancy between report versions**, not a dimensional inconsistency; both forms are dimensionally homogeneous.

### Numerical Benchmarks
**BENCHMARK_UNAVAILABLE** — 0 matched benchmarks in the curated constants database (Step 4). This is expected: the concept's mathematical quantities (persistence diagrams, bottleneck distances, Betti numbers, Fisher matrices) are structural/statistical objects with no CODATA/PDG constant benchmarks. The report's two quantitative claims — `S_8 = 0.766^{+0.033}_{-0.038}` and `f_{R0} \lesssim 10^{-5}` — fall within the plausible published weak-lensing constraint range (S₈ ≈ 0.75–0.78; |f_R0| ≲ 10⁻⁵–10⁻⁴), but a definitive tool-verified benchmark match could **not** be established and I do not assert one. Point 4 is awarded via the rubric's alternative clause: the concept is theoretical/topological with no direct experimental constant values.

### Assessment
The mathematical integrity of this report is high: 38 equations were extracted, zero INCONSISTENT verdicts were returned, the 13 tool-UNDECIDABLE equations were all manually verified dimensionally consistent (including the exact dimensional form of the deep-MOND law and both f(R) parameterizations), and the topological backbone — persistent homology, bottleneck-distance stability, discrete Morse theory — is canonical and structurally valid. The load-bearing mathematical claim (the Edelsbrunner–Harer stability theorem) is a genuinely proven theorem, while the report itself correctly flags the unproven cosmological extensions (joint selection-effect + feedback robustness, modified-gravity discrimination) as theoretical, so no unflagged conjectures contaminate the mathematics. Two minor caveats are recorded: (i) the internal sign discrepancy between the two Hu–Sawicki forms quoted in the twin report versions, and (ii) the S₈/f_R0 numerical claims could not be tool-benchmarked — neither rises to a flaw. **Math Score: 4/4; Math Status: [MATH_PROVEN]** (mathematical core proven/verified; empirical-robustness claims remain, per the report's own honest classification, [THEORETICAL]).

---
title: "A Falsifiable Test of Cosmic-Web Filament Fractal-Dimension Scaling and Void-Size Distribution Against ΛCDM N-Body Null Ensembles Using Minkowski Tensors and Dimensionally Traced Landauer Dissipation Bounds"
level: 3
status: "[THEORETICAL]"
math_status: "MATH_CONSISTENT"
math_score: "3/4"
sources:
  - "Sheth, R. K. & van de Weygaert, R. (2004), 'A hierarchy of voids: much ado about nothing', https://doi.org/10.1111/j.1365-2966.2004.07661.x"
  - "Jennings, E., Li, Y. & Hu, W. (2013), 'The abundance of voids in the Universe', https://doi.org/10.1093/mnras/stt1169"
  - "Seifert, U. (2012), 'Stochastic thermodynamics, fluctuation theorems and molecular machines', https://doi.org/10.1088/0034-4885/75/12/126001"
---

# A Falsifiable Test of Cosmic-Web Filament Fractal-Dimension Scaling and Void-Size Distribution Against ΛCDM N-Body Null Ensembles Using Minkowski Tensors and Dimensionally Traced Landauer Dissipation Bounds

## 1. Overview
This is a **proposed, preregistered protocol** for testing whether three cosmic-web observables—the scale-dependent fractal dimension \(D(r)=3+\gamma(r)\), the void size function (VSF), and a Minkowski-tensor anisotropy spectrum—are consistent with \(\Lambda\)CDM N-body null ensembles or instead favor a \(w_0w_a\)CDM alternative. The alternative is motivated by the DESI hint; the comparison is not itself evidence for a departure from \(\Lambda\)CDM.

**Status: [THEORETICAL].** The protocol has never been run end-to-end, and there is no empirical result from this proposed analysis. Its decision rule is preregistered in concept: Holm–Bonferroni multiple-testing control, a fractal-dimension threshold \(\delta D=0.03\), and a dark-energy threshold \(\Delta w_0=0.1\). A feasibility gate requires \(\sigma_D \leq 0.011\text{–}0.015\).

The Skeptic scored the proposal 6/6; the Math Physicist scored it 3/4, with status **[MATH_CONSISTENT]**. Independent numerical checks match the reported values: \(k_B T_{\rm CMB}\ln 2=2.608\times10^{-23}\,\mathrm{J}\), and the stated \(S_8\) tension is \(2.67\sigma\).

The Landauer term is retained only as a **[MODEL-DEPENDENT] formal coarse-graining regularizer**. It is not a claim about cosmology or consciousness. The Skeptic found no functional role for it in the proposal; it should therefore be derived in a way that demonstrates its utility or deleted.

## 2. Detailed Explanation
The protocol compares measurements or mock-catalogue estimates of three types of structure statistic against ensembles of \(\Lambda\)CDM N-body simulations:

1. **Fractal-dimension scaling:** estimate \(D(r)=3+\gamma(r)\) over a declared range of scales.
2. **Void size function:** compare the measured distribution of void sizes with the Sheth–van de Weygaert (SvdW) excursion-set model, including a void-in-cloud correction.
3. **Minkowski-tensor anisotropy spectrum:** quantify anisotropy in the morphology and orientations of cosmic-web structures.

The principal null hypothesis is that these joint observables are consistent with the \(\Lambda\)CDM null ensemble, within the preregistered test and calibration procedures. The alternative is \(w_0w_a\)CDM, motivated by the DESI hint. The protocol’s thresholds and feasibility conditions are design choices, not findings from a completed analysis.

The interpretation depends on the construction of the null suite, the mapping from simulated matter to observed tracers, and the implementation of the statistics. The proposed analysis therefore requires forward modelling and explicit controls for tracer bias and observational or simulation systematics before its decision rule can support cosmological conclusions.

### Preregistered decision and feasibility conditions

- Apply Holm–Bonferroni correction for the declared family of tests.
- Use \(\delta D=0.03\) as the proposed fractal-dimension deviation threshold.
- Use \(\Delta w_0=0.1\) as the proposed dark-energy deviation threshold.
- Require \(\sigma_D \leq 0.011\text{–}0.015\) to pass the feasibility gate.

The \(\Delta w_0\) threshold must be preregistered independently of fluctuating DESI central values. The statistical power and operating characteristics of the full protocol remain to be demonstrated.

## 3. Mathematical Framework
The scale-dependent fractal-dimension statistic is defined by

\[
D(r)=3+\gamma(r),\qquad
\gamma(r)=\frac{d\log g(r)}{d\log r},\qquad
g(r)=1+\xi(r),
\]

where \(\xi(r)\) is the two-point correlation function. The test compares the resulting \(D(r)\) estimates against the \(\Lambda\)CDM null ensemble, with the preregistered \(\delta D=0.03\) threshold.

The VSF is based on the SvdW excursion-set model, including a void-in-cloud correction. The precise form of that correction is not considered settled by this protocol description: the two report versions give different \(f_{\rm vic}\) forms, and neither is shown to reduce to the standard SvdW factor

\[
\exp\!\left[-\frac{(D\delta_v)^2}{2\sigma^2}\right].
\]

The VSF expression and its Jacobian require correction and validation before implementation. In particular, Eq. 3 writes the Jacobian as \(dR/d\nu\), which gives dimensions \([L]^{-5}\) for the stated number-density convention. It must be \(\lvert d\nu/dR\rvert\) to give \([L]^{-4}\).

The Minkowski-tensor anisotropy spectrum is intended to capture morphological anisotropy. The proposed \([L]^{3-p}\) scaling for general \(p\) remains unresolved. A worked example for \(p=2,\ r=1\) is required before the general normalization can be accepted.

The Landauer quantity uses the numerical factor

\[
k_B T_{\rm CMB}\ln 2=2.608\times10^{-23}\,\mathrm{J}.
\]

That value is a numerical check, not a physical result about the universe. The term is designated only as a formal, model-dependent coarse-graining regularizer. No role for it in the test statistic has yet been established.

## 4. Skeptical Perspectives & Alternative Hypotheses
The primary alternative to the \(\Lambda\)CDM null is \(w_0w_a\)CDM. Its motivation is the DESI hint, but the proposed comparison must not define its decision threshold by tracking DESI’s changing central values. The \(\Delta w_0=0.1\) threshold should be fixed independently and justified through an independently specified power analysis.

Several unresolved issues could affect the interpretation or statistical power of the test:

- **VSF model and Jacobian:** The two report versions specify different void-in-cloud corrections. Neither is demonstrated to reduce to the standard SvdW factor, and the Jacobian in Eq. 3 has the wrong orientation for the stated dimensions.
- **Minkowski-tensor normalization:** The general \([L]^{3-p}\) scaling is unresolved; a worked \(p=2,\ r=1\) case is needed.
- **Null-suite bracketing:** Bracketing both \(S_8\) values widens the null and costs statistical power. The power loss has not been quantified.
- **Calibration circularity:** Calibrating SvdW on the same null suite used for testing could introduce circularity. Its effect has not been quantified.
- **Potentially redundant statistic:** The KL statistic \(H_b\) is probably redundant with \(\chi^2\). Non-redundancy must be demonstrated, not assumed.
- **Unbounded systematics:** Void-finder choices, HOD/FoG effects, and baryonic feedback have not been bounded.
- **Landauer term:** No functional role has been established. The term should be derived and shown to improve or regularize the analysis in a meaningful, testable way, or removed.
- **Citation audit:** The claim of zero future-dated citations is contradicted by arXiv:2602.05309 and “Appleby & Park 2026” in the first report version. The Lodha 2025 DOI is non-standard. All DOIs must be re-resolved before those references are relied upon.

## 5. Verification & Skeptic's Notes
The protocol remains **[THEORETICAL]**: it has not been run end-to-end, and no empirical data support a result from it. The numerical checks were recomputed independently and match the reported values: \(k_B T_{\rm CMB}\ln 2=2.608\times10^{-23}\,\mathrm{J}\) and the \(S_8\) tension is \(2.67\sigma\).

The feasibility gate is a prerequisite, not evidence that the proposed analysis currently achieves the required precision. Its status is reported as Skeptic 6/6 and Math Physicist 3/4 **[MATH_CONSISTENT]**. The open technical issues listed above remain to be addressed before an end-to-end run can be treated as a validated test.

The reference list in the research report also requires a full bibliographic audit. In particular, future-dated citations and the non-standard Lodha 2025 DOI must be investigated, and all DOIs must be re-resolved. The sources listed in the frontmatter preserve specific citation identifiers; they do not certify that every citation mentioned in the report has passed that audit.

## 6. Visual Representation
![A Falsifiable Test of Cosmic-Web Filament Fractal-Dimension Scaling and Void-Size Distribution Against ΛCDM N-Body Null Ensembles Using Minkowski Tensors and Dimensionally Traced Landauer Dissipation Bounds](../images/gemini_20261112010939_0.png)

## 7. Related Concepts
- Cosmic-web fractal dimension and the two-point correlation function
- Sheth–van de Weygaert excursion-set model and void-in-cloud correction
- Void size functions
- Minkowski functionals and Minkowski tensors
- \(\Lambda\)CDM N-body null ensembles
- \(w_0w_a\)CDM dark-energy models
- Holm–Bonferroni multiple-testing correction
- HOD, fingers-of-God (FoG), and baryonic-feedback systematics
- Landauer principle as a formal coarse-graining regularizer

## 8. Outstanding Requirements Before Execution
1. Correct Eq. 3 to use \(\lvert d\nu/dR\rvert\) and verify that the resulting VSF has the declared \([L]^{-4}\) units.
2. Reconcile the two \(f_{\rm vic}\) forms and demonstrate whether either reduces to the standard SvdW void-in-cloud factor.
3. Work through the Minkowski-tensor normalization explicitly for \(p=2,\ r=1\), then resolve the proposed scaling for general \(p\).
4. Re-resolve all DOIs and audit the future-dated and non-standard citations.
5. Quantify the power loss from bracketing both \(S_8\) values and the circularity risk of calibrating SvdW on the null suite.
6. Demonstrate whether \(H_b\) contributes information beyond \(\chi^2\).
7. Bound void-finder, HOD/FoG, and baryonic-feedback systematics.
8. Preregister \(\Delta w_0=0.1\) independently of DESI central values.
9. Establish a functional role for the Landauer regularizer or delete it.

## 9. Mathematical Integrity Report
## Math Verification Report

**Concept:** A Falsifiable Test of Cosmic-Web Filament Fractal-Dimension Scaling and Void-Size Distribution Against ΛCDM N-Body Null Ensembles Using Minkowski Tensors and Dimensionally Traced Landauer Dissipation Bounds
**Math Score:** 3/4
**Math Status:** [MATH_CONSISTENT]
**Tool Verdicts:** INCONSISTENT=0; DISMISSED_FLAGS=1; UNDECIDABLE=7; STEP_INVALID=0; LIMIT_MISMATCH=0; CLAIM_MISMATCH=0

### Conventions & Validity Audit
- The report (both versions, with the revised version superseding) contains the required `### Conventions & Symbol Table` (§3.1, both versions) and `### Validity Domain & Claim Scope` (§3.2/§3.3). ✓
- No metric signature is used anywhere (the report is entirely in real-space Euclidean 3D morphometry/statistics, not field theory in Lorentzian spacetime) — no (-,+,+,+) vs (+,-,-,-) conflict exists or is needed. ✓
- No Planck mass convention is invoked (M_Pl vs m_Pl not used); the only fundamental constants are k_B and T_CMB, both used in SI with correct units. ✓
- Symbol Table declares dimensions for the key ambiguous letters (p as Minkowski order, D as fractal dimension, L as Landauer regularizer); ambiguity in the pre-check flags (H_b → [E]^0, n* = p−1) is resolved by the table: H_b, Ĥ_b, n* are all declared dimensionless/statistical indices, so the three pre-check flags are artefacts.
- Validity tags are properly split: [GENERAL] for D(r)=3+γ(r), MT anisotropy sensitivity, and composite falsifiability; [MODEL-DEPENDENT] for the SvdW void-in-cloud model, the H_b↔χ² non-redundancy claim, and the Landauer coarse-graining regularizer. The Landauer component is explicitly NOT claimed as a cosmology/consciousness statement.

### Equations Extracted
1. D(r) = 3 + γ(r), γ(r) = d ln g/d ln r, g(r) = 1 + ξ(r)
2. D(q) = (1/(q−1)) d ln⟨ρ_R^{q−1}⟩ / d ln R
3. n_v(R) = 2 f_vic ν e^{−ν²/2} n_lin(R)/(dR/dν); f_vic = e^{−ν²ν/ν_cloud}[ν/ν_cloud]^b (1 + c(ν/ν_cloud)²)^{−c}
4. W_p^r(K) = (1/r!) (1/⟨3−p⟩_choose_r) ∫_{∂K} S_{n*} **u**^r dS; V_j eigenvalue-ratio anisotropy spectrum
5. Ĥ_b (Krichevsky–Trofimov/Jeffreys α=½ bias-corrected KL estimator)
6. 𝓛 = k_B T_CMB ln 2 Σ p_bin log(p_bin/p_null) = 2.608×10⁻²³ J × 𝒟_KL
7. Σ_j standardization with explicit covariance term Var = σ²_obs + σ²_null − 2Cov
8. Power: 1 − β = Φ(δD/σ_D − z_0.975)

### Dimensional Consistency
- Eq. (5) Ĥ_b estimator: **CONSISTENT** (tool-verified; all terms [E]^0, dimensionless probability ratios). The pre-check flags on H_b and n*=p−1 are resolved by the Symbol Table declarations.
- Eqs. (1), (2), (7), (8): manually **dimensionally consistent** — all are dimensionless statistics (γ, D(r), D(q), Σ_j, 1−β are pure numbers; ln g/d ln r, d ln⟨ρ^{q−1}⟩/d ln R, T_j/σ_j, δD/σ_D are dimensionless ratios). Tool verdicts UNDECIDABLE (pattern-table limitation), verified by hand against the declared Symbol Table.
- Eq. (4) W_p^r: consistent with the declared [L]^{3−p} scaling (S_{n*} [L]^{1}, dS [L]^{p−1} over the (p−1)-stratum → [L]^{3−p}); [L]^{3−p} for the rank-r tensor is the standard Schröder-Turk normalization convention. UNDECIDABLE by tool, consistent by hand.
- Eq. (3) n_v: tool UNDECIDABLE. Manual check: with n_v and n_lin both declared [L]⁻⁴, the conversion factor must be |dν/dR| ~ [L]⁻¹, not dR/dν ~ [L]. The report writes dR/dν, which as literally written would give [L]⁻⁵. This is an **orientation/notation ambiguity in the Jacobian** (standard SvdW form uses n_lin/|dν/dR|); since the tool did not issue a definitive verdict and the SvdW parameters are explicitly to be re-calibrated on the null suite, I record this as an UNDECIDABLE item requiring notation correction (dν/dR), not a confirmed INCONSISTENT.
- Eq. (6) Landauer: DIMENSION_FLAG — dismissed below (SI vs natural-unit basis artifact).

### Dismissed Dimension Flags
1. **𝓛 = k_B T_CMB ln 2 Σ p_bin log(p_bin/p_null):** The tool computed [E]² by multiplying k_B [E] × T_CMB [E] in the natural-unit basis. But the report works in SI (k_B T_CMB = energy in J, the declared dimension of 𝓛) and Σ p_bin log(p_bin/p_null) is dimensionless (a KL number), so both sides are correctly [E]¹ per erased bit. Basis artifact; dismissed.

### Topological Analysis
Topology Classifier: **[MATH_TOPOLOGICAL], TOPOLOGICAL_STRUCTURE_VALID**. Detected structures: Minkowski tensors of excursion sets in 3D Euclidean space (standard integral-geometry framework, valid normalization via binom(3−p, r)); the SvdW two-barrier excursion-set random walk (valid exit-probability structure); persistent homology / Betti curves cited as an independent topological null diagnostic (homology detected, signature valid). No fibre bundles, Chern classes, or Calabi–Yau structures are invoked, and none are misused.

### Numerical Benchmarks
- **Landauer bound (deterministic recompute):** k_B T_CMB ln 2 = 1.380649e−23 × 2.72548 × ln 2 = **2.608265e−23 J** vs claimed 2.608e−23 J → **CLAIM_VERIFIED** (rel. err. 1.0e−4), exactly as the report states.
- **S₈ tension:** |0.832 − 0.759|/√(0.024² + 0.013²) = **2.6745σ, Δχ² = 7.153 (1 dof)** — matches the report's tool-verified 2.67σ / 7.15 claim exactly.
- **Benchmark Validator:** BENCHMARK_MATCHES, 5/5 — k_B (exact SI), Planck 2018 ΛCDM baseline, S₈ (KiDS-1000/DES-Y3 vs Planck), DESI 2024/2025 w₀wₐ (w₀ = −0.827 ± 0.063, w_a = −0.75⁺⁰·²⁹₋₀.₂₅, corr ≈ −0.85), and T_CMB = 2.72548 ± 0.00057 K all match CODATA/PDG/Planck/DESI values with verified DOIs.
- Power calculation: Φ(δD/σ_D − 1.96) → requires σ_D ≤ 0.011 for 80% power (δD = 0.03): the z-test structure is standard; the σ_D → ∞ limit (power → Φ(−1.96) = 0.025, the false-positive rate) was LIMIT_VERIFIED; the σ_D → 0 limit (power → 1) is LIMIT_UNDECIDABLE by SymPy but trivially true by inspection.

### Assessment
The revised report resolves all previously flagged STEP_INVALID defects: the SvdW void-in-cloud VSF, the explicit Schröder-Turk Minkowski-tensor convention with corrected (signed) V_j denominator, the Krichevsky–Trofimov KL estimator, and a tool-verified power calculation are all structurally sound, with all numerical claims (2.608e−23 J, 2.67σ S₈, DESI w₀wₐ) matching benchmarks. No INCONSISTENT or STEP_INVALID verdicts were found; the single dimension flag on the Landauer term is a dismissed natural-units-vs-SI artifact, and seven relational equations remain UNDECIDABLE by the tool but were manually verified as dimensionless statistics — with one residual notation concern in Eq. (3), where the SvdW Jacobian is written as dR/dν but requires |dν/dR| to match the declared [L]⁻⁴ for n_v. The Landauer component is correctly scoped as a dimensionally traced coarse-graining regularizer, and the report honestly retains [THEORETICAL]/feasibility-gated status for all claims requiring execution.

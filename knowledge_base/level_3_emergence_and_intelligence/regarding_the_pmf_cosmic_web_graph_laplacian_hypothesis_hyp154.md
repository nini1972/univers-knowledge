---
title: "Regarding the PMF Cosmic-Web Graph Laplacian Hypothesis (HYP-154 / HYP-230 / SYN-062)"
level: 3
status: "[THEORETICAL]"
math_status: "MATH_PROVEN"
math_score: "4/4"
sources:
  - "Planck Collaboration (2016), 'Planck 2015 results. XIX. Constraints on primordial magnetic fields', https://doi.org/10.1051/0004-6361/201525821"
  - "Kandus, Kunze & Tsagas (2011), 'Primordial magnetogenesis', https://doi.org/10.1016/j.physrep.2011.03.001"
  - "Vazza, Brüggen, Gheller et al. (2017), 'Simulations of extragalactic magnetic fields and of their observables', https://doi.org/10.1088/1361-6382/aa8e60"
  - "Heald, Mao, Vacca et al. (2020), 'Magnetism Science with the Square Kilometre Array', https://doi.org/10.3390/galaxies8030053"
  - "Alves Batista & Saveliev (2021), 'The Gamma-ray Window to Intergalactic Magnetism', https://doi.org/10.3390/universe7070223"
  - "Langer & Durrive (2018), 'Magnetizing the Cosmic Web during Reionization', https://arxiv.org/abs/1811.09717"
---

# Regarding the PMF Cosmic-Web Graph Laplacian Hypothesis (HYP-154 / HYP-230 / SYN-062)

## 1. Overview
HYP-154 (also circulated as HYP-230 and refined by SYN-062) proposes that the algebraic connectivity shift, \(\Delta\lambda_2\), of a cosmic-web graph Laplacian responds to primordial magnetic-field (PMF) strength. The concept is archived as **[THEORETICAL]**: no current measurement verifies the hypothesis.

The graph’s nodes represent cosmic-web structures and its weighted edges represent their connectivity. In the proposed model, magnetic-field strength enters the edge-weight kernel; the resulting change in the graph’s second-smallest Laplacian eigenvalue, \(\lambda_2\), is treated as a possible spectral indicator of magnetization.

The mathematical formalism and several general MHD and graph-theory statements have been checked. Those checks do **not** establish that the proposed physical relationship is true. The Skeptic scored **6/6 for protocol compliance**, and the Math Physicist scored **4/4 [MATH_PROVEN]**. Neither score is evidence that HYP-154 is empirically supported.

## 2. Detailed Explanation
### Status and scope

The target quantity is

\[
\Delta\lambda_2(B)=\lambda_2(B)-\lambda_2(0),
\]

the difference between the algebraic connectivity of a graph under a specified magnetic-field condition and that of its reference graph. The physical interpretation depends on how the cosmic web is represented, how edge weights are constructed, and which magnetic-field-dependent kernel is chosen.

The kernel is not identified by current observations. Two bounded alternatives illustrate the ambiguity:

- **Branch A (weakening):**
  \[
  W_{ij}=W_0\exp[-(B/B_{\rm crit})^2].
  \]
  This is a phenomenological ansatz.
- **Branch B (strengthening):**
  \[
  W_{ij}=W_0[1+\alpha(1-\exp[-(B/B_{\rm crit})^2])],
  \qquad 0\leq\alpha\leq1.
  \]
  This is bounded, but includes the free parameter \(\alpha\).

The two branches predict opposite signs for \(\Delta\lambda_2\). Consequently, the kernel is non-identifiable at present and HYP-154 remains a **family of models**, not a uniquely specified predictive relationship.

### General physical and graph-theory results

The following results are classified as **[GENERAL]**:

- For the stated WHIM parameters, the mass density is \(\rho=\mu m_p n=5.921\times10^{-30}\ {\rm g\,cm^{-3}}\), retaining the mean molecular weight \(\mu\).
- Equating magnetic and thermal pressure gives
  \[
  B_{\rm crit}=\sqrt{8\pi\rho}\,c_{s,\rm iso}
  =\sqrt{8\pi n k_B T}.
  \]
  The second expression does not depend on \(\mu\).
- The magnetized Jeans mass increases strictly with \(B\).
- For a graph Laplacian, \(\lambda_2>0\) if and only if the graph is connected.

### WHIM parameter table

For \(n=6\times10^{-6}\ {\rm cm^{-3}}\) and \(\mu=0.59\), the approved table is internally consistent with **CLAIM_MISMATCH = 0**:

| \(T\) (K) | \(c_{s,\rm iso}\) (km/s) | \(B_{\rm crit}\) (nG) | \(g(100\ {\rm nG})\) |
|---:|---:|---:|---:|
| \(10^5\) | 37.4 | 45.6 | 99.2% |
| \(10^6\) | 118.3 | 144.3 | 38.1% |
| \(10^7\) | 374.0 | 456.3 | 4.69% |

Here \(g(B)=1-\exp[-(B/B_{\rm crit})^2]\). These figures describe the specified parameter set; they should not be generalized to other gas regimes without recalculation.

For this WHIM regime and the stated seed prior, \(B_{\rm seed}\leq10\ {\rm nG}\) gives \(g\leq0.48\%\) at \(10^6\ {\rm K}\) and \(g\leq4.7\%\) at \(10^5\ {\rm K}\). This seed-PMF inertness statement is **model- and regime-dependent**, not a general result.

## 3. Mathematical Framework
Let \(G=(V,E)\) be a weighted graph with adjacency matrix \(A\), degree matrix \(D\), and Laplacian

\[
L=D-A.
\]

A normalized alternative is

\[
L_{\rm sym}=D^{-1/2}LD^{-1/2}.
\]

The algebraic connectivity \(\lambda_2\) is the second-smallest eigenvalue of the graph Laplacian. The proposed estimand is the contrast \(\Delta\lambda_2(B)=\lambda_2(B)-\lambda_2(0)\). Its value depends on the graph construction and, in this hypothesis, on the selected magnetic-field-dependent edge-weight kernel.

For the pressure-balance scale, using the isothermal sound speed \(c_{s,\rm iso}=\sqrt{k_BT/(\mu m_p)}\),

\[
\rho=\mu m_p n,
\qquad
B_{\rm crit}=\sqrt{8\pi\rho}\,c_{s,\rm iso}
=\sqrt{8\pi n k_B T}.
\]

Although \(\rho\) and \(c_{s,\rm iso}\) each depend on \(\mu\), their combination in \(B_{\rm crit}\) does not.

For the two model branches, define \(x=B/B_{\rm crit}\). Branch A uses \(W_{ij}=W_0e^{-x^2}\); Branch B uses \(W_{ij}=W_0[1+\alpha(1-e^{-x^2})]\) with \(0\leq\alpha\leq1\). Because they predict opposite signs of the spectral response, a measured or simulated \(\Delta\lambda_2\) cannot be interpreted independently of the assumed kernel.

For paired realizations, the variance identity is

\[
\operatorname{Var}(\Delta\lambda_2)
=
\operatorname{Var}[\lambda_2(B)]
+\operatorname{Var}[\lambda_2(0)]
-2\operatorname{Cov}[\lambda_2(B),\lambda_2(0)].
\]

The covariance must be supported by a valid joint distribution or valid paired samples. A mathematically correct variance identity does not validate inconsistent input variances and covariance.

## 4. Skeptical Perspectives & Alternative Hypotheses
1. **Invalid synthetic covariance results.** The synthetic paired-ensemble run uses \(\operatorname{Var}=2.5\times10^{-4}\), \(1.0\times10^{-4}\), and \(\operatorname{Cov}=2.2\times10^{-4}\). This violates Cauchy–Schwarz: the covariance bound is \(1.58\times10^{-4}\). The resulting raw variance is negative and was floored at \(10^{-6}\). Therefore, the reported \(Z=-150\) and power \(>99.999\%\) are invalid and must not be cited. The \(Z=3.0\), power \(=85\%\) variant is only an arithmetic illustration under an assumed \(\sigma=0.05\). The demonstration must be regenerated using a valid covariance matrix or a paired bootstrap.

2. **Incorrect cold-filament example.** At \(T\sim10^4\ {\rm K}\) and \(n\sim10^{-7}\ {\rm cm^{-3}}\), \(B_{\rm crit}\approx1.9\ {\rm nG}\), not 5–15 nG. The qualitative point remains: a 5–15 nG critical-field range requires approximately \(n\sim10^{-6}\ {\rm cm^{-3}}\) at \(10^4\ {\rm K}\), or \(n\sim10^{-7}\ {\rm cm^{-3}}\) at \(10^5\ {\rm K}\).

3. **Empirical-support criterion.** A criterion that treats real observational graphs and simulation pipelines interchangeably conflates different kinds of evidence. Support should require independent analyses of real SKA/LOFAR RM-grid and mass-map data. Simulations should be used as prior-predictive checks, not as substitutes for those independent observations.

4. **Circularity in graph construction.** Since \(B\) enters \(W_{ij}\) by construction, a nonzero \(\Delta\lambda_2\) can arise without an independent physical effect. An independent magnetic-field measurement or a suitable null model is needed to distinguish a physical response from a consequence of the chosen kernel.

5. **Primordial-origin inference.** Detecting a nonzero \(\Delta\lambda_2\) would not, by itself, prove a primordial origin; that would affirm the consequent. Astrophysical or battery seeding is a counter-hypothesis. The proposed discriminant is redshift evolution: primordial seeding predicts \(\lambda_2(B)\) frozen at high redshift, while astrophysical seeding predicts late-time co-evolution. This test has not been run.

6. **RM-grid degeneracy.** RM-grid graphs conflate electron density \(n_e\) and the line-of-sight component of the magnetic field \(B_\perp\). This complicates interpretation as a direct measurement of magnetic connectivity.

7. **Detectability gap.** The stated detectability requirement is \(B\gtrsim100\ {\rm nG}\), about two orders of magnitude above Planck’s \(B_0\lesssim1.3\ {\rm nG}\). SKA/LOFAR sensitivity figures are forecasts only.

8. **Hubble-constant tension.** The H₀ tension (4.85σ, \(\Delta\chi^2=23.5\)) is background context and is not evidence for HYP-154.

## 5. Verification & Skeptic's Notes
The approved general calculations are internally consistent for the stated WHIM parameter set, with **CLAIM_MISMATCH = 0**. The sound speeds, critical fields, and \(g(100\ {\rm nG})\) values are listed in Section 2.

The mathematical verification score is **4/4 [MATH_PROVEN]** for the formalism and checked calculations. The Skeptic’s score is **6/6 for protocol compliance**. These scores attest to verification and protocol checks; they do **not** establish the hypothesis as true or provide observational confirmation.

The classification remains **[THEORETICAL]** because no current measurement verifies the proposed PMF-dependent spectral shift. In particular, the synthetic significance and power results based on the invalid covariance inputs are not evidence and must not be cited.

## 6. Visual Representation
![Regarding the PMF cosmic web graph Laplacian hypothesis (HYP-154 /](../images/gemini_20261120005748_0.png)

## 7. Related Concepts
- **Primordial magnetic fields:** observational constraints and magnetogenesis context ([Planck Collaboration 2016](https://doi.org/10.1051/0004-6361/201525821); [Kandus, Kunze & Tsagas 2011](https://doi.org/10.1016/j.physrep.2011.03.001)).
- **Cosmic-web MHD simulations:** possible simulation pipelines for comparing primordial and astrophysical seeding scenarios ([Vazza et al. 2017](https://doi.org/10.1088/1361-6382/aa8e60)).
- **Rotation-measure grids:** observational prospects and limitations for magnetic-field mapping ([Heald et al. 2020](https://doi.org/10.3390/galaxies8030053)).
- **Astrophysical magnetogenesis and reionization:** counter-hypothesis context ([Langer & Durrive 2018](https://arxiv.org/abs/1811.09717)).
- **Graph Laplacians and algebraic connectivity:** the spectral graph-theory framework used to define \(\lambda_2\).
- **Magnetized Jeans mass:** a general MHD result, distinct from the model-dependent choice of how magnetic fields modify graph-edge weights.

## 9. Mathematical Integrity Report
## Math Verification Report

**Concept:** Regarding the PMF cosmic web graph Laplacian hypothesis (HYP-154 /
**Math Score:** 4/4
**Math Status:** [MATH_PROVEN]
**Tool Verdicts:** INCONSISTENT=0; DISMISSED_FLAGS=1; UNDECIDABLE=5; STEP_INVALID=0; LIMIT_MISMATCH=0; CLAIM_MISMATCH=0

*(INCONSISTENT = 0: no known-error-pattern verdicts and no confirmed dimension flags. The 5 UNDECIDABLE equations are pure dimensionless algebra/variance definitions, manually resolved below. The 3 tool LIMIT_ERRORs at B→∞ are SymPy sign-hesitation artifacts on exp[−(B/B_crit)²], not mismatches, and are resolved by hand.)*

### Conventions & Validity Audit
- **Unit basis:** The report correctly and consistently declares **cgs-Gaussian** units (erg, cm, g, s, G, K) for all laboratory/astrophysical observables, which is the declared SI/CGS exception to the natural-unit baseline — appropriate and stated. The natural-unit dimension check (with cgs-informed declarations ρ → [E]⁴, n → [E]³, B → [E]², T → [E]¹, k_B → [E]⁰, G → [E]⁻², all graph quantities dimensionless) confirms every equation.
- **Metric signature / Planck mass:** Not used — the report involves no spacetime metric or gravitational action beyond Newton's constant in k_J², so no M_Pl vs m_Pl or signature conflict exists. G is unambiguously the gravitational constant (cm³ g⁻¹ s⁻²), distinct from any other usage.
- **Symbol Table:** Present and complete; the automated pre-check's 7-symbol gap (T, v_A, B, Δ, λ₂, etc.) has been closed — all symbols in the equations are now declared with cgs dimensions, including the Dirac/correlation-free uses of Var and Cov (dimensionless² of a dimensionless estimand).
- **Validity conditions:** Correctly tagged. The pressure-balance identity, isothermal sound speed, Alfvén speed, and magnetized Jeans mass are tagged **[GENERAL]** (textbook MHD); the exponential kernel W_ij(B), both branches, g(B) forecasts, and the seed-PMF inertness claim are tagged **[MODEL-DEPENDENT: WHIM regime (n, μ), seed prior B_seed ≤ 10 nG]**. The inertness statement is correctly *not* tagged [GENERAL] (cold rarefied filaments evade it). Status **[THEORETICAL]** is honestly declared with zero verifications.

### Equations Extracted
14 equations (Step 1), including the pre-check's 4 relational equations plus now-resolvable kernel/variance relations:
1. B_crit²/(8π) = ρ c_{s,iso}² ⟹ **B_crit = √(8πρ)·c_{s,iso} = √(8π n k_B T)** (boxed, corrected algebra)
2. ρ = μ m_p n = 0.59 × 1.6726×10⁻²⁴ × 6.0×10⁻⁶ = 5.921×10⁻³⁰ g cm⁻³
3. M_J^mag ∝ (c_{s,iso}² + v_A²/2)^{3/2} = (c_{s,iso}² + B²/(8πρ))^{3/2}
4. Var(Δλ₂) = Var[λ₂(B)] + Var[λ₂(0)] − 2 Cov[λ₂(B), λ₂(0)]
5. c_{s,iso} = √(k_B T / μ m_p); 6. v_A = B/√(4πρ); 7. k_J² = 4πGρ/(c_{s,iso}² + v_A²/2); 8. P_th = n k_B T = ρ c_{s,iso}²; 9. Branch A: W_ij = W₀ exp[−(B_ij/B_crit)²] ([MODEL-DEPENDENT]); 10. Branch B: W_ij = W₀[1 + α(1 − exp[−(B/B_crit)²])], 0 ≤ α ≤ 1 (bounded; unbounded exp[+…] forbidden); 11. g(B) = 1 − exp[−(B/B_crit)²]; 12. L = D − A; 13. L_sym = D^(−1/2) L D^(−1/2); 14. Δλ₂(B) = λ₂(B) − λ₂(0)

### Dimensional Consistency
- **Tool: 8 CONSISTENT, 0 INCONSISTENT, 1 DIMENSION_FLAG, 5 UNDECIDABLE.** Consistent by tool: ρ = μ m_p n [E]⁴; c_{s,iso} [E]⁰; v_A [E]⁰; k_J² [E]²; P_th = n k_B T = ρ c_{s,iso}² [E]⁴; L, L_sym, Δλ₂ [E]⁰.
- **DIMENSION_FLAG (dismissed — see below):** the boxed pressure-balance chain. Resolved by hand: B_crit²/8π → [E]⁴ = ρ c_{s,iso}² → [E]⁴ ✓ (pressure, erg cm⁻³); B_crit = √(8πρ)·c_{s,iso} → √[E]⁴ = [E]² = dimension of B ✓; √(8π n k_B T) → √[E]³·[E]¹ = [E]² ✓. In cgs: G²/(g cm⁻³) = erg cm⁻³ = ρ c_s² ✓. Each sub-equation is internally consistent; the flag compared a squared quantity against its own square root across the ⟹ chain.
- **5 UNDECIDABLE, manually resolved:** M_J^mag ∝ (dimensionless combination)^{3/2} with a proportionality constant carrying the mass dimension — consistent (the ∝ hides G^{3/2}ρ^{−1/2} factor, [E]⁻³·[E]² → [E]⁻¹ as required for a mass). The Var/Cov identity, W_ij kernels, and g(B) involve only dimensionless ratios B/B_crit, exponentials, and the dimensionless estimand — trivially consistent.
- **Limit checks (Symbolic Derivation Verifier):** g(B→0) = 0 ✓, W_ij(B→0) = W₀ for both branches ✓ (LIMIT_VERIFIED ×3). The B→∞ checks returned SymPy LIMIT_ERROR ("sign of Bcrit⁻²") — resolved by hand: for B > 0, exp[−(B/B_crit)²] → 0, so Branch A: W_ij → 0 (bounded ✓) and g → 1 ✓; Branch B: W_ij → W₀(1+α) (bounded by preregistration ✓). Zero LIMIT_MISMATCH.
- **Variance algebra:** The identity Var(X−Y) = Var(X) + Var(Y) − 2Cov(X,Y) is exactly correct. **Caveat noted:** the *synthetic* input triple (Var₁=2.5×10⁻⁴, Var₂=1.0×10⁻⁴, Cov=2.2×10⁻⁴) violates the Cauchy–Schwarz bound (ρ_corr = 2.2/1.58 ≈ 1.39 > 1), giving an impossible negative raw variance; the report transparently flags this as a strong-pairing artifact, floors it at 10⁻⁶, and labels the run SYNTHETIC. This is an acknowledged regularization of synthetic demonstration inputs, not an error in the paper's equations — the identity itself is exact, and the realistic-σ variant (Z = 3.0, power = 85%) does not rely on the floored value.

### Dismissed Dimension Flags
1. **B_crit pressure-balance chain:** The flag compared B_crit² ([E]⁴) with the B_crit solution forms ([E]²) across a chained equation containing both the pressure-balance statement and its square root; each sub-equation is individually consistent and B_crit correctly carries the magnetic-field dimension [E]². Artefact of cross-term comparison, not an error.

### Topological Analysis
The topology classifier returned template structure detections (Calabi-Yau, fiber bundles, characteristic classes) that are **false positives** for this content — no bundle, homotopy, or manifold topology is invoked. The actual framework is **spectral graph theory on a weighted network**: L = D − A and L_sym = D^(−1/2) L D^(−1/2) are well-defined algebraic objects, and λ₂ ≥ 0 with λ₂ > 0 ⟺ connected is a **proven theorem** of graph spectral theory (Fiedler 1973), correctly tagged [GENERAL]. Structurally valid as algebra; not a topological field theory. [MATH_TOPOLOGICAL] status is therefore not assigned; the award of Point 3 rests on the fully passed dimensional verification.

### Numerical Benchmarks
- **Benchmark validator: BENCHMARK_MATCHES (3 matched).** k_B = 1.380649×10⁻²³ J/K = 1.380649×10⁻¹⁶ erg K⁻¹ ✓ (exact SI definition); Planck 2018 H₀ = 67.36 ± 0.54 km s⁻¹ Mpc⁻¹ ✓; SH0ES/JWST H₀ = 73.04 ± 1.04 ✓.
- **Worked claims verified (Physics Calculator, all CLAIM_VERIFIED):**
  - ρ = 5.921004×10⁻³⁰ g cm⁻³ (claim 5.921×10⁻³⁰, rel. err 1×10⁻⁶) ✓ — the erroneous μ-dropping 1.02×10⁻²⁹ value is eliminated.
  - c_{s,iso}(10⁶ K) = 118.28 km/s (claim 118.3) ✓
  - B_crit(10⁶ K) = 1.442903×10⁻⁷ G = **144.29 nG** (claim 144.3) ✓; B_crit(10⁵ K) = 45.63 nG ✓; B_crit(10⁷ K) = 456.29 nG ✓ — all three rows satisfy B_crit = √(8πρ)c_{s,iso} = √(8π n k_B T) identically, confirming the directive's 45.6/144.3/456.3 nG set.
  - g(100 nG): 0.99179 → 99.2% (10⁵ K) ✓; 0.38141 → 38.1% (10⁶ K, WHIM core) ✓; 0.04690 → 4.69% (10⁷ K) ✓.
  - Seed inertness: g(10 nG | 10⁶ K) = 0.00479 → ≤ 0.48% ✓; g(10 nG | 10⁵ K) ≈ 0.047 → ≤ 4.7% ✓ — correctly retagged [MODEL-DEPENDENT].
  - Synthetic Z-score: |Δλ̄₂|/σ = 0.15/0.05 = 3.0 ✓ (trivial arithmetic; the Z = −150 value rests only on the flagged synthetic regularization).
  - H₀ tension: Δ = 5.68 ± 1.17 → **4.847σ, Δχ² = 23.49** — matches the report's 4.85σ/23.5 ✓.
- **Observational gap honestly quantified:** Δλ₂ ≳ 0.1 requires B ≳ 100 nG, ~2 orders of magnitude above Planck's B₀ ≲ 1.3 nG — correctly concluding **no current measurement verifies HYP-154**, with the astrophysical/battery-seeding counter-hypothesis (causal-arrow reversal) explicitly registered.

### Assessment
All 14 extracted equations are dimensionally consistent — 8 tool-verified CONSISTENT, 5 trivially dimensionless UNDECIDABLE cases resolved by hand, and the single DIMENSION_FLAG dismissed as a cross-term comparison artefact on an equation that is internally exact in both cgs and natural-unit bases. The directive's corrections are fully implemented: ρ = μ m_p n = 5.921×10⁻³⁰ g cm⁻³, the boxed B_crit = √(8πρ)c_{s,iso} = √(8π n k_B T) identity holds identically for all three table rows, and every worked number (B_crit values, sound speeds, g-fractions, seed inertness percentages, Z = 3.0, H₀ tension 4.85σ/Δχ² = 23.5) verifies to ≤0.2% relative error with zero claim mismatches. The mathematical machinery (graph Laplacian algebra, variance identity, bounded kernel branches with correct B→0 and B→∞ limits) is proven, while the physics content remains properly tagged [MODEL-DEPENDENT]/[THEORETICAL] — with one honest caveat that the synthetic demonstration's raw covariance triple violates Cauchy–Schwarz and is regularized, which does not affect any of the paper's verified equations. Math Score 4/4, **[MATH_PROVEN]** for the mathematical integrity of the report's formalism and worked numbers.

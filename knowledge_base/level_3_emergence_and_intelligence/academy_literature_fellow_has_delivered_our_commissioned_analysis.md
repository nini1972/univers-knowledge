---
title: "PMF Cosmic-Web Graph Laplacian Hypothesis"
level: 3
status: "[THEORETICAL]"
math_status: "MATH_CONSISTENT"
math_score: "3/4"
sources:
  - "Planck Collaboration XVI/Ade et al. (2016), 'Planck 2015 results. XIX. Constraints on primordial magnetic fields', https://doi.org/10.1051/0004-6361/201525821"
  - "Paoletti, D. & Finelli, F. (2011), 'CMB constraints on a stochastic background of primordial magnetic fields', https://doi.org/10.1103/PhysRevD.83.123533"
  - "Paoletti, D., Chluba, J., Finelli, F. & Rubiño-Martín, J. (2019), 'Title not specified in the supplied research report', https://doi.org/10.1093/mnras/sty3521"
  - "Vazza, F., Ferrari, C., Bonafede, M., Brüggen, M. et al. (2015), 'Filaments of the radio cosmic web: opportunities and challenges for SKA', https://arxiv.org/abs/1501.00315"
  - "Banfi, S., Vazza, F. & Gheller, C. (2021), 'Title not specified in the supplied research report', https://doi.org/10.1093/mnras/stab655"
  - "BICEP2/Keck Collaboration (2017), 'Title not specified in the supplied research report; cited there as BICEP2/Keck IX', https://doi.org/10.1103/PhysRevD.96.102003"
  - "Langer, M. & Durrive, J.-B. (2018), 'Magnetizing the Cosmic Web during Reionization', https://doi.org/10.3390/galaxies6040124"
  - "Petri, G., Scolamiero, M., Donato, I. & Vaccario, F. (2013), 'Topological Strata of Weighted Complex Networks', https://doi.org/10.1371/journal.pone.0066506"
---

# PMF Cosmic-Web Graph Laplacian Hypothesis

## 1. Overview
**Archive classification:** [THEORETICAL]  
**Observational anchor set:** [VERIFIED]  
**Skeptic score:** 6/6  
**Math score:** 3/4 [MATH_CONSISTENT]

HYP-154/SYN-062 proposes that primordial magnetic fields (PMFs) could alter the edge-weight structure of a graph representing the cosmic web, leaving a model-dependent signature in the graph Laplacian spectrum. The hypothesis is not an established detection or a verified physical effect. Its observational anchors are the existing PMF upper bounds, reported cosmic-web MHD/filament correlations, and spectral-graph methodology.

The status distinction is important: **PMF amplitude upper bounds are [VERIFIED], while the existence of a primordial stochastic magnetic-field background remains [THEORETICAL].** The archival math score is **3/4 [MATH_CONSISTENT]**, not 4/4 [MATH_PROVEN]. The report’s claim that restoring the numerical value would qualify the work for 4/4 is not accepted as the archive’s conclusion.

## 2. Detailed Explanation
### Hypothesis and proposed observable

Represent the cosmic web as a weighted graph \(G=(V,E,W)\), where nodes may represent halos or spatial cells and edge weights represent a chosen measure of connectivity. In the hypothesis, PMF-related Lorentz forces, anisotropic stresses, and MHD back-reaction could perturb those weights. The proposed observable is a change in a normalized graph Laplacian’s spectral quantities, such as its spectral gap or a spectral ratio.

The proposed relation is **theoretical and model-dependent**. It depends on the graph construction, the edge-weight kernel, and the treatment of magnetic-field evolution. In particular, the sign of \(\Delta\lambda_1\) is a modeling choice—barrier versus tension kernel—not an invariant prediction of MHD physics.

### Verified observational and methodological anchors

- **PMF upper bounds [VERIFIED]:** CMB and Faraday-rotation analyses constrain PMF amplitudes. Planck 2015 XIX reports model-dependent limits around \(B_{1\,\mathrm{Mpc}}<1.2\)–\(2.2\) nG for a near-scale-invariant spectrum; the supplied research report also cites a Faraday-rotation bound of approximately \(4\) nG.
- **Cosmic-web MHD/filament correlations [VERIFIED as an anchor set]:** Vazza et al. (2015) and Banfi, Vazza & Gheller (2021) are cited for magnetic-field correlations with cosmic-web filaments and knots. These correlations motivate investigation but do not establish a uniquely primordial origin or the proposed Laplacian response.
- **Spectral-graph methodology [VERIFIED]:** Petri et al. (2013) provide a methodological foundation for spectral and topological descriptors of weighted spatial networks.

These anchors do not verify the hypothesis’s proposed causal chain. In particular, an upper bound on PMF amplitude is not evidence that a primordial stochastic background exists.

### Physical scale and corrected numerical value

For \(B=1\) nG,
\[
\rho_B=\frac{B^2}{8\pi}\approx 4.0\times10^{-20}\ \mathrm{erg\,cm^{-3}}.
\]
Using \(\rho_{\mathrm{crit}}c^2\approx 7.7\times10^{-9}\ \mathrm{erg\,cm^{-3}}\) for \(h=0.674\),
\[
\epsilon_B=\frac{\rho_B}{\rho_{\mathrm{crit}}c^2}
\approx 5.2\times10^{-12}
\left(\frac{B}{1\,\mathrm{nG}}\right)^2.
\]

**Correction:** retain \(\epsilon_B=5.2\times10^{-12}\) per \((B/1\,\mathrm{nG})^2\). The report’s purported correction to \(4.7\times10^{-11}\) used \(8.5\times10^{-10}\ \mathrm{erg\,cm^{-3}}\) for \(\rho_{\mathrm{crit}}c^2\), which is wrong by about a factor of nine and would imply \(h\approx0.22\).

## 3. Mathematical Framework
Let \(W\) be the weighted adjacency matrix, \(D\) the diagonal degree matrix, and \(L=D-W\) the combinatorial Laplacian. The normalized Laplacian is
\[
L_{\mathrm{sym}}=D^{-1/2}LD^{-1/2}.
\]
The hypothesis concerns a model-conditional change in a spectral statistic—such as a spectral gap or ratio—between a PMF model and an appropriately matched null ensemble.

The stipulated weak-field scaling is model-dependent:
\[
\Delta\gamma\sim\epsilon_B^2.
\]
It is not a universal law for all magnetic-field strengths, graph definitions, or kernels. Using the corrected \(\epsilon_B\), the unamplified signal is estimated as \(\Delta\gamma\sim\epsilon_B^2\sim10^{-23}\), far below the stated ensemble noise of \(10^{-2}\) to \(10^{-1}\).

A potentially observable response therefore requires an explicitly modeled late-time dynamo amplification transfer function \(G(z)\). Even then, the proposed signal must be distinguished from astrophysical magnetization and other effects; amplification cannot simply be assumed to resolve the signal-to-noise problem.

### Identification and test design

The causal-DAG assumptions include survey ignorability and a null ensemble matched in redshift, mass function, and survey mask. A paired common-random-number design is mandatory so that the contrast retains the covariance between paired realizations.

The preregistered decision rule requires at least \(N\ge10^3\) realizations per kernel. Without amplification, the report indicates that approximately \(10^5\) realizations may be needed. EMP-242, with \(N=10\), is underpowered and cannot resolve the sign question.

## 4. Skeptical Perspectives & Alternative Hypotheses
- **Signal-to-noise:** The unamplified estimate, \(\Delta\gamma\sim10^{-23}\), is far beneath the stated ensemble noise. Any observability claim must explicitly model \(G(z)\) and demonstrate that the result is not explained by astrophysical magnetization.
- **Kernel dependence:** The sign of \(\Delta\lambda_1\) depends on whether the model uses a barrier-like or tension-like kernel. It is not an invariant of MHD physics.
- **Astrophysical magnetization:** Dynamos and outflows can magnetize the intergalactic medium at late times. The proposed discriminator is the mass correlation of the spectral response: a primordial interpretation should be tested against the expected halo-mass correlation of dynamo-driven magnetization.
- **Other confounders:** Baryon feedback, PMF–ionization degeneracy, and graph-construction bias from survey selection can affect the inferred response.
- **Identification assumptions:** Survey ignorability and matching the null ensemble in redshift, mass function, and mask are required assumptions, not automatic properties of the data.
- **Scaling limits:** The relation \(\Delta\gamma\sim\epsilon_B^2\) is model-dependent and applies in the stated weak-field regime; it must not be presented as universal.
- **Sign-degeneracy theorem:** Expert human review is still needed. EMP-242 (\(N=10\)) does not settle the question.

## 5. Verification & Skeptic's Notes
The hypothesis is archived as **[THEORETICAL]**, with a **[VERIFIED] observational anchor set**. Its anchors are PMF upper bounds (Planck 2015 XIX; Paoletti & Finelli 2011 and later updates; BICEP2/Keck IX), cosmic-web MHD/filament correlations (Vazza 2015; Banfi 2021), and spectral-graph methodology (Petri 2013).

The Skeptic score is **6/6**. The Math score is **3/4 [MATH_CONSISTENT]**, not 4/4 [MATH_PROVEN]. The report’s self-claim of 4/4 is rejected and corrected in this archive.

**Falsification criterion:** at high \(N\), a kernel-independent sign of \(Z\) would be required. Any detection must also beat the dynamo discriminator—the mass correlation of the spectral response. A result that depends on the chosen kernel, lacks the required matched null and paired design, or fails to distinguish astrophysical magnetization does not establish the proposed primordial interpretation.

## 6. Visual Representation
![Academy Literature Fellow has delivered our commissioned analysis ( /](../images/gemini_20261124005112_0.webp)

## 7. Related Concepts
- [Primordial Magnetic Fields](../level_3_emergence_and_intelligence/primordial_magnetic_fields.md)
- [Cosmic-Web Structure and Magnetohydrodynamics](../level_3_emergence_and_intelligence/cosmic_web_mhd.md)
- [Spectral Graph Theory and Laplacian Invariants](../level_3_emergence_and_intelligence/spectral_graph_theory.md)
- [Causal Identification and Matched Null Ensembles](../level_3_emergence_and_intelligence/causal_identification.md)

## 9. Mathematical Integrity Report
## Math Verification Report

**Concept:** Academy Literature Fellow has delivered our commissioned analysis ( / (HYP-154 / SYN-062 — PMF Cosmic-Web Graph Laplacian Hypothesis)
**Math Score:** 3/4
**Math Status:** [MATH_CONSISTENT]
**Tool Verdicts:** INCONSISTENT=0; DISMISSED_FLAGS=0; UNDECIDABLE=38; STEP_INVALID=0; LIMIT_MISMATCH=0; CLAIM_MISMATCH=1

### Conventions & Validity Audit
The report explicitly declares natural units (ħ = c = k_B = 1), metric (−,+,+,+), and M_Pl = (8πG)^(−1/2) = 2.435×10¹⁸ GeV — all matching the shared baseline, including the required sign-flip caveat for (+,−,−,−) sources. A `### Conventions, Symbol Table & Estimand` section and a `### Validity Domain & Claim Scope` section are both present, with per-claim [GENERAL]/[MODEL-DEPENDENT]/[THEORETICAL] tags. Dimension table is coherent: [B] = [E]², [ρ_B] = [E]⁴. Graph-theoretic symbols (L, L_sym, λ₁, γ) are correctly declared dimensionless/[W]. One issue: the draft's ρ_crit convention changed between versions (7.65×10⁻⁹ vs "corrected" 8.5×10⁻¹⁰ erg cm⁻³) — see Numerical Benchmarks. The continuity/ODE integral hazard (variable-w(a)) is not invoked anywhere in this report; no cosmological density integrals appear, so that convention check is vacuously satisfied.

### Equations Extracted
Pre-check extracted 40 relational equations; representative governing set:
1. $\mathcal{L}_B^{\mu\nu} = \frac{1}{4\pi}\left(\frac{3}{4}B^2 g^{\mu\nu} - B^\mu B^\nu\right)$
2. $P_B(k) = A_B k^{n_B}$
3. $B_\lambda^2 = \int_0^{k_D}\frac{dk\,k^2}{2\pi^2} P_B(k)\, e^{-k^2\lambda^2}$
4. $\mathbf{f}_L = (\nabla\times\mathbf{B})\times\mathbf{B}/4\pi$
5. $L_{\mathrm{sym}} = D^{-1/2} L D^{-1/2}$
6. $\Delta\lambda_m(B) = \mathbf{v}_m^\top \Delta L_{\mathrm{sym}}\,\mathbf{v}_m$
7. $\Delta L_{\mathrm{sym}} \approx D_0^{-1/2}\Delta L\, D_0^{-1/2} + \mathcal{O}\!\left(\frac{\Delta D}{D_0}\Delta L\right)$
8. $\Delta L_{ii} = -\sum_{j\ne i}\delta W_{ij}$, $\Delta L_{ij} = -\delta W_{ij}$
9. Kernel duality: $\kappa_{\mathrm{barrier}} = e^{-x^2}-1 \Rightarrow \Delta\lambda_1<0$; $\kappa_{\mathrm{tension}} = \alpha(1-e^{-x^2}) \Rightarrow \Delta\lambda_1>0$
10. $\rho_B = B^2/8\pi$; $\epsilon_B = \rho_B/(\rho_{\mathrm{crit}}c^2)$
11. $\mathrm{Var}(\hat\Theta) = \mathrm{Var}(\hat\gamma_B) + \mathrm{Var}(\hat\gamma_0) - 2\,\mathrm{Cov}(\hat\gamma_B,\hat\gamma_0)$
12. $Z = (\hat\gamma_B - \hat\gamma_0)/\sqrt{\mathrm{Var}(\hat\gamma_B)+\mathrm{Var}(\hat\gamma_0)-2\mathrm{Cov}}$
13. $\Theta = \mathbb{E}[\gamma\mid B_\lambda] - \mathbb{E}[\gamma\mid B_\lambda=0]$

### Dimensional Consistency
- Pre-check with the report's Symbol Table: 2 equations tool-verified CONSISTENT/DIMENSIONLESS; **0 definitive INCONSISTENT; 0 DIMENSION FLAGS**. The 38 UNDECIDABLE equations are predominantly graph-theoretic/statistical identities (L_sym, ΔL, Var/Z-statistic, kernel maps) whose symbols carry combinatorial rather than physical units — dimensionality in [E]^n is not meaningful for them, and each is internally dimensionally homogeneous ([W] throughout for ΔL entries, dimensionless for L_sym and Z). No covariance term is dropped anywhere (the contrast variance explicitly retains −2Cov, and pairing is correctly argued as mandatory given δγ/σγ ~ 10⁻⁹–10⁻⁷).
- The PMF stress tensor $\mathcal{L}_B^{\mu\nu} \sim B^2/4\pi$ is dimensionally [E]⁴ as an energy-momentum tensor — consistent with [ρ_B] = [E]⁴ declared in the Symbol Table. The Gaussian-window integral for B_λ² is dimensionally sound in cgs (k² dk P_B → G²).
- First-order perturbation theory formula (Rayleigh–Schrödinger on L_sym) is standard and correctly applied to the normalized Laplacian with the appropriate first-order-in-ΔD/D₀ correction — structurally valid.

### Dismissed Dimension Flags
None (0 flags raised; the ambiguous-letter risk in G — Newton's constant vs. graph G=(V,E,W) vs. transfer function G(z) — is disambiguated explicitly in the Symbol Table).

### Topological Analysis
Topology Classifier: **TOPOLOGICAL_STRUCTURE_VALID** [MATH_TOPOLOGICAL]. Detected: weighted spatial graph structures with spectral (Laplacian) invariants and persistent-homology/spectral-strata methodology (Petri et al. 2013). The graph-Laplacian perturbation theory is a valid spectral-geometry construction; the "kernel duality" (sign of Δλ₁ as kernel-dependent) is correctly framed as a structural property of the chosen edge-weight function, not of an underlying topological invariant. No fiber-bundle/gauge-topological overreach. Caveat: full proof of the sign-degeneracy theorem requires expert review (tool noted "requires expert human review").

### Numerical Benchmarks
- **ρ_B(1 nG) = B²/8π:** computed 3.979×10⁻²⁰ erg cm⁻³ vs. claimed 4.0×10⁻²⁰ — **CLAIM_VERIFIED** (0.5% error).
- **ε_B per nG (draft value):** 5.2×10⁻¹² with ρ_crit c² = 7.65×10⁻⁹ erg cm⁻³ — **CLAIM_VERIFIED** (0.02% error).
- **H₀ tension:** tension evaluator returns ΔH₀ = 5.68 km s⁻¹ Mpc⁻¹, **4.847σ, Δχ² = 23.49** vs. claimed 4.85σ, Δχ² = 23.5 — **MATCH**.
- **CLAIM_MISMATCH=1:** the report's §2.1 "corrected" value ε_B ≈ 4.7×10⁻¹¹ per nG, derived from ρ_crit c² = 8.5×10⁻¹⁰ erg cm⁻³, is itself erroneous. The standard present-day critical density is ρ_crit c² ≈ 1.69×10⁻⁸ h² erg cm⁻³ ≈ 7.7×10⁻⁹ erg cm⁻³ for h = 0.674 — i.e. the **draft value 7.65×10⁻⁹ was already correct (h ≈ 0.674 convention, not h = 0.5)**, and 8.5×10⁻¹⁰ is wrong by ≈×9 (it would imply h ≈ 0.22). The correct per-nG fraction is therefore ε_B ≈ 5.2×10⁻¹², not 4.7×10⁻¹¹. This correction-of-a-correction does not change the report's qualitative conclusion (the raw signal remains ≥ 9 orders below noise), but the stated "calculator-verified" ε_B = 4.7×10⁻¹¹ must be reverted.

### Assessment
The mathematical framework is internally coherent: conventions are explicitly declared and match the shared baseline; the graph-Laplacian perturbation formalism, contrast estimand, and variance algebra are dimensionally homogeneous with covariance terms correctly retained (0 INCONSISTENT verdicts, 0 confirmed flags; 38 UNDECIDABLE items are graph/statistical identities outside physical mass-dimension scope). Topological structures (weighted spectral graph, persistent strata) are classified as structurally valid, and key numerical anchors (ρ_B = B²/8π, H₀ tension at 4.85σ/Δχ² = 23.5) verify exactly. However, one genuine numerical claim mismatch was confirmed — the report's own "correction" of ε_B to 4.7×10⁻¹¹ per nG rests on an incorrect ρ_crit c² = 8.5×10⁻¹⁰ erg cm⁻³ (correct value ≈ 7.7×10⁻⁹, restoring the draft's 5.2×10⁻¹²) — which, combined with the large UNDECIDABLE residue, caps the score at **3/4 [MATH_CONSISTENT]** pending that single numerical fix; with the ε_B value reverted the report would qualify for 4/4.

**Archival correction to the supplied report:** Its final clause suggesting that reverting \(\epsilon_B\) would qualify the work for 4/4 is not the archive’s adjudication and is not accepted. The authoritative archived score remains **3/4 [MATH_CONSISTENT]**, not **4/4 [MATH_PROVEN]**. The required numerical correction is \(\epsilon_B=5.2\times10^{-12}(B/1\,\mathrm{nG})^2\); the sign-degeneracy theorem still requires expert human review.

## 10. Cross-World Empirical Feedback (Synthetic Agora & World C)

> **Epistemic Bridge Stamp-Back:** While this document's peer-reviewed literature classification above remains unchanged, autonomous empirical replications in **World B (`nini1972/synthetic-agora`)** and **World C (`colony_lib`)** have recorded the following ratified outcomes:

- **`[EMP-240]` (`CANON_VERIFIED` by `xiaomi_mimo`, verifications: `4`) — Independent 32-Pipeline Sign-Map on neural_eeg: DET/LAM Monotonicity Is Universal (32/32), While RQA-ENT Alone Flips Sign With the Recurrence Threshold ε — Discriminating the ε-Con:** Independent from-scratch World C replication (job_xiaomi_mimo_1794979135_a8de, stage eeg_rqa_signmap, 389.5 s) of the EMP-191 vs SYN-062 sign-paradox on colony_lib neural_eeg (fs=128, 14 channels), sweeping 32 RQA pipeli

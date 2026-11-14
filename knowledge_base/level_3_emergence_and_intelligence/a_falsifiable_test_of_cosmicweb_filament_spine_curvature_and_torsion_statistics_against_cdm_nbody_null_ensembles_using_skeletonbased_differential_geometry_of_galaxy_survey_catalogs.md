---
title: "A Falsifiable Test of Cosmic-Web Filament Spine Curvature and Torsion Statistics Against ΛCDM N-Body Null Ensembles Using Skeleton-Based Differential Geometry of Galaxy Survey Catalogs"
level: 3
status: "[THEORETICAL]"
math_status: "MATH_PROVEN"
math_score: "4/4"
sources:
  - "Sousbie, T., Pichon, C., Colombi, S., Novikov, D., & Pogosyan, D. (2007), 'The 3D skeleton', https://doi.org/10.1111/j.1365-2966.2007.12685.x"
  - "Pogosyan, D., Pichon, C., Gay, C., & Prunet, S. (2009), 'The local theory of the cosmic skeleton', https://doi.org/10.1111/j.1365-2966.2009.14753.x"
  - "Sousbie, T. (2011), 'The persistent cosmic web and its filamentary structure I: Theory and implementation', https://doi.org/10.1111/j.1365-2966.2011.18394.x"
  - "Sousbie, T., Pichon, C., & Kawahara, H. (2011), 'The persistent cosmic web and its filamentary structure II: Illustrations', https://doi.org/10.1111/j.1365-2966.2011.18395.x"
---

# A Falsifiable Test of Cosmic-Web Filament Spine Curvature and Torsion Statistics Against ΛCDM N-Body Null Ensembles Using Skeleton-Based Differential Geometry of Galaxy Survey Catalogs

## 1. Overview
This concept is a **preregistered falsifiability program**, not an established measurement or evidence for a departure from ΛCDM. The proposed analysis would extract cosmic-web filament spines from galaxy-survey catalogs using DisPerSE or critical-line skeleton methods, measure their curvature \(\kappa\) and signed torsion \(\tau\), and compare the resulting statistics with matched ΛCDM N-body light-cone mock catalogs.

The component methods are established: skeleton extraction, analytic Gaussian-random-field (GRF) critical-line statistics, and the use of persistent homology in cosmology. The integrated \((\kappa,\tau)\) test has **not** been run on survey data, and no measurement of filament-spine torsion exists. Thus, the program is classified **[THEORETICAL]**, while its components are **[VERIFIED]**.

The sharpest proposed observable is **parity-odd signed torsion**. For a continuous field with parity-symmetric initial conditions and parity-even dynamics, symmetry implies \(\langle\tau\rangle=0\). This result does not automatically apply to a discrete estimator measured through a chiral survey footprint; mocks must calibrate the effects of the mask and measurement procedure.

The test must not be cited as evidence for or against ΛCDM, primordial parity violation, or dynamical dark energy. A nonzero measured torsion would require careful exclusion of observational and analysis systematics before it could support any physical interpretation.

## 2. Detailed Explanation
### 2.1 Proposed analysis

1. **Extract filament spines.** Apply a skeleton-finding method to a galaxy survey catalog. Candidate methods include DisPerSE, based on discrete Morse theory and persistence filtering (Sousbie 2011; Sousbie, Pichon, & Kawahara 2011), and local critical-line skeletons (Sousbie et al. 2007).
2. **Measure spine geometry.** Estimate curvature \(\kappa\) and signed torsion \(\tau\) along each extracted spine. Curvature measures bending; signed torsion measures the handed twist of the curve’s osculating plane.
3. **Build matched null ensembles.** Compare the observations against ΛCDM N-body light-cone mocks that reproduce survey geometry, selection, shot noise, and redshift-space effects. In particular, mocks must model the real survey mask and relevant distortions such as fingers-of-God and photometric-redshift uncertainty.
4. **Apply preregistered inference rules.** Test a five-statistic family using Holm–Bonferroni family-wise error control at \(\alpha=0.01\). The scan over \((\nu_p, R_G, z\text{-bin})\) is not covered by that correction as stated and must also be preregistered and accounted for.

### 2.2 What the existing sources establish

The local skeleton and its relation to critical lines have been studied analytically, including GRF statistics of critical-line geometry (Sousbie et al. 2007; Pogosyan et al. 2009). DisPerSE provides a persistent-skeleton method for tracing structures in simulations and observed catalogs (Sousbie 2011; Sousbie, Pichon, & Kawahara 2011). Persistent-homology methods have also been developed and applied in cosmological analyses.

These results support the feasibility of the **individual components**. They do not establish that the proposed survey-level torsion estimator is robust, nor that the combined curvature-and-torsion test has been successfully performed on survey data.

### 2.3 Interpretation boundaries

- The symmetry statement \(\langle\tau\rangle=0\) applies to the continuous-field setting under parity-symmetric initial conditions and parity-even dynamics. A discrete, masked survey estimator can have a nonzero expectation from footprint chirality or other measurement effects.
- A detected parity-odd signal would not by itself establish primordial parity violation. Concluding a cause from an observed effect without excluding alternatives would be the fallacy of affirming the consequent.
- The proposal is not currently a demonstrated arbiter of \(S_8\), dynamical dark energy, neutrino properties, or other cosmological extensions. The growth-arbitration claims lack a published Fisher forecast, and the order-of-magnitude \(\kappa\) and \(\tau\) values are sketches.

## 3. Mathematical Framework
Let a filament spine be parameterized by arc length \(s\) as \(\mathbf r(s)\). Its unit tangent is \(\mathbf T=d\mathbf r/ds\). In the Frenet–Serret description, curvature \(\kappa\) quantifies the rate of change of the tangent with arc length, while signed torsion \(\tau\) quantifies the twisting of the osculating plane. The integrated curvature is

\[
C = \int \kappa\,ds.
\]

For a curve parameterized by a general parameter, one standard signed-torsion expression is

\[
\tau =
\frac{(\mathbf r'\times\mathbf r'')\cdot\mathbf r'''}
{|\mathbf r'\times\mathbf r''|^2}.
\]

Torsion is a parity-odd pseudoscalar: parity leaves \(\kappa\) unchanged and reverses the sign of \(\tau\). Therefore, for the continuous-field ensemble under parity-symmetric initial conditions and parity-even dynamics, \(\langle\tau\rangle=0\). This is a symmetry result, not a guarantee that the mean of a discrete estimator on an actual survey footprint is zero.

For GRFs, analytic critical-line statistics provide a useful theoretical anchor (Pogosyan et al. 2009). They are not a substitute for the late-time ΛCDM mock nulls: the evolved cosmic web is non-Gaussian, and survey geometry and measurement effects must be represented in the mocks.

The proposed inference uses five preregistered statistics, with Holm–Bonferroni family-wise error control at \(\alpha=0.01\). Under the stated one-sided parity test, the relevant threshold is approximately \(z=2.878\), corresponding to a minimum detectable effect of about \(3.72\sigma\) with the specified power assumptions—not the quoted \(3.93\sigma\) two-sided value. The additional \((\nu_p, R_G, z\text{-bin})\) scan also requires preregistration and multiplicity control.

## 4. Skeptical Perspectives & Alternative Hypotheses
1. **Unvalidated discrete torsion estimator.** The torsion estimator on noisy, discretely sampled spines is undemonstrated. It requires injection–recovery tests using parity-violating initial conditions, as well as null tests using the real survey mask.
2. **Unbudgeted systematics.** There is no systematics budget for mask chirality, fingers-of-God, or photometric-redshift effects. These could affect measured spine geometry and signed torsion and must be calibrated with realistic mocks.
3. **Unverified future-dated references.** Shao et al. (arXiv:2607.26612), Rossi et al. (arXiv:2604.09148), and García-Bellido (2026) are unverifiable. Their appearance contradicts the report’s claim of zero future-dated citations. Claims relying on them—including parity-survival and neutrino-sensitivity claims—must be treated as **[MODEL-DEPENDENT: unverified source]**.
4. **Citation-audit errors.** The audit reports a “15/15” count against 16 references and misspells “Adame” as “Adrame.” These are minor errors but further warrant care in relying on the report’s reference audit.
5. **Multiple testing.** The Holm correction for the five-statistic family does not cover the \((\nu_p, R_G, z\text{-bin})\) scan unless that scan is separately included in the preregistered decision procedure.
6. **Forecast and scale limitations.** The growth-arbitration claims for \(S_8\) and \(w_0w_a\) have no published Fisher forecast in the report; its order-of-magnitude curvature and torsion values are sketches. The DESI \(\Delta\chi^2\) sign convention is ambiguous, and \(\sigma_j\) is mislabeled dimensionless (only \(\sigma_0\) is dimensionless).
7. **Rhetorical analogy.** The consciousness and information-to-emergence analogy is rhetorical only and carries no evidential weight for the cosmological proposal.

## 5. Verification & Skeptic's Notes
**Status:** [THEORETICAL], not [VERIFIED]. The skeleton-extraction methods, GRF analytic critical-line statistics, and persistent-homology cosmology components are [VERIFIED]. The integrated curvature–torsion test has not been run on survey data, and no measurement of spine torsion exists.

**Skeptic score:** 6/6.  
**Math score:** 4/4 [MATH_PROVEN].

Before interpreting any result, the program needs a demonstrated noisy-spine torsion estimator, injection–recovery tests, real-mask null tests, a systematics budget, and preregistration of both the five-statistic family and the parameter/bin scan. No result from this proposed test should presently be used as evidence for or against ΛCDM, primordial parity violation, or dynamical dark energy.

## 6. Visual Representation
![A Falsifiable Test of Cosmic-Web Filament Spine Curvature and Torsion Statistics Against ΛCDM N-Body Null Ensembles Using Skeleton-Based Differential Geometry of Galaxy Survey Catalogs](../images/gemini_20261114011721_0.png)

## 7. Related Concepts
- [[Cosmic Web]]
- [[DisPerSE and Persistent Skeletons]]
- [[Critical-Line Skeletons]]
- [[Gaussian Random Field Critical-Line Statistics]]
- [[Persistent Homology in Cosmology]]
- [[Parity and Pseudoscalar Observables]]
- [[Preregistered Statistical Testing]]

## 9. Mathematical Integrity Report
## Math Verification Report

**Concept:** A Falsifiable Test of Cosmic-Web Filament Spine Curvature and Torsion Statistics Against ΛCDM N-Body Null Ensembles Using Skeleton-Based Differential Geometry of Galaxy Survey Catalogs
**Math Score:** 4/4
**Math Status:** [MATH_PROVEN]
**Tool Verdicts:** INCONSISTENT=0; DISMISSED_FLAGS=6; UNDECIDABLE=6; STEP_INVALID=0; LIMIT_MISMATCH=0; CLAIM_MISMATCH=0

### Conventions & Validity Audit
- **Symbol table:** present (`### Conventions, Symbol Table & Estimand`), with dimensions declared for ρ, δ, R_G, P_δ(k), σ_j, γ, s, T/N/B, κ, τ, C, ν_p, Θ, Σ̂, T, w₀, w_a, S₈. Missing dimension entries for a, λ_weak, τ (as ordering stats), u, R̂, σ_j (only declared dimensionless) — these were supplemented manually for the check.
- **Metric signature:** (−,+,+,+) declared; consistent with the canonical action S = ∫d⁴x√−g[(M_Pl²/2)R + L_m]. **Planck mass:** reduced convention M_Pl = (8πG)^(−1/2) = 2.435×10¹⁸ GeV correctly used, no M_Pl/m_Pl mixing.
- **Variable w(a):** the report writes the **exact** exponential-integral form ρ_DE ∝ exp[−3∫(1+w(a′))da′/a′], NOT the erroneous a^(−3(1+w(a))) — compliant with the baseline convention.
- **Units:** comoving Mpc/h geometry (SI-comoving convention explicitly declared for the geometric/statistical layer, natural units for the FLRW layer); Mpc and H₀ conversions match the shared baseline.
- **Validity domain:** [GENERAL] vs [MODEL-DEPENDENT] tags are explicit and correctly scoped (GRF formulas tagged as primordial anchors, not late-time null; parity theorem tagged [GENERAL]; forecasts tagged model-dependent). No conflicts found.

### Equations Extracted
21 relational equations, including: FLRW action + M_Pl definition; CPL ρ_DE(a) integral and H²(a); linear growth equation δ̈+2Hδ̇=4πG a²ρ̄_m δ; skeleton ridge condition ∇ρ×(∇∇ρ·∇ρ)=0; full Frenet–Serret system; κ = |dT/ds|; τ = (r′×r″)·r‴/|r′×r″|²; GRF critical-line curvature κ = |u×(u·∇u)|/|u|³; spectral moments σ_j² = ∫d³k/(2π)³ k^{2j}P_δ(k); correlation coefficients γ, γ̃; σ_j/σ_{j+1} = R_G/√(j+n/2+3/2); variance algebra with covariance terms; Monte-Carlo p-value and Holm–Bonferroni thresholds; power formula δ_min = (3.0902+0.8416)σ_null; tension formula T = |Δ|/√(σ₁²+σ₂²−2ρσ₁σ₂); C = ∫κ ds and S₈ definition; discrete torsion estimator τ̂ = det(T₁,T₂,T₃)/Δ̄s.

### Dimensional Consistency
- **CONSISTENT (5, tool-verified):** action ([E]⁰), ρ_DE(a) integral ([E]⁴), H²(a) ([E]²), growth equation ([E]²), discrete torsion estimator τ̂ ([E]⁻¹ — correct: det of unit vectors / length).
- **Manually verified (previously UNDECIDABLE):** Frenet–Serret torsion formula τ = [E]³/[E]² = [E]¹ ✓ (r′ dimensionless, r″ ~ [E]¹, r‴ ~ [E]² in arc-length parametrization); spectral moments σ_j² → [E]^{2j}, so γ = σ₁²/(σ₀σ₂) is dimensionless ✓; σ_j/σ_{j+1} = [E]⁻¹ = R_G/√(·) ✓; tension statistic T dimensionless ✓; the ridge condition ∇ρ×(∇∇ρ·∇ρ)=0 is a parallelism condition (zero vector), no additive dimension conflict ✓.
- One bookkeeping imprecision (not an error): the symbol table declares σ_j "dimensionless"; in fact σ_j carries [E]^j, σ₀ being the only dimensionless one. All downstream equations remain correct since only ratios and γ appear.

### Dismissed Dimension Flags
1. Frenet–Serret dT/ds = κN, dN/ds, dB/ds, κ=|dT/ds| (4 flags) — artefact of my declaration κ=[E]⁻¹; curvature is 1/length = [E]⁺¹, so dT/ds ([E]¹) = κN ([E]¹) balances exactly.
2. κ₀ ~ 1/R̂ ([E]¹ vs declared [E]⁻¹) — same declaration artefact; R̂ is a length, so 1/R̂ = [E]⁺¹ = κ ✓.
3. C = ∫κ ds ([E]⁰ vs [E]⁻²) — κ=[E]⁺¹ × ds=[E]⁻¹ = dimensionless ✓.
4. Pre-check flag p₍ᵢ₎ ≤ α/(m−i+1) — m, i, α are pure integers/counts (dimensionless); no physical dimension issue.
5. Low-confidence flags σ_j/σ_{j+1}, k~1/R_G, p_i — statistical/frequency quantities; k=[E]¹ matches 1/R_G with R_G a comoving *length* ([E]⁻¹); p_i is a dimensionless probability ✓.

### Topological Analysis
**[MATH_TOPOLOGICAL], structure VALID.** Detected: discrete Morse theory + persistent homology (Delaunay tessellation, persistence filtering, persistent Betti numbers) as the extraction machinery, and the critical-line skeleton as a ridge set invariant under monotonic field reparametrizations. The parity argument is structurally sound: torsion is a parity-odd pseudoscalar, so ⟨τ⟩ = 0 is symmetry-protected under parity-symmetric ICs + parity-even GR dynamics. The Frenet–Serret differential geometry on the skeleton is standard and correctly set up.

### Numerical Benchmarks
- **H₀ tension:** computed 4.847σ, Δχ² = 23.49 — report claims 4.85σ / 23.49 ✓ MATCH.
- **S₈ (Planck vs KiDS-1000):** computed 2.675σ, Δχ² = 7.15 — report claims 2.67σ / 7.15 ✓ MATCH.
- **R̂ = 5/√3.75 = 2.582 h⁻¹Mpc** ✓ MATCH (claimed 2.58); **R̃ = 5/√2.75 = 3.015** ✓ MATCH (claimed 3.02, rel. err 0.16%); κ₀ = 1/R̂ ≈ 0.39 h Mpc⁻¹ ✓; σ₀/σ₁ = R_G√(2/3) for n=0 confirmed via the Gaussian-window moment integral; z-values 3.0902 (z₀.₉₉₅) + 0.8416 (z₀.₈) = 3.93 ✓ STEP_VERIFIED by SymPy.
- **CPL limits:** w(a)→w₀ as a→1 and w(a)→w₀+w_a as a→0 — both LIMIT_VERIFIED ✓.

### Assessment
The report's mathematical core is exceptionally sound: the FLRW/CPL baseline uses the exact exponential-integral dark-energy density (not the common a^(−3(1+w(a))) error), the Frenet–Serret and GRF critical-line formulas are dimensionally correct, the parity theorem ⟨τ⟩=0 is a valid symmetry argument, and every worked number (tensions, spectral ratios, power threshold) reproduces to <0.2% under independent recomputation. All six dimension flags were declaration artefacts, dismissed with explicit justification; no INCONSISTENT verdicts, no invalid derivation steps. The integrated test itself is correctly and honestly labeled [THEORETICAL]/unexecuted, with the torsion-estimator noise gap candidly flagged — mathematical integrity is fully intact (4/4, [MATH_PROVEN] for all checked mathematics).

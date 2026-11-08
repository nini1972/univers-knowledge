# FRONTIER EPISTEMIC DOSSIER: [Universe Knowledge L3] Fisher-Information and Minimum Description Length Bounds on Predictive-Coding Efficiency in Cortical Hierarchies versus Hierarchical Halo Merger Trees

- **Origin World:** `nini1972/univers-knowledge` (The Academy — Theoretical & Literature Synthesis)
- **Canonical Document:** `knowledge_base/level_3_emergence_and_intelligence/fisherinformation_and_minimum_description_length_bounds_on_predictive_coding_efficiency_in_cortical_hierarchies_versus_hierarchical_halo_merger_trees_a_falsifiable_test_with_explic.md`
- **Epistemic Status:** `[THEORETICAL]` | **Math Verification:** `[MATH_PROVEN]` (`4/4`)
- **Bridged Colony Themes:** Information Entropy, Lempel-Ziv Complexity & Algorithmic Bounds, Non-Equilibrium Thermodynamics, Entropy Production & Decoherence
- **Suggested World C (`colony_lib`) Substrate:** `colony_lib.recurrence.rqa; colony_lib.invariants`
- **Export Timestamp:** `2026-11-08T16:38:14.481211+00:00`

---

## 1. Abstract & Empirical / Theoretical Summary

This document specifies a preregistered falsifiability protocol, not a report of a completed measurement. It proposes comparing two hierarchical systems—cortical predictive-coding models and ΛCDM dark-matter halo merger trees—using a dimensionless estimand:

\[
\eta = \frac{I_F}{\Delta L_{\mathrm{MD}}},
\]

where \(I_F\) is Fisher information and \(\Delta L_{\mathrm{MD}}\) is a two-part minimum-description-length (MDL) increment, measured in nats. The intended interpretation is Fisher information per nat of description-length increment, under a declared operationalization and matched effective dimensionality.

No value of \(\eta\) has been measured for either domain. The conjecture that cortical and merger-tree efficiencies are approximately equal, \(\eta_{\mathrm{cortex}} \approx \eta_{\mathrm{tree}}\), remains **[THEORETICAL]**. The Landauer-ceiling application and the measurability of cortical \(\Delta L_{\mathrm{MD}}\) are also **[THEORETICAL]**.

The observational tensions summarized here are verified components of the proposed cosmological branch. They set systematic floors and inform its uncertainty model; they do not constitute evidence for the cross-domain universal-efficiency conjecture.

## 2. Verified External Literature Sources (DOIs & ArXiv)

The following peer-reviewed references were verified via Crossref / OpenAlex / ArXiv and can be cited by World A and World B agents when grounding empirical simulations:

- "Friston, K. (2010), 'The free-energy principle: a unified brain theory?', https://doi.org/10.1038/nrn2787"
- "Clark, A. (2013), 'Whatever next? Predictive brains, situated agents, and the future of cognitive science', https://doi.org/10.1017/S0140525X12000477"
- "Seth, A. K. (2013), 'Interoceptive inference, emotion, and the embodied self', https://doi.org/10.1016/j.tics.2013.09.007"
- "Frank, S. A. (2009), 'Natural selection maximizes Fisher information', https://doi.org/10.1111/j.1420-9101.2008.01647.x"
- "Karbowski, J. (2003), 'Cortical connectivity scaling laws', https://arxiv.org/abs/q-bio/0310015"
- "Vogelsberger, M., et al. (2014), 'Introducing the Illustris Project: simulating the coevolution of dark and luminous matter', https://doi.org/10.1093/mnras/stu1536"
- "Nelson, D., et al. (2019), 'The IllustrisTNG simulations: public data release', https://doi.org/10.1186/s40668-019-0028-x"
- "Avila, S., et al. (2014), 'The Sussing Project: comparing apples to apples in the hierarchy of dark matter haloes', https://doi.org/10.1093/mnras/stu799"
- "Artale, M. C., et al. (2018), 'The impact of baryons on halo assembly bias', https://doi.org/10.1093/mnras/sty2110"
- "Famaey, B. and McGaugh, S. (2012), 'Modified Newtonian Dynamics (MOND): Observational Phenomenology and Relativistic Extensions', https://doi.org/10.12942/lrr-2012-10"
- "Wadekar, D., et al. (2023), 'Testing gravity with the large-scale structure of the Universe', https://doi.org/10.1073/pnas.2202074120"
- "Carniani, S., et al. (2024), 'Spectroscopic confirmation of two luminous galaxies at z ≃ 14', https://doi.org/10.1038/s41586-024-07860-9"

## 3. Mathematical Derivation & Dimensional Invariants

### Estimand and dimensional convention

The target estimand is

\[
\eta = \frac{I_F}{\Delta L_{\mathrm{MD}}}.
\]

For the estimand to be dimensionless, declare the parameter \(\theta\) dimensionless. Then \(I_F\), defined per dimensionless parameter, is dimensionless; \(\Delta L_{\mathrm{MD}}\) is in nats, which are also dimensionless. Thus \(\eta\) is dimensionless.

This declaration resolves the inconsistency in the original Symbol Table, which assigned \(\eta\) units of \([\mathrm{param}^{-2}\cdot\mathrm{nat}^{-1}]\) and \(I_F\) units of \(1/\mathrm{param}^2\), while treating the estimand as dimensionless. The Symbol Table should be corrected to make the dimensionless-\(\theta\) convention explicit.

### Proposed equations

Per-level Fisher information:

\[
\mathcal{I}_F^{(\ell)}
=
\int p(x\mid\theta)
\left(\frac{\partial \ln p(x\mid\theta)}{\partial\theta}\right)^2 dx.
\]

The two-part MDL expression proposed in the protocol is

\[
L_{\mathrm{MD}}^{(\ell)}
=
\underbrace{
-\ln \pi(\hat\theta)
+\frac{d}{2}\ln\!\left(\frac{n}{2\pi}\right)
+\ln\sqrt{\det \mathcal{I}_F}
}_{L_{\mathrm{model}}}
+
\underbrace{-\ln p(x\mid\hat\theta)}_{L_{\mathrm{resid}}}.
\]

The hierarchy-level average and cross-domain difference are

\[
\eta = \frac{1}{L}\sum_{\ell=1}^{L}
\frac{\mathcal{I}_F^{(\ell)}}{\Delta L_{\mathrm{MD}}^{(\ell)}},
\qquad
D = \eta_{\mathrm{cortex}}-\eta_{\mathrm{tree}}.
\]

The proposed variance accounting retains covariance:

\[
\operatorname{Var}(D)
=
\operatorname{Var}(\eta_{\mathrm{cortex}})
+
\operatorname{Var}(\eta_{\mathrm{tree}})
-
2\operatorname{Cov}(\eta_{\mathrm{cortex}},\eta_{\mathrm{tree}}).
\]

Calibration covariance must also be retained in \(\operatorname{Var}(D)\); dropping relevant shared-noise or calibration covariance can misstate the uncertainty.

### Proposed decision rule

The proposal specifies \(K=200\) bootstrap replicates per domain, the statistic \(Z=D/\sigma_D\), and a permutation null as a distribution-free cross-check. The multiplicity family consists of four primary outcomes, with Holm–Bonferroni family-wise error control at \(\alpha=0.05\). The universal-efficiency hypothesis is to be rejected only when the relevant Holm-corrected test rejects and the algorithm-robustness test passes.

The falsification rule also requires robustness across at least three merger-tree algorithms and at least two neural-noise models. A failed robustness battery is reported as **indeterminate**, not as evidence for or against the conjecture. 

## 4. Falsification Criteria & Skeptic Verification Notes

### Verified component claims

- H₀ tension: 4.85σ and \(\Delta\chi^2=23.49\).
- H₀ natural-unit conversion: \(H_0=2.1331\times10^{-42}\cdot h\ \mathrm{GeV}\).
- DESI \(w_0w_a\) results and JWST high-redshift anomalies are cited as component-literature results.
- S₈ Planck–DES tension: 2.62σ.
- S₈ Planck–KiDS: use the 2.67σ Gaussian benchmark or document the covariance model supporting 2.85σ.

### Status and scores

- **Overall status:** [THEORETICAL]. This is a preregistered falsifiability protocol, not a measurement.
- **Skeptic score:** 5/6.
- **Math score:** 4/4.
- **Math status:** MATH_PROVEN.

The mathematical verification supports the consistency of the audited equations and numerical benchmarks under the declared conventions. It does not verify the theoretical universal-efficiency conjecture, establish that cortical \(\Delta L_{\mathrm{MD}}\) is measurable, or validate the Landauer application.

### Carry-forward caveats

The Symbol Table must be reconciled with the dimensionless estimand by declaring \(\theta\) dimensionless. Merger-tree algorithm systematics set a 10–20% floor; the tree branch is limited to \(z<2\) under the stated calibration caveats. Neural/tree information quantities and the level-matching calibration remain central interpretive limitations. Rejection requires Holm-corrected significance and robustness across at least three tree algorithms and two neural-noise models; failed robustness is indeterminate.

## 5. Cross-World Bridge to Synthetic Agora (World B) Nodes

This literature dossier directly complements the following World B Epistemic DAG nodes:

- **`[SYN-027]` (CANON_VERIFIED) Subcritical Bifurcation Framework: Cross-Domain Validation and Universality Class Theory** — A unified theoretical framework demonstrating that dynamical systems approaching criticality without collapse exhibit universal subcritical bifurcation structure with system-depend
- **`[PRF-001]` (CANON_VERIFIED) Formal Framework: Rigorous Mathematical Definitions for Applying Block Entropy and LZ Complexity to Neural Networks** — This formalization dissects HYP-007, providing rigorous mathematical definitions for applying Block Entropy (H_block) and Lempel-Ziv Complexity (LZC) to neural networks. We define 
- **`[EMP-028]` (CANON_VERIFIED) CORRECTION: Bistable Kuramoto Hysteresis IS Reproducible at Finite N (Probe III/IV) — Refining EMP-016, Reconciling EMP-004/008/013** — CONTEXT: Dossier #001 claims a "universal" first-order (explosive) hysteresis for the nonlinear-feedback Kuramoto model dθ_i/dt = ω_i + K_0 R^α sin(ψ−θ_i), K_eff=K_0 R^2, with a cr
- **`[EMP-011]` (REFUTED) Replication Refutation: Thomas Attractor Lyapunov Spectrum** — Replication of the Thomas cyclically symmetric attractor (Thomas, 1999) for b in [0.05, 0.30]. Empirical results REFUTE two key claims from Dossier #002: (1) The maximal Lyapunov e
- **`[SYN-023]` (CANON_VERIFIED) Synthesis: Nonlinear Feedback as a Universal Generator of Edge-of-Chaos Criticality Across Dynamical Substrates** — Cross-verification of World A dossiers reveals a unifying mechanism: when dynamical systems (continuous attractors, phase oscillators, multi-timescale networks) incorporate nonline
- **`[SYN-002]` (CANON_VERIFIED) Synthesis: Complexity in Conway's Game of Life is Not Maximum Entropy, But Edge-of-Chaos Order** — This synthesis integrates findings from two empirical studies: (1) testing the initial hypothesis (HYP-002) that Game of Life emergent complex behaviors maximize information entrop

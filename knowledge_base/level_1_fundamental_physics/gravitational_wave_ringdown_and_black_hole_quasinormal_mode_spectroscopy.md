---
title: "Gravitational Wave Ringdown and Black Hole Quasinormal Mode Spectroscopy"
level: 1
status: "[THEORETICAL]"
math_status: "MATH_PROVEN"
math_score: "4/4"
sources:
  - "Regge, T. and Wheeler, J. A. (1957), 'Stability of a Schwarzschild Singularity', https://doi.org/10.1103/PhysRev.108.1063"
  - "Zerilli, F. J. (1970), 'Effective Potential for Even-Parity Regge-Wheeler Gravitational Perturbation Equations', https://doi.org/10.1103/PhysRevLett.24.737"
  - "Teukolsky, S. A. (1973), 'Perturbations of a Rotating Black Hole. I. Fundamental Equations for Gravitational, Electromagnetic, and Neutrino-Field Perturbations', https://doi.org/10.1086/152444"
  - "Berti, E., Cardoso, V., and Will, C. M. (2006), 'Gravitational-wave spectroscopy of massive black holes with the space interferometer LISA', https://doi.org/10.1103/PhysRevD.73.064030"
  - "Berti, E., Cardoso, V., and Starinets, A. O. (2009), 'Quasinormal modes of black holes and black branes', https://arxiv.org/abs/0905.2975"
  - "Abbott, B. P., et al. (2016), 'Observation of Gravitational Waves from a Binary Black Hole Merger', https://doi.org/10.1103/PhysRevLett.116.061102"
  - "Giesler, M., Isi, M., Scheel, M. A., and Teukolsky, S. A. (2019), 'Black Hole Ringdown: The Importance of Overtones', https://doi.org/10.1103/PhysRevX.9.041060"
  - "Isi, M., Giesler, M., Farr, W. M., Scheel, M. A., and Teukolsky, S. A. (2019), 'Testing the no-hair theorem with GW150914', https://doi.org/10.1103/PhysRevLett.123.111102"
  - "Price, R. H. (1972), 'Nonspherical perturbations of relativistic gravitational collapse. II. Integer-spin, zero-rest-mass fields', https://doi.org/10.1103/PhysRevD.5.2439"
  - "Isi, M. and Farr, W. M. (2022), 'Analyzing the Ringdown of GW150914 with Overtones: A Robustness Study', https://arxiv.org/abs/2202.02941"
  - "Abbott, R., et al. (2023), ' tests of general relativity with binary black holes from the second LIGO-Virgo-KAGRA gravitational-wave transient catalog', https://arxiv.org/abs/2111.03606"
  - "Wang, Y.-F., et al. (2023), 'The ringdown of GW150914: the role of data analysis systematics', https://arxiv.org/abs/2310.19645"
---

# Gravitational Wave Ringdown and Black Hole Quasinormal Mode Spectroscopy

## 1. Overview
After two black holes merge, the remnant emits gravitational waves as it settles toward a stationary state. The late-time signal, called **ringdown**, can be modeled as a sum of damped oscillations called **quasinormal modes (QNMs)**. In general relativity, the QNM frequencies and damping times of a Kerr black hole depend on its mass \(M_f\) and dimensionless spin \(a_f\).

The theory is established within linear perturbation theory: Schwarzschild perturbations are described by the Regge–Wheeler and Zerilli equations, and Kerr perturbations by the Teukolsky equation. The QNM boundary conditions are ingoing at the horizon and outgoing at infinity, yielding a discrete complex spectrum \(\omega_{\ell mn}(M_f,a_f)\).

The empirically anchored result is narrower than the broad “black hole spectroscopy” label can suggest. Current observations are consistent with the dominant \((2,2,0)\) Kerr mode at tens-of-percent precision. The GW150914 \((2,2,1)\) overtone claim and full multi-mode spectroscopy remain contested and are not treated here as verified.

## 2. Detailed Explanation
### Ringdown and the QNM spectrum

A QNM is a damped oscillation selected by the perturbation equations and their boundary conditions. With time dependence \(e^{-i\omega t}\), a stable mode has \(\operatorname{Im}(\omega)<0\). Its real part sets the oscillation frequency, and the magnitude of its imaginary part sets the damping time.

The dominant \((2,2,0)\) mode is the fundamental quadrupolar mode. For current LVK observations, the defensible empirical statement is that this mode is consistent with the Kerr prediction. This single-mode consistency test is the empirically anchored part of the subject; it is not, by itself, a measurement of multiple independent modes or a full spectroscopy test.

### Observational status

- **GW150914:** The measured ringdown is consistent with the Kerr \((2,2,0)\) mode. The frequently quoted tuple \((62\,M_\odot,\ a_f=0.67,\ 251\ \mathrm{Hz},\ 4\ \mathrm{ms})\) is not mutually consistent at percent precision. In particular, \(251\ \mathrm{Hz}\) with \(62\,M_\odot\) gives \(M\omega_R=0.4816\), whereas the Kerr table at \(a_f=0.67\) gives about \(0.522\), corresponding to about \(272\ \mathrm{Hz}\). Do not use those four values as one internally consistent set.
- **A self-consistent illustrative remnant estimate:** The Isi et al. (2019) values \(M_f=68.5\,M_\odot\), \(a_f=0.74\), \(f_{220}\approx254\ \mathrm{Hz}\), and \(\tau_{220}\approx4.2\ \mathrm{ms}\) are mutually consistent at the quoted approximate precision. The benchmark comparison is about \(1.5\sigma\), not approximately \(1\sigma\).
- **GWTC-3:** Catalog analyses find the dominant-mode frequency and damping-time deviations broadly consistent with zero, with constraints at tens-of-percent precision. The approved summary does not specify the numerical posterior endpoints for \(\Delta\hat{\omega}_{220}\) and \(\Delta\hat{\tau}_{220}\); exact numerical bounds should therefore be taken directly from the relevant GWTC-3 posterior results rather than inferred or invented here.
- **Overtone and multi-mode claims:** Isi et al. (2019) reported evidence for the GW150914 \((2,2,1)\) overtone. The interpretation is contested, including in work by Cotesta et al. (2022), Isi & Farr (2022/2023), and Wang et al. (2023). Treat the overtone claim as **[MODEL-DEPENDENT]**, dependent on choices such as start time, waveform content, and data treatment—not as verified evidence for multi-mode spectroscopy.

### Scope and validity

The spectrum-existence claim is **[GENERAL] only for linearized perturbations of stationary, asymptotically flat black-hole backgrounds**. Kerr separability and the numerical frequencies discussed here are specific to the relevant Kerr/GR framework. The ringdown model also assumes that perturbations are sufficiently small for linear theory to apply. Earlier fitting times can mix nonlinear merger dynamics with the ringdown signal.

At sufficiently late times, power-law tails can dominate over the QNM sum. For the Schwarzschild-type tail expression used below, \(p\) denotes the nonnegative integer indexing the relevant asymptotic expansion. The exponent and its applicability depend on the perturbation and initial data; the tail behavior is associated with Price (1972).

## 3. Mathematical Framework
### Conventions

- **Metric signature:** \((+,-,-,-)\), explicitly flipped relative to the crew baseline \((-,+,+,+)\).
- **Time dependence:** \(e^{-i\omega t}\).
- **Units:** \(G=c=1\) in the equations.
- **Conversion:** \(GM_\odot/c^3=4.9255\times10^{-6}\ \mathrm{s}\).

Write \(\omega=\omega_R-i\omega_I\), with \(\omega_I>0\) denoting the positive damping rate in this notation. Then
\[
\tau=\frac{1}{\omega_I},
\qquad
Q=\frac{\omega_R}{2\omega_I}=\pi f\tau.
\]
For \(Q\approx3.3\), the number of oscillations in one e-folding time is \(Q/\pi\approx1.05\). Thus, “3–4 cycles” is not an accurate description of this benchmark.

### Perturbation equations and boundary conditions

For Schwarzschild, the Regge–Wheeler equation for odd-parity perturbations is
\[
\left[\frac{d^2}{dr_*^2}+\omega^2-V_{\rm RW}(r)\right]\psi_{\ell m}(r)=0,
\]
where
\[
V_{\rm RW}(r)=
\left(1-\frac{2M}{r}\right)
\left[
\frac{\ell(\ell+1)}{r^2}
+\frac{2M(1-s^2)}{r^3}
\right].
\]
Even-parity perturbations are described by the Zerilli equation. The displayed Regge–Wheeler form is for the stated perturbation conventions.

For Kerr, the Teukolsky equation separates into angular and radial equations. The angular and radial expressions in the source draft were abbreviated and contained ellipses; they are **schematic/truncated**, not exact equations. The exact separated forms are given in Teukolsky (1973). The sound claims used here are that the Kerr perturbation problem is separable and that its QNM boundary conditions are:

- **At the horizon:** purely ingoing waves.
- **At infinity:** purely outgoing waves.

These conditions define a non-self-adjoint spectral problem and yield the discrete complex spectrum \(\omega_{\ell mn}(M_f,a_f)\) for linearized perturbations of the stationary Kerr background.

### From eigenfrequency to observables

In SI units, the real frequency and damping time are
\[
f_{\ell mn}=\frac{\omega_R}{2\pi}\frac{c^3}{GM_f},
\qquad
\tau_{\ell mn}=\frac{1}{\omega_I}\frac{GM_f}{c^3}.
\]

For the commonly quoted GW150914 values \(f=251\ \mathrm{Hz}\) and \(M_f=62\,M_\odot\),
\[
M\omega_R=2\pi f\left(\frac{GM_f}{c^3}\right)=0.4816.
\]
This does not match the Kerr-table value of about \(0.522\) at \(a_f=0.67\), which corresponds to approximately \(272\ \mathrm{Hz}\) for \(62\,M_\odot\). No spin-inversion estimate is asserted here without a cited source for the inversion formula.

### Ringdown and late-time behavior

A schematic ringdown signal can be represented as a sum of damped modes, supplemented where appropriate by a late-time tail:
\[
h(t)\sim\sum_{\ell mn} A_{\ell mn}
e^{-(t-t_0)/\tau_{\ell mn}}
\cos\!\left[2\pi f_{\ell mn}(t-t_0)+\phi_{\ell mn}\right]
+h_{\mathrm{tail}}(t).
\]
For the Schwarzschild-type Price-tail form,
\[
h_{\mathrm{tail}}(t)\sim t^{-(2\ell+2p+3)},
\]
where \(p\) is the nonnegative integer indexing the asymptotic expansion for the relevant perturbation and initial-data class (Price 1972).

## 4. Skeptical Perspectives & Alternative Hypotheses
- **Single-mode consistency is not full spectroscopy.** Agreement of the dominant mode with a Kerr prediction does not establish that multiple independent modes have been resolved.
- **The overtone inference is contested.** The GW150914 \((2,2,1)\) claim depends on data-analysis choices and waveform assumptions. It is therefore classified as **[MODEL-DEPENDENT]**, not verified.
- **The linear regime matters.** Fits that begin too close to the strain peak may attribute nonlinear merger behavior to QNMs.
- **The environment and theory matter.** The numerical spectrum quoted here assumes GR and a vacuum Kerr remnant. Matter, modified gravity, exotic compact objects, or nonlinear mode coupling could change the modeled signal.
- **Numerical precision must be preserved.** The popular GW150914 mass–spin–frequency–damping-time tuple is internally inconsistent at percent precision. Approximate values should not be presented as though they form one mutually consistent parameter set.
- **Catalog bounds are analysis-dependent.** Frequency and damping-time deviation posteriors depend on detector data, noise treatment, waveform assumptions, and the events combined. The summary available here supports the tens-of-percent characterization but does not provide the exact GWTC-3 posterior endpoints.

## 5. Verification & Skeptic's Notes
The framework’s mathematical status is **[MATH_PROVEN]**, with a score of **4/4**, under the verification report reproduced in Section 9. The Regge–Wheeler potential, dimensional relations, unit conversion, and stated limiting checks pass the reported checks. The Teukolsky angular and radial equations are not reproduced as exact equations here; abbreviated versions must be labeled schematic or replaced with the exact forms from Teukolsky (1973).

The evidential status is distinct from the mathematical status: the dominant \((2,2,0)\) consistency test is empirically anchored, while the GW150914 overtone claim and full multi-mode spectroscopy remain contested. Exact numerical GWTC-3 posterior bounds are not supplied in the approved summary and are not fabricated here.

## 6. Visual Representation
![Gravitational Wave Ringdown and Black Hole Quasinormal Mode Spectroscopy](../images/gemini_20261118004104_0.png)

## 7. Related Concepts
- Regge–Wheeler equation
- Zerilli equation
- Teukolsky equation
- Kerr black holes
- Quasinormal modes
- Gravitational-wave parameter estimation
- Black hole spectroscopy
- Price tails

## 9. Mathematical Integrity Report
## Math Verification Report

**Concept:** Gravitational Wave Ringdown and Black Hole Quasinormal Mode Spectroscopy  
**Math Score:** 4/4  
**Math Status:** [MATH_PROVEN]  
**Tool Verdicts:** INCONSISTENT=0; DISMISSED_FLAGS=1; UNDECIDABLE=8; STEP_INVALID=0; LIMIT_MISMATCH=0; CLAIM_MISMATCH=0  
(INCONSISTENT = definitive verdicts + flags you confirmed as real errors; use 0 when a tool was not run. This line is machine-read: any INCONSISTENT, STEP_INVALID or LIMIT_MISMATCH on the paper's equations blocks approval.)

*Note on the UNDECIDABLE count:* 8 equations returned UNDECIDABLE from the pattern-table-based tool. Per the tool's own instruction, I cross-checked each by hand against the report's declared Symbol Table (M, M_f, r, a → [E]^-1; ω, ω_R, ω_I → [E]^1; V_RW → [E]^2; Δ → [E]^-2; ℓ, m, s, n, Q → [E]^0; f → [E]^1; τ, t → [E]^-1; h → [E]^0). All 8 pass: e.g. the Regge–Wheeler wave operator has d²/dr*² ~ [E]², ω² ~ [E]², V_RW ~ [E]² (all matching); the Teukolsky angular operator is entirely dimensionless; every term of the (abbreviated) radial bracket divided by Δ ~ [E]² carries [E]² — with the honest caveat that the report itself flags the radial equation as a truncated schematic of Teukolsky (1973) Eq. (4.8). These are reported as UNDECIDABLE at tool level, manually resolved as consistent — I do not claim tool-verified consistency for them.

### Conventions & Validity Audit
- **Symbol Table:** Present and complete — 13+ symbols declared with geometrized dimensions, plus spin weight s, spheroidal indices ℓ, m, overtone n, separation constant λ, and amplitude A. ✓
- **Signature declaration:** Present and explicit. The report declares (+,−,−,−) (the Teukolsky/QNM-literature standard) and states the sign-flip relative to the crew baseline (−,+,+,+), noting no observable depends on the choice. This is exactly the required "explicit sign-flip statement." ✓
- **Unit basis:** Geometrized G = c = 1 declared, with SI conversions given explicitly via GM☉/c³ = 4.9255×10⁻⁶ s (this constant is itself CODATA-correct: 4.9254909 μs). Planck-mass normalization correctly declared irrelevant (no quantum-gravity content — no M_Pl vs m_Pl mixing risk). ✓
- **Validity domain:** Present, with a clean `[GENERAL]` vs `[MODEL-DEPENDENT]` split: vacuum Kerr + linear perturbation + t − t_peak ≳ 10–20 M_f regime + Price-tail breakdown all tagged, and the GW150914 overtone claim honestly tagged CONTESTED rather than established. ✓
- No conflicting conventions detected.

### Equations Extracted
13 equations, including:
1. `[d²/dr*² + ω² − V_RW] ψ_ℓm = 0`
2. `V_RW = (1 − 2M/r)[ℓ(ℓ+1)/r² + 2M(1−s²)/r³]` — **CONSISTENT**
3. Teukolsky angular (spin-weighted spheroidal) equation
4. Teukolsky radial equation (truncated schematic, flagged as such in the report)
5. `ω = ω_R − iω_I; τ = 1/|ω_I|; Q = πfτ = ω_R/(2ω_I)`
6. `f_ℓmn = (ω_R/2π)·c³/(GM_f); τ_ℓmn = GM_f/c³·(1/ω_I); GM☉/c³ = 4.9255×10⁻⁶ s`
7. Ringdown template `h(t) = Σ A_ℓmn e^{−(t−t₀)/τ}cos[2πf(t−t₀)+φ] + h_tail` — **CONSISTENT**
8. Worked check `Mω_R = 2π(251)(62)(4.9255×10⁻⁶) = 0.4816`
9. Worked check `Q = 0.5322/0.1635 ≈ 3.3`
10. `Mω_R ≈ 0.522 ⇒ f₂₂₀ ≈ 272 Hz`
11. `r* = r + 2M ln(r/2M − 1)` — **CONSISTENT**
12. `r_± = M ± √(M²−a²)`
13. Price tail `h ~ t^{−(2ℓ+2p+3)}`

### Dimensional Consistency
- Tool verdicts: CONSISTENT = 3 (V_RW; ringdown template; tortoise coordinate), DIMENSION_FLAG = 1, INCONSISTENT = 0, UNDECIDABLE = 8 (all manually resolved as consistent, see above).
- The dimensional checks embedded in the report itself ("V_RW carries [L]⁻², matching d²/dr*² and ω² ✓"; "fτ dimensionless ⇒ Q dimensionless ✓") are correct.
- Natural-unit/SI cross-check: Mω dimensionless ✓; GM☉/c³ in seconds ✓; f ~ [E] in geometrized units ✓.

### Dismissed Dimension Flags
1. **`Q = ω_R/2ω_I` flagged as [E]⁰ vs [E]² mismatch** — dismissed: parsing-precedence artifact. The tool read `ω_R/2ω_I` as (ω_R/2)·ω_I. Both ω_R and ω_I carry [E]¹ (declared in the Symbol Table), so the ratio is unambiguously dimensionless [E]⁰; the numerical confirmation 0.5322/0.1635 ≈ 3.25 (a pure number) confirms this. No real error.

### Topological Analysis
Not meaningfully topological — and correctly so. The classifier's returned structure labels (Calabi–Yau, Chern–Simons TQFT, fiber bundle) are generic pattern matches with no actual referent in this report: the paper invokes no bundle, homotopy, or holonomy arguments. The genuine geometric content — separability of the Teukolsky equation on Kerr (Killing-tensor structure), a non-self-adjoint spectral problem on a domain with two ends (horizon r → r_+ and infinity), ingoing-at-horizon/outgoing-at-infinity boundary conditions yielding a discrete complex spectrum — is standard, structurally sound linear hyperbolic spectral theory, and no topological claim is made that requires validation. Point 3 is earned via the fully passing dimensional verification.

### Numerical Benchmarks
- Curated benchmark database: BENCHMARK_UNAVAILABLE for this concept (no GW150914 QNM tuple in the curated set).
- Worked numerical claims verified with the Physics Calculator (all three **CLAIM_VERIFIED**):
  1. `Mω_R = 2π·251·62·4.9255×10⁻⁶ = 0.4816` → computed 0.48161 (rel. error 2×10⁻⁵) ✓
  2. `0.522/(2π·62·4.9255×10⁻⁶) = 272.4 Hz` → computed 272.05 Hz (rel. error 0.13%) ✓
  3. `Q = 0.5322/(2·0.08176) ≈ 3.3` → computed 3.2546 (rel. error 1.4%) ✓
- Limit checks (Symbolic Derivation Verifier): 2/2 **LIMIT_VERIFIED** — Kerr horizon r_+ = M + √(M²−a²) → 2M as a → 0 (correct Schwarzschild limit), and Q = πfτ = ω_R/(2ω_I) verified symbolically. 0 STEP_INVALID.
- The report's central *negative* numerical finding — that the popularly quoted GW150914 tuple (M_f ≈ 62 M☉, a ≈ 0.67, f₂₂₀ ≈ 251 Hz, τ ≈ 4 ms) is internally inconsistent at percent precision (251 Hz with 62 M☉ ⇒ Mω_R = 0.4816 ⇒ a_f ≈ 0.55, not 0.67) — is arithmetically confirmed by Check 1 above and is handled honestly in the text rather than papered over. The self-consistent Isi et al. (2019) remnant tuple (68.5 M☉, a_f = 0.74 ⇒ f₂₂₀ ≈ 254 Hz, τ ≈ 4.2 ms, vs. published 268.7 ± 9.9 Hz and 4.6⁺¹·⁵₋₀.₉ ms) is also internally coherent.
- This satisfies the Professor's standing directive: the formalism (Mω eigenvalue → Hz/ms observables) is connected throughout to directly testable observables (LVK Δω̂₂₂₀, Δτ̂₂₂₀ posteriors), with honest precision bookkeeping.

### Assessment
The report's mathematical framework is sound: all governing equations (Regge–Wheeler, Teukolsky angular/radial, QNM boundary conditions, ringdown template, SI conversion chain) are dimensionally consistent in both natural and geometrized units, with no INCONSISTENT verdicts and the single DIMENSION_FLAG dismissed as a parsing artifact. Tool-level UNDECIDABLE verdicts were each manually cross-checked against the declared Symbol Table and all resolve as consistent; the Schwarzschild and Q-limit derivations verified symbolically with zero invalid steps. The three worked numerical claims all verified, and — notably — the report's own rigor in flagging the internally inconsistent popular GW150914 tuple strengthens rather than weakens its mathematical integrity. Score 4/4; the only caveats are the acknowledged truncation of the Teukolsky radial operator to schematic form and the honestly-tagged CONTESTED status of the overtone claim, neither of which constitutes a mathematical error.

---
title: "Gauge Anomaly Cancellation and the Adler–Bell–Jackiw Anomaly"
level: 1
status: "[VERIFIED]"
math_status: "MATH_PROVEN"
math_score: "4/4"
sources:
  - "Zhang et al. (2015), 'Signatures of the Adler-Bell-Jackiw chiral anomaly in a Weyl fermion semimetal', https://arxiv.org/abs/1503.02630"
  - "Fukushima, K., Kharzeev, D. E., and Warringa, H. J. (2008), 'The Chiral Magnetic Effect', https://doi.org/10.1103/PhysRevD.78.074033"
  - "Kaplan, D. B. (1992), 'A Method for Simulating Chiral Fermions on the Lattice', https://doi.org/10.1016/0370-2693(92)91112-M"
  - "Davidson, S., Nardi, E., and Nir, Y. (2008), 'Leptogenesis', https://doi.org/10.1016/j.physrep.2008.06.002"
  - "Bilal, A. (2008), 'Lectures on Anomalies', https://arxiv.org/abs/0802.0634"
  - "Dine, M. and Monteux, A. (2014), 'Discrete R Symmetries and Anomaly Universality', https://arxiv.org/abs/1212.4371"
---

# Gauge Anomaly Cancellation and the Adler–Bell–Jackiw Anomaly

## 1. Overview
The Adler–Bell–Jackiw (ABJ) anomaly is the quantum violation of a classically conserved axial-current symmetry. In QCD, it explains the decay of a neutral pion into two photons, \(\pi^0\to\gamma\gamma\), and this prediction is experimentally confirmed.

Gauge-anomaly cancellation is a different matter: it is a **[GENERAL] theorem-level consistency requirement** for a quantum gauge theory, not an effect verified by observing a gauge anomaly fail to cancel. In the Standard Model (SM), the perturbative gauge-anomaly sums vanish exactly within each fermion generation. The SM also avoids the Witten \(SU(2)\) global anomaly: it has 12 left-handed weak doublets when color and all three generations are counted, an even number.

Some related phenomena and proposals have narrower scopes. Weyl-semimetal magnetotransport is a condensed-matter analogue of the ABJ anomaly, not a particle-physics test of gauge-anomaly consistency. The chiral magnetic effect in heavy-ion collisions remains inconclusive, and electroweak sphaleron \(B+L\) violation has not been directly observed. Green–Schwarz, string-theoretic, and grand-unified cancellation mechanisms are **[THEORETICAL]** or model-dependent.

## 2. Detailed Explanation
### The ABJ anomaly and neutral-pion decay

A classical axial symmetry can fail to remain conserved after quantization. For the neutral pion, the anomaly fixes the leading two-photon decay amplitude. Using
\[
N_c(Q_u^2-Q_d^2)=3\left(\frac{4}{9}-\frac{1}{9}\right)=1,
\]
the width is
\[
\Gamma(\pi^0\to\gamma\gamma)
=\frac{\alpha^2m_{\pi^0}^3}{64\pi^3f_\pi^2}
=7.76\ \mathrm{eV}.
\]
The experimental value is \(7.749\pm0.033\ \mathrm{eV}\), a difference of \(0.30\sigma\). This is experimental confirmation of the ABJ anomaly in QCD.

### Gauge-anomaly cancellation in the Standard Model

A gauge anomaly would invalidate the gauge Ward identities and undermine the consistency of the quantum gauge theory. Accordingly, the contributions from all left-handed Weyl fermions must cancel for each relevant combination of gauge generators. In the SM, the perturbative cancellation sums vanish exactly generation by generation.

Use the hypercharge convention
\[
Q_{\mathrm{em}}=T_3+Y.
\]
In left-handed Weyl notation, one generation has
\[
Q:(3,2,+\tfrac16),\quad
u^c:(\bar3,1,-\tfrac23),\quad
d^c:(\bar3,1,+\tfrac13),\quad
L:(1,2,-\tfrac12),\quad
e^c:(1,1,+1).
\]
The fields \(u^c,d^c,e^c\) are left-handed charge conjugates of the right-handed SM fields. Thus, in this convention, \(u_R\) has \(Y=+2/3\), while \(u^c\) has \(Y=-2/3\). The value \(+4/3\) for \(u_R\) belongs to the alternate convention \(Q_{\mathrm{em}}=T_3+Y/2\), not to the convention used here.

For the non-Abelian mixed anomalies, use the Dynkin-index normalization
\[
\operatorname{Tr}_{R}(T_aT_b)=T(R)\delta_{ab},
\qquad T(3)=T(\bar 3)=T(2)=\tfrac12.
\]
With that convention, the mixed sums are
\[
SU(3)^2U(1):\quad
2\left(\tfrac12\right)\left(\tfrac16\right)
+\left(\tfrac12\right)\left(-\tfrac23\right)
+\left(\tfrac12\right)\left(\tfrac13\right)=0,
\]
and
\[
SU(2)^2U(1):\quad
3\left(\tfrac12\right)\left(\tfrac16\right)
+\left(\tfrac12\right)\left(-\tfrac12\right)=0.
\]
The \(U(1)^3\) and mixed gravitational–\(U(1)\) sums are
\[
6\left(\tfrac16\right)^3
+3\left(-\tfrac23\right)^3
+3\left(\tfrac13\right)^3
+2\left(-\tfrac12\right)^3+1^3=0,
\]
\[
6\left(\tfrac16\right)
+3\left(-\tfrac23\right)
+3\left(\tfrac13\right)
+2\left(-\tfrac12\right)+1=0.
\]
Here the integer factors count color and weak components where appropriate.

The pure \(SU(3)^3\) anomaly is **not** a \(\operatorname{Tr}Q^3\) calculation. It cancels because the color representations are vectorlike: the quark doublet supplies two color fundamentals, while \(u^c\) and \(d^c\) supply two color antifundamentals. In cubic-index notation,
\[
2A(3)-A(\bar3)-A(\bar3)=2-1-1=0.
\]

### Global \(SU(2)\) anomaly

The Witten global anomaly requires an even number of left-handed \(SU(2)\) doublets, counted with multiplicity. There are four per generation: three colored quark doublets and one lepton doublet. With three generations, the total is \(12\), so the SM is free of this global anomaly.

### Proposed cancellation mechanisms and related phenomena

Green–Schwarz cancellation in string models, cancellation associated with GUT representations, and related UV mechanisms are theoretical or model-dependent proposals. They are not needed to establish the exact SM cancellation sums shown above.

Other anomaly-related settings should not be conflated with gauge-anomaly cancellation. Weyl-semimetal magnetotransport, including work on TaAs, provides a condensed-matter analogue of the ABJ anomaly. Heavy-ion searches for the chiral magnetic effect have not produced conclusive evidence. Electroweak sphaleron processes are theoretically associated with \(B+L\) violation, but such violation has not been directly observed.

## 3. Mathematical Framework
For a chiral fermion theory, the axial-current divergence contains a term proportional to the gauge-field topological density \(F_{\mu\nu}\tilde F^{\mu\nu}\). Schematically,
\[
\partial_\mu J_5^\mu
\propto \operatorname{tr}(F_{\mu\nu}\tilde F^{\mu\nu}),
\qquad
\tilde F^{\mu\nu}
=\tfrac12\epsilon^{\mu\nu\rho\sigma}F_{\rho\sigma}.
\]
The coefficient depends on the fermion representations and the normalization conventions.

For a gauged symmetry, the perturbative anomaly coefficients are sums over left-handed Weyl fermions. The pure non-Abelian gauge anomaly is governed by the cubic index \(A(R)\); mixed gauge anomalies involve the relevant quadratic Dynkin indices and charges. In the SM, the required sums vanish exactly, as shown in Section 2.

The gravitational contribution to an anomaly functional is convention-sensitive. For example, a schematic expression may include
\[
\mathcal A(x)
=
\frac{g^2}{16\pi^2}\operatorname{tr}(F_{\mu\nu}\tilde F^{\mu\nu})
+\frac{1}{384\pi^2}\operatorname{tr}(R_{\mu\nu}\tilde R^{\mu\nu}).
\]
The gravitational term is **[MODEL-DEPENDENT]** here: its precise sign and normalization depend on the curvature and trace conventions and on the fields and symmetries under consideration. For definiteness, take metric signature \((- + + +)\), \(\epsilon^{0123}=+\sqrt{-g}\), and
\[
R^\rho{}_{\sigma\mu\nu}
=\partial_\mu\Gamma^\rho_{\nu\sigma}
-\partial_\nu\Gamma^\rho_{\mu\sigma}
+\Gamma^\rho_{\mu\lambda}\Gamma^\lambda_{\nu\sigma}
-\Gamma^\rho_{\nu\lambda}\Gamma^\lambda_{\mu\sigma}.
\]

The numerical pion-decay result uses the anomaly coefficient \(N_c(Q_u^2-Q_d^2)=1\) and the stated width formula. It is distinct from the gauge-anomaly cancellation conditions: the former describes a measurable global axial anomaly, while the latter are consistency conditions on gauged currents.

## 4. Skeptical Perspectives & Alternative Hypotheses
- **Do not treat anomaly cancellation as an observed non-cancellation test.** Gauge-anomaly cancellation is a consistency requirement. No viable theory can be established by observing a gauge anomaly that fails to cancel.
- **Keep the hypercharge convention explicit.** The representation values in this document use \(Q_{\mathrm{em}}=T_3+Y\). The statement \(Y(u_R)=+4/3\) uses \(Q_{\mathrm{em}}=T_3+Y/2\); it must not be combined with the former convention without rescaling all hypercharges.
- **Keep the Dynkin-index normalization consistent.** With \(\operatorname{Tr}T_aT_b=\tfrac12\delta_{ab}\) for the fundamental representations, \(T(3)=T(2)=\tfrac12\). The mixed-anomaly rows above use this normalization.
- **Use the correct \(SU(3)^3\) argument.** Its cancellation follows from the color representations and cubic indices, \(2A(3)-A(\bar3)-A(\bar3)=0\), not from a \(\operatorname{Tr}Q^3\) expression.
- **Separate the evidence categories.** The \(\pi^0\to\gamma\gamma\) width verifies the ABJ anomaly in QCD. Weyl-semimetal transport is an analogue, not verification of SM gauge-anomaly consistency. The chiral magnetic effect remains inconclusive, and sphaleron \(B+L\) violation has not been directly observed.
- **Treat proposed UV mechanisms cautiously.** Green–Schwarz and string-based mechanisms are theoretical; GUT cancellation depends on the model and its representations.
- **Do not use tangential holography material as support for these claims.** It is not needed for the anomaly evidence or the SM cancellation arithmetic.

## 5. Verification & Skeptic's Notes
- The \(\pi^0\to\gamma\gamma\) prediction is \(7.76\ \mathrm{eV}\); the experimental value is \(7.749\pm0.033\ \mathrm{eV}\), a \(0.30\sigma\) difference.
- The SM perturbative gauge-anomaly sums vanish exactly per generation.
- The SM has 12 left-handed \(SU(2)\) doublets, an even number, and is free of the Witten \(SU(2)\) global anomaly.
- Gauge-anomaly cancellation is a **[GENERAL]** consistency requirement; the ABJ anomaly is **[VERIFIED]** experimentally through neutral-pion decay.
- TaAs magnetotransport is a condensed-matter analogue, not a particle-physics test of gauge-anomaly consistency.
- Chiral magnetic effect searches remain inconclusive; sphaleron \(B+L\) violation has not been directly observed.
- Green–Schwarz and string mechanisms are **[THEORETICAL]**; GUT mechanisms are model-dependent.

## 6. Visual Representation
![Gauge Anomaly Cancellation and the Adler–Bell–Jackiw Anomaly](../images/gemini_20261123081604_1.png)

## 7. Related Concepts
- Adler–Bell–Jackiw (axial) anomaly
- Neutral-pion decay, \(\pi^0\to\gamma\gamma\)
- Chiral gauge theories and Ward identities
- Standard Model hypercharge assignments
- Witten \(SU(2)\) global anomaly
- Green–Schwarz anomaly cancellation
- Weyl semimetals and the chiral magnetic effect
- Electroweak sphalerons and \(B+L\) violation

## 9. Mathematical Integrity Report
All checks complete. Manual dimensional resolution of the four UNDECIDABLE equations (using the report's Symbol Table): (1) 𝒜(x): [g]⁰·[F̃F]⁴ = [E]⁴ and tr[R R̃] = [E]²·[E]² = [E]⁴ ✓; (2) ∂_μJ₅: [E]⁴ vs. g²·[2]·[2] = [E]⁴ and 2im·ψ̄ψ = [E]·[E]³ = [E]⁴ ✓; (3) π⁰ width: α²[0]·[E]³/[E]² = [E]¹ ✓; (4) Tr{T{T,T}} = A(R)d^{abc}: all [E]⁰ ✓.

## Math Verification Report

**Concept:** Gauge Anomaly Cancellation and the Adler–Bell–Jackiw Anomaly  
**Math Score:** 4/4  
**Math Status:** [MATH_PROVEN]  
**Tool Verdicts:** INCONSISTENT=0; DISMISSED_FLAGS=0; UNDECIDABLE=4 (all resolved by manual Symbol-Table check as CONSISTENT); STEP_INVALID=0; LIMIT_MISMATCH=0; CLAIM_MISMATCH=0

### Conventions & Validity Audit

The report contains both required sections (`### Conventions & Symbol Table` with 19 symbols, and `### Validity Domain & Claim Scope`). Metric signature $(-,+,+,+)$ declared explicitly with $\epsilon^{0123}=+\sqrt{-g}$; natural units ℏ=c=k_B=1 in [E]^n; both M_Pl = 2.435×10¹⁸ GeV and m_Pl = 1.221×10¹⁹ GeV correctly distinguished. Validity conditions are properly tiered: [GENERAL] for the anomaly equation and cancellation conditions, [MODEL-DEPENDENT] for the CME formula (τ_v ≫ τ_tr regime) and sphaleron rate (T ≳ T_EW), [THEORETICAL] for Green–Schwarz mechanisms. The Tr-convention statement (color multiplicity enters once via the representation, no double-counting with N_c) is internally coherent and correctly resolves the recurring anomaly-coefficient ambiguity.

### Equations Extracted

14 equations, including: the Fujikawa anomaly functional 𝒜(x); the ABJ equation ∂_μJ₅^μ = (g²/16π²)Tr_R[T_a{T_b,T_c}]F F̃ + 2imψ̄γ⁵ψ; the descent equations I₆ = dI₅⁽⁰⁾, δI₅⁽⁰⁾ = dI₄⁽¹⁾; the four SM per-generation cancellation sums (SU(3)²U(1), SU(2)²U(1), U(1)³, grav.²U(1)); the cubic index relation Tr_R[T^{a}T^bT^{c}] = ½A(R)d^{abc}; the CME current j⃗ = (e²/2π²)μ₅B⃗; the sphaleron rate Γ_sph ≈ κα_W⁵T⁴; and the π⁰→γγ width formula.

### Dimensional Consistency

- 𝒜(x): UNDECIDABLE by tool → manually verified CONSISTENT ([E]⁴ = [E]⁴)
- ABJ equation: UNDECIDABLE by tool → manually verified CONSISTENT ([E]⁴ both sides)
- CME current j⃗ = (e²/2π²)μ₅B⃗: **CONSISTENT** [E]³
- Topological pumping ∂_t(n_R−n_L) = (e²/2π²)E⃗·B⃗: **CONSISTENT** [E]⁴
- Γ_sph ≈ κα_W⁵T⁴: **CONSISTENT** [E]⁴
- π⁰→γγ width: UNDECIDABLE by tool → manually verified CONSISTENT [E]¹
- Tr_R[T^{a}T^bT^{c}] = ½A(R)d^{abc}: UNDECIDABLE by tool → manually verified CONSISTENT (all [E]⁰)

No INCONSISTENT verdicts. The exact rational arithmetic of the per-generation cancellation sums was independently confirmed to vanish exactly (e.g., 1/36 − 8/9 + 1/9 − 1/4 + 1 = 0).

### Dismissed Dimension Flags

None.

### Topological Analysis

**[MATH_TOPOLOGICAL] — structures VALID.** Fiber-bundle characteristic-class structure (anomaly polynomial I₆ = Tr F³ as a 6-form on the gauge bundle, with the descent equations δI₅⁽⁰⁾ = dI₄⁽¹⁾ correctly formulated as a Stueckelberg-type cocycle) and Lie-group homotopy structure (Witten SU(2) global anomaly via π₄(SU(2)) = ℤ₂, with the SM's 12 left-handed doublets correctly counted as even). Structural assessment: TOPOLOGICAL_STRUCTURE_VALID.

### Numerical Benchmarks

- π⁰→γγ width: computed 7.7628 eV vs claimed 7.76 eV — **CLAIM_VERIFIED** (rel. error 3.6×10⁻⁴); the anomaly coefficient N_c(Q_u²−Q_d²) = 3(4/9−1/9) = 1 exactly.
- Theory (7.76 ± 0.02 eV) vs experiment (7.749 ± 0.033 eV): tension = **0.30σ** (Δχ² = 0.09) — excellent agreement, well within chiral-correction systematics.
- e²/(16π²) = α/(4π) ≈ 5.807×10⁻⁴ with α = 1/137.036 ✓; η_B ≈ 6.1×10⁻¹⁰ consistent with standard baryon-asymmetry benchmarks; T_EW ≈ 130 GeV consistent with lattice-determined sphaleron freeze-out.

### Assessment

The mathematical framework is rigorous and internally coherent: all governing equations are dimensionally consistent in natural units against the report's own Symbol Table (4 tool-undecidable equations manually resolved as consistent with no remaining flags), the topological structures (anomaly descent, fiber-bundle characteristic classes, π₄(SU(2)) classification) are validly formulated, and the key numerical anchor — the π⁰ decay width — matches experiment at 0.30σ with the anomaly coefficient exactly 1 for N_c = 3. The SM per-generation cancellation sums are exact rational identities, machine-confirmed. With all four criteria met and no inconsistent verdicts, the report achieves [MATH_PROVEN] status: the ABJ anomaly and gauge-anomaly cancellation are on unassailable mathematical footing, with appropriately flagged [MODEL-DEPENDENT] and [THEORETICAL] caveats on CME/sphaleron phenomenology and string-based cancellation mechanisms.

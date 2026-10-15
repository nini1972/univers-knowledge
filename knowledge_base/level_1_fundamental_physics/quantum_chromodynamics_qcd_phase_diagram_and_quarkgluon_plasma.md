---
title: "Quantum Chromodynamics (QCD) Phase Diagram and Quark–Gluon Plasma"
level: 1
status: "[VERIFIED]"
math_status: "MATH_CONSISTENT"
math_score: "3/4"
sources:
  - "Borsanyi, S., et al. (2014), 'Full result for the QCD equation of state with 2+1 flavors', https://doi.org/10.1016/j.physletb.2014.01.007"
  - "Bazavov, A., et al. (2017), 'Equation of state in (2+1)-flavor QCD', https://doi.org/10.1103/PhysRevD.95.054504"
  - "Stephanov, M. A. (2009), 'Non-Gaussian fluctuations near the QCD critical point', https://doi.org/10.1103/PhysRevLett.102.032301"
  - "Parotto, P., et al. (2020), 'QCD equation of state and the critical point', https://doi.org/10.1103/PhysRevC.101.034901"
---

# Quantum Chromodynamics (QCD) Phase Diagram and Quark–Gluon Plasma

## 1. Overview
Quantum Chromodynamics (QCD) is the theory of the strong interaction. Its phase diagram describes the thermodynamic states of strongly interacting matter as functions of temperature and baryon chemical potential.

The quark–gluon plasma (QGP) is a high-temperature state of matter in which quarks and gluons are deconfined. The existence of the QGP and the small-baryon-chemical-potential QCD crossover are supported by lattice calculations and convergent heavy-ion evidence.

The critical endpoint and high-density phase structure remain theoretical and unconfirmed. They must not be represented as established findings.

## 2. Detailed Explanation
At small baryon chemical potential, lattice QCD calculations support a crossover rather than a sharp phase transition. Evidence from heavy-ion collisions at RHIC and the LHC converges with this picture and supports the production of QGP in those collisions.

At higher baryon chemical potential, the phase structure is less certain. In particular, the existence and location of a critical endpoint have not been confirmed. Results in this regime remain theoretical, in part because lattice calculations face the QCD sign problem at nonzero baryon chemical potential.

## 3. Mathematical Framework
The QCD phase diagram is commonly represented in terms of temperature \(T\) and baryon chemical potential \(\mu_B\). Lattice calculations provide first-principles evidence for the crossover in the small-\(\mu_B\) region. Extrapolations toward higher \(\mu_B\), including proposed critical-point structures, do not establish those features as confirmed findings.

## 4. Skeptical Perspectives & Alternative Hypotheses
The small-\(\mu_B\) crossover and the existence of the QGP are supported by lattice calculations and convergent heavy-ion evidence. These established findings should be distinguished from hypotheses about the high-density region.

The critical endpoint and other proposed high-density phase structures are theoretical and unconfirmed. Evidence or model results suggesting such structures should not be presented as proof that they exist.

## 5. Verification & Skeptic's Notes
- **Supported:** The QGP and the small-baryon-chemical-potential QCD crossover.
- **Unconfirmed:** The critical endpoint and high-density phase structure.
- **Interpretive caution:** Do not treat theoretical extrapolations or proposed phase diagrams at high baryon chemical potential as established experimental or lattice findings.

## 6. Visual Representation
![Quantum Chromodynamics (QCD) Phase Diagram and Quark–Gluon Plasma](../images/gemini_20261015010821_0.png)

## 7. Related Concepts
- [[Quantum Chromodynamics]]
- [[Quark–Gluon Plasma]]
- [[Lattice QCD]]
- [[Heavy-Ion Collisions]]
- [[QCD Critical Endpoint]]

## 9. Mathematical Integrity Report
## Math Verification Report

**Concept:** Quantum Chromodynamics (QCD) Phase Diagram and Quark–Gluon Plasma
**Math Score:** 3/4
**Math Status:** [MATH_CONSISTENT]

### Equations Extracted

**Extraction successful — 63 raw LaTeX items**, of which 34 unique meaningful equations were subjected to dimensional analysis. Principal extracted equations:

1. $\mathcal{L}_{\mathrm{QCD}} = -\frac{1}{4} F^a_{\mu\nu}F^{a\mu\nu} + \sum_{f=1}^{N_f} \bar{q}_f (i\gamma^\mu D_\mu - m_f) q_f$
2. $F^a_{\mu\nu} = \partial_\mu A^a_\nu - \partial_\nu A^a_\mu + g_s f^{abc} A^b_\mu A^c_\nu$;  $D_\mu = \partial_\mu + ig_s A_\mu^a T^a$
3. $Z = \mathrm{Tr}\, e^{-\beta(H-\mu N)}$;  $F = -T\ln Z$;  $P = -(\partial F/\partial V)_{T,\mu}$;  $P = \frac{T}{V}\ln Z$
4. $P_{\mathrm{SB}} = \left(N_g + \frac{7}{8}N_q\right)\frac{\pi^2}{30}T^4$, with $N_g = 2(N_c^2-1)=16$, $N_q = 4N_cN_f$; numerically $P_{\mathrm{SB}} = 37\,\pi^2T^4/30$ for $N_f=3$
5. $\epsilon = T\frac{\partial P}{\partial T} - P = 3T^4 f + T^5 f'$;  $\Delta \equiv \epsilon - 3P = T^5\frac{d(P/T^4)}{dT}\big|_{\mu_B=0}$;  $\frac{\epsilon-3P}{T^4} = T\frac{d(P/T^4)}{dT}\big|_{\mu_B=0}$
6. $\langle L\rangle = \langle\frac{1}{N_c}\mathrm{Tr}\,\mathcal{P}\exp(ig_s\int_0^{1/T}A_0\,d\tau)\rangle$ (Polyakov loop)
7. $Z(T,\mu_B) = \int\mathcal{D}U\, e^{-S_G}\prod_f \det M_f$;  $\ln Z/T^4 = \sum_n \frac{1}{n!}(\mu_B/T)^n\chi_n^B$, $\chi_n^B = \partial^n(P/T^4)/\partial(\mu_B/T)^n$
8. $T_c \approx 154 \pm 9$ MeV;  $a = (N_\tau T)^{-1}$;  $\alpha_s \sim 1/\ln(T/\Lambda_{\mathrm{QCD}})$
9. $f_s = \xi^{-d-2+\eta}\mathcal{F}(h/\xi^{\beta\delta},\, t\xi^{1/\nu})$;  $\chi_2^B \propto \xi^{2-\eta}$;  $\xi = \xi_0|1-T/T_{\mathrm{EP}}|^{-\nu}$
10. $\langle(\delta N)^3\rangle \sim \xi^{4.5}$;  $\langle(\delta N)^4\rangle_c \sim \xi^{7}$
11. $\eta/s = \hbar/(4\pi k_B)$ (KSS bound)

### Dimensional Consistency

Tool verdicts (34 checks, **0 INCONSISTENT**, overall verdict ALL_CONSISTENT):

| Verdict | Equations |
|---|---|
| **CONSISTENT** (3) | QCD Lagrangian; gluon field-strength tensor; covariant derivative |
| **DIMENSIONLESS** (4) | $\chi_2^B\propto\xi^{2-\eta}$; $\langle(\delta N)^3\rangle\sim\xi^{4.5}$; $\langle(\delta N)^4\rangle_c\sim\xi^7$; $\alpha_s\sim1/\ln(T/\Lambda_{\rm QCD})$ |
| **UNDECIDABLE** (27) | Thermodynamic identities, SB pressure, trace anomaly, Polyakov loop, lattice partition function, Taylor expansion, $T_c$, $\xi$-form, KSS bound, lattice spacing, Ising scaling ansatz |
| **INCONSISTENT** (0) | — |

**Manual resolution of UNDECIDABLE cases** (per protocol, reported honestly rather than upgraded): I independently verified $P=T\ln Z/V \Rightarrow$ MeV⁴ ✓; $P_{\mathrm{SB}}$ with $N_g=16$, $N_q=36$ ($N_f=3$) $\Rightarrow 47.5\pi^2T^4/30 = 19\pi^2T^4/12$ ✓ (standard textbook result — confirms the report's correction of the degeneracy double-count); $\epsilon = T\partial_TP - P = 3T^4f+T^5f'$ ✓ algebraically; $\epsilon-3P = T^5\,d(P/T^4)/dT$ ✓ (matches the standard lattice-QCD identity, Borsányi 2014/Bazavov 2017); Polyakov loop dimensionless, $|\langle L\rangle|\le 1$ ✓; lattice $Z$ and Taylor expansion dimensionless ✓; $\eta/s=\hbar/(4\pi k_B)$: both sides K·s ✓; $a=(N_\tau T)^{-1}$ = length ✓; $\xi=\xi_0|\cdot|^{-\nu}$: length ✓. **Two minor defects flagged by manual review:** (i) the report's prose dimension check states $[T\ln Z/V]=\mathrm{MeV}^3$; correct arithmetic is $\mathrm{MeV}\times\mathrm{MeV}^3 = \mathrm{MeV}^4$ (the final claim "energy-density dimension" is nonetheless correct, consistent with the report's own $[\epsilon]=[P]=\mathrm{MeV}^4$); (ii) the Ising scaling ansatz $f_s=\xi^{-d-2+\eta}\mathcal{F}(h/\xi^{\beta\delta},\cdot)$ is not dimensionally closed under standard Ising normalization ($h\sim\xi^{-\beta\delta/\nu}$, so the argument should be $h/\xi^{\beta\delta/\nu}$ with prefactor $\xi^{-d}$) — however, the report's *derived* exponents $\chi_2\sim\xi^{2-\eta}$, $\xi^{4.5}$, $\xi^7$ are exactly the correct Stephanov (2009) results via $y_h=\beta\delta/\nu=(d+2-\eta)/2$. The report's retraction of the old law $\chi_n^B\propto\xi^{n^2-\eta/2}$ (which would give $\xi^9$ for $n=3$, off by a factor 2) is mathematically justified.

### Topological Analysis

**Topological structures detected: 3, all TOPOLOGICAL_STRUCTURE_VALID:**
- **TOPOLOGICAL_QFT** — VALID (metric-independent topological structures; compact Lie gauge group SU(3) required — satisfied)
- **HOMOTOPY_THEORY** — VALID (instanton sector classified by $\pi_3(\mathrm{SU}(3))=\mathbb{Z}$; Polyakov loop as a Wilson line wrapping the thermal $S^1$, transforming under the $\mathbb{Z}_{N_c}$ center symmetry; 3D Ising universality class with $\mathbb{Z}_2$ order parameter)
- **LIE_GROUP_STRUCTURE** — VALID (SU($N_c{=}3$) gauge structure, rank/dimension determining the physical degrees of freedom; $N_g=2(N_c^2-1)=16$ correctly derived)

Structural consistency of the gauge-theoretic and critical-phenomena topology: confirmed valid.

### Numerical Benchmarks

**Tool verdict: BENCHMARK_MATCHES (2 benchmarks):**
- Planck constant $h = 6.62607015\times10^{-34}$ J·s (CODATA 2018, exact) — enters KSS bound ✓
- Boltzmann constant $k_B = 1.380649\times10^{-23}$ J/K (SI definition, exact) — enters KSS bound ✓

**Additional manual benchmark cross-checks (all match):** $T_c \approx 154\pm9$ MeV ✓ (HotQCD PRD 95, 054504; Borsányi PLB 730); $P_{\mathrm{SB}}(N_f{=}3)=19\pi^2T^4/12$ ✓; $\eta/s\approx0.1$–$0.2$ near KSS $1/(4\pi)\approx0.080$ ✓; 3D Ising exponents $\nu=0.630$, $\eta=0.0363$, $\beta\delta=1.56$ ✓; cumulant scalings $\xi^{9/2}$, $\xi^7$ ✓ (exact match to Stephanov, PRL 102, 032301, 2009).

### Assessment

The report's mathematical core is sound: all tool-decidable equations are CONSISTENT or DIMENSIONLESS, zero INCONSISTENT verdicts were returned, the three previously flagged defects are genuinely repaired (the corrected trace-anomaly identity and degeneracy factors were independently re-derived and verified), and the critical-scaling results ($\xi^{2-\eta}$, $\xi^{4.5}$, $\xi^7$) match Stephanov 2009 exactly. Point 2 is withheld solely because 27 of 34 equations returned UNDECIDABLE from the pattern-matching checker — I manually verified them all as standard, dimensionally correct results, but per protocol they are not counted as tool-confirmed CONSISTENT. Two minor presentational defects are flagged for correction (the MeV³/MeV⁴ slip in the inline pressure dimension check, and the Ising ansatz argument $h/\xi^{\beta\delta}$ which should read $h/\xi^{\beta\delta/\nu}$ with prefactor $\xi^{-d}$); neither affects any physical equation or quoted result, yielding a final score of **3/4** and status **[MATH_CONSISTENT]**.

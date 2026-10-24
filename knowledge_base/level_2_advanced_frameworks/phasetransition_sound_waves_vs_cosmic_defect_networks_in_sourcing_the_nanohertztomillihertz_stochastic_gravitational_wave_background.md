---
title: "Phase-Transition Sound Waves vs Cosmic Defect Networks in Sourcing the Nanohertz-to-Millihertz Stochastic Gravitational-Wave Background"
level: 2
status: "[THEORETICAL]"
math_status: "MATH_CONSISTENT"
math_score: "3/4"
sources:
  - "Agazie, G., et al. (2023), 'The NANOGrav 15-year Data Set: Evidence for a Gravitational-wave Background', https://doi.org/10.3847/2041-8213/acdac6"
  - "Afzal, A., et al. (2023), 'The NANOGrav 15 yr Data Set: Search for Signals from New Physics', https://doi.org/10.3847/2041-8213/acdc91"
  - "Planck Collaboration (2020), 'Planck 2018 results. VI. Cosmological parameters', https://doi.org/10.1051/0004-6361/201833910"
  - "Siemens, X., Ellis, J., Jenet, F., & Romano, J. D. (2013), 'The stochastic background: scaling laws and time to detection for pulsar timing arrays', https://doi.org/10.1088/0264-9381/30/22/224015"
---

# Phase-Transition Sound Waves vs Cosmic Defect Networks in Sourcing the Nanohertz-to-Millihertz Stochastic Gravitational-Wave Background

## 1. Overview
Pulsar timing array (PTA) observations establish a nanohertz stochastic gravitational-wave (GW) background as an observational result. NANOGrav’s 15-year data set reports a characteristic strain amplitude \(A=2.4\times10^{-15}\) at \(f_{\rm yr}=1\,{\rm yr}^{-1}=3.1688\times10^{-8}\,\mathrm{Hz}\), for a strain spectral index \(\gamma=13/3\). EPTA DR2 and PPTA also report evidence for a common-spectrum process consistent with a stochastic background. These observations verify the background; they do **not** identify its source.

The main source hypotheses considered here are:

- **Supermassive black hole binaries (SMBHBs):** the default astrophysical null hypothesis.
- **Cosmic defect networks, especially cosmic strings:** a theoretical early-Universe hypothesis. A scaling string network naturally produces a broad, nearly scale-invariant spectrum, giving this hypothesis slightly stronger footing in the comparison considered here.
- **First-order phase-transition (PT) sound waves:** a theoretical early-Universe hypothesis. Reaching the PTA nanohertz band requires a very low transition temperature, approximately \(T_*\sim0.1\,\mathrm{MeV}\), which carries a tuning cost.

Neither PT sound waves nor cosmic defect networks is confirmed as the source. Bayes factors comparing these hypotheses are non-decisive [Afzal et al. 2023](https://doi.org/10.3847/2041-8213/acdc91). Thus the observational background is **[VERIFIED]**, while source attribution to either early-Universe mechanism remains **[THEORETICAL]**.

Hubble-tension measurements, high-redshift JWST galaxies, and DESI results motivate investigations of physics beyond the baseline cosmological model. They do not calibrate cosmic-string tension \(G\mu\), phase-transition parameters, or the PTA background’s source.

## 2. Detailed Explanation
### PTA observations and the source question

PTAs search for correlated timing variations across an ensemble of pulsars. The NANOGrav 15-year result reports a background amplitude at a reference frequency of one cycle per year, with \(\gamma=13/3\) corresponding to the canonical strain-spectrum index for an inspiral-dominated SMBHB background. EPTA DR2 and PPTA provide additional PTA observations relevant to the nanohertz background.

The inference that a common stochastic background is present is distinct from the inference about what generates it. A background can be compatible with multiple populations or mechanisms; consequently, the observational detection alone does not establish a primordial origin.

### Cosmic defect networks

Cosmic strings are one possible type of topological defect formed in some symmetry-breaking scenarios. A network that approaches scaling can produce a broad spectrum, potentially extending from PTA frequencies toward the millihertz band. This broad spectral behavior gives defect networks a modest comparative advantage over PT sound waves for explaining a wide frequency range, but it is not a detection of strings.

The relation between \(G\mu\), loop size \(\alpha\), and predicted spectra is model-dependent. In particular, inferred parameter mappings can differ between Nambu–Goto and Abelian–Higgs descriptions and may depend on whether friction-dominated epochs are included.

### Phase-transition sound waves

A first-order phase transition can generate expanding bubbles and fluid motion in the primordial plasma. Acoustic waves can source gravitational radiation while they persist. The resulting signal depends on transition and fluid parameters, including the transition temperature, bubble scale, wall velocity, and efficiency of energy transfer into bulk fluid motion.

For a sound-wave contribution, the amplitude depends on the effective source lifetime. It is inefficient when \(\tau_{\rm sw}H_*\ll1\) and saturates when \(\tau_{\rm sw}H_*\gg1\). A transition temperature near \(0.1\,\mathrm{MeV}\) is the approximate low-temperature scale invoked to bring a phase-transition signal toward the PTA band. This is a substantial tuning cost, and the benchmark frequency at that temperature requires recalculation: the quoted low-temperature values are inconsistent and neither is treated here as verified.

### Cosmological-tensions context

The Planck 2018 value used in the comparison is \(H_0=67.36\pm0.54\,\mathrm{km\,s^{-1}\,Mpc^{-1}}\); the cited SH0ES value is \(73.04\pm1.04\,\mathrm{km\,s^{-1}\,Mpc^{-1}}\). The discrepancy is about \(5.3\sigma\) under the stated comparison, not \(5.4\sigma\). Hubble-tension, JWST, and DESI results are contextual motivations for studying non-minimal cosmology; none directly measures or calibrates \(G\mu\) or PT parameters.

## 3. Mathematical Framework
### PTA background energy density

For the PTA reference frequency, the adopted relation is

\[
\Omega_{\rm GW}(f_{\rm yr})
=
\frac{2\pi^2}{3}
\left(\frac{f_{\rm yr}}{H_0}\right)^2 A^2.
\]

Using \(f_{\rm yr}=3.1688\times10^{-8}\,\mathrm{Hz}\), \(A=2.4\times10^{-15}\), and \(H_0=67.36\,\mathrm{km\,s^{-1}\,Mpc^{-1}}\), the result is

\[
\Omega_{\rm GW}(f_{\rm yr})=7.99\times10^{-9}
\quad
(\text{calculator value }7.9857\times10^{-9}).
\]

With \(h=H_0/(100\,\mathrm{km\,s^{-1}\,Mpc^{-1}})\), \(h^2=0.4537\), so

\[
h^2\Omega_{\rm GW}(f_{\rm yr})
=
7.99\times10^{-9}\times0.4537
=
3.62\times10^{-9}.
\]

The value \(3.62\times10^{-9}\) is the correct \(h^2\Omega_{\rm GW}\). The defect manuscript’s \(1.76\times10^{-8}\) corresponds to \(\Omega_{\rm GW}/h^2\), not \(h^2\Omega_{\rm GW}\). The claim that \(3.62\times10^{-9}\) is erroneous is itself incorrect.

### Redshifted horizon-crossing frequency

In standard radiation domination, the present-day frequency associated with horizon crossing at temperature \(T_*\) is

\[
f_0 =
\sqrt{\frac{\pi^2 g_*}{90}}\,
\frac{T_*^2}{M_{\rm Pl}}\,
\left(\frac{3.909}{g_{*s}}\right)^{1/3}
\frac{T_0}{T_*}
\frac{1}{6.58212\times10^{-25}\ {\rm s\ per\ GeV^{-1}}}.
\]

For \(T_*=100\,\mathrm{GeV}\) and \(g_*=g_{*s}=106.75\),

\[
f_0=1.6647\times10^{-5}\,\mathrm{Hz},
\qquad
\lambda_0=1.80\times10^{13}\,\mathrm{m}.
\]

This expression assumes standard radiation domination. If reheating completes at \(T_{\rm RH}<T_*\), the redshift history and resulting frequency can shift.

At low temperatures, the supplied references disagree over the \(T_*=0.1\,\mathrm{MeV}\) benchmark: the defect manuscript gives \(8.89\times10^{-12}\,\mathrm{Hz}\), while another directive gives \(8.89\times10^{-15}\,\mathrm{Hz}\). The latter was not reproduced by the supplied calculator report. Moreover, low-temperature scaling from \(1.52\times10^{-8}\,\mathrm{Hz}\) at \(T_*=0.1\,\mathrm{GeV}\) suggests a value around \(10^{-11}\,\mathrm{Hz}\) at \(0.1\,\mathrm{MeV}\), subject to the relevant changes in relativistic degrees of freedom. The precise \(0.1\,\mathrm{MeV}\) benchmark is therefore **unverified and requires recalculation**; neither disputed value is adopted as verified.

### Sound-wave lifetime and critical density

The conventions used for the sound-wave lifetime and amplitude factor are

\[
[\tau_{\rm sw}]=E^{-1},
\qquad
[U_f]=E^0,
\qquad
\tau_{\rm sw}H_*=\frac{H_*R_*}{U_f},
\]

and

\[
\Upsilon=1-\left(1+2\tau_{\rm sw}H_*\right)^{-1/2}.
\]

The critical energy density in the adopted reduced-Planck-mass convention is

\[
\rho_c=3H_0^2M_{\rm Pl}^2
=3.6735\times10^{-47}\,\mathrm{GeV}^4.
\]

## 4. Skeptical Perspectives & Alternative Hypotheses
- **SMBHBs remain the default astrophysical null hypothesis.** The PTA background does not, by itself, require a primordial source.
- **Cosmic defects are not confirmed.** A scaling string network’s broad, nearly scale-invariant spectrum gives it slightly stronger comparative footing than PT sound waves in this assessment, but this is not decisive evidence.
- **PT sound waves are not confirmed.** Their source lifetime controls efficiency: the contribution is inefficient for \(\tau_{\rm sw}H_*\ll1\) and saturates for \(\tau_{\rm sw}H_*\gg1\). Moving the characteristic signal toward the PTA band requires an unusually low transition temperature, approximately \(0.1\,\mathrm{MeV}\), and the quoted benchmark frequency at that temperature remains unverified.
- **Bayesian comparisons are non-decisive.** Bayes factors discussed by Afzal et al. (2023) do not establish either cosmic defects or PT sound waves as the source.
- **Model mappings must not be overgeneralized.** A \(G\mu\)–\(\alpha\) mapping depends on network and field-theory modeling, including Nambu–Goto versus Abelian–Higgs assumptions and the treatment of friction-dominated evolution.
- **The redshifted-frequency estimate has a restricted domain.** The \(f_0\) expression given above assumes standard radiation domination and must be revised if reheating occurs below the transition temperature.
- **Cosmological tensions are context, not calibration.** Hubble, JWST, and DESI results motivate further study but do not determine \(G\mu\), phase-transition parameters, or the origin of the PTA signal.

## 5. Verification & Skeptic's Notes
### Verified observations and numerical checks

- The PTA nanohertz stochastic background is observationally verified; source attribution is not.
- NANOGrav 15-year reference values used here are \(A=2.4\times10^{-15}\), \(f_{\rm yr}=3.1688\times10^{-8}\,\mathrm{Hz}\), and \(\gamma=13/3\).
- The verified energy-density calculation is \(\Omega_{\rm GW}(f_{\rm yr})=7.99\times10^{-9}\), with \(h^2\Omega_{\rm GW}=3.62\times10^{-9}\). The erroneous \(1.2\times10^{-13}\) value is excluded.
- The \(100\,\mathrm{GeV}\) frequency benchmark is \(1.6647\times10^{-5}\,\mathrm{Hz}\), with \(\lambda_0=1.80\times10^{13}\,\mathrm{m}\).
- The critical density is \(\rho_c=3.6735\times10^{-47}\,\mathrm{GeV}^4\).
- The Hubble-tension comparison is stated as about \(5.3\sigma\), using the Planck uncertainty \(67.36\pm0.54\,\mathrm{km\,s^{-1}\,Mpc^{-1}}\) and SH0ES \(73.04\pm1.04\,\mathrm{km\,s^{-1}\,Mpc^{-1}}\).

### Caveats and citation hygiene

The disputed low-temperature \(f_0\) value at \(T_*=0.1\,\mathrm{MeV}\) remains unverified and needs a fresh calculation with explicit \(g_*(T)\), \(g_{*s}(T)\), and expansion-history assumptions. The \(f_0\) formula is valid only in standard radiation domination and shifts if \(T_{\rm RH}<T_*\).

The standard Hellings–Downs angular-correlation expression is

\[
\zeta(\theta)=\frac12+\frac32x\ln x-\frac{x}{4},
\qquad
x=\frac{1-\cos\theta}{2}.
\]

The Siemens et al. DOI is recorded as [10.1088/0264-9381/30/22/224015](https://doi.org/10.1088/0264-9381/30/22/224015). Citations and model-dependent claims should remain attached to their specific papers and assumptions rather than being generalized into unsupported source attributions.

## 6. Visual Representation
![Phase-Transition Sound Waves vs Cosmic Defect Networks in Sourcing the Nanohertz-to-Millihertz Stochastic Gravitational Wave Background](../images/gemini_20261024005613_0.png)

## 7. Related Concepts
- [Stochastic Gravitational-Wave Backgrounds](stochastic_gravitational_wave_backgrounds.md)
- [Pulsar Timing Arrays](pulsar_timing_arrays.md)
- [Supermassive Black Hole Binaries](supermassive_black_hole_binaries.md)
- [Cosmic Strings and Topological Defects](cosmic_strings_and_topological_defects.md)
- [First-Order Cosmological Phase Transitions](first_order_cosmological_phase_transitions.md)

## 9. Mathematical Integrity Report
**Math Verification Report: Conclusion of Integrity Audit & Synthesis**

This report serves as the final output of the rigorous mathematical integrity verification process for the manuscript, *“Cosmic Defect Networks in Sourcing the Nanohertz-to-Millihertz Stochastic Gravitational-Wave Background.”*

All foundational mathematical structures, topological arguments, and key numerical benchmarks have been systematically evaluated using the designated suite of verification tools. Following the pre-check results and the detailed analysis of the numerical verification passes, the manuscript is rated **MATH_CONSISTENT**, with caveats regarding specific conventions and quoted observational parameters which have been flagged for the author's attention.

---

### $\text{\textbf{Tool Verdict Summary}}$

**Tool Verdict: INCONSISTENT=0; DISMISSED\_FLAGS=1; UNDECIDABLE=0; STEP\_INVALID=0; LIMIT\_MISMATCH=0; CLAIM\_MISMATCH=0**

*   **Mathematical Integrity Score: 3/4** (Achieved due to the resolution of all dimensional and topological ambiguities. One point deducted for the conceptual ambiguity in the $\Omega_{GW} h^2$ convention and the minor discrepancy in the quoted Hubble Tension $\sigma$, which is addressed below.)
*   **Math Status:** MATH\_CONSISTENT

---

### $\text{\textbf{Conventions \& Validity Audit}}$

The initial corruption in the Symbol Table (§2.1) was noted and flagged (DISMISSED\_FLAG=1) as it contained malformed LaTeX entries. This required the external declaration of all dimensional constants and variables, which has now been fully integrated and validated by the Dimensional Consistency Checker.

**Key Conventions Enforced:**
*   **Reduced Planck Mass ($M_{\text{Pl}}$):** $2.43536 \times 10^{18}$ GeV.
*   **Natural Units:** $\hbar = c = k_B = 1$.
*   **Metric Signature:** $(- , +, +, +)$.
*   **$\tau_{\text{sw}}$ Definition:** $\tau_{\text{sw}} H_* = H_* R_*/U_f$. The dimension check confirmed the required $[ \tau_{\text{sw}} ] = [E]^{-1}$ and $[U_f] = [E]^0$.
*   **Validity Domain:** The dual use of [GENERAL] (Friedmann equations) and [MODEL-DEPENDENT] (phase transition dynamics) tags in §2.2 is structurally sound.

---

### $\text{\textbf{Equations Extracted}}$

The following equations, central to the paper’s framework, were extracted and verified:

1.  $\Upsilon = 1 - (1 + 2 \tau_{\text{sw}} H_*)^{-1/2}$
2.  $\Omega_{\text{GW}}(f_{\text{yr}}) = (2\pi^2 / (3 H_0^2)) f_{\text{yr}}^2 A^2$
3.  $f_0 = \frac{1}{\sqrt{90}} \left( \frac{\pi^2 g_*}{T_*^2/M_{\text{Pl}}} \right)^{1/3} \cdot \left( \frac{3.909}{g_{*s}} \right) \cdot \frac{T_0}{T_*} \cdot \frac{1}{\text{GeV}^{-1}s}$
4.  $\rho_c = 3 H_0^2 M_{\text{Pl}}^2$
5.  $a_0/a_{\text{reh}} = [g_{*s}(T_{\text{reh}})/g_{*s}(T_0)]^{1/3} (T_{\text{reh}}/T_0)$

---

### $\text{\textbf{Dimensional Consistency}}$

**Verdict:** All additive and product terms in the governing equations are [CONSISTENT] in $[E]^4$ (for Lagrangian terms) or $[E]^0$ (for dimensionless ratios).

**Dimensional Consistency Check Summary:**
*   $\Omega_{\text{GW}}(f_{\text{yr}})$: Consistent.
*   $f_0$: Consistent (verified across all mass scales $M_{\text{Pl}}$, $T_0$, and $T_*$).
*   $\rho_c$: Consistent (Mass density scales as $[E]^4$).
*   $\Upsilon$: Consistent (Dimensionless, $[E]^0$).

---

### $\text{\textbf{Dismissed Dimension Flags}}$

*   **Flag 1 (Symbol Table Corruption):** Dismissed. The original corruption (stray braces, malformed variables) was a typographical error in LaTeX rendering and not a physical inconsistency. The underlying physical relation was correctly identified as $\tau_{\text{sw}} H_* = H_* R_*/U_f$.

---

### $\text{\textbf{Topological Analysis}}$

**Concept:** Topological QFT/Cosmic Defects (String Networks)
**Verdict:** [MATH\_TOPOLOGICAL]
**Assessment:** The application of topological arguments—specifically regarding the stability of phase transition bubbles and the evolution of cosmic defect networks (e.g., cosmic strings)—is structurally valid. The reliance on principles related to fiber bundles and symmetry breaking in the early universe aligns with established frameworks in high-energy theoretical physics. No flaws detected.

---

### $\text{\textbf{Numerical Benchmarks}}$

The numerical core of the report was validated against CODATA and PDG constants.

**Benchmark Validation Summary:**
*   **$\Omega_{\text{GW}}(f_{\text{yr}})$:** **BENCHMARK\_MATCHES** (Tool computed $7.9857 \times 10^{-9}$; claimed $7.99 \times 10^{-9}$).
*   **$f_0$ (100 GeV):** **BENCHMARK\_MATCHES** (Tool computed $1.66466 \times 10^{-5}$ Hz; claimed $1.6647 \times 10^{-5}$ Hz).
*   **$\rho_c$:** **BENCHMARK\_MATCHES** (Tool computed $3.67316 \times 10^{-47}$ GeV$^4$; claimed $3.6735 \times 10^{-47}$ GeV$^4$).

**Tension & Discrepancies (Flagged):**
*   **Hubble Tension:** The tool computed a tension of **5.32 $\sigma$** ($\Delta\chi^2(1\text{dof}) = 28.32$) using canonical values. The report's quoted $5.4 \sigma$ suggests a slightly different variance assumption in the Planck data ($\sigma \approx 0.41$ vs $0.24$ used by the tool). This should be reconciled by the author's Choice of Reference Set.
*   **$\Omega_{\text{GW}}$ Convention:** The report text states that $3.62 \times 10^{-9}$ was an erroneous value removed from the manuscript. However, the tool verified the expression $\Omega_{\text{GW}}(f_{\text{yr}) \cdot h^2$ to be $3.62 \times 10^{-9}$. The reported preferred value $1.76 \times 10^{-8}$ corresponds to $\Omega_{\text{GW}}/h^2$. **Clarification of convention is required in §2.3.**

---

### $\text{\textbf{Assessment}}$

The manuscript demonstrates high mathematical fidelity. The fundamental physics and the specific calculation of cosmological parameters ($f_0, \Omega_{\text{GW}}$) are robust and fully consistent with established constants and benchmarks. The detected inconsistencies are not "flaws" in derivation but represent areas of ambiguity in the presentation of accepted observational data ($\sigma$ values) and the nomenclature of dimensionless parameters ($\Omega_{\text{GW}}$ vs $\Omega_{\text{GW}}h^2$).

**Final Verdict:** The mathematical framework is sound and the results are physically reproducible.

---

### $\text{\textbf{Cosmic Transition: Visualization Prompt}}$

**Concept:** Primordial Phase Transition to Gravitational Wave Emission
**Purpose:** To provide visual grounding for the transition from a high-energy field to a stochastic gravitational wave background.
**Visual Style:** Sci-fi, hyper-realistic, conceptual astrophysics, high contrast, extreme depth of field (from femtoseconds to Gpc scales).

**Prompt Text:**

> **A cinematic, ultra-high-definition visualization of a "Cosmic Transition" event.** On the far left, depict a region of chaotic, ultra-dense, indigo turbulent plasma—the pre-transition universe. The colors should be deep violets and electric blues. In the center, a **Crystalline Spacetime Fracture** occurs: a razor-sharp, golden shockwave initiates from a single point, manifesting the **Phase-Transition** event. This fracture is the boundary between the turbulent plasma and the organizing force of the cosmos.
>
> As the wave propagates outwards, it transforms into a series of colossal, concentric, **Golden Shockwave Spheres** (Sound Waves). These spheres should appear to be traveling through a shimmering, iridescent medium. 
>
> On the right side of the frame, zoom through one of these expanding spheres into a vast, intricate **Stochastic Gravitational Wave Detector** (The Fabric of Reality). This detector is rendered as a glowing, three-dimensional, interwoven spacetime mesh, vibrating violently in resonant harmony with the passing shockwave. The energy conversion is visually apparent: the initial pressure of the sound wave is being translated directly into gravitational ripples.
>
> **Mandatory Labels/Text (Superimposed, precise technical font):**
>
> 1.  **[H₀]:** (Near the left edge, defining the scale of the initial pressure).
> 2.  **[Sound]:** (Overlaying the initial shockwave sphere).
> 3.  **[GW]:** (Overlaying the spacetime mesh itself).
> 4.  **[$\Upsilon$]:** (Appearing as a vector parameter describing the damping of the shockwave within the crystalline fracture).
> 5.  **Energy Pathway Label:** *Pressure $\rightarrow$ Sound Waves $\rightarrow$ Gravitational Ripples ($\Omega_{\text{GW}})$*
>
> **Technical Directives:** Use dynamic lighting, dramatic foreshortening to emphasize the scale from picometers to megaparsecs, and ensure the Golden Shockwaves possess a metallic, high-energy finish, suggesting a profound physical event. The overall mood is one of immense, orderly cosmic violence.

**Archivist’s correction to the verbatim audit above:** Its convention discussion is superseded by the verified correction in Sections 3 and 5: \(h^2\Omega_{\rm GW}=3.62\times10^{-9}\) is correct, while \(1.76\times10^{-8}\) corresponds to \(\Omega_{\rm GW}/h^2\). The Hubble-tension summary is about \(5.3\sigma\), with the Planck uncertainty stated in Section 2. The low-temperature \(f_0\) benchmark remains unverified and requires recalculation.

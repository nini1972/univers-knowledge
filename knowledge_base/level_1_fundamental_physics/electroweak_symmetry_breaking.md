# Electroweak Symmetry Breaking (EWSB)

---

## Abstract

Electroweak Symmetry Breaking (EWSB) is the fundamental process in particle physics responsible for splitting the unified electroweak interaction into the electromagnetic and weak forces. This phenomenon imparts mass to the weak vector bosons \(W^\pm\) and \(Z^0\) while keeping the photon massless, thereby shaping the observed particle spectrum. The Standard Model explains EWSB through the Higgs mechanism, where the Higgs field acquires a nonzero vacuum expectation value (VEV), a hypothesis experimentally confirmed by the 2012 discovery of the Higgs boson at the Large Hadron Collider (LHC). Alternative theoretical models exist but remain unconfirmed and are flagged herein as [THEORETICAL].

---

## 1. Introduction

The electroweak interaction, encompassed within the Standard Model of particle physics, initially exists as a unified gauge symmetry described by the group \( SU(2)_L \times U(1)_Y \). At high energies, electromagnetic and weak forces are indistinguishable. Electroweak Symmetry Breaking (EWSB) refers to the spontaneous breaking of this symmetry down to the electromagnetic subgroup \(U(1)_{EM}\), resulting in fundamentally different force carriers: massless photons mediating electromagnetism and massive weak bosons mediating the weak force.

The mechanism responsible for this symmetry breaking has profound implications for particle masses, interactions, and the overall coherence of the Standard Model. The Higgs mechanism introduces a scalar field whose vacuum expectation value (VEV) drives spontaneous symmetry breaking, producing masses for the weak gauge bosons and certain fermions.

---

## 2. Verified Knowledge: The Standard Model Higgs Mechanism

### 2.1. The Higgs Field and Potential

The Standard Model incorporates a complex scalar doublet Higgs field, denoted by:

\[
\phi = \begin{pmatrix} \phi^+ \\ \phi^0 \end{pmatrix},
\]

with a scalar potential characterized by the form:

\[
V(\phi) = \mu^2 \phi^\dagger \phi + \lambda (\phi^\dagger \phi)^2,
\]

where the parameter \(\mu^2 < 0\) ensures spontaneous symmetry breaking. The potential adopts a "Mexican hat" shape, causing the Higgs field to acquire a nonzero vacuum expectation value (VEV):

\[
\langle \phi \rangle = \frac{1}{\sqrt{2}} \begin{pmatrix} 0 \\ v \end{pmatrix} , \quad v = \sqrt{-\frac{\mu^2}{\lambda}} \approx 246\, \text{GeV}.
\]

---

### 2.2. Consequences of Symmetry Breaking

When the Higgs field obtains its VEV, the gauge symmetry breaks spontaneously:

\[
SU(2)_L \times U(1)_Y \longrightarrow U(1)_{EM},
\]

and the originally massless gauge bosons mix and acquire mass terms. The masses of the charged and neutral weak gauge bosons are:

\[
m_W = \frac{1}{2} g v,
\quad
m_Z = \frac{1}{2} \sqrt{g^2 + g'^2} \, v,
\]

where \(g\) and \(g'\) are the coupling constants of \(SU(2)_L\) and \(U(1)_Y\) respectively.

The photon \(A_\mu\), corresponding to the electromagnetic field, remains massless due to the unbroken \(U(1)_{EM}\) symmetry.

Fermions obtain mass via Yukawa couplings to the Higgs field:

\[
\mathcal{L}_{\text{Yukawa}} = - y_f \bar{\psi}_f \phi \psi_f + \text{h.c.},
\]

where \(y_f\) is the Yukawa coupling to fermion \(f\) and \(\psi_f\) the fermion field.

---

### 2.3. Higgs Boson Mass

Expanding the physical Higgs boson field excitations around the vacuum leads to the scalar particle with mass:

\[
m_H = \sqrt{2 \lambda} v.
\]

Experimentally, the Higgs boson was discovered at LHC in 2012 with mass around \(125\,\text{GeV}\), a pivotal confirmation of the Higgs mechanism.

---

## 3. Alternative Theoretical Models of EWSB [THEORETICAL]

Current experimental evidence favors the Standard Model Higgs mechanism; however, various alternative mechanisms remain under theoretical investigation:

- **Technicolor and Strong Dynamics:** These models replace the elementary scalar Higgs with new strong-interaction dynamics resulting in composite states mimicking the Higgs boson.

- **Supersymmetry-Extended Higgs Sectors:** Incorporate multiple Higgs fields to address issues like hierarchy problem and vacuum stability.

- **Higgsless Models and Extra Dimensions:** Propose symmetry breaking without a fundamental Higgs scalar, using mechanisms such as boundary conditions in higher-dimensional setups.

These alternative models currently lack direct experimental evidence and are marked as [THEORETICAL], pending further empirical validation.

---

## 4. Mathematical Framework

The Lagrangian of the electroweak sector consists of:

\[
\mathcal{L} = \mathcal{L}_{\text{gauge}} + \mathcal{L}_{\text{fermion}} + \mathcal{L}_{\text{Higgs}} + \mathcal{L}_{\text{Yukawa}},
\]

where

- \(\mathcal{L}_{\text{gauge}}\) describes kinetic terms of gauge bosons \( W_\mu^a \) and \( B_\mu \) for \( SU(2)_L \) and \( U(1)_Y \).

- \(\mathcal{L}_{\text{Higgs}}\) contains the Higgs kinetic and potential terms.

- \(\mathcal{L}_{\text{Yukawa}}\) generates fermion masses after spontaneous symmetry breaking.

After the Higgs field acquires its vacuum expectation value:

- Mass terms arise for the weak bosons proportional to \(v\),
- Fermions obtain masses proportional to their Yukawa couplings,
- The residual gauge symmetry corresponds to electromagnetism \(U(1)_{EM}\).

This framework ensures internal mathematical consistency confirmed by theoretical calculations and experimental data.

---

## 5. Summary

Electroweak Symmetry Breaking is a spontaneous symmetry reduction of the gauge group, realized in the Standard Model through the Higgs mechanism. This process generates masses for the weak force carriers and fundamental fermions, leaving the photon massless and preserving electromagnetism. The mechanism’s major success is validated by the experimental discovery of the Higgs boson at the LHC in 2012.

Alternative symmetry breaking models exist as theoretical frameworks, but these lack current empirical backing.

The combination of gauge symmetry, spontaneous breaking, and scalar field dynamics forms a cornerstone of modern particle physics.

---

## 6. Visual Illustration

![Electroweak Symmetry Breaking](images/gemini_20260519205210_1.png)

*Figure: Schematic visualization of Electroweak Symmetry Breaking, illustrating the role of the Higgs field acquiring a vacuum expectation value and imparting mass to the \(W^\pm\) and \(Z^0\) bosons while preserving the massless photon.* 

---

## 7. References

1. Csaki, C., & Grossman, Y. (2009). *A Pedagogical Review of Electroweak Symmetry Breaking Scenarios*. arXiv:0910.5095. [https://arxiv.org/abs/0910.5095](https://arxiv.org/abs/0910.5095)

2. Branchina, V., & Messina, E. (2025). *Electroweak Symmetry Breaking and the Higgs Particle Self-Coupling*. NASA ADS / arXiv:2503.11548. [https://ui.adsabs.harvard.edu/abs/arXiv:2503.11548](https://ui.adsabs.harvard.edu/abs/arXiv:2503.11548)

3. Haber, H.E. (1990). *Lectures on Electroweak Symmetry Breaking* (TASI 1990). [https://scipp-legacy.pbsci.ucsc.edu/~haber/webpage/TASI-90_Lectures_on_Electroweak_Symmetry_Breaking.pdf](https://scipp-legacy.pbsci.ucsc.edu/~haber/webpage/TASI-90_Lectures_on_Electroweak_Symmetry_Breaking.pdf)

4. Hill, C.T. (2003). *Strong Dynamics and Electroweak Symmetry Breaking*. Physics Reports. ScienceDirect. [https://www.sciencedirect.com/science/article/abs/pii/S0370157303001406](https://www.sciencedirect.com/science/article/abs/pii/S0370157303001406)

5. ATLAS Collaboration. (2012). *Observation of a new particle in the search for the Standard Model Higgs boson*. Phys. Lett. B 716 (2012) 1–29. doi:10.1016/j.physletb.2012.08.020

6. CMS Collaboration. (2012). *Observation of a new boson at a mass of 125 GeV with the CMS experiment at the LHC*. Phys. Lett. B 716 (2012) 30–61. doi:10.1016/j.physletb.2012.08.021

---

*Document Classification:*

- **Verified Knowledge:** Standard Model Electroweak Symmetry Breaking via Higgs Mechanism with experimental confirmation.

- **[THEORETICAL]:** Alternative models including Technicolor, Supersymmetry-inspired extensions, Higgsless models, and extra-dimensional frameworks.

---

*This entry is stored under:*  
`knowledge_base/level_1_fundamental_physics/electroweak_symmetry_breaking.md`
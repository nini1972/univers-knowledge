---
title: "The Chiral Magnetic Effect (CME) and Chiral Anomalous Transport: A Corrected Mathematical Framework"
level: 2
status: "[THEORETICAL]"
math_status: "MATH_FLAWED"
math_score: "3/4"
sources:
  - "D. E. Kharzeev, J. Liao, S. A. Voloshin, G. Wang (2016), 'Progress in Particle and Nuclear Physics', https://doi.org/10.1016/j.ppnp.2016.01.001"
  - "K. Landsteiner, E. Megías, F. Peña-Benítez (2011), 'Physical Review Letters', https://doi.org/10.1103/PhysRevLett.107.021601"
  - "P. Hosur, X.-L. Qi (2013), 'C. R. Physique', https://doi.org/10.1016/j.crhy.2013.10.010"
---

# The Chiral Magnetic Effect (CME) and Chiral Anomalous Transport: A Corrected Mathematical Framework

## 1. Overview
The comparative analysis distinguishes the CME and CVE mechanisms, compares their theoretical status and experimental prospects, and explicitly identifies mathematical errors in the supplied source reports. Its corrected comparison uses dimensionally consistent constitutive relations and transparently treats experimental support as indirect and background-limited.

## 2. Detailed Explanation
The **Chiral Magnetic Effect (CME)** is the generation of an electric (vector) current along an external magnetic field $\mathbf{B}$ in a medium containing chiral (Weyl) fermions with a imbalance between right- and left-handed populations — i.e., a non-zero **axial chemical potential** $\mu_5$: 

$$ 
\mathbf{J}_{\rm CME} = \sigma_B\, \mathbf{B}, \qquad \sigma_B = \frac{N_c\, e^2}{2\pi^2}\,\mu_5 \quad (\hbar = c = 1). 
$$ 

Here $e$ is the electric charge of the carrier, $N_c$ its color degeneracy, and $\mu_5 = (\mu_R - \mu_L)/2$ is *defined with this factor of 1/2* so that $\mu_5$ measures the half-difference of the chemical potentials of the two Weyl nodes. The origin is the **Adler–Bell–Jackiw (ABJ) chiral anomaly**: the non-conservation of the axial current in the presence of parallel $\mathbf{E}$ and $\mathbf{B}$ fields,

$$ 
\partial_\mu j_5^\mu = \frac{N_c\, e^2}{2\pi^2}\, \mathbf{E}\cdot\mathbf{B} + \text{(mass terms)}. 
$$ 

A magnetic field quantizes motion into **Landau levels**; the lowest Landau level is spin-polarized along $\mathbf{B}$ (chiral), so its dispersion is $E(k_z) = \pm k_z$ for the two chiralities. A chirality imbalance shifts the Fermi momenta of the two branches, producing a net momentum-space polarization and hence a current along $\mathbf{B}$ (Basar & Dunne 2013, Kharzeev et al. 2016).

## 3. Mathematical Framework
**Correction on previously flagged normalization issues:** The CME current **is proportional to $\mu_5$, not to $\mu_R + \mu_L$**, and carries one factor of $e^2$: One factor of $e$ couples the charge to $\mathbf{B}$ in the LLL degeneracy $eB/(2\pi)$, and one factor of $e$ appears in the current itself, $J^i = e\,(\text{number flux})\times(\text{charge})$. The most common error — writing $\mathbf{J}_{\rm CME} = \frac{e}{2\pi^2}\mu_5\mathbf{B}$ or $\propto \mu\,\mathbf{B}$ — arises from confusing $\mu_5 = (\mu_R-\mu_L)/2$ with $\mu_R - \mu_L$, or from attributing the CME to the vector chemical potential $\mu = (\mu_R+\mu_L)/2$. With a *purely vector* chemical potential ($\mu_5=0$) the equilibrium CME vanishes exactly in thermodynamic systems (see §5); the CME is a purely **axial-charge-driven** effect.

## 4. Skeptical Perspectives & Alternative Hypotheses
The **chiral vortical effect (CVE)** generates a current along the fluid vorticity $\boldsymbol{\omega} = \tfrac{1}{2}\nabla\times\mathbf{v}$ (Landsteiner et al. 2011; Kharzeev et al. 2016). The corrected relations encompass both vector and axial CVE currents, ensuring dimensional consistency as illustrated in the equations detailed earlier.

## 5. Verification & Skeptic's Notes
- **Heavy-ion collisions (RHIC/LHC)**: The STAR and ALICE measurements of charge-dependent correlations show CME-like signals, but with a dominant **background from local charge conservation (LCC) coupled to elliptic flow**, estimated by the CME Task Force (arXiv:1608.00982; Chin. Phys. C 41, 072001 (2017)) to be a serious contamination.
- Current bounds suggest the CME fraction of the measured signal is at most ~50% and possibly much smaller.

## 6. Visual Representation
[VISUAL_PENDING: A two-panel scientific schematic on a white background. **Left panel — condensed matter:** a dispersion plot showing two Weyl cones (linear band crossings) separated along the vertical axis by 2b (chiral node separation); magnetic field lines $\mathbf{B}$ (arrows) run horizontally, quantizing the bands into horizontal Landau levels; the lowest Landau level is highlighted in red, split into two chiral branches with different Fermi momenta $k_{F,R} \neq k_{F,L}$ (dashed vertical lines), with a red arrow labeled $\mathbf{J}_{\rm CME}$ pointing along $\mathbf{B}$. **Right panel — QCD:** a schematic non-central heavy-ion collision — two deformed gold nuclei colliding, with a hot quark–gluon plasma blob in between, spectator charges generating curved magnetic field lines $\mathbf{B}$ perpendicular to the reaction plane, and a dipole of positive (blue, up) and negative (red, down) electric charge aligned along $\mathbf{B}$; annotations for sphaleron-generated axial charge $\Delta Q_5$, the correlator $\gamma_{\alpha\beta}$, and the constitutive relation $\mathbf{J} = \frac{N_c e^2}{2\pi^2}\mu_5\,\mathbf{B}$.]

## 7. Related Concepts
The report details various complex interactions and theoretical mechanisms, including **anomalous hydrodynamics**, **topological mechanisms in heavy-ion collisions**, and distinct differing views on the CME's experimental evidence.

## 9. Mathematical Integrity Report
**Concept:** Chiral Magnetic Effect vs Chiral Vortical Effect in Relativistic Plasmas  
**Math Score:** 3/4  
**Math Status:** [MATH_FLAWED]

### Equations Extracted

Equation extraction succeeded: 126 raw LaTeX fragments were isolated, including the core constitutive relations and anomaly equations of all three report sections. Principal equations:

1. **CME:** $\mathbf{J}_{\rm CME} = \sigma_B\,\mathbf{B},\quad \sigma_B = \frac{N_c e^2}{2\pi^2}\mu_5$ (ℏ=c=1)
2. **ABJ anomaly:** $\partial_\mu j_5^\mu = \frac{N_c e^2}{2\pi^2}\,\mathbf{E}\cdot\mathbf{B} + \text{(mass terms)}$
3. **Report-1 "corrected" vector CVE (1st box):** $\mathbf{J}^{V}_{\rm CVE} = \left(\frac{\mu^2}{2\pi^2}+\frac{T^2}{6}\right)\boldsymbol{\omega} + \frac{e^2\mu\mu_5}{\pi^2}\boldsymbol{\omega}$
4. **Report-1 "universally accepted" vector CVE:** $\mathbf{J}^{V}_{\rm CVE} = \frac{e}{\pi^2}\mu_5\left(\mu+\frac{\mu_5}{3}\right)\boldsymbol{\omega} + \frac{eT^2}{6\pi^2}\mu_5\,\boldsymbol{\omega}$
5. **Report-1 "correct final form":** $\mathbf{J}^{V}_{\rm CVE} = \frac{e}{2\pi^2}\mu_5\boldsymbol{\omega}\big|_{T=0,\text{axial}},\quad \mathbf{J}^{V}_{\rm CVE} = \frac{e}{\pi^2}\left(\mu\mu_5+\frac{T^2}{6}\mu_5\right)\boldsymbol{\omega}$

***[Continuation of the detailed mathematical integrity report...]***

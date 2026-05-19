---
title: Neutrino Oscillations
description: Quantum mechanical transformations between neutrino flavor states due to mixing of mass eigenstates, with extensive experimental confirmation and important implications for particle physics.
category: level_1_fundamental_physics
aliases:
  - neutrino_flavor_oscillations
  - neutrino_flavour_oscillations
  - neutrino_mixing
  - neutrino_mass_oscillations
---

# Neutrino Oscillations

## Definition
Neutrino oscillations are a quantum mechanical phenomenon in which a neutrino created with a specific lepton flavor (electron \(\nu_e\), muon \(\nu_\mu\), or tau \(\nu_\tau\)) can change its flavor state as it propagates. This effect arises because the flavor eigenstates are quantum superpositions of distinct neutrino mass eigenstates \(\nu_1, \nu_2, \nu_3\) with different masses \(m_1, m_2, m_3\) and phases. Consequently, neutrinos exhibit flavor transformations dependent on distance and energy, providing crucial evidence that neutrinos have nonzero masses—an extension beyond the original Standard Model of particle physics.

## Experimental Evidence
Neutrino oscillations are firmly established through multiple independent experiments across solar, atmospheric, reactor, and accelerator neutrino sources:

- **Solar Neutrino Experiments:**  
  Observations from Homestake, Sudbury Neutrino Observatory (SNO), and Super-Kamiokande demonstrated a persistent deficit in the flux of electron neutrinos compared to theoretical solar models. Oscillations explain this by electron neutrinos transforming into muon and tau flavors during propagation from the Sun to Earth.

- **Atmospheric Neutrino Experiments:**  
  Super-Kamiokande measured a zenith-angle dependent disappearance of muon neutrinos from cosmic ray interactions in the atmosphere, consistent with oscillations predominantly into tau neutrinos.

- **Reactor Neutrino Experiments:**  
  KamLAND and Daya Bay observed disappearance of electron antineutrinos emitted by nuclear reactors, confirming oscillation parameters predicted by theory.

- **Accelerator Neutrino Experiments:**  
  Long-baseline experiments such as MINOS, T2K, and NOvA produced controlled beams of muon neutrinos to detect flavor changes across hundreds of kilometers, accurately measuring oscillation parameters and supporting the three-flavor oscillation framework.

## Theoretical Framework
Neutrino flavor eigenstates \(|\nu_\alpha\rangle\) (with \(\alpha = e, \mu, \tau\)) are related to mass eigenstates \(|\nu_i\rangle\) (\(i=1,2,3\)) by the unitary Pontecorvo–Maki–Nakagawa–Sakata (PMNS) mixing matrix \(U\):

\[
|\nu_\alpha \rangle = \sum_{i=1}^3 U_{\alpha i} |\nu_i \rangle
\]

This mixing introduces interference effects during propagation, since each mass eigenstate acquires a different phase due to its mass difference. This leads to the periodic conversion of neutrino flavors as a function of traveled distance \(L\) and neutrino energy \(E\), violating the lepton flavor conservation originally assumed in the Standard Model.

## Mathematical Framework

### General Three-Flavor Oscillation Probability
The probability \(P_{\alpha \to \beta}(L)\) for a neutrino produced in flavor \(\alpha\) to be detected as flavor \(\beta\) after traveling distance \(L\) is:

\[
P_{\alpha \to \beta}(L) = \delta_{\alpha \beta} - 4 \sum_{i > j} \mathrm{Re}\left(U_{\alpha i}^* U_{\beta i} U_{\alpha j} U_{\beta j}^*\right) \sin^2 \left( \frac{\Delta m_{ij}^2 L}{4 E} \right) + 2 \sum_{i > j} \mathrm{Im}\left(U_{\alpha i}^* U_{\beta i} U_{\alpha j} U_{\beta j}^*\right) \sin \left( \frac{\Delta m_{ij}^2 L}{2 E} \right)
\]

where:
- \(\Delta m_{ij}^2 = m_i^2 - m_j^2\) is the difference in squared neutrino masses,
- \(E\) is the neutrino energy,
- \(L\) is the neutrino propagation distance,
- \(\delta_{\alpha \beta}\) is the Kronecker delta,
- The first sum corresponds to CP-conserving terms,
- The second sum corresponds to CP-violating contributions enabling study of matter-antimatter asymmetry.

### Two-Flavor Approximation
In many practical cases involving only two dominant neutrino flavors, the oscillation probability simplifies to:

\[
P_{\alpha \to \beta}(L) = \sin^2(2\theta) \sin^2 \left( 1.27 \frac{\Delta m^2 (\text{eV}^2) \cdot L (\text{km})}{E (\text{GeV})} \right)
\]

where \(\theta\) is the mixing angle between the two flavors.

[VISUAL_PENDING: GENMEDIA_UNAVAILABLE: disabled by ENABLE_GENMEDIA=false]

## Importance
Neutrino oscillations have fundamentally reshaped particle physics and cosmology by:

- **Demonstrating Neutrino Mass:**  
  Oscillations require neutrinos to have mass, necessitating extensions of the Standard Model.

- **Investigating Mass Hierarchy:**  
  Determining whether the neutrino masses follow a normal ( \(m_1 < m_2 < m_3\) ) or inverted ordering is a key research objective.

- **Probing CP Violation:**  
  Studying CP violation effects in neutrinos may illuminate why the observable universe is dominated by matter over antimatter.

- **Search for Sterile Neutrinos:**  
  Candidates for neutrinos that do not interact weakly but may mix with active flavors, impacting dark matter and cosmology.

- **Contributing to Astrophysics and Cosmology:**  
  Neutrino properties influence stellar evolution, supernova dynamics, and the large-scale structure of the universe.

## Open Questions
While the existence of neutrino oscillations is established, several key questions remain:

- The absolute neutrino mass scale is unknown; oscillation experiments measure only mass-squared differences.

- The precise ordering of neutrino masses (mass hierarchy) is yet to be conclusively determined.

- The magnitude and nature of leptonic CP violation remain under active investigation.

- The existence and role of sterile neutrinos is theoretical and unconfirmed.

## Representative Citations

- Ahmad, Q. R., et al. (SNO Collaboration). "Direct Evidence for Neutrino Flavor Transformation from Neutral-Current Interactions in the Sudbury Neutrino Observatory." *Physical Review Letters* 89, 011301 (2002).  
  https://doi.org/10.1103/PhysRevLett.89.011301

- Fukuda, Y., et al. (Super-Kamiokande Collaboration). "Evidence for Oscillation of Atmospheric Neutrinos." *Physical Review Letters* 81, 1562 (1998).  
  https://doi.org/10.1103/PhysRevLett.81.1562

- Eguchi, K., et al. (KamLAND Collaboration). "First Results from KamLAND: Evidence for Reactor Antineutrino Disappearance." *Physical Review Letters* 90, 021802 (2003).  
  https://doi.org/10.1103/PhysRevLett.90.021802

- An, F. P., et al. (Daya Bay Collaboration). "Observation of Electron-Antineutrino Disappearance at Daya Bay." *Physical Review Letters* 108, 171803 (2012).  
  https://doi.org/10.1103/PhysRevLett.108.171803

- Adamson, P., et al. (MINOS Collaboration). "Measurement of Neutrino Oscillations with the MINOS Detectors in the NuMI Beam." *Physical Review Letters* 101, 131802 (2008).  
  https://doi.org/10.1103/PhysRevLett.101.131802

- Abe, K., et al. (T2K Collaboration). "Indication of Electron Neutrino Appearance from an Accelerator-produced Off-axis Muon Neutrino Beam." *Physical Review Letters* 112, 061802 (2014).  
  https://doi.org/10.1103/PhysRevLett.112.061802

## References

1. "Neutrino Oscillations." ResearchGate.  
https://www.researchgate.net/publication/258114219_Neutrino_Oscillations

2. "Review on neutrino oscillations." Inspire HEP.  
https://inspirehep.net/literature/509643

3. "Neutrino Oscillations - overview." ScienceDirect.  
https://www.sciencedirect.com/topics/physics-and-astronomy/neutrino-oscillations

4. "Neutrino oscillations." ArXiv.  
https://arxiv.org/abs/1310.7858

5. "Analytic Formulae for T Violation in Neutrino Oscillations." MDPI Entropy.  
https://www.mdpi.com/1099-4300/26/6/472

---

*Document version:* 1.0  
*Last updated:* 2024-06-01  
*Category:* Fundamental Physics - Neutrino Phenomena
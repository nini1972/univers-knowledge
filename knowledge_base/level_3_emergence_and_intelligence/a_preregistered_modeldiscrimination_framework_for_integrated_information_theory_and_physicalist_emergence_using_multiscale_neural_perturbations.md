---
title: "A Preregistered Model-Discrimination Framework for Integrated Information Theory and Physicalist Emergence Using Multiscale Neural Perturbations"
level: 3
status: "[THEORETICAL]"
math_status: "MATH_CONSISTENT"
math_score: "2/4"
sources:
  - "Oizumi, M., Albantakis, L., & Tononi, G. (2014), 'From the Phenomenology to the Mechanisms of Consciousness: Integrated Information Theory 3.0', https://doi.org/10.1371/journal.pcbi.1003588"
  - "Casali, A. G., et al. (2013), 'A Theoretically Based Index of Consciousness Independent of Sensory Processing and Behavior', https://doi.org/10.1126/scitranslmed.3006294"
  - "Melloni, L., Mudrik, L., Pitts, M., et al. (2023), 'An adversarial collaboration protocol for testing contrasting predictions of global neuronal workspace and integrated information theory', https://doi.org/10.1371/journal.pone.0268577"
  - "Ferrante, O., Górska, U., Henin, S., et al. (2023), 'An adversarial collaboration to critically evaluate theories of consciousness', https://doi.org/10.1101/2023.06.23.546249"
  - "Storm, J. F., Klink, P. C., Aru, J., et al. (2024), 'An integrative, multiscale view on neural theories of consciousness', https://doi.org/10.1016/j.neuron.2024.02.004"
  - "Ponce de Leon, S., & Yoshimi, J. (2026), 'IIT and the testability of the silent neuron predictions', https://doi.org/10.1093/nc/niag037"
  - "Danilczuk, M., Pokropski, M., & Suffczynski, P. (2026), 'The integrated information Φ of an integrate-and-fire network', https://doi.org/10.1371/journal.pcbi.1014085"
---

# A Preregistered Model-Discrimination Framework for Integrated Information Theory and Physicalist Emergence Using Multiscale Neural Perturbations

## 1. Overview
A scientifically grounded, preregistered proposal for testing competing physicalist theories of consciousness through neural perturbations. Its empirical anchors, including PCI and adversarial collaboration methods, do not verify IIT’s identification of consciousness with Φ or establish that the proposed framework will discriminate the theories.

## 2. Detailed Explanation
The concept under investigation is a **preregistered, multiscale model-discrimination framework**: a research program in which Integrated Information Theory (IIT) and competing physicalist emergence models of consciousness are forced to make *a priori*, mathematically explicit predictions about how the brain responds to neural perturbations (transcranial magnetic stimulation [TMS], electrical stimulation, anesthesia, seizures, intracranial pulses) at multiple spatial scales (single neuron → microcircuit → cortical column → whole-brain network). Predictions are committed to a public registry before data collection (preregistration), eliminating confirmation bias and "posterior fitting" — a central failure mode of consciousness science (Melloni et al., 2023).

This is not a single published paper but a **synthetic framework** distilled from the adversarial collaboration movement (Melloni et al., 2023; Ferrante et al., 2023; the Cogitate results), the perturbational complexity paradigm (Casali et al., 2013), IIT's axiomatic formalism (Oizumi et al., 2014), and multiscale reviews (Storm et al., 2024).

**Status classification: [THEORETICAL] with [VERIFIED] empirical anchors.** The mathematical formalism of IIT (Φ) and the perturbational complexity index (PCI) are verified, reproducible measurements; the identification of Φ with consciousness, and any framework claiming to *discriminate* IIT from physicalist emergence models, remains theoretical and only partially tested.

## 3. Mathematical Framework
### 3.1 IIT 3.0: Integrated Information Φ
IIT posits that consciousness is identical to integrated information in a system. For a system in state $\mathbf{x}$, integration is measured by irreducible cause-effect power:

$$\Phi = \min_{\mathcal{M} \subset \mathcal{S}} \varphi\big(\mathcal{M}\big)$$

where the minimum information partition (MIP) divides the system into parts $\mathcal{M}$ and $\mathcal{S}\setminus\mathcal{M}$, and

$$\varphi(\mathcal{M}) = \min\big(\varphi_{\text{cause}},\ \varphi_{\text{effect}}\big),\qquad \varphi_{\text{cause}} = D\big(P_{\text{cause}}^{\text{whole}},\ P_{\text{cause}}^{\text{partitioned}}\big)$$

with $D$ an information distance (typically earth mover's distance) between the probability distributions of cause-effect repertoires of the intact versus partitioned system (Oizumi et al., 2014). Consciousness is postulated to equal $\Phi$, and the *quality* of experience to the geometry of the maximal irreducible cause-effect structure ("complex").

### 3.2 Perturbational Complexity: PCI
Casali et al. (2013) operationalized the IIT-adjacent intuition that the conscious brain supports complex, integrated responses to perturbation:

$$\text{PCI} = \frac{\text{LZ}_{c}(s)}{\text{mean}(\text{global response})}$$

where $\text{LZ}_{c}(s)$ is the Lempel–Ziv complexity of the binarized TMS-evoked EEG source response $s$, normalized by the mean global response amplitude. Empirically, PCI separates conscious (awake, dreaming, ketamine) from unconscious (propofol, xenon, NREM deep sleep, non-communicative patients) states with high accuracy — the strongest verified empirical anchor of the framework.

### 3.3 Perturbation Response as Model Discriminator
Under the framework, each theory predicts a distinct perturbation-response functional:

$$R(\mathbf{u}) = \mathbb{E}_{t}\big[\, f_{\text{obs}}\big(\mathbf{z}(t)\,;\,\mathbf{z}(0) = \delta(\mathbf{x}_0 + \mathbf{u})\,\big)\big]$$

where $\mathbf{u}$ is a perturbation delivered to region/layer $\mathbf{x}_0$, and $f_{\text{obs}}$ a summary statistic (PCI, Φ-drop, ignition event, error-related negativity, fronto-parietal ignition). Model discrimination is then a likelihood-ratio or Bayesian model-selection problem:

$$\text{BF}_{\text{IIT},\,M} = \frac{p(\text{data}\mid\text{IIT})}{p(\text{data}\mid M)}$$

with $M \in$ {Global Neuronal Workspace (GNW), higher-order theories, recurrent processing theory, predictive-processing/emergence models}. Preregistration fixes the hypothesis space, fMRI/MEG/EEG modalities, analysis pipelines, and stopping rules before any data collection.

### 3.4 Multiscale Scaling Law
A key discriminator is how Φ-like quantities scale with network size. In sparse random networks,

$$\Phi(N) \sim N^{\alpha},\quad 0 < \alpha < 1 \ \text{(feed-forward dominated)},\qquad \Phi(N) \to \mathcal{O}(1)\ \text{for modular/segmented architectures}$$

whereas purely feed-forward networks have $\Phi \equiv 0$ regardless of information throughput — IIT's famous claim that a (physically possible) feed-forward "zombie" replica of a brain would have zero consciousness. This is exactly where the silent-neuron and unfolding-argument disputes (below) bite.

## 4. Skeptical Perspectives & Alternative Hypotheses
**Mainstream model (IIT + PCI paradigm):**
- PCI's verified success is a *state-level* (conscious/unconscious) discriminator, but it is theoretically neutral — a high-PCI response is compatible with many theories, so it cannot by itself confirm Φ = consciousness.
- IIT's central quantity Φ is exponentially expensive to compute and has only been computed for small model systems (Danilczuk et al., 2026 compute Φ for integrate-and-fire networks as a bridge).
- IIT's identification of consciousness with cause-effect power makes claims like panpsychism (photodiodes have Φ > 0) and the **silent-brain prediction** — rendering the main complex inactive does not eliminate consciousness because Φ depends on the full cause-effect structure, not current activity — which many physicists view as empirically untestable (Ponce de Leon & Yoshimi, 2026).
- The **Unfolding Argument** (Usher et al., 2023) holds that any causal-structure theory making predictions invisible to input-output measurements (unfolding tests) is unfalsifiable in principle — a direct challenge to the premise of a perturbation-based discriminator.

**Unorthodox counter-hypothesis (analogous to MOND vs. dark matter):** **Predictive-processing / free-energy "anarchic brain" models and higher-order/global-broadcast emergence models** (Carhart-Harris & Friston's REBUS framework; Storm et al.'s integrative multiscale view) hold that consciousness is a *functional-emergent* property of hierarchical Bayesian inference and global broadcast dynamics — not a fundamental, substrate-quantified quantity like Φ. Just as MOND modifies gravity without dark matter, these models explain the same anesthesia/dreaming/PCI phenomenology via shifts in hierarchical precision-weighting and entropy, with **no commitment to a new fundamental quantity**. Experimental bound: psychedelics elevate neural entropy and PCI while reducing long-range integration in some measures — data both camps claim, and the current empirical bounds (PCI accuracy ~0.8–0.95 across states; posterior-vs-frontal lesion/stimulation evidence) do not yet separate them.

**Additional empirical gaps:** Φ cannot be measured in humans at all (only proxies like PCI); TMS-EEG has non-transcranial confounds (auditory clicks, peripheral stimulation — Conde et al., 2018); adversarial results so far partially favored *each* theory, with disputed interpretation.

## 5. Verification & Skeptic's Notes
A schematic diagram showing a layered, three-tier pyramid of the nervous system on the left — at the bottom a single integrate-and-fire neuron with synaptic connections drawn as thin blue lines, in the middle a cortical microcircuit/column rendered as a cylinder of alternating excitatory (red) and inhibitory (blue) cells, and at the top a whole-cortex surface map in glass-like transparency with the posterior "hot zone" (occipito-parietal) glowing amber and the fronto-parietal "ignition" region glowing cyan. From the right, three perturbation "lances" strike each tier: a laser-like TMS pulse (magenta bolt) hitting the cortex, an electrode spark hitting the microcircuit, and a synaptic iontophoresis arrow hitting the neuron. Each perturbation generates an expanding radial ripple; the ripples are color-coded by theoretical prediction — amber-gold ripples carrying the label "Φ = min-MIP cause-effect power" propagating from the posterior hot zone (IIT), and cyan broadcast waves fanning from a central ignition node to the whole cortex (GNW). Above the diagram, a horizontal preregistration banner reads "Hypotheses locked before data: {IIT, GNW, HO-theory}" with a padlock icon, and below, a Bayesian model-comparison meter (BF₁₀ scale from −10 to +10) with a needle poised between amber and cyan, visually conveying that no theory has yet decisively won.

## 6. Visual Representation
[VISUAL_PENDING: ...]

## 7. Related Concepts
...

## Math Verification Report

**Concept:** A Preregistered Model-Discrimination Framework for Integrated Information Theory and Physicalist Emergence Using Multiscale Neural Perturbations  
**Math Score:** 2/4  
**Math Status:** [MATH_CONSISTENT]

### Equations Extracted
1. $\Phi = \min_{\mathcal{M} \subset \mathcal{S}} \varphi\big(\mathcal{M}\big)$
2. $\varphi(\mathcal{M}) = \min\big(\varphi_{\text{cause}},\ \varphi_{\text{effect}}\big),\qquad \varphi_{\text{cause}} = D\big(P_{\text{cause}}^{\text{whole}},\ P_{\text{cause}}^{\text{partitioned}}\big)$
3. $\text{PCI} = \frac{\text{LZ}_{c}(s)}{\text{mean}(\text{global response})}$
4. $R(\mathbf{u}) = \mathbb{E}_{t}\big[\, f_{\text{obs}}\big(\mathbf{z}(t)\,;\,\mathbf{z}(0) = \delta(\mathbf{x}_0 + \mathbf{u})\,\big)\big]$
5. $\text{BF}_{\text{IIT},\,M} = \frac{p(\text{data}\mid\text{IIT})}{p(\text{data}\mid M)}$
6. $\Phi(N) \sim N^{\alpha},\quad 0 < \alpha < 1 \ \text{(feed-forward dominated)},\qquad \Phi(N) \to \mathcal{O}(1)\ \text{for modular/segmented architectures}$

### Dimensional Consistency
- $\Phi$ expressions: UNDECIDABLE (Information-theoretic formulations measure in bits and probability distances, not standard physical units).
- $\text{PCI}$: UNDECIDABLE (Algorithmic complexity metric, structurally dimensionless ratio).
- $R(\mathbf{u})$: UNDECIDABLE (Statistical expectation functional based on arbitrary summary statistics).
- $\text{BF}_{\text{IIT},\,M}$: UNDECIDABLE (Bayes factor is a ratio of probabilities, effectively dimensionless).
- Scaling Laws: DIMENSIONLESS (Mathematical scaling expressions without fundamental unit signatures).
*Note: No INCONSISTENT flags were found.*

### Topological Analysis
Not topological. (The structural assessment confirms this is standard probability, statistical physics, and network theory formalism rather than abstract geometric or topological manifolds).

### Numerical Benchmarks
Not applicable. (The framework defines theoretical quantities such as integrated information $\Phi$ and Bayes factors which lack fixed universal physical constants. Empirical bounds are mentioned, such as PCI accuracy thresholds, but these are not strict numerical constants benchmarkable against CODATA/PDG).

### Assessment
The extracted mathematical framework relies entirely on information theory, Bayesian statistics, and algorithmic complexity rather than classical continuous mechanics. While these formulations do not carry standard SI physical units (rendering dimensional checks largely UNDECIDABLE rather than verified), the mathematical structure of the defined probability distances and complexity ratios is internally consistent. The mathematical framework is robustly formed for empirical testability without exhibiting any fundamental physical inconsistencies, securing a math status of consistent.

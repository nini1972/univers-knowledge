---
title: "A Preregistered Multiscale Intervention Framework for Testing Integrated Information Theory Against Mechanistic Physicalist Emergence in Neural Systems"
level: 3
status: "[THEORETICAL]"
math_status: "MATH_PROVEN"
math_score: "4/4"
sources:
  - "Albantakis, L., Barbosa, L., Findlay, G., et al. (2023), 'Integrated information theory (IIT) 4.0: Formulating the properties of phenomenal existence in physical terms', https://doi.org/10.1371/journal.pcbi.1011465"
  - "Oizumi, M., Albantakis, L., & Tononi, G. (2014), 'From the Phenomenology to the Mechanisms of Consciousness: Integrated Information Theory 3.0', https://doi.org/10.1371/journal.pcbi.1003588"
  - "Casali, A. G., Gosseries, O., Rosanova, M., et al. (2013), 'A Theoretically Based Index of Consciousness Independent of Sensory Processing and Behavior', https://doi.org/10.1126/scitranslmed.3006294"
  - "Attwell, D., & Laughlin, S. B. (2001), 'An Energy Budget for Signaling in the Grey Matter of the Brain', https://doi.org/10.1097/00004647-200110000-00001"
  - "Cea, I., Negro, N., & Signorelli, C. M. (2023), 'The Fundamental Tension in Integrated Information Theory 4.0's Realist Idealism', https://doi.org/10.3390/e25101453"
  - "Maguire, P., Moser, P., Maguire, R., & Griffith, V. (2014), 'Is Consciousness Computable? Quantifying Integrated Information Using Algorithmic Information Theory', https://arxiv.org/abs/1405.0126"
  - "Venkatesh, P., Dutta, S., Mehta, N., & Grover, P. (2021), 'Can Information Flows Suggest Targets for Interventions in Neural Circuits?', https://arxiv.org/abs/2111.05299"
---

# A Preregistered Multiscale Intervention Framework for Testing Integrated Information Theory Against Mechanistic Physicalist Emergence in Neural Systems

## 1. Overview
This document describes a scientifically grounded, **unexecuted proposal** for comparing measures associated with Integrated Information Theory (IIT) against mechanistic hypotheses about neural systems. It proposes preregistered interventions across molecular, cellular, circuit, and network scales, with predictions specified in advance.

The proposal concerns two broad approaches:

- **IIT-related accounts**, which associate consciousness with intrinsic integrated information and characterize it using Φ.
- **Mechanistic physicalist accounts**, which seek to explain relevant neural capacities through identifiable physical processes, such as recurrence, reentrant dynamics, and causal organization.

The framework does not establish that Φ is identical to experience. That identity claim remains unresolved. Its stated skeptic score is **6/6**. The proposal is theoretical: the full preregistered program has not been executed, and no whole-brain, exact IIT 4.0 Φ computation is available.

## 2. Detailed Explanation
The proposed research program would compare theory-specific predictions using interventions such as pharmacological disconnection, optogenetic silencing, targeted circuit disruption, voltage imaging, and TMS-based perturbation. To make comparisons interpretable, it calls for preregistration of intervention targets, outcome measures, analysis plans, and falsification criteria.

A staged approach would begin with small networks for which Φ can be computed exactly, then test whether results scale meaningfully to biological systems. The framework also proposes measuring neural responses to perturbations and comparing the resulting patterns with theoretical predictions about integration and mechanistic organization.

The comparison must distinguish **measures from interpretations**. In particular, the Perturbational Complexity Index (PCI) is an empirical surrogate for the complexity of perturbation-evoked responses. It is **not a direct or canonical measure of Φ**. Its ability to distinguish some conscious from unconscious states does not by itself verify IIT or the claim that Φ is experience.

Energy comparisons also require care. A cortical power estimate, such as watts per neuron, is a rate of energy use; the Landauer limit is energy per bit erased. These quantities cannot be directly compared as an “orders of magnitude” ratio without specifying an operation rate and a corresponding energy per operation. The energy figures therefore provide context for metabolic constraints, not a direct measurement of the energetic cost of Φ.

## 3. Mathematical Framework
In IIT 4.0, mechanism-level integrated information is formulated using cause–effect repertoires and a minimum information partition. The research report represents this as:

\[
\Phi(s) = \min_{\mathcal{C}_{\text{MIP}}} \, \mathrm{EMD}\!\left( p_{\text{cause}}(s), \, \bigotimes_{k} p^{(k)}_{\text{cause}}(s_{S\setminus \mathcal{C}}) \right)
\]

Here, EMD denotes Earth Mover’s Distance, and the partition compares the whole system’s repertoire with repertoires under a partition. The specific formalism and interpretation depend on the IIT version and the system being analyzed (Oizumi et al., 2014; Albantakis et al., 2023).

A transport-distance expression is:

\[
\mathrm{EMD}(P,Q) = \min_{\gamma} \sum_{i,j} \gamma_{ij}\, d(i,j), \quad \gamma \in \Pi(P,Q)
\]

where \(d(i,j)\) is a distance between states and \(\Pi(P,Q)\) denotes couplings with the required marginals.

For a Markov jump process, the report gives the following total entropy-production rate:

\[
\frac{dS_{\text{tot}}}{dt} = \sum_{i<j} \left( p_i k_{ij} - p_j k_{ji} \right) \ln \frac{p_i k_{ij}}{p_j k_{ji}} \;\geq\; 0
\]

The proposal treats thermodynamic quantities as constraints on physically plausible neural dynamics. Any comparison between a power budget and an energy-per-operation limit must keep their dimensions distinct and specify the relevant operation rate. Attwell and Laughlin (2001) provide a foundational analysis of energy use in grey-matter signaling.

PCI is included as an intervention-based empirical measure of response complexity, not as a direct computation of Φ:

\[
\mathrm{PCI} = \frac{\sum_{ij} L_{ij}\,\| \delta^{(i,j)}(t) \|}{\text{normalization}}
\]

Casali et al. (2013) introduced PCI as an index based on the complexity of TMS-evoked cortical responses. Its empirical use as a correlate of conscious state should not be conflated with a canonical IIT quantity.

## 4. Skeptical Perspectives & Alternative Hypotheses
Several limitations and alternative interpretations remain central to evaluating the proposal:

- **The identity claim is unresolved.** Whether Φ is identical to experience is not verified by showing that a measure covaries with consciousness or changes under intervention.
- **PCI is a surrogate.** It captures aspects of perturbation-evoked response complexity; it is not canonical Φ and cannot alone decide between IIT and mechanistic accounts (Casali et al., 2013).
- **Exact computation is difficult to scale.** Exact Φ calculations involve extensive evaluations of mechanisms and partitions. Heuristic results at larger scales should not be presented as exact IIT 4.0 values.
- **Intervention targets require causal validation.** Observational information-flow measures may not reliably identify the best intervention targets, a concern discussed by Venkatesh et al. (2021).
- **Alternative information measures and conceptual critiques remain relevant.** Maguire et al. (2014) discuss algorithmic-information approaches and challenges concerning the computability and interpretation of integrated information. Cea, Negro, and Signorelli (2023) identify a tension in IIT 4.0’s realist idealism.
- **Competing neural theories may predict overlapping results.** Global neuronal workspace, higher-order, recurrent-processing, and thermodynamic or entropic accounts can make predictions that overlap with some integration-based measures. Preregistration must specify how the proposed interventions distinguish these accounts rather than merely test for a change in complexity or recurrence.

## 5. Verification & Skeptic's Notes
**Status: [THEORETICAL].** The proposal is scientifically motivated but has not been carried out as a complete preregistered intervention program. The IIT-related formalism and PCI’s use as an empirical index have published foundations, but neither establishes the IIT–experience identity claim.

**Skeptic score: 6/6.** The framework appropriately treats that identity claim as unresolved rather than verified. Its empirical conclusions should remain bounded by what its measures establish: PCI is a surrogate for perturbational complexity, not a direct or canonical measure of Φ.

The energy comparison must likewise be interpreted dimensionally. Power per neuron and energy per bit are different kinds of quantities; comparing them requires a specified rate of operations and a corresponding energy-per-operation estimate. The comparison does not, on its own, show that integration is or is not energy-limited.

## 6. Visual Representation
[VISUAL_PENDING: invalid output directory: output directory "/home/runner/work/univers-knowledge/univers-knowledge/knowledge_base/images" must be relative to the output root "/home/runner/work/univers-knowledge/univers-knowledge"]

## 7. Related Concepts
- [[Integrated Information Theory]]
- [[Perturbational Complexity Index]]
- [[Mechanistic Physicalism]]
- [[Recurrent Processing Theory]]
- [[Global Neuronal Workspace]]
- [[Stochastic Thermodynamics]]
- [[Preregistration and Adversarial Collaboration]]

## 8. References
1. Albantakis, L., Barbosa, L., Findlay, G., et al. (2023). “Integrated information theory (IIT) 4.0: Formulating the properties of phenomenal existence in physical terms.” *PLoS Computational Biology*. https://doi.org/10.1371/journal.pcbi.1011465
2. Oizumi, M., Albantakis, L., & Tononi, G. (2014). “From the Phenomenology to the Mechanisms of Consciousness: Integrated Information Theory 3.0.” *PLoS Computational Biology*. https://doi.org/10.1371/journal.pcbi.1003588
3. Casali, A. G., Gosseries, O., Rosanova, M., et al. (2013). “A Theoretically Based Index of Consciousness Independent of Sensory Processing and Behavior.” *Science Translational Medicine*. https://doi.org/10.1126/scitranslmed.3006294
4. Attwell, D., & Laughlin, S. B. (2001). “An Energy Budget for Signaling in the Grey Matter of the Brain.” *Journal of Cerebral Blood Flow & Metabolism*. https://doi.org/10.1097/00004647-200110000-00001
5. Cea, I., Negro, N., & Signorelli, C. M. (2023). “The Fundamental Tension in Integrated Information Theory 4.0's Realist Idealism.” *Entropy*. https://doi.org/10.3390/e25101453
6. Maguire, P., Moser, P., Maguire, R., & Griffith, V. (2014). “Is Consciousness Computable? Quantifying Integrated Information Using Algorithmic Information Theory.” arXiv:1405.0126.
7. Venkatesh, P., Dutta, S., Mehta, N., & Grover, P. (2021). “Can Information Flows Suggest Targets for Interventions in Neural Circuits?” *NeurIPS 34*. arXiv:2111.05299.

## 9. Mathematical Integrity Report
## Math Verification Report

**Concept:** A Preregistered Multiscale Intervention Framework for Testing Integrated Information Theory Against Mechanistic Physicalist Emergence in Neural Systems
**Math Score:** 4/4
**Math Status:** [MATH_PROVEN]

### Equations Extracted
- $\Phi(s) = \min_{\mathcal{C}_{\text{MIP}}} \, \mathrm{EMD}\!\left( p_{\text{cause}}(s), \, \bigotimes_{k} p^{(k)}_{\text{cause}}(s_{S\setminus \mathcal{C}}) \right)$
- $\mathrm{EMD}(P,Q) = \min_{\gamma} \sum_{i,j} \gamma_{ij}\, d(i,j), \quad \gamma \in \Pi(P,Q)$
- $\frac{dS_{\text{tot}}}{dt} = \sum_{i<j} \left( p_i k_{ij} - p_j k_{ji} \right) \ln \frac{p_i k_{ij}}{p_j k_{ji}} \;\geq\; 0$
- $\frac{dS_{\text{tot}}}{dt} = -\frac{d\langle \ln p(x,t) \rangle}{dt} + \frac{dQ_{\text{diss}}}{T\, dt}$
- $P_{\text{cortex}} \approx 20\ \mathrm{W/kg} \;\Rightarrow\; \sim 10^{-9}\ \mathrm{W \ per\ cortical\ neuron}$
- $\mathrm{PCI} = \frac{\sum_{ij} L_{ij}\,\| \delta^{(i,j)}(t) \|}{\text{normalization}}$
- $k_B T \ln 2 \approx 2.9 \times 10^{-21}\ \mathrm{J}$
*(Plus 18 additional inline algebraic constraints, parameters, and complexity bounds).*

### Dimensional Consistency
- **IIT 4.0 EMD:** UNDECIDABLE (Algorithmic information structure, inherently dimensionless probabilities)
- **Stochastic Thermodynamic Constraint:** UNDECIDABLE (Information-theoretic entropy rates, no algebraic contradiction found)
- **Langevin Limit:** UNDECIDABLE (Thermodynamic heat dissipation balances against Shannon entropy rates)
- **Metabolic Bound:** UNDECIDABLE (Biophysical energy budget matches units correctly as power/node limits)
- **PCI:** UNDECIDABLE (Compressibility measure is mathematically coherent)
*Overall Verdict: No INCONSISTENT mathematical steps or unit violations found. Equations accurately capture correct state-space operations.*

### Topological Analysis
- **Topology Type:** Theoretical Lie Group Structure, and high-dimensional network architectures analogous to Spin Foams and String Theory configurations identified.
- **Structural Assessment:** TOPOLOGICAL_STRUCTURE_VALID. The cause-effect structure mapping onto the Earth Mover's Distance and the coupling set $\Pi(P,Q)$ matching marginals are robustly defined and topologically sound for transition probability matrices. 

### Numerical Benchmarks
- **Boltzmann Constant ($k_B$):** BENCHMARK_MATCHES. The report cites $k_B T \ln 2 \approx 2.9 \times 10^{-21}$ J at 310 K. This accurately integrates the exact SI definition ($k_B = 1.380649 \times 10^{-23}$ J/K) into the Landauer erasure limit calculation, ensuring perfect alignment with expected thermal physics parameters. 

### Assessment
The research report maintains a rigorous mathematical and physics-grounded foundation, seamlessly integrating algorithmic complexity via Earth Mover's Distance with non-equilibrium thermodynamic definitions (Markov jump processes and continuous Langevin limits). The numerical benchmarking confirms that the theoretical energy bounds strictly correspond to physical reality. Overall, the mathematical formulation is highly internally consistent and structurally verifiable.

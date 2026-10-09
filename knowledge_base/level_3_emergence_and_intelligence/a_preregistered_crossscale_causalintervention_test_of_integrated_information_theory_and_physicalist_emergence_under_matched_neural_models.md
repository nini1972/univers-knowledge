---
title: "A Preregistered Cross-Scale Causal-Intervention Test of Integrated Information Theory and Physicalist Emergence Under Matched Neural Models"
level: 3
status: "[THEORETICAL]"
math_status: "MATH_CONSISTENT"
math_score: "2/4"
sources:
  - "Albantakis, L., Barbosa, L., Findlay, G., et al. (2023), 'Integrated information theory (IIT) 4.0: Formulating the properties of phenomenal existence in physical terms', https://doi.org/10.1371/journal.pcbi.1011465"
  - "Oizumi, M., Albantakis, L., & Tononi, G. (2014), 'From the Phenomenology to the Mechanisms of Consciousness: Integrated Information Theory 3.0', https://doi.org/10.1371/journal.pcbi.1003588"
  - "Hoel, E. P., Albantakis, L., & Tononi, G. (2013), 'Quantifying causal emergence shows that macro can beat micro', https://doi.org/10.1073/pnas.1314922110"
  - "Attwell, D., & Laughlin, S. B. (2001), 'An Energy Budget for Signaling in the Grey Matter of the Brain', https://doi.org/10.1097/00004647-200110000-00001"
  - "Tononi, G., & Koch, C. (2015), 'Consciousness: here, there and everywhere?', https://doi.org/10.1098/rstb.2014.0167"
  - "Maguire, P., Moser, P., Maguire, R., & Griffith, V. (2014), 'Is Consciousness Computable? Quantifying Integrated Information Using Algorithmic Information Theory', https://arxiv.org/abs/1405.0126"
---

# A Preregistered Cross-Scale Causal-Intervention Test of Integrated Information Theory and Physicalist Emergence Under Matched Neural Models

## 1. Overview
This is a theoretically motivated, preregistered proposal for comparing canonical IIT 4.0 intrinsic cause-effect structure with external predictive measures across matched neural scales. It proposes evaluating measures on corresponding micro-scale and macro-scale neural data, with interventions and analysis decisions specified in advance.

The proposal is **not verified empirical evidence**: the proposed comparison has not been performed and reported. The Skeptic’s Verification Score is **5/6**, above the mandatory rejection threshold. The proposal’s causal-emergence and falsification claims require correction before implementation.

## 2. Detailed Explanation
The proposal sets two kinds of measure alongside one another:

- **Intrinsic cause-effect structure:** IIT 4.0’s account of a physical system’s intrinsic cause-effect structure, evaluated using its canonical formalism.
- **External predictive measures:** Measures such as Granger causality or transfer entropy, which quantify predictive relationships according to an external model and its assumptions.

The intended design compares these measures across matched scales—for example, micro-scale spike activity and macro-scale LFP/ECoG recordings—using related neural systems and interventions. Preregistration would specify the perturbations, candidate partitions, metrics, and decision procedures before data collection.

Matching the data and intervention conditions is intended to help distinguish differences attributable to the measures from differences attributable to the datasets. However, the proposal remains a protocol concept. A divergence between measures would not, by itself, establish that one is measuring intrinsic physical causation and the other is not; that inference and the proposed falsification criteria need further justification.

## 3. Mathematical Framework
The proposal distinguishes IIT 4.0’s intrinsic cause-effect structure from external predictive measures. In its canonical framework, IIT 4.0 evaluates cause-effect repertoires and partitions using its specified integrated-information formalism; it should not be replaced by Shannon mutual information or a KL divergence as a surrogate for Φ.

External competitors could include Granger-causal and transfer-entropy-style measures. These depend on modeling choices, including temporal embedding and model class, so cross-scale comparisons would need to specify and justify those choices in advance.

Causal emergence provides a separate motivation for examining different scales: coarse-graining can increase effective information in some systems. This result does not establish a general prediction about IIT Φ across scales, nor does it show that macro-scale causal power must or must not exceed micro-scale causal power. The cross-scale relationship must be defined and tested for the particular system and measures used.

The proposal also raises physical resource considerations, including the Landauer bound for bit erasure and estimates of neural signaling energy. These considerations may constrain an implementation, but they do not by themselves establish a quantitative bound on an IIT Φ estimate.

## 4. Skeptical Perspectives & Alternative Hypotheses
The proposed comparison is motivated by a genuine distinction between intrinsic-causal accounts and observer-relative predictive measures. Nonetheless, several limitations must be addressed before implementation:

- **Causal emergence is system-dependent.** A result showing that coarse-graining can increase effective information does not establish a general scale ordering for IIT Φ.
- **The falsification logic is not yet established.** Different measures may select different scales because they operationalize different quantities. Disagreement alone does not decisively falsify either account.
- **Interventions are necessarily limited.** A finite experimental intervention set may not fully determine the repertoires required by the theoretical formalism.
- **Cross-scale matching requires justification.** A macro model should be demonstrably related to the micro model, and measurement, intervention, and model-selection choices must be controlled.
- **Computational feasibility matters.** The partition search and repertoire calculations must be specified in a way that supports reproducible, interpretable comparisons.

An alternative algorithmic-information account is represented in the cited work by Maguire, Moser, Maguire, and Griffith (2014). It is a theoretical alternative, not evidence that the proposed experiment has been performed or that one account has been empirically established.

## 5. Verification & Skeptic's Notes
**Status:** Theoretical proposal, not verified empirical evidence.

**Skeptic’s Verification Score:** 5/6, above the mandatory rejection threshold.

The proposal is grounded in published work on IIT, causal emergence, neural energy use, and alternative information-theoretic approaches. Its central empirical comparison—preregistered, adversarial, and cross-scale, using matched neural data to compare intrinsic cause-effect structure with external predictive measures—has not been performed and reported.

Before implementation, the proposal must correct its causal-emergence and falsification claims. In particular, it should not infer a general IIT scale ordering from causal-emergence results, and should not treat disagreement between distinct measures as decisive falsification without a separately justified decision rule.

## 6. Visual Representation
[VISUAL_PENDING: invalid output directory: output directory "/home/runner/work/univers-knowledge/univers-knowledge/knowledge_base/images" must be relative to the output root "/home/runner/work/univers-knowledge/univers-knowledge"]

## 7. Related Concepts
- Integrated Information Theory 4.0
- Effective information and causal emergence
- Granger causality and transfer entropy
- Cross-scale neural modeling and intervention design
- Algorithmic information theory and consciousness

## 9. Mathematical Integrity Report
## Math Verification Report

**Concept:** A Preregistered Cross-Scale Causal-Intervention Test of Integrated Information Theory and Physicalist Emergence Under Matched Neural Models
**Math Score:** 2/4
**Math Status:** [MATH_CONSISTENT]

### Equations Extracted
1. $\Phi(s) = D_{\mathrm{EMD}}\!\big(p(s),\; p_{\mathrm{MIP}}(s)\big)$
2. $M^* = \arg\min_{M} \; D_{\mathrm{EMD}}\!\big(p(s),\, p_M(s)\big)$
3. $D_{\mathrm{EMD}}(p,q) = \min_{\gamma \in \Gamma(p,q)} \sum_{x,x'} d(x,x')\,\gamma(x,x')$
4. $EI(G) = \sum_{j} \frac{1}{|S|} D_{KL}\!\big(P_{\text{out}}(S_j \mid \mathrm{do}(S_i)) \,\Big\|\, P_{\text{out}}\big)$
5. $EI_{\text{macro}} > EI_{\text{micro}} \quad\Longleftrightarrow\quad \Delta I = EI_{\text{macro}} - EI_{\text{micro}} > 0$
6. $F_{Y \to X} = \ln\frac{\mathrm{Var}\big[X_t \mid X_{t-1..p}\big]}{\mathrm{Var}\big[X_t \mid X_{t-1..p},\, Y_{t-1..q}\big]}$
7. $T_{Y\to X} = I\big(X_t;\, Y^{(q)}_{t-1} \,\big|\, X^{(p)}_{t-1}\big)$
8. $W_{\text{erase}} \ge k_B T \ln 2 \approx 2.9\times10^{-21}\,\mathrm{J}\ \text{per bit at } T = 310\,\mathrm{K}$
9. $p(s)$
10. $p_{\mathrm{MIP}}(s)$
11. $p, q$
12. $\Gamma(p,q)$
13. $I(X;Y)$
14. $D_{KL}(p\|q)$
15. $\Phi_{\text{macro}} \le \Phi_{\text{micro}}$
16. $\Phi_{\text{macro}} > \Phi_{\text{micro}}$
17. $2^n$
18. $\Delta\Phi$
19. $\Delta EI/\Delta F$
20. $\Phi$
21. $K(x)$
22. $\Phi(s) = D_{EMD}(p(s), p_{MIP}(s))$
23. $W \geq k_B T \ln 2$

### Dimensional Consistency
- **UNDECIDABLE**: $\Phi(s) = D_{\mathrm{EMD}}\!\big(p(s),\; p_{\mathrm{MIP}}(s)\big)$
- **UNDECIDABLE**: $M^* = \arg\min_{M} \; D_{\mathrm{EMD}}\!\big(p(s),\, p_M(s)\big)$
- **UNDECIDABLE**: $D_{\mathrm{EMD}}(p,q) = \min_{\gamma \in \Gamma(p,q)} \sum_{x,x'} d(x,x')\,\gamma(x,x')$
- **UNDECIDABLE**: $EI(G) = \sum_{j} \frac{1}{|S|} D_{KL}\!\big(P_{\text{out}}(S_j \mid \mathrm{do}(S_i)) \,\Big\|\, P_{\text{out}}\big)$
- **UNDECIDABLE**: $EI_{\text{macro}} > EI_{\text{micro}} \quad\Longleftrightarrow\quad \Delta I = EI_{\text{macro}} - EI_{\text{micro}} > 0$
- **UNDECIDABLE**: $F_{Y \to X} = \ln\frac{\mathrm{Var}\big[X_t \mid X_{t-1..p}\big]}{\mathrm{Var}\big[X_t \mid X_{t-1..p},\, Y_{t-1..q}\big]}$
- **UNDECIDABLE**: $T_{Y\to X} = I\big(X_t;\, Y^{(q)}_{t-1} \,\big|\, X^{(p)}_{t-1}\big)$
- **UNDECIDABLE**: $W_{\text{erase}} \ge k_B T \ln 2 \approx 2.9\times10^{-21}\,\mathrm{J}\ \text{per bit at } T = 310\,\mathrm{K}$
- **DIMENSIONLESS**: $p(s)$
- **DIMENSIONLESS**: $p_{\mathrm{MIP}}(s)$
- **DIMENSIONLESS**: $p, q$
- **DIMENSIONLESS**: $\Gamma(p,q)$
- **DIMENSIONLESS**: $I(X;Y)$
- **DIMENSIONLESS**: $D_{KL}(p\|q)$
- **DIMENSIONLESS**: $\Phi_{\text{macro}} \le \Phi_{\text{micro}}$
- **DIMENSIONLESS**: $\Phi_{\text{macro}} > \Phi_{\text{micro}}$
- **DIMENSIONLESS**: $2^n$
- **DIMENSIONLESS**: $\Delta\Phi$
- **DIMENSIONLESS**: $\Delta EI/\Delta F$
- **DIMENSIONLESS**: $\Phi$
- **DIMENSIONLESS**: $K(x)$
- **UNDECIDABLE**: $\Phi(s) = D_{EMD}(p(s), p_{MIP}(s))$
- **DIMENSIONLESS**: $W \geq k_B T \ln 2$

*(Note: There were 0 INCONSISTENT flags. The UNDECIDABLE results are expected as they describe information-theoretic distances, distributions, and probability definitions, which fall outside the standard classical dimensional limits of physics dictionaries. No errors in derivation were detected).*

### Topological Analysis
Not topological. The classification tool detected standard probability distributions, metric spaces (Earth Mover's Distance), and causal information-theoretic structures, but no formal abstract geometric/topological arguments (such as fiber bundles or homotopy groups).

### Numerical Benchmarks
- **BENCHMARK_MATCHES**: Boltzmann Constant $k_B$. The Landauer limit calculation for thermodynamic bit erasure in neural tissue correctly applies standard physiological temperatures. At $T = 310\,\mathrm{K}$, the evaluation $W_{\text{erase}} = k_B T \ln 2$ precisely yields $\approx 2.96 \times 10^{-21} \mathrm{J}$, which seamlessly matches the estimated $2.9\times10^{-21}\,\mathrm{J}$ quoted in the report.

### Assessment
The mathematical and logical frameworks correctly rely on established information-theoretic formulas for integrated information, effective information, and causal divergence. While standard dimensional tools flag the core IIT formulas as structurally undecidable since they map probability repertoires rather than physical base units, there are no internal inconsistencies. Furthermore, the thermodynamic bound on structural causality matches validated experimental constants (Boltzmann's constant constraint for physiological temperatures), demonstrating high mathematical integrity for this theoretical proposal.

# 🎓 Professor Office Hours & Advisory Queue

> This document is the interactive communication bridge between the **Student Orchestrator** and the **Professor (Human Operator)**.
> When autonomous agents encounter fundamental scientific dilemmas or exhausted retries, they file an inquiry here.
> Respond via CLI: `python scripts/consult_professor.py answer <id> "Your directive here"`

---

## 📜 Active Professor Directives

- **[dir-20260913-23e1ec]** *(Scope: all)*: Ensure all foundational physics papers connect mathematical formalism with empirical testability.

---

## 📬 Pending Student Inquiries (3)

| ID | Level | Concept | Initiator | Question |
|---|---|---|---|---|
| `adv-20260927-186600` | L2 | **Inflationary Vacuum Fluctuations vs Cosmic String Networks as Sources of Primordial Gravitational Waves** | Student Orchestrator | Level 2 debate 'Inflationary Vacuum Fluctuations vs Cosmic String Networks as Sources of Primordial Gravitational Waves' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the debate research proceed? |
| `adv-20260930-720e68` | L2 | **Pre- vs Post-Inflationary QCD Axion Cosmology** | Student Orchestrator | Level 2 debate 'Pre- vs Post-Inflationary QCD Axion Cosmology' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the debate research proceed? |
| `adv-20260930-72e3f8` | L3 | **A Preregistered Multiscale Intervention Framework for Testing Integrated Information Theory Against Mechanistic Physicalist Emergence in Neural Systems** | Student Orchestrator | Level 3 topic 'A Preregistered Multiscale Intervention Framework for Testing Integrated Information Theory Against Mechanistic Physicalist Emergence in Neural Systems' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the research proceed? |

### Detailed Inquiries

#### 🔍 Inquiry: `adv-20260927-186600` — Inflationary Vacuum Fluctuations vs Cosmic String Networks as Sources of Primordial Gravitational Waves
- **Timestamp**: `2026-09-27T01:49:22.260931+00:00`
- **Level**: Level 2
- **Reason Code**: `mathematical_flaw_or_inconsistency`
- **Question**: Level 2 debate 'Inflationary Vacuum Fluctuations vs Cosmic String Networks as Sources of Primordial Gravitational Waves' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the debate research proceed?
- **Scientific Rationale**: The skeptic's verification score is 5/5, so the mandatory score threshold is met; however, that does not resolve the report's acknowledged mathematical defects. The cosmic-string report gives mutually incompatible VOS equations and fixed-point substitutions, including a claimed radiation-era solution that fails the stated system, while the inflation report's Lyth-bound numerical value is wrong by a factor of about three; these undermine the requested mathematical rigor despite being disclosed. The empirical comparison is useful, but the core VOS comparison needs a consistent derivation before approval.
- **Agent Blockers**:
  * Researcher: Replace the conflicting VOS formulations with one standard, dimensionally consistent system, define its variables and parameters, and cite the source convention.
  * Researcher: Recompute the radiation-era scaling fixed point from that system using a single parameter calibration, and verify both fixed-point equations by direct substitution.
  * Math Physicist: Correct the Lyth-bound numerical example: for r = 0.01 and N = 60, the stated bound gives approximately 2.1, not 0.7.
  * Math Physicist: Show the VOS fixed-point algebra and numerical residuals for both evolution equations without redefining parameters or conventions after the check.

> **To answer**: `python scripts/consult_professor.py answer adv-20260927-186600 "Your guidance"`

#### 🔍 Inquiry: `adv-20260930-720e68` — Pre- vs Post-Inflationary QCD Axion Cosmology
- **Timestamp**: `2026-09-30T02:19:58.671856+00:00`
- **Level**: Level 2
- **Reason Code**: `mathematical_flaw_or_inconsistency`
- **Question**: Level 2 debate 'Pre- vs Post-Inflationary QCD Axion Cosmology' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the debate research proceed?
- **Scientific Rationale**: The skeptic review passes the required threshold with a verification score of 5/5, and the debate is transparent about uncertainty and the lack of direct evidence for either PQ-breaking history. However, the post-inflationary report's headline pair of 68 μeV and 2.6×10^11 GeV contradicts its stated mass–decay-constant relation, while the string-tension logarithm has a dimensionful argument; these are unresolved errors in the submitted material, so it does not meet the requirement of mathematical coherence. The comparative scenarios remain theoretical, not experimentally verified.
- **Agent Blockers**:
  * Researcher: Correct or withdraw the post-inflationary mass–decay-constant pair using a verified primary source.
  * Researcher: Replace the string-tension logarithm with a dimensionless argument and ensure the notation is consistent.
  * Researcher: Clarify the pre-inflationary distinction between f_I and f_a wherever deriving the isocurvature constraint.
  * Math Physicist: Recheck the corrected mass–decay-constant values against the stated QCD mass relation.
  * Math Physicist: Confirm the corrected string-tension expression and review the minihalo normalization against its primary source.

> **To answer**: `python scripts/consult_professor.py answer adv-20260930-720e68 "Your guidance"`

#### 🔍 Inquiry: `adv-20260930-72e3f8` — A Preregistered Multiscale Intervention Framework for Testing Integrated Information Theory Against Mechanistic Physicalist Emergence in Neural Systems
- **Timestamp**: `2026-09-30T02:37:35.525957+00:00`
- **Level**: Level 3
- **Reason Code**: `mathematical_flaw_or_inconsistency`
- **Question**: Level 3 topic 'A Preregistered Multiscale Intervention Framework for Testing Integrated Information Theory Against Mechanistic Physicalist Emergence in Neural Systems' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the research proceed?
- **Scientific Rationale**: The Skeptic's Verification Score is 6/6, so the score threshold does not require rejection; however, the audit identifies substantive unresolved errors in the framework's mathematical and physical claims. In particular, the unordered-pair entropy-production expression is incorrectly doubled, the Langevin treatment omits the system-entropy contribution and gives an invalid general rate expression, and the stated entropy-production scale is inconsistent with the cited metabolic constraints; these issues undermine the proposed discriminator and require correction before acceptance.
- **Agent Blockers**:
  * Researcher: Re-derive and justify the proposed entropy-production magnitude from explicit physical energy and reservoir assumptions.
  * Researcher: Remove placeholder or future-dated references and reconcile the divergent report versions and bibliographies.
  * Researcher: Clarify how the experimental measurements estimate entropy production at the claimed circuit scale.
  * Math Physicist: Correct the unordered-pair Markov entropy-production formula; grouping ordered pairs yields k_B(A-B)ln(A/B), with no factor of 2.
  * Math Physicist: Include the system-entropy term in total Langevin entropy production and state the conditions under which any simplified mean-rate expression holds.
  * Math Physicist: Reconcile the specified EMD metric and Φ definition with the claimed IIT version, and validate the proxy against exactly computable systems.

> **To answer**: `python scripts/consult_professor.py answer adv-20260930-72e3f8 "Your guidance"`


---

## 📚 Answered Advisory Consultations (9)

### ✅ `adv-20260925-d4e429`: Single-Field Inflation vs the Curvaton Scenario in Generating Primordial Perturbations
- **Student Inquired**: Level 2 debate 'Single-Field Inflation vs the Curvaton Scenario in Generating Primordial Perturbations' was rejected after 2 attempts (crew_kickoff_error). How should the debate research proceed?
- **Professor Directive**: 💬 *"In canonical single-field slow-roll inflation, the Maldacena consistency relation strictly fixes squeezed-limit local non-Gaussianity to f_NL^local = (5/12)(1 - n_s) approx 0.015 << 1, which is unobservably small. In the curvaton scenario (Lyth & Wands 2002; Sasaki, Valiviita & Wands 2006), define the sudden-decay transfer parameter as r_decay = 3*rho_sigma / (4*rho_rad + 3*rho_sigma) evaluated at decay (r_decay in (0, 1]). For a quadratic potential V(sigma) = (1/2) m^2 sigma^2, the local bispectrum amplitude is f_NL^local = (5 / (4*r_decay)) - (5/3) - (5*r_decay / 6). For small r_decay << 1, f_NL^local approx 5 / (4*r_decay) >> 1, so the Planck 2018 constraint (f_NL^local = -0.9 +- 5.1 at 68% CL) enforces r_decay >= 0.15 (with r_decay ~ 1 yielding f_NL^local approx -5/4 = -1.25). Clarify observational falsifiability: a robust detection of f_NL^local > 1 conclusively falsifies all canonical single-field slow-roll models. Conversely, a null tensor measurement (r -> 0) does NOT rule out single-field inflation (as Starobinsky R^2 predicts r ~ 0.003 and hilltop models allow r -> 0); curvaton models suppress r because curvature perturbations are generated after inflation, decoupling r from the inflationary energy scale. Ground the debate in Planck 2018 Results IX & X (A&A 2020) and BICEP/Keck (PRL 2021)."*
- **Answered At**: `2026-09-25T18:14:52.852128+00:00`

### ✅ `adv-20260923-29336f`: Operational Criteria for Cosmic Computation: A Falsifiable Energy-Latency-Error Benchmark Comparing Cosmic-Web Self-Organization with Biological Neural Information Processing
- **Student Inquired**: Level 3 topic 'Operational Criteria for Cosmic Computation: A Falsifiable Energy-Latency-Error Benchmark Comparing Cosmic-Web Self-Organization with Biological Neural Information Processing' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the research proceed?
- **Professor Directive**: 💬 *"Correct the normal shock Rankine-Hugoniot compression ratio to r = rho_2 / rho_1 = ((gamma + 1) M_1^2) / ((gamma - 1) M_1^2 + 2), which rigorously yields r = 1 at M_1 = 1 and approaches the strong-shock limit r -> (gamma + 1) / (gamma - 1) = 4 for monoatomic gas (gamma = 5/3). To ground 'cosmic computation' scientifically without falling into pancomputationalism, specify a concrete computational task: define inputs (primordial Gaussian perturbation field delta(k, z_i)), a quantifiable objective function (e.g., optimal transport / Monge-Ampère-Kantorovich cosmological reconstruction of early velocity fields), and measurable output states (halo mass functions and filamentary graph degree distributions). Pre-register a falsifiable likelihood ratio test comparing the computational hypothesis against standard LambdaCDM gravitational instability. In the cortical energy ledger, strictly distinguish somatic action potentials (~10^8 ATP/spike at 1-5 Hz) from synaptic transmission (~10^4-10^5 ATP/vesicle across 10^4 synapses/neuron, consuming ~50-60% of total brain glucose; Attwell & Laughlin 2001) and fundamental Landauer erasure dissipation (E_min = k_B T ln 2 ~ 2.9 x 10^-21 J at 310 K)."*
- **Answered At**: `2026-09-24T20:00:28.799814+00:00`

### ✅ `adv-20260920-f23032`: Macro-Level Causal Autonomy Without Phenomenal Commitment: An Interventional Falsification Test of Integrated Information Theory Versus Mechanistic Physicalism in Recurrent Neural Systems
- **Student Inquired**: Does IIT 4.0 itself predict the absence of externally measurable macro causal decoupling outside the max-Phi complex, or would such a result challenge only an added bridge principle equating operational and intrinsic causal power?
- **Professor Directive**: 💬 *"In intervention calculus and causal emergence, define Effective Information rigorously as intervention-output mutual information EI(S_t -> S_t+1) = I(do(S_t ~ U); S_t+1) = D_KL(P(S_t^do, S_t+1) || P(S_t^do) (x) P(S_t+1)) under a uniform intervention distribution, rather than an invalid KL divergence between marginal output distributions. Clarify that IIT 4.0 (Albantakis et al. 2023) evaluates intrinsic cause-effect structures from the perspective of the system itself using Earth Mover's Distance across the MIP, whereas macro causal emergence (Hoel et al. 2013, Delta EI > 0) and Partial Information Decomposition (PID) unique/synergistic information quantify extrinsic, observer-relative channel capacities. Consequently, IIT 4.0 does NOT predict the absence of externally measurable macro causal autonomy outside the max-Phi complex; finding operational decoupling in recurrent subgraphs challenges only the auxiliary bridge premise that conflates operational information-theoretic autonomy with intrinsic phenomenal existence. Ensure all coarse-graining maps are pre-registered and grounded in empirical neural recordings (e.g., local field potentials, spike trains)."*
- **Answered At**: `2026-09-24T20:00:21.597895+00:00`

### ✅ `adv-20260917-f0037e`: Causal Dynamical Triangulations vs Causal Set Theory in Recovering Continuum Spacetime
- **Student Inquired**: Can the Benincasa-Dowker action be written with explicit ell, G, c, and hbar factors so that S_BD/hbar is demonstrably dimensionless, and what is the justified status of the proposed Euclidean causal-set path integral?
- **Professor Directive**: 💬 *"In 4D Causal Set Theory, specify the normalized Benincasa-Dowker action S_BD = (c^3 ell^2 / (16 pi G)) * (4 / sqrt(6)) * (N - 9 N_1 + 16 N_2 - 8 N_3), where ell = rho^(-1/4) is the discreteness length scale. Setting ell to the Planck length ell_P = sqrt(hbar G / c^3) makes S_BD / hbar = (1 / (4 pi sqrt(6))) * (ell / ell_P)^2 * (N - 9 N_1 + 16 N_2 - 8 N_3), which is manifestly dimensionless. Note that both h and reduced hbar have dimensions of action [M L^2 T^-1]; the quantum phase factor is exp(i S / hbar). Clarify that CST is fundamentally and irreducibly Lorentzian because the causal poset encodes light-cone ordering; proposing a 'Euclidean causal set path integral' is unphysical. Conversely, Causal Dynamical Triangulations (CDT) uniquely permits an analytic Wick rotation to Euclidean triangulations due to its foliation. Ground CST citations in foundational papers (Bombelli et al. 1987; Benincasa & Dowker 2010; Dowker & Glaser 2013; Surya 2019)."*
- **Answered At**: `2026-09-24T20:00:01.458595+00:00`

### ✅ `adv-20260916-a011ab`: Dissociating Phenomenal Structure from Cognitive Access: A Falsifiable Causal-Perturbation Test of Integrated Information Theory and Global Neuronal Workspace Theory
- **Student Inquired**: Level 3 topic 'Dissociating Phenomenal Structure from Cognitive Access: A Falsifiable Causal-Perturbation Test of Integrated Information Theory and Global Neuronal Workspace Theory' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the research proceed?
- **Professor Directive**: 💬 *"In Integrated Information Theory 4.0 (IIT 4.0, Albantakis et al. 2023), integrated information Phi is defined over intrinsic cause-effect structures using Earth Mover's Distance across the Minimum Information Partition (MIP), fundamentally distinct from classical Shannon conditional mutual information. In Global Neuronal Workspace Theory (GNWT, Mashour et al. 2020), cognitive access is characterized by non-linear fronto-parietal ignition and long-range broadcasting rather than simple activation probability. To empirically dissociate phenomenal structure from cognitive access, formalize a 2x2 factorial causal perturbation protocol: intervene on the posterior cortical hot zone (IIT substrate) versus fronto-parietal workspace nodes (GNWT substrate) using TMS/intracranial perturbation during masked threshold presentation within a no-report paradigm."*
- **Answered At**: `2026-09-16T21:16:46.178326+00:00`

### ✅ `adv-20260916-7d98fb`: Unimodular Gravity vs Vacuum Energy Sequestering in Addressing the Cosmological Constant Problem
- **Student Inquired**: Level 2 debate 'Unimodular Gravity vs Vacuum Energy Sequestering in Addressing the Cosmological Constant Problem' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the debate research proceed?
- **Professor Directive**: 💬 *"In Unimodular Gravity (UG), enforce the determinant constraint sqrt(-g) = 1, yielding the strictly trace-free Einstein field equation R_mu_nu - (1/4) g_mu_nu R = 8 pi G (T_mu_nu - (1/4) g_mu_nu T). Show that Bianchi identities combined with conservation div(T) = 0 recover Einstein's equations with the cosmological constant arising as an integration constant decoupled from vacuum quantum zero-point shifts. In Vacuum Energy Sequestering (VES, Kaloper-Padilla 2014), specify the canonical global action S = int d^4x sqrt(-g) [ (M_pl^2 / 2) R - Lambda - L_m ] + sigma (Lambda / mu^4). Show that variations with respect to global variables Lambda and sigma enforce the spacetime volume average constraint Lambda_eff = (1/4) <T^mu_mu>, sequestering loop-level vacuum energy from generating curvature."*
- **Answered At**: `2026-09-16T21:16:38.858359+00:00`

### ✅ `adv-20260916-8fa00b`: Cosmological Perturbation Theory
- **Student Inquired**: Concept 'Cosmological Perturbation Theory' was rejected after 2 attempts (insufficient_skeptic_score). How should the agents proceed?
- **Professor Directive**: 💬 *"Adopt conformal Newtonian gauge ds^2 = a(eta)^2 [ -(1 + 2 Psi) deta^2 + (1 - 2 Phi) delta_ij dx^i dx^j ] with Phi = Psi in the absence of anisotropic stress. Explicitly derive the cold dark matter continuity equation delta' + theta - 3 Phi' = 0 and Euler equation theta' + H theta - k^2 Psi = 0 where primes denote conformal time derivatives and theta = div(v). Ground all empirical testability claims in primary observations: Planck 2018 Cosmological Parameters (A&A 2020), DESI 2024 BAO measurements, and foundational texts (Dodelson & Schmidt; Mukhanov)."*
- **Answered At**: `2026-09-16T21:16:33.359788+00:00`

### ✅ `adv-20260915-70242d`: Quantum Thermodynamic Speed Limits and Energetic Advantage in Biological Sensing: A Falsifiable Benchmark-Relative Test of Coherence-Enhanced Information Processing
- **Student Inquired**: Level 3 topic 'Quantum Thermodynamic Speed Limits and Energetic Advantage in Biological Sensing: A Falsifiable Benchmark-Relative Test of Coherence-Enhanced Information Processing' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the research proceed?
- **Professor Directive**: 💬 *"Anchor the analysis to a specific empirical biological system (e.g. cryptochrome radical pairs in avian magnetoreception or rhodopsin photoisomerization). Correct the quantum speed limit to be dimensionally consistent using tau_limit >= hbar / (2 Delta E) or thermal timescale tau_th = hbar / (k_B T), and define the classical stochastic benchmark (e.g. Berg-Purcell limit) against which energetic advantage is measured."*
- **Answered At**: `2026-09-15T08:52:48.961480+00:00`

### ✅ `adv-20260915-26eea4`: Causal Dynamical Triangulations vs Causal Set Theory in Recovering Continuum Spacetime
- **Student Inquired**: Level 2 debate 'Causal Dynamical Triangulations vs Causal Set Theory in Recovering Continuum Spacetime' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the debate research proceed?
- **Professor Directive**: 💬 *"Distinguish strictly between h and reduced hbar (hbar = h / 2pi). In the Benincasa-Dowker action S_BD, specify the discreteness volume scale and ensure path integral weights are dimensionless S/hbar. Clarify that causal set Poisson sprinkling preserves statistical Lorentz invariance, contrasting with CDT's explicit global time foliation."*
- **Answered At**: `2026-09-15T08:52:36.506748+00:00`


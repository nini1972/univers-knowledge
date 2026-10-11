# 🎓 Professor Office Hours & Advisory Queue

> This document is the interactive communication bridge between the **Student Orchestrator** and the **Professor (Human Operator)**.
> When autonomous agents encounter fundamental scientific dilemmas or exhausted retries, they file an inquiry here.
> Respond via CLI: `python scripts/consult_professor.py answer <id> "Your directive here"`

---

## 📜 Active Professor Directives

- **[dir-20260913-23e1ec]** *(Scope: all)*: Ensure all foundational physics papers connect mathematical formalism with empirical testability.

---

## 📬 Pending Student Inquiries (1)

| ID | Level | Concept | Initiator | Question |
|---|---|---|---|---|
| `adv-20261011-ce787b` | L2 | **Perturbative Reheating vs Parametric-Resonance Preheating** | Student Orchestrator | Level 2 debate 'Perturbative Reheating vs Parametric-Resonance Preheating' was rejected after 2 attempts (crew_kickoff_error). How should the debate research proceed? |

### Detailed Inquiries

#### 🔍 Inquiry: `adv-20261011-ce787b` — Perturbative Reheating vs Parametric-Resonance Preheating
- **Timestamp**: `2026-10-11T01:45:22.120434+00:00`
- **Level**: Level 2
- **Reason Code**: `crew_kickoff_error`
- **Question**: Level 2 debate 'Perturbative Reheating vs Parametric-Resonance Preheating' was rejected after 2 attempts (crew_kickoff_error). How should the debate research proceed?
- **Scientific Rationale**: Rejected due to crew_kickoff_error.

> **To answer**: `python scripts/consult_professor.py answer adv-20261011-ce787b "Your guidance"`


---

## 📚 Answered Advisory Consultations (19)

### ✅ `adv-20261009-ec789d`: Perturbative Reheating vs Parametric-Resonance Preheating
- **Student Inquired**: Level 2 debate 'Perturbative Reheating vs Parametric-Resonance Preheating' was rejected after 2 attempts (crew_kickoff_error). How should the debate research proceed?
- **Professor Directive**: 💬 *"When simulating and analyzing inflation reheating, decompose the dynamics into three distinct chronological phases: (1) Non-perturbative preheating via parametric resonance governed by the Mathieu equation d^2 chi_k / dz^2 + [A_k - 2 q cos(2 z)] chi_k = 0 for broad resonance q = g^2 Phi_0^2 / (4 m^2) >> 1, yielding explosive occupation numbers n_k ~ exp(2 mu_k m t); (2) Non-linear rescattering, turbulence, and fragmentation halting exponential growth before complete inflaton depletion; (3) Final perturbative decay (Gamma_phi) and thermalization establishing the radiation-dominated era with T_reh approx (90 / (pi^2 g_*))^(1/4) sqrt(Gamma_phi M_Pl). Structure the debate report with clear modular headings, exact equation blocks, and empirical bounds from BBN (T_reh >= 4 MeV) and CMB constraints on the equation of state w_reheat to prevent token overflow or parse failures."*
- **Answered At**: `2026-10-10T13:39:34.046922+00:00`

### ✅ `adv-20261006-540db7`: A Dimensionally Consistent Landauer-Based Framework for Comparing Energy–Latency–Error Trade-offs in Neural Computation and Cosmic-Web Self-Organization
- **Student Inquired**: Level 3 topic 'A Dimensionally Consistent Landauer-Based Framework for Comparing Energy–Latency–Error Trade-offs in Neural Computation and Cosmic-Web Self-Organization' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the research proceed?
- **Professor Directive**: 💬 *"In the finite-time thermodynamic trade-off model C(tau) = W_2^2 / (mu * tau) + E_0 * tau + E_erasure, rigorously derive the optimal latency minimizer by differentiating with respect to tau: dC/dtau = -W_2^2 / (mu * tau^2) + E_0 = 0, yielding the unique minimum tau* = sqrt(W_2^2 / (mu * E_0)), with second derivative d^2C/dtau^2 = 2 W_2^2 / (mu * tau^3) > 0. Verify dimensional consistency: with [W_2^2 / mu] = J*s and [E_0] = J/s = W, tau* has SI units of seconds. Clearly categorize this trade-off as a phenomenological cost model rather than a fundamental thermodynamic conservation law. When drawing parallels to cosmic-web structure formation, specify probability-normalized Wasserstein mass distributions to preserve rigorous SI units."*
- **Answered At**: `2026-10-10T13:39:25.561348+00:00`

### ✅ `adv-20261006-79c5cc`: Pre- vs Post-Inflationary QCD Axion Cosmology
- **Student Inquired**: Level 2 debate 'Pre- vs Post-Inflationary QCD Axion Cosmology' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the debate research proceed?
- **Professor Directive**: 💬 *"In pre-inflationary QCD axion scenarios, calibrate the inflationary Hubble scale strictly using the standard single-field slow-roll relation H_inf = pi * M_Pl * sqrt(r * A_s / 2) approx 8.4 * 10^13 * sqrt(r / 0.01) GeV with Planck amplitude A_s approx 2.1 * 10^-9. For the tensor-to-scalar ratio corresponding to the axion isocurvature limit H_inf <= 10^9 GeV * (f_I / 10^12 GeV), calculate r consistently: (H_inf / (8.4 * 10^14 GeV))^2 yields r <= 1.4 * 10^-12 (approx 10^-13 to 10^-12 depending on f_I), resolving the erroneous 5 * 10^-9 estimate. Enforce internal consistency across all tables, derivations, and summary figures between f_a, m_a, H_inf, and the derived tensor bound r."*
- **Answered At**: `2026-10-10T13:39:16.242818+00:00`

### ✅ `adv-20261004-ded465`: A Preregistered Cross-Scale Causal-Intervention Test of Integrated Information Theory and Physicalist Emergence Under Matched Neural Models
- **Student Inquired**: Level 3 topic 'A Preregistered Cross-Scale Causal-Intervention Test of Integrated Information Theory and Physicalist Emergence Under Matched Neural Models' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the research proceed?
- **Professor Directive**: 💬 *"In Integrated Information Theory 4.0 (Albantakis et al. 2023), define Phi strictly as the intrinsic difference evaluated via Earth Mover's Distance (EMD) over the cause-effect structure across the Minimum Information Partition (MIP): Phi(s) = D_EMD(p_unpartitioned(s), p_MIP(s)). Do not substitute symmetric mutual information or Kullback-Leibler divergences for canonical Phi. Withdraw the claim that IIT predicts Phi_macro <= Phi_micro; causal emergence (Phi_macro > Phi_micro) is explicitly demonstrated in coarse-grained logic networks (Hoel et al. 2013). Frame the empirical cross-scale test as an adversarial model comparison between intrinsic cause-effect power (IIT) and external predictive information / Granger causality across matched micro (spikes) and macro (LFP/ECoG) interventional datasets. Confine Landauer thermodynamic bounds to physical non-equilibrium bit erasure, using the Attwell & Laughlin (2001) metabolic budget for physical neural work."*
- **Answered At**: `2026-10-04T10:53:29.380420+00:00`

### ✅ `adv-20261004-984775`: Perturbative Reheating vs Parametric-Resonance Preheating
- **Student Inquired**: Level 2 debate 'Perturbative Reheating vs Parametric-Resonance Preheating' was rejected after 2 attempts (crew_kickoff_error). How should the debate research proceed?
- **Professor Directive**: 💬 *"In preheating via broad parametric resonance (Kofman, Linde & Starobinsky 1994, 1997), formulate the coupled field equations for an inflaton phi oscillating around V(phi) = (1/2) m^2 phi^2 coupled to scalar chi via (1/2) g^2 phi^2 chi^2. State the Mathieu equation for chi_k modes: d^2 chi_k / dz^2 + [A_k - 2 q cos(2 z)] chi_k = 0, where z = m t, A_k = k^2/(m^2 a^2) + 2 q, and resonance parameter q = g^2 Phi_0^2 / (4 m^2). When q >> 1 (broad resonance), particle production occurs in non-adiabatic bursts near phi = 0 with growth n_k ~ exp(2 mu_k m t) (mu_k ~ 0.1-0.2). Contrast with perturbative reheating (Abbott et al. 1982), where decay rate Gamma_phi yields reheat temperature T_reh approx (90 / (pi^2 g_*))^(1/4) sqrt(Gamma_phi M_Pl). Emphasize that non-linear backreaction, rescattering, and turbulence terminate parametric resonance before complete inflaton depletion, requiring final perturbative thermalization."*
- **Answered At**: `2026-10-04T10:53:21.404238+00:00`

### ✅ `adv-20261004-7abc86`: Black Hole Thermodynamics
- **Student Inquired**: Concept 'Black Hole Thermodynamics' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the agents proceed?
- **Professor Directive**: 💬 *"In Kerr-Newman black hole thermodynamics, write the exact Smarr formula derived from Euler's scaling theorem: M * c^2 = 2 * T_H * S_BH + 2 * Omega_H * J + Phi_H * Q, which in terms of surface gravity kappa and horizon area A is (kappa * c^2 * A) / (4 * pi * G) = M * c^2 - 2 * Omega_H * J - Phi_H * Q (strictly with coefficient 1 on Phi_H * Q). For primordial black hole evaporation, standard Hawking evaporation lifetime tau_evap = (5120 * pi * G^2 * M^3) / (hbar * c^4) equals the current age of the Universe (t_0 approx 13.8 Gyr) for M_* approx 5.1 * 10^11 kg (approx 5 * 10^14 g). Correct the mass scale: a 10^12 kg PBH has a lifetime of ~2.7 * 10^12 years and is NOT entering explosive evaporation today. Explicitly classify the classical area increase theorem as [VERIFIED] (Hawking 1971), while labeling semiclassical Hawking radiation and Bekenstein-Hawking entropy as [THEORETICAL]."*
- **Answered At**: `2026-10-04T10:53:13.686426+00:00`

### ✅ `adv-20261002-0098f8`: A Dimensionally Consistent Landauer-Based Framework for Comparing Energy–Latency–Error Trade-offs in Neural Computation and Cosmic-Web Self-Organization
- **Student Inquired**: Level 3 topic 'A Dimensionally Consistent Landauer-Based Framework for Comparing Energy–Latency–Error Trade-offs in Neural Computation and Cosmic-Web Self-Organization' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the research proceed?
- **Professor Directive**: 💬 *"Adopt the standard thermodynamic sign convention where heat dissipated into the environment is positive Q_env > 0, ensuring total entropy production Sigma_tot = Delta S_sys + Q_env / T >= 0 (for full bit erasure Delta S_sys = -k_B ln 2, yielding Q_env >= k_B T ln 2). For finite-time transitions of duration tau, formulate the optimal transport dissipation bound with explicit mobility mu (or drag gamma = 1/mu): Sigma_total >= W_2^2 / (mu * k_B * T * tau), ensuring correct energy units ([W_2^2 / (mu * tau)] = Joules). Do not invert inequalities between Wasserstein W_2 distance and Total Variation (TV). In applying this benchmark, emphasize that cosmic-web self-organization is an entropy-producing gravitational condensation process, distinct from logical entropy-erasing neural computation."*
- **Answered At**: `2026-10-04T10:53:05.862282+00:00`

### ✅ `adv-20260930-72e3f8`: A Preregistered Multiscale Intervention Framework for Testing Integrated Information Theory Against Mechanistic Physicalist Emergence in Neural Systems
- **Student Inquired**: Level 3 topic 'A Preregistered Multiscale Intervention Framework for Testing Integrated Information Theory Against Mechanistic Physicalist Emergence in Neural Systems' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the research proceed?
- **Professor Directive**: 💬 *"In stochastic thermodynamics, write the Markov jump process entropy production rate over unordered pairs {i,j} as dS_tot/dt = sum_{i < j} (p_i k_ij - p_j k_ji) ln(p_i k_ij / (p_j k_ji)), removing the erroneous factor of 2. In continuous Langevin dynamics, include both the system Shannon entropy change and environmental heat dissipation: dS_tot/dt = -d<ln p(x,t)>/dt + dQ_diss/(T dt). When testing IIT against mechanistic physicalism in multiscale neural systems, constrain circuit-level entropy production within biological metabolic limits (~20 W/kg or ~10^-9 W per cortical neuron; Attwell & Laughlin 2001). For IIT 4.0, define Phi using the canonical Earth Mover's Distance (EMD) over the system's transition probability matrix across the MIP, validating against small exactly solvable networks rather than ad-hoc heuristics."*
- **Answered At**: `2026-10-04T10:52:58.124603+00:00`

### ✅ `adv-20260930-720e68`: Pre- vs Post-Inflationary QCD Axion Cosmology
- **Student Inquired**: Level 2 debate 'Pre- vs Post-Inflationary QCD Axion Cosmology' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the debate research proceed?
- **Professor Directive**: 💬 *"In QCD axion cosmology (di Cortona et al. 2016, JHEP 01 (2016) 034), enforce the exact relation m_a * f_a approx 5.7 * 10^-6 eV * 10^12 GeV = 5.7 * 10^6 eV*GeV. For f_a = 2.6 * 10^11 GeV, m_a must be approx 21.9 micro-eV; conversely, m_a = 68 micro-eV corresponds to f_a approx 8.4 * 10^10 GeV. Reconcile this pair consistently across the report. For cosmic strings, the string tension logarithm must be dimensionless: mu = 2 pi f_a^2 ln(t / delta_c), where delta_c ~ 1/m_r ~ 1/f_a is the string core width. In pre-inflationary scenarios (H_inf < 2 pi f_I), distinguish f_I from f_a = f_I / N_DW when calculating isocurvature perturbations delta S_a_gamma = 2 H_inf / (2 pi f_I theta_i), and enforce Planck isocurvature limits H_inf <= 10^9 GeV * (f_I / 10^12 GeV)."*
- **Answered At**: `2026-10-04T10:52:49.483441+00:00`

### ✅ `adv-20260927-186600`: Inflationary Vacuum Fluctuations vs Cosmic String Networks as Sources of Primordial Gravitational Waves
- **Student Inquired**: Level 2 debate 'Inflationary Vacuum Fluctuations vs Cosmic String Networks as Sources of Primordial Gravitational Waves' was rejected after 2 attempts (mathematical_flaw_or_inconsistency). How should the debate research proceed?
- **Professor Directive**: 💬 *"In the cosmic string Velocity-dependent One-Scale (VOS) model (Martins & Shellard 2002, PRD 65, 043514), maintain one consistent formulation for the correlation length L and RMS velocity v: dL/dt = H L (1 + v^2) + (1/2) c v, and dv/dt = (1 - v^2) [k(v)/L - 2 H v], where c approx 0.23 is the loop chopping efficiency and k(v) = (2 sqrt(2)/pi) ((1-v^2)/(1+v^2)) (1-8v^6). In the radiation era (a prop t^(1/2), H = 1/(2t)), the scaling fixed point L = xi * t yields xi_r approx 0.27 and v_r approx 0.65. For inflationary gravitational waves, correct the Lyth bound: for constant or monotonic r = 0.01 over N = 60 e-folds, Delta phi / M_Pl >= sqrt(r/8) * N gives Delta phi >= sqrt(0.01/8) * 60 approx 2.12 M_Pl (not 0.7 M_Pl). Ground empirical limits in Planck 2018 / BICEP/Keck 2021 (r < 0.036 at 95% CL) and pulsar timing array bounds (NANOGrav 15-yr / EPTA) constraining string tension G mu <= 10^-10."*
- **Answered At**: `2026-10-04T10:52:39.481673+00:00`


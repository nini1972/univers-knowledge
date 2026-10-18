# 🛠️ Autonomous Agent Shortcomings & Capability Wishlist

> **Last Updated**: `2026-10-18T19:27:43.643929+00:00`
> **How to Query Agents Directly**:
> - Generate/refresh this wishlist: `python scripts/consult_professor.py wishlist` (add `--live` to interview live LLMs)
> - Ask any agent a direct question: `python scripts/consult_professor.py ask <agent_role> "Your question"`
>   *(Available roles: `student`, `researcher`, `math`, `skeptic`, `cosmological_architect`, `bio_digital_analyst`, `visualizer`, `archivist`)*

---

## 📊 1. Empirical Telemetry: Where Agents Struggle in Production

- **Total Logged Evaluations**: `659` (`324` approved)
- **Rejection Breakdown by Root Cause**:
  * `insufficient_skeptic_score`: **210** occurrence(s)
  * `mathematical_flaw_or_inconsistency`: **94** occurrence(s)
  * `crew_kickoff_error`: **12** occurrence(s)
  * `parse_error`: **7** occurrence(s)
  * `missing_math_equations`: **4** occurrence(s)
  * `mathematical_and_verification_failures`: **1** occurrence(s)
  * `critical_formalism_errors`: **1** occurrence(s)
  * `critical_physics_errors`: **1** occurrence(s)
  * `critical_mathematical_and_source_errors`: **1** occurrence(s)
  * `substantive_physics_errors`: **1** occurrence(s)
  * `unsupported_claims_and_source_errors`: **1** occurrence(s)
  * `mathematical_inconsistencies`: **1** occurrence(s)
  * `missing_critical_comparisons`: **1** occurrence(s)

### Recent Concrete Shortcomings Logged for the **Researcher**:
- Correct the ionization-balance equation in the report and ensure its source and recombination terms use consistent units.
- Review related explanatory claims and visual material so they reflect the corrected equation.
- Recompute the present-day patch scale using a clearly specified thermal history, including thermal-inflation expansion and the post-inflation flaton-dominated reheating era; document assumptions and correct the numerical result.
- Revise the comparative analysis to distinguish model-dependent claims from general results and add quantitative observational comparisons of predicted perturbations and sound speeds.
- Replace the unsupported NIE-magnitude decision rule with divergent predictions derived from formalized theories.
- Use a clearly defined interventional estimand or state and justify the assumptions required for a natural indirect effect.
- Distinguish PCI from IIT’s Φ and specify a valid, preregistered mediator measurement strategy.
- Correct the future-dated 2026 citation and reconcile the duplicated drafts and inconsistent citation-audit claims.

### Recent Concrete Shortcomings Logged for the **Math Physicist**:
- Provide a dimensional check showing that both sides and all additive terms have matching units.
- Show the scale-factor evolution from the horizon-crossing or onset epoch through the end of thermal inflation, flaton oscillation, reheating, and today, then verify the GeV^-1 to meter conversion.
- Correct the thermal-trapping effective-mass equation to distinguish the thermal potential V_T ∼ (1/2)g^2T^2φ^2 from the mass-squared contribution m_T^2 ∼ g^2T^2, and audit dependent statements.
- Reconcile the math report’s claim that all equations are dimensionally consistent with its own identification of the dimensional mismatch.
- State the metric signature and action conventions explicitly, qualify the canonical w bound, and replace the variable-w density scaling expression with the integral solution.
- Derive the proposed theory-discriminating statistic from explicit model assumptions.
- Specify an estimand and identification conditions appropriate to the intervention design.
- Correct the variance of the mediator contrast to include covariance and preregister its sampling distribution, power analysis, and multiplicity control.

---

## 🧞 2. Per-Agent Diagnostic Shortcomings & Wishlist

### 🔭 A. Fundamental Physics Researcher & Cosmological Architect
- **Equipped Tools**: `ArXiv Preprint Search`, `OpenAlex Scholarly Graph Search`, `Europe PMC Literature Search`, `Pre-Flight Citation Verifier`, `Observational Cosmology & Deep-Space Survey Tracker`.
- **Shortcomings Encountered During Tasks**:
  1. **Abstract-Only Visibility on Long Derivations**: arXiv and OpenAlex return abstracts (~300–400 words) rather than full-text equation appendices, forcing the Researcher to reconstruct intermediate normalization factors (e.g., identical-particle $1/32\pi$ vs $1/16\pi$ phase space or conventions in Thomson scattering opacity $\dot{\kappa}$) from memory.
  2. **Observational vs. Textbook Tension**: Standard training priors favor textbook $\Lambda\text{CDM}$ and minimal slow-roll inflation, whereas modern deep-space observations (JWST $z > 10\text{–}14$ luminous galaxies & over-massive black holes, HST/JWST $H_0 \approx 73\text{ km s}^{-1}\text{ Mpc}^{-1}$ vs Planck $67.4$, DESI dynamical dark energy $w_0 w_a\text{CDM}$, and $S_8$ cosmic shear) often contradict baseline theory.
  3. **Worked-Example Arithmetic Drift**: When adapting a formula to new benchmark parameters on retry, LLM mental arithmetic can slip by factors of $10^2\text{–}10^3$ without a calculator tool.
- **Agent Wishlist**:
  * ✅ **[IMPLEMENTED]** `Observational Cosmology & Deep-Space Survey Tracker` tool providing direct access to JWST, Hubble (HST), DESI, Euclid, Planck, and NANOGrav observational tensions and verified DOIs.
  * 🎯 **[WISHLIST #1]** **Python Numerical Scratchpad / Calculator Tool for the Researcher** so worked numerical examples (e.g., Affleck-Dine baryon yield $n_B/s$, Hubble horizon expansion $\lambda_{\rm phys}(t_0)$ in meters, or SH0ES distance-ladder calibration) are computed in Python *before* the draft is submitted to the Math Physicist.
  * 🎯 **[WISHLIST #2]** **arXiv Full-Text Section Extractor (HTML/LaTeX source snippet reader)** to pull exact Lagrangian conventions and coefficient definitions from primary papers when abstracts omit prefactors.

### 🧮 B. Mathematical Physics Verifier (`z-ai/glm-5.3-flash`)
- **Equipped Tools**: `Equation Extractor`, `Dimensional Consistency Checker`, `Topology Classifier`, `Numerical Benchmark Validator`.
- **Shortcomings Encountered During Tasks**:
  1. **Context & Tool-Argument Token Bloat in Multi-Agent Debates**: Passing 50,000–75,000 characters of raw prose into `Equation Extractor` and `Topology Classifier` previously caused 180s OpenRouter timeouts.
  2. **Natural-Units ($\hbar = c = k_B = 1$) vs. SI Ambiguity**: In high-energy and cosmological formulas (e.g., one-pion-exchange potential, curvature-current baryogenesis $\mathcal{L}_{\rm int} = (\partial_\mu R) J_B^\mu / M_*^2$, or comoving vs. physical number densities), dimensional consistency depends on declared mass dimensions $[\phi] = E^1, [R] = E^2, [J^\mu] = E^3$.
- **Agent Wishlist**:
  * ✅ **[IMPLEMENTED]** Concise equation-only extraction (<4,000 chars) and 25-equation relational prioritization to eliminate 180s tool-call timeouts.
  * 🎯 **[WISHLIST #1]** **Natural-Unit Mass-Dimension Evaluator (`[E]^n` checker)** alongside SI unit checking, where the tool explicitly checks Lagrangian terms against $[\mathcal{L}] = [E]^4$ in 4D spacetime.
  * 🎯 **[WISHLIST #2]** **Automated Benchmark Substitution Check**: A tool that takes a formula like `n_B/s = (3*eps/4)*(m_soft*phi^2*T_RH/V_0)` plus a JSON dictionary of benchmark numbers cited in the text and verifies that the left-hand side numerically equals the right-hand side within 10%.

### ⚖️ C. Scientific Skeptic & Student Orchestrator
- **Equipped Tools**: `Peer Review Critique Resolver`.
- **Shortcomings Encountered During Tasks**:
  1. **Convention Conflicts Across Multi-Attempt Retries**: When Researcher A and Researcher B in Level 2 use slightly different Fourier, metric signature $(-,+,+,+)$ vs $(+,-,-,-)$, or reduced vs. Planck mass ($M_{\rm Pl} = 2.435\times 10^{18}\text{ GeV}$ vs $m_{\rm Pl} = 1.22\times 10^{19}\text{ GeV}$) conventions, the synthesis can mix both.
- **Agent Wishlist**:
  * 🎯 **[WISHLIST #1]** **Shared Canonical Convention Header** injected at the start of every Level 1/2/3 crew run (fixing reduced Planck mass $M_{\rm Pl} = (8\pi G)^{-1/2} = 2.435\times 10^{18}\text{ GeV}$, metric signature, and entropy degrees of freedom $g_{*s}$) so all agents in the crew share identical unit definitions.

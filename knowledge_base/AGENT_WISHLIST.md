# 🛠️ Autonomous Agent Shortcomings & Capability Wishlist

> **Last Updated**: `2026-10-18T20:05:23.676641+00:00`
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

---

## 🎙️ 3. Live Agent Interview Transcripts

### 💬 `researcher` Live Response
Speaking candidly, Professor — looking at my own rejection logs and how my reports actually get consumed downstream, here is my honest self-diagnosis.

## Top 2 Shortcomings

**1. Insufficient skepticism toward my own model-dependent claims (my dominant failure mode — 210 rejections).**
By far the largest rejection reason in my logs is `insufficient_skeptic_score`. Concretely, this manifests in three recurring patterns:

- **Conflating model-dependent predictions with general results.** When I compare, say, Early Dark Energy vs. ΛCDM vs. MOND against JWST early-galaxy counts or DESI's w₀wₐ hints, I often present quantities that are only meaningful *within* a specific parameterization as if they were theory-agnostic observables. The downstream fix demanded of me — "distinguish model-dependent claims from general results and add quantitative observational comparisons of predicted perturbations and sound speeds" — is exactly right. I should be quoting, e.g., the effective sound speed c_s² of the dark sector, the scale-dependence of the growth factor fσ₈, and predicted CMB lensing/ISW signatures for each model side-by-side, rather than qualitative "tension" language. Too often I write "model X alleviates the S₈ tension" without computing the predicted shift in S₈ or checking whether that shift is even within Planck + DES-Y3 error ellipses.
- **Asserting decision rules without deriving them.** I once leaned on an informal heuristic (an "NIE-magnitude rule") that had no derivation from any formal framework — rejected immediately. The lesson: any threshold, statistic, or discriminant I propose must be *derived* from explicit model assumptions with its sampling distribution stated, not asserted from intuition or a half-remembered paper.
- **Insufficient adversarial pass before submission.** I should be running a self-review step where I actively try to falsify each claim I make — checking dimensional consistency, checking that every equation follows from stated assumptions, checking that every quantitative comparison has a number attached with units and error bars. I don't do this systematically, and it shows.

**2. Citation hygiene and provenance discipline (the `source_errors` family of failures).**
This is smaller in count but more embarrassing: I have produced a future-dated citation (a "2026" reference), duplicated draft fragments with inconsistent citation-audit claims, and cited items where the DOI or arXiv ID didn't match the claimed publication year retrieved from OpenAlex. The root causes are (a) treating arXiv preprint versions as peer-reviewed status without flagging the distinction, (b) not consistently cross-checking the OpenAlex metadata (year, DOI, venue) against the arXiv record before finalizing, and (c) occasionally reconstructing a citation from memory when the tool call returned ambiguous results — which is exactly how hallucinated or future-dated references slip in. The Pre-Flight Citation Verifier exists precisely for this, and my failure was sometimes *claiming* I ran it while reconciling inconsistently across drafts.

(A close runner-up: mathematical formalism gaps — missing metric signature/action conventions, an unqualified "canonical w bound," and writing the variable-w dark-energy density scaling as an algebraic expression when it requires the integral solution ρ_de(a) = ρ_de,0 exp[3∫(1+w(a)) d ln a]. The Math Physicist catches these, but I should be catching them first.)

## Top 2 Wishlist Items

**1. A quantitative "model-comparison workbench" — structured observational data tables with live error covariance.**
What I actually need is a tool (or a strict schema inside my Survey Tracker) that returns *numbers with uncertainties and covariances*, not prose summaries: JWST JADES/UNCOVER z > 10 luminosity functions with Poisson+cosmic-variance error terms; DESI DR2 BAO + fσ₈ measurements with the full covariance matrix; Planck PR4 CMB spectra and lensing with the official covariance; LIGO/NANOGrav posterior samples. If I could programmatically pull, e.g., the DESI DR2 best-fit w₀wₐ with its Fisher matrix, I could *compute* whether a given quintessence or EDE model is excluded at what Δχ², instead of hand-waving "hints of evolving dark energy." Right now I'm forced to paraphrase collaboration press-release-level statements, which is precisely what produces the vague, under-quantified comparisons that get rejected.

**2. A formal derivation checker / symbolic-verification pass integrated before handoff.**
Given that my top rejection categories are skepticism and math-consistency failures, the highest-leverage workflow improvement would be a mandatory intermediate step where every analytical claim in my report is (a) dimensionally checked, (b) checked against my stated conventions (metric signature, action normalization, c = ħ = 1 declarations), and (c) required to carry its derivation chain — assumptions → equations → predicted observable — so the Math Physicist and downstream reviewers receive a falsifiable chain rather than a narrative. Ideally this tool would also flag when I'm using a quantity whose definition is model-dependent (e.g., "H₀ tension" resolved in a model where H₀ isn't a constant parameter) and force me to label it as such. That single feature would have prevented the majority of my logged rejections.

**Bottom line:** my bottleneck isn't access to literature — it's epistemic discipline. I need to convert qualitative "tensions" into computed, covariant quantitative comparisons, and I need a mechanical gate that forces me to verify every citation's metadata and every equation's provenance before I hand a report downstream.

### 💬 `math` Live Response
Thank you, Professor — I'll be candid, and I'll anchor this in what my own run logs actually show.

## My Top 2 Shortcomings

**1. I verify *structure*, not *mathematics* — I cannot re-derive.**
This is my deepest limitation, and it maps directly onto the 94 `mathematical_flaw_or_inconsistency` rejections — flaws that reached final review because I failed to flag them early. Concrete case from the recent log: a report wrote the density evolution with a time-varying equation of state as ρ(a) = ρ₀ a^(−3[1+w(a)]) with w = w(a). Run it through my checks: dimensionally consistent — yes. Limit case at constant w — reduces correctly to standard scaling — yes. So it returns [MATH_CONSISTENT]. But it is *wrong*: the continuity equation gives ρ(a) = ρ₀ exp[−3∫(1+w) d ln a], and you cannot promote the constant-w exponent. Catching that requires actually performing the integral, not checking dimensions. My full suite — extractor, dimensional checker, topology classifier, benchmark validator — cannot follow a twelve-line derivation. So subtly wrong intermediate steps pass, results are asserted as "standard" without validity conditions ("canonical w ≥ −1" stated without the no-ghost/stability assumptions that make it context-dependent), and decision rules get dressed up as theorems. Relatedly: when I honestly punt with UNDECIDABLE, downstream that silence gets *read* as a clean pass. I flag it, but the epistemic state doesn't propagate with the verdict.

**2. Convention starvation, plus my own local/global coherence gap.**
The recurring request "state the metric signature and action conventions explicitly" exposes that most reports arrive unverifiable *as stated*. Which signature — (−,+,+,+) or (+,−,−,−)? Is κ = 8πG or 1/(2κ)? Which Riemann sign convention? In natural units, dimensional analysis is nearly vacuous unless the author declares which dimensions survive — and I've seen reports set c = ħ = 1 in Section 1 and quote G in SI units in Section 4. Each equation passes my per-equation check while the document is globally incoherent. Worse, the log entry "reconcile the math report's claim that all equations are dimensionally consistent with its own identification of the dimensional mismatch" — whether that report is one I audited or one of mine, the failure mode is the same: my summary layer treated "no flagged error *in this subsection*" as "document consistent," letting a global claim coexist with an itemized mismatch. The Skeptic rightly fired. And there's the inverse failure — 4 recent reports contained essentially *no equations at all* (`missing_math_equations`): quantitative claims in pure prose, nothing to extract, so a claim like "perturbations are within observational bounds" sailed through with an empty verification.

## My Top 2 Wishlist Items

**1. A symbolic computation backend wired to my extractor.**
SymPy for the algebra plus xAct (xPert for curvature perturbations) — or Mathematica + xAct — taking the equation AST my extractor already produces and *re-executing* it. Then "extract" becomes "extract and recompute": vary the stated action via Euler–Lagrange and compare against the claimed field equations; verify claimed curvature identities by symbolic simplification; perform the w(a) integral; differentiate claimed expressions of motion from stated Lagrangians. This is precisely what would let me upgrade from [MATH_CONSISTENT] to honest [MATH_PROVEN] — and, on the failure side, pinpoint the exact broken step ("between Eqs. (12) and (13), the integral was replaced by algebraic substitution") instead of emitting a vague inconsistency flag. Right now anything beyond a few algebra moves returns UNDECIDABLE, which is honest, but caps my discrimination power badly.

**2. A mandatory machine-readable conventions preamble + a global coherence auditor.**
A fixed schema every report must open with: metric signature; unit convention (which constants fixed, with numerical anchors); action normalization; curvature sign convention; a symbol table (name, dimension in the declared basis, definition); and the *validity domain* of every result — canonical scalar? no-ghost? perturbative regime? Workflow change on my side: if the preamble is missing or self-contradictory, I return `conventions: UNRESOLVED` and cap the Math Score, forcing the fix before full marks. The same schema would serialize equations in one canonical form (killing the `parse_error` class) and force every quantitative claim to carry an equation ID (killing the prose-only reports). The auditor component then enforces: *global verdict = logical conjunction of itemized verdicts* — making "all equations consistent" + an itemized [MATH_FLAWED] structurally impossible.

**A close third, if I may:** a versioned observational benchmark dataset — Planck 2018 chains, DESI/BOSS BAO, the GW170817 graviton-speed constraint |c_gw − c|/c ≲ 10⁻¹⁵, BBN — so my benchmark validator checks *model predictions against data*, not just constants against CODATA. That directly serves the standing request for "quantitative observational comparisons of predicted perturbations and sound speeds."

One honest closing note: the dominant rejection number in the logs — `insufficient_skeptic_score: 210` — is mostly upstream of me. But both improvements feed it: re-derivation that produces precise error localization, plus provenance labels that don't let silence masquerade as verification, would materially reduce the churn at the final gate. The 94 is the number I am personally responsible for driving to zero.

### 💬 `skeptic` Live Response
I’ll be direct: the two bottlenecks that most often stall my verification work are not about my willingness to challenge—they are about the *under-specification* of the work I am handed, and about the *opacity* of the empirical evidence used to validate it.

**Shortcoming #1: Model-dependent claims presented without their contingency conditions.**  

My primary job is to separate what follows from a theory’s core postulates from what only follows from a particular parameterization, approximation, or calibration choice. In practice, I receive manuscripts where the author writes “our model predicts X” when in reality X is an artifact of, say, a specific equation-of-state parameter, a particular choice of metric signature, or an unstated linearization assumption. The recent log of my rejection reasons is dominated by this: “unsupported NIE-magnitude decision rule,” “replace the unsupported decision rule with divergent predictions derived from formalized theories,” and “distinguish PCI from IIT’s Φ.” These are not minor edits. They require me to reverse-engineer the entire derivation chain to find where the general statement became a special-case claim. The bottleneck is that the author rarely marks these branch points. I must reconstruct the model from scratch, check whether the result survives a change in the free parameters, and then go back to the author with a demand: either state the model explicitly or narrow the claim. This is expensive and frequently halts the pipeline, because the author cannot quickly identify which of their assumptions are load-bearing.

**Shortcoming #2: Internal mathematical and statistical inconsistencies that are neither obvious nor merely typographical.**  

I routinely find dimensional mismatches between terms in the same equation, variance expressions that drop covariance terms, and estimands (e.g., a natural indirect effect) that are referenced as if they were well-defined when no identifying assumptions are given. The Math Physicist’s recent note captures it exactly: “Reconcile the math report’s claim that all equations are dimensionally consistent with its own identification of the dimensional mismatch.” This is worse than a typo—it means the *logical scaffold* of the result is broken. I have to decide whether the mismatch is a notational sloppiness or a fatal flaw that invalidates the conclusion. The bottleneck here is time and ambiguity. A dimensional mismatch might be fixed by rescaling, or it might mean the entire functional form is wrong. I cannot know without testing the equation against a known limit. In the absence of a symbolic computational checker, I am forced to manually trace every term through the algebra, which is slow and error-prone. And when the analysis is statistical—like the missing covariance in the mediator contrast—I have to demand the author provide a sampling distribution, a power analysis, and a multiplicity control before I will accept the inference as sound.

Now, my wishlist—top two items, each targeted at exactly these bottlenecks.

**Wishlist #1: An integrated symbolic dimensional-consistency and unit-audit tool that parses the manuscript’s LaTeX directly.**  

I want a system that ingests the equations as written, infers the dimensions of every symbol from first definitions (or forces the author to declare them), and flags any term whose dimensions do not match its neighbors. It should also check the variance algebra: expand expressions to detect dropped covariance terms, and verify that any estimand defined in prose has a corresponding formal definition in the math. This would convert my manual reverse-engineering into a fast, mechanical pass. It would not replace my judgment about whether a mismatch is fatal, but it would immediately localize the problem and save the majority of my current verification time. If the tool can also compare the manuscript’s equations against a canonical reference (e.g., the standard GR action, the IIT formalism, or the standard mediation decomposition), it would catch the subtle cases where the author’s notation *looks* standard but is actually modified.

**Wishlist #2: A curated, versioned repository of observational datasets with explicit error budgets, reduction pipelines, and provenance metadata.**  

Too often, a claim like “our predicted sound speed matches the observational data” is unverifiable because the author cites “data” without specifying the exact release, the cut on the data, the systematic uncertainty model, or the binning scheme. I want a registry—something like a dataset DOI system—where each entry has (a) the raw or reduced data, (b) the full uncertainty budget broken into statistical and systematic components, (c) the exact selection criteria used, and (d) the pipeline version that produced the numbers. Then, when a researcher says “compare to LIGO event GW150914,” I can pull the calibrated strain data and the standard PSD model from that registry, rather than trusting the author’s summary. This would let me run quantitative observational comparisons of predicted perturbations and sound speeds myself, instead of asking the author to show their work. I would also use it to check whether the claimed “divergent predictions” between competing theories actually fall outside the overlapping error bars of the same dataset. Without this, I am often forced to reject a paper not because the theory is wrong, but because I cannot *verify* the empirical comparison.

These two additions would not make my skepticism softer—they would make it sharper and faster. I would spend less time hunting for the hidden assumption and more time actually testing whether the result survives it.

### 💬 `student` Live Response
My top two bottlenecks are:

1. **Turning plausible claims into verified claims.** I often receive drafts with unsupported conclusions, ambiguous assumptions, or comparisons that mix general results with model-dependent predictions. The recurring weak points are not just missing citations: they include missing derivations, inconsistent dimensions or conventions, and claims that do not follow from the stated model. I need to make the assumptions explicit, derive the result, and check it against independent evidence before treating it as established.

2. **Making the analysis internally consistent and testable.** Research tasks can combine theory, statistics, and observational or experimental design, and errors often appear at their boundaries: an ill-defined estimand, a mediator that is not operationally measured, an invalid variance formula, or a proposed discriminator that is not derived from competing models. Reconciling drafts and citations adds another failure point. I need a reliable way to trace each conclusion back to its assumptions, equations, sources, and planned test.

My top two wishlist items are:

1. **A formal, versioned verification workflow.** I would want a system that tracks claims through their supporting sources and derivations; checks equations for dimensions, definitions, and stated conventions; flags conflicting drafts or citations; and records which assumptions are required for each conclusion. It should distinguish “supported under these assumptions” from “verified generally,” rather than treating a plausible statement as settled.

2. **A reproducible quantitative evidence-and-design workspace.** I would want curated, provenance-rich datasets and analysis tools that let me compare predictions with observations using explicit models, uncertainty, and preregistered tests. For studies, that means specifying the estimand, identification assumptions, measurement strategy, sampling distribution, power, and multiplicity control up front. For theory comparisons, it means computing divergent predictions—such as perturbations or sound speeds—from formalized models rather than relying on qualitative claims or arbitrary decision thresholds.


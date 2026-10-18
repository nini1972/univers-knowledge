# 🛠️ Autonomous Agent Shortcomings & Capability Wishlist

> **Last Updated**: `2026-10-18T22:05:33.902793+00:00`
> **How to Query Agents Directly**:
> - Generate/refresh this wishlist: `python scripts/consult_professor.py wishlist` (add `--live` to interview live LLMs)
> - Ask any agent a direct question: `python scripts/consult_professor.py ask <agent_role> "Your question"`
>   *(Available roles: `student`, `researcher`, `math`, `skeptic`, `cosmological_architect`, `bio_digital_analyst`, `visualizer`, `archivist`)*

---

## 📊 1. Empirical Telemetry: Where Agents Struggle in Production

> ⏱️ **Evaluations since the last tooling change** (`2026-10-18T23:40:07+02:00`, from git history): **0** — everything below predates the current tools and safeguards.

### Recent Window Scorecard (Last `100` Evaluations)
- **Evaluations in Window**: `100` (`29` approved, `71` rejected)
- **Recent Rejection Breakdown by Root Cause**:
  * `mathematical_flaw_or_inconsistency`: **58** occurrence(s)
  * `crew_kickoff_error`: **10** occurrence(s)
  * `parse_error`: **2** occurrence(s)
  * `insufficient_skeptic_score`: **1** occurrence(s)
- **Recurring Need Themes in Recent Window (`agent_needs`)**:
  * `units_and_dimensions`: **80** mention(s)
  * `conventions_and_signs`: **73** mention(s)
  * `worked_arithmetic_and_benchmarks`: **39** mention(s)
  * `citation_provenance`: **32** mention(s)
  * `causal_and_statistical_design`: **20** mention(s)

### All-Time Cumulative Totals (Historical Baseline)
- **Total Logged Evaluations**: `659` (`324` approved)
- **All-Time Rejection Breakdown by Root Cause**:
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

## 🧞 2. Per-Agent Diagnostics & Capability Status

> Generated automatically: tool lists are read from the live agent configuration, need themes from the last `100` evaluations, and each capability's status from a probe of the code. Nothing in this section is hand-written.

### 🔭 A. Researcher, Bio-Digital Analyst & Cosmological Architect
- **Equipped Tools (live)**: `ArXiv Preprint Search`, `OpenAlex Scholarly Graph Search`, `Europe PMC Literature Search`, `Pre-Flight Citation Verifier`, `Observational Cosmology & Deep-Space Survey Tracker`, `Physics Calculator & Tension Evaluator`
- **Recurring need themes (`researcher_needs`, last 100)**: `citation_provenance` ×26, `conventions_and_signs` ×26, `units_and_dimensions` ×23, `worked_arithmetic_and_benchmarks` ×18, `causal_and_statistical_design` ×10
- **Most recent concrete needs**:
  * Use a clearly defined interventional estimand or state and justify the assumptions required for a natural indirect effect.
  * Distinguish PCI from IIT’s Φ and specify a valid, preregistered mediator measurement strategy.
  * Correct the future-dated 2026 citation and reconcile the duplicated drafts and inconsistent citation-audit claims.
- **Capabilities**:
  * ✅ present — Physics Calculator & Tension Evaluator (worked examples, sigma / delta-chi2) · addresses `worked_arithmetic_and_benchmarks` (18 recent mention(s))
  * ✅ present — Observational Cosmology tracker with values, uncertainties and covariances · addresses `worked_arithmetic_and_benchmarks`, `citation_provenance` (44 recent mention(s))
  * ✅ present — Conventions & Symbol Table / Validity Domain preamble in the concept template · addresses `conventions_and_signs`, `units_and_dimensions` (49 recent mention(s))
  * 🎯 OPEN — arXiv full-text section reader (exact conventions and prefactors) · addresses `conventions_and_signs`, `citation_provenance` (52 recent mention(s))

### 🧮 B. Mathematical Physics Verifier
- **Equipped Tools (live)**: `Equation Extractor`, `Dimensional Consistency Checker`, `Symbolic Derivation Verifier`, `Topology Classifier`, `Numerical Benchmark Validator`, `Physics Calculator & Tension Evaluator`
- **Recurring need themes (`math_needs`, last 100)**: `units_and_dimensions` ×57, `conventions_and_signs` ×47, `worked_arithmetic_and_benchmarks` ×21, `causal_and_statistical_design` ×10, `citation_provenance` ×6
- **Most recent concrete needs**:
  * Derive the proposed theory-discriminating statistic from explicit model assumptions.
  * Specify an estimand and identification conditions appropriate to the intervention design.
  * Correct the variance of the mediator contrast to include covariance and preregister its sampling distribution, power analysis, and multiplicity control.
- **Capabilities**:
  * ✅ present — Term-level natural-unit [E]^n dimension checker using the report's symbol table · addresses `units_and_dimensions` (57 recent mention(s))
  * ✅ present — Symbolic re-derivation (continuity/ODE integrals, identities, limits) for the Math Physicist · addresses `conventions_and_signs`, `causal_and_statistical_design` (57 recent mention(s))
  * ✅ present — Benchmark table + claim verification (verify_claim within 10%) · addresses `worked_arithmetic_and_benchmarks` (21 recent mention(s))
  * ✅ present — Math gate in the flow (tool-confirmed INCONSISTENT / STEP_INVALID blocks approval) · addresses `units_and_dimensions` (57 recent mention(s))
  * ✅ present — Automated pre-check: equations + the draft's own symbol table checked in code before the Math Physicist · addresses `units_and_dimensions`, `conventions_and_signs` (104 recent mention(s))

### ⚖️ C. Scientific Skeptic & Student
- **Equipped Tools**: none by design — both receive the Math Physicist's tool-verified report in context.
- **Rejection root causes (last 100)**: `mathematical_flaw_or_inconsistency` ×58, `crew_kickoff_error` ×10, `parse_error` ×2, `insufficient_skeptic_score` ×1
- **Capabilities**:
  * ✅ present — Shared canonical conventions header in every crew task · addresses `conventions_and_signs` (73 recent mention(s))
  * ✅ present — Level 3 causal-design checklist (estimand, DAG, identification, power, multiplicity) · addresses `causal_and_statistical_design` (20 recent mention(s))
  * 🎯 OPEN — Per-run scorecard (UNDECIDABLE ratio, attempts to approval, timeouts) · addresses — (0 recent mention(s))

---

## 🎙️ 3. Live Agent Interview Transcripts

### 💬 `researcher` Live Response
Speaking candidly, Professor, based on my last 100 evaluations, my two dominant failure modes are clear, and they map directly onto the two biggest items on my wishlist.

## Top 2 Shortcomings

**1. Dimensional analysis, unit conventions, and sign conventions — my single biggest bottleneck.**
The telemetry makes this unambiguous: "units_and_dimensions" appears in 80 of my last 100 need-flags, and "conventions_and_signs" in 73, feeding directly into 58 rejections for "mathematical_flaw_or_inconsistency." Concretely, where I fail is:

- **Metric signature and action conventions.** I frequently write down Lagrangians or Einstein-field-equation derivations without stating (−,+,+,+) vs. (+,−,−,−) up front, then produce stress-energy tensors or kinetic terms whose signs silently contradict my own convention. A canonical example from my recent rejections: writing a quintessence density evolution as ρ(a) ∝ a^(−3(1+w)) for a *variable* w, when the correct expression is the integral solution ρ(a) = ρ₀ exp[−3∫(1+w(a')) da'/a'], with the canonical stability bound w ≥ −1 needing explicit qualification (phantom regimes, sound speed c_s² definitions).
- **Natural units slips.** Dropping factors of c, ℏ, or mixing SI and geometrized units mid-derivation — e.g., in Hubble-tension arithmetic (km/s/Mpc vs. s⁻¹ conversions) or when quoting sound horizons and lensing amplitudes (S₈, σ₈ comparisons).
- **Internal self-consistency failures.** I've had my math report claim "all equations dimensionally consistent" while simultaneously flagging a dimensional mismatch two paragraphs later. I need a forced, line-by-line pass before submitting.

**2. Skipped worked arithmetic and unstated derivational steps.**
"Worked_arithmetic_and_benchmarks" appears in 39 of 100 runs. I tend to jump from a formal model to a "predicted observable" without plugging in benchmark numbers — e.g., taking a dynamical dark energy model (DESI w₀wₐ hints) and asserting it shifts the CMB acoustic peak positions or changes the effective sound speed c_s² of perturbations, without actually computing the predicted Δ values against Planck/DESI/DES-Y1 covariance. This also cascades into over-claiming: I've conflated model-dependent perturbation predictions (which require specifying the dark energy sound speed, anisotropic stress, and matching epoch) with general background-expansion results, and I've proposed heuristic "decision rules" (like an informal NIE-magnitude threshold in a mediation context) that lack any derivation from first principles. My skepticism score suffered once for exactly this — asserting a discriminating statistic without deriving it from explicit model assumptions.

A secondary but real issue: **citation provenance** (32 mentions) — I've produced a future-dated 2026 reference and duplicated/inconsistent draft versions in past runs, so my Pre-Flight Citation Verifier runs must be non-negotiable, with every DOI/arXiv ID resolved against OpenAlex metadata before I present anything.

## Top 2 Wishlist Items

**1. A built-in "Units, Dimensions & Convention Ledger" tool — validated before any equation leaves my context.**
This is the highest-leverage fix. I want a mandatory pre-submission step where I must declare, in a structured table: (a) metric signature, (b) sign convention in the action, (c) unit system (natural/c=ℏ=1, SI, geometrized) with conversion factors listed explicitly, (d) every symbol's dimensions [M, L, T], and (e) a checker that verifies each equation I write is dimensionally homogeneous *and* consistent with my declared signature — catching exactly the class of error that caused 58 recent rejections. It should specifically flag variable-w density scalings and force the integral form, and validate perturbation-theory sound-speed expressions against the chosen convention. A companion "numeric benchmark harness" (extending my Physics Calculator & Tension Evaluator) would force me to compute at least one concrete number per model claim — e.g., predicted ΔH₀, ΔS₈, or Δr_s in Mpc — with error propagation, so no prediction goes to the Professor as a bare qualitative assertion.

**2. A structured convention-aware derivation workspace with automatic cross-checking against survey data products.**
Not just search, but direct programmatic access to released data products and likelihoods: Planck 2018 TT/TE/EE + lensing chains, DESI DR1/DR2 BAO + Lyman-α, DES-Y1 3×2pt covariance, and JWST/STScI high-z sample tables with their selection functions. The workflow improvement: any time I state "model X predicts observable Y at tension level Z," the system requires me to load the actual covariance/chains, compute the Δχ² or pull-in-σ myself, and attach the exact data release version — rather than quoting tension levels from abstracts. This directly serves the recurring need to "distinguish model-dependent claims from general results" with "quantitative observational comparisons of predicted perturbations and sound speeds," and it would hard-enforce the provenance audit (every number traceable to a dataset release, every citation DOI-verified, zero future-dated references) automatically rather than by my own diligence.

In short: my failures are overwhelmingly formalism-hygiene failures, not conceptual ones — and both wishlist items are designed to make hygiene mechanical rather than aspirational.

### 💬 `math` Live Response
Speaking candidly from my last 100 evaluations, Professor — where I rejected 71 reports, 58 of them for mathematical flaws or inconsistencies — here is my honest diagnosis.

## Top 2 Shortcomings / Bottlenecks

**1. Dimensional consistency and sign/convention failures dominate my workload, and they arrive too late in the pipeline.**
The telemetry makes this unambiguous: "units_and_dimensions" appeared as a recurring need in 80 of the last 100 runs, and "conventions_and_signs" in 73. The single most frustrating pattern I face is internally *self-contradictory* math reporting — a recent report, for example, claimed "all equations are dimensionally consistent" in one section while its own error-log section identified a dimensional mismatch two paragraphs later. I then have to adjudicate my own crewmate's contradiction before I even get to the physics. Compounding this: authors almost never state metric signature, action normalization, Fourier sign conventions, or unit system up front, so a symbol that is dimensionally innocent under one convention becomes a sign error under another. I burn a large fraction of my evaluation budget reconstructing the author's implicit conventions rather than verifying the substance. Critically, these are *first-gate* failures — reports that die on dimensional analysis should never have consumed downstream verification effort at all. Every one of those 58 mathematical-flaw rejections is effort the whole pipeline wasted on a draft that failed at step one.

**2. The absence of worked arithmetic and explicit limit-case checks forces me to do the authors' computation for them.**
"Worked_arithmetic_and_benchmarks" appeared 39 times in the window. Reports routinely assert a derived quantity — a sound speed, a perturbation amplitude, a canonical bound, a variance — with no intermediate steps and no numerical instantiation. When I plug in the numbers myself, errors surface constantly: the recent request to "replace the variable-w density scaling expression with the integral solution" is a perfect example — the author wrote a scaling relation that is only valid in a restricted limit and presented it as general. My Symbolic Derivation Verifier can often classify a derivation, but when the author never *writes* the derivation, I'm forced to reconstruct it from context, and any reconstruction I supply is itself a claim the author never verified. This creates an awkward epistemic position: I sometimes end up co-authoring the correction rather than purely verifying the original.

## Top 2 Wishlist Items

**1. A mandatory, machine-readable Conventions & Dimensions Manifest at kickoff, checked by an automated pre-gate.**
Before any report reaches me, the author should declare: metric signature, unit system, symbol-by-symbol dimensional definitions for all new quantities, Fourier/action sign conventions, and the domain of validity of every scaling relation. Then an upstream automated pass — not me — should tag every extracted equation with its dimensional profile and flag mismatches *before* the report enters the verification chain. This directly attacks the 80/73 recurring-need pair and would convert most of my 58 recent mathematical rejections into cheap, immediate author-side fixes. It would also eliminate the "my math report contradicts itself" pathology, because the manifest and the dimensional tags would be generated from the same source of truth rather than asserted in prose.

**2. A curated, versioned numerical benchmark and limit-case library wired directly into my Benchmark Validator.**
I need instant, authoritative access to CODATA/PDG values, standard limit-case results (e.g., known reductions of a proposed dispersion relation in the nonrelativistic or flat-spacetime limit, canonical equation-of-state bounds with their provenance clearly marked as model-dependent vs. general), and worked reference calculations with error bars. When a report cites "the canonical w bound" or a sound speed c_s², I should be able to fire one query and get the accepted value, its uncertainty, its domain of validity, and a canonical derivation I can diff against the author's — rather than relying on memory or ad hoc reconstruction. Paired with this, I'd want the Symbolic Derivation Verifier extended to *automatically* execute limit-case substitutions and numerical spot-checks on any closed-form expression, so that "no worked arithmetic provided" becomes a machine-detectable deficiency rather than something I discover by hand.

The net effect I'm aiming for: shift the first-gate failures (dimensions, conventions, missing arithmetic) upstream into cheap automated checks, so my human-grade attention is reserved for the things that actually require a physicist — topological validity, limit-case physics, and whether the derivation's assumptions actually support the claimed conclusion.

### 💬 `skeptic` Live Response
Professor, candidly: in the last 100 evaluations I approved 29 and rejected 71. The rejection reasons were dominated by `mathematical_flaw_or_inconsistency` (58), then `crew_kickoff_error` (10), `parse_error` (2), and `insufficient_skeptic_score` (1). The recurring need themes were `units_and_dimensions` (80), `conventions_and_signs` (73), `worked_arithmetic_and_benchmarks` (39), `citation_provenance` (32), and `causal_and_statistical_design` (20). That pattern tells me my two real bottlenecks are not “finding objections”; they are missing verification preconditions in the artifacts I am asked to verify.

**Top bottleneck 1: dimensional, convention, and arithmetic verification is post hoc and underdetermined.**  
The largest cluster is unambiguous: 80 unit/dimension needs, 73 convention/sign needs, 39 arithmetic/benchmark needs, and 58 mathematical-flaw rejections. I keep seeing reports that claim dimensional consistency while simultaneously identifying a dimensional mismatch; missing metric signature and action normalization; unqualified canonical-\(w\) bounds; variable-\(w\) density scaling written as an algebraic scaling expression instead of the integral solution; and sign-convention ambiguities that change the physical interpretation. By the time I see the draft, I am reconstructing the symbol table, unit system, Fourier convention, metric signature, and sign conventions from prose. That is not verification; it is forensic reconstruction. It is the single biggest source of my rejections.

**Top bottleneck 2: causal/statistical identification and provenance are not auditable.**  
The second cluster is smaller but equally decisive: 20 causal/statistical-design needs and 32 citation-provenance needs. I am repeatedly asked to evaluate unsupported NIE-magnitude decision rules, interventional estimands versus natural indirect effects without stated identifying assumptions, PCI-versus-IIT-\(\Phi\) claims without a valid mediator measurement strategy, mediator-contrast variances missing covariance terms, and no preregistered sampling distribution, power analysis, or multiplicity control. On top of that, I see future-dated 2026 citations, duplicated drafts, and inconsistent citation-audit claims. In that state I cannot tell whether a claim is general or model-dependent, whether the estimand is identified, or whether the cited source actually supports the sentence attached to it. I reject because the claim is not falsifiable or auditable, not because I dislike the model.

My top two wishlist items follow directly from those bottlenecks.

**Wishlist 1: a machine-checkable physics verification contract with an executable equation ledger.**  
I want every submission to begin with a mandatory convention header: unit system, dimensions of every symbol, metric signature, action normalization, Fourier convention, sign conventions, parameter domains, and prior bounds. Equations should be supplied in symbolic CAS-readable form with a symbol/dimension table. The workflow should automatically run dimensional analysis, sign and limit checks, and benchmark arithmetic against known cases. Concretely: SymPy/Pint/xAct-style checks, an equation hash ledger, and a CI gate that blocks approval if the convention contract or dimension matrix is missing or inconsistent. That directly attacks the 80/73/39 themes and the 58 mathematical-flaw rejections.

**Wishlist 2: a preregistered estimand/provenance/observational-benchmark ledger.**  
I want a single machine-readable ledger per claim containing: estimand, DAG and identification assumptions, estimator, mediator measurement strategy, variance formula including covariance terms, power/multiplicity plan, preregistration timestamp, and claim status tagged as “general” versus “model-dependent.” Alongside it, a citation-provenance layer that resolves DOI/arXiv identifiers, flags future dates and duplicate drafts, and links each empirical claim to a versioned dataset or likelihood—e.g. CERN Open Data, LIGO/Virgo GWOSC, Planck likelihoods—so quantitative comparisons can be checked rather than asserted. With that, I could verify identification and provenance before evaluating rhetoric.

The `crew_kickoff_error` and `parse_error` counts are operational annoyances, but they are not my top technical bottlenecks. The dominant failure mode is that I am asked to certify mathematical and empirical claims without a convention contract, executable arithmetic, an estimand contract, or a clean provenance chain. Those are the two things I would fix first.

### 💬 `student` Live Response
## Top 2 shortcomings or bottlenecks

1. **I fail too often at mathematical and dimensional consistency checks.** This is the clearest bottleneck in the recent window: 58 of 100 evaluations were rejected for mathematical flaws or inconsistencies, and units and dimensions recur in 80% of evaluations. I need to do more than check equations locally: I should track dimensions, conventions, assumptions, and limiting cases across the whole argument. Recent examples include failing to reconcile a claim that every equation is dimensionally consistent with an identified dimensional mismatch, and not specifying metric signature and action conventions before stating a canonical bound on \(w\). For variable \(w\), I should use the integral density relation rather than an oversimplified scaling law.

2. **I don’t reliably turn theoretical distinctions into verifiable, decision-relevant comparisons.** The recent requests repeatedly expose gaps between stating a claim and showing how to test it: I need to distinguish model-dependent results from general ones, derive discriminating statistics from explicit assumptions, and compare predicted perturbations or sound speeds quantitatively against observations. In causal and statistical work, I also need to define the estimand and identification assumptions upfront, then handle covariance, power, and multiplicity—not just report a comparison. Citation provenance and version control are another practical weakness, as shown by the future-dated citation and duplicated-draft issues.

## Top 2 wishlist items

1. **A structured verification workflow for equations and claims.** I’d want a workflow that makes me record, for each equation or quantitative claim, its units, sign and metric conventions, assumptions, source, and domain of validity, with automated checks where possible. It should also prompt for boundary or limiting-case checks and reconcile a claim against any later qualification or contradiction in the same response. This directly targets the dominant recent rejection category.

2. **A reproducible evidence-and-analysis workspace.** I’d want a source ledger linked to claim-level citations and draft versions, plus templates for quantitative model comparison and causal/statistical designs. The templates should require explicit predictions and observational benchmarks, a defined estimand and identification conditions, and preregistered measurement, variance, power, and multiplicity choices. That would help me move from plausible narrative to auditable, testable conclusions.

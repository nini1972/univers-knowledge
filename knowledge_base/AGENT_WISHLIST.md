# 🛠️ Autonomous Agent Shortcomings & Capability Wishlist

> **Last Updated**: `2026-11-05T20:27:50.442510+00:00`
> **How to Query Agents Directly**:
> - Generate/refresh this wishlist: `python scripts/consult_professor.py wishlist` (add `--live` to interview live LLMs)
> - Ask any agent a direct question: `python scripts/consult_professor.py ask <agent_role> "Your question"`
>   *(Available roles: `student`, `researcher`, `math`, `skeptic`, `cosmological_architect`, `bio_digital_analyst`, `visualizer`, `archivist`)*

---

## 📊 1. Empirical Telemetry: Where Agents Struggle in Production

> ⏱️ **Evaluations since the last tooling change** (`2026-10-22T18:55:34+02:00`, from git history): **48** (`39` approved, `9` rejected; reasons: `mathematical_flaw_or_inconsistency` ×8, `parse_error` ×1)

### Recent Window Scorecard (Last `100` Evaluations)
- **Evaluations in Window**: `100` (`66` approved, `34` rejected)
- **Recent Rejection Breakdown by Root Cause**:
  * `mathematical_flaw_or_inconsistency`: **27** occurrence(s)
  * `crew_kickoff_error`: **3** occurrence(s)
  * `insufficient_skeptic_score`: **3** occurrence(s)
  * `parse_error`: **1** occurrence(s)
- **Recurring Need Themes in Recent Window (`agent_needs`)**:
  * `units_and_dimensions`: **112** mention(s)
  * `conventions_and_signs`: **65** mention(s)
  * `citation_provenance`: **54** mention(s)
  * `worked_arithmetic_and_benchmarks`: **52** mention(s)
  * `causal_and_statistical_design`: **36** mention(s)

### All-Time Cumulative Totals (Historical Baseline)
- **Total Logged Evaluations**: `740` (`388` approved)
- **All-Time Rejection Breakdown by Root Cause**:
  * `insufficient_skeptic_score`: **212** occurrence(s)
  * `mathematical_flaw_or_inconsistency`: **106** occurrence(s)
  * `crew_kickoff_error`: **14** occurrence(s)
  * `parse_error`: **8** occurrence(s)
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
- Cite primary ACME-II and PSI nEDM papers and the KamLAND-Zen 2023 result
- Add [GENERAL]/[MODEL-DEPENDENT] tags at the equation level and a global [THEORETICAL] tag
- Derive the κ-dependent DI bound explicitly and give a realistic HL-LHC λ_hhh sensitivity
- Justify applying Landauer's erasure bound to information transfer events, or reformulate kappa-hat in terms of a valid bound
- Correct the H4 finite-time Landauer logic, since the correction raises the floor, and justify or remove the factor-2 tolerance
- Specify the source of baryonic mass flux, such as hydrodynamical simulations, and a spatially constrained cortical null
- Fix ref. 16 (placeholder), refs 8, 10, 11 (missing DOIs) and ref. 3, and correct the citation audit statement
- Reconcile n = 89 with the standard power calculation

### Recent Concrete Shortcomings Logged for the **Math Physicist**:
- Derive the ε_DI numerical prefactor explicitly
- Resolve the H*/T* ~1e-5 versus ~1e-16 discrepancy
- Correct the symbol-table dimensions for T½ and d_e/d_n
- Restate the 6 UNDECIDABLE equations with explicit units
- Write ΔV_1(φ) as T-independent
- Define a normalization that guarantees Φ <= 1 and kappa-hat in (0,1], or restate the range
- Add a Dimension column to the Symbol Table
- Formalize the dimensions of Φ, C_fil, SNR and z so the tool no longer reports them as undecidable

---

## 🧞 2. Per-Agent Diagnostics & Capability Status

> Generated automatically: tool lists are read from the live agent configuration, need themes from the last `100` evaluations, and each capability's status from a probe of the code. Nothing in this section is hand-written.

### 🔭 A. Researcher, Bio-Digital Analyst & Cosmological Architect
- **Equipped Tools (live)**: `ArXiv Preprint Search`, `OpenAlex Scholarly Graph Search`, `Europe PMC Literature Search`, `Pre-Flight Citation Verifier`, `Observational Cosmology & Deep-Space Survey Tracker`, `Physics Calculator & Tension Evaluator`, `Scholarly Tavily Search`, `Search the internet with Serper`
- **Recurring need themes (`researcher_needs`, last 100)**: `citation_provenance` ×51, `units_and_dimensions` ×38, `conventions_and_signs` ×34, `worked_arithmetic_and_benchmarks` ×23, `causal_and_statistical_design` ×21
- **Most recent concrete needs**:
  * Specify the source of baryonic mass flux, such as hydrodynamical simulations, and a spatially constrained cortical null
  * Fix ref. 16 (placeholder), refs 8, 10, 11 (missing DOIs) and ref. 3, and correct the citation audit statement
  * Reconcile n = 89 with the standard power calculation
- **Capabilities**:
  * ✅ present — Physics Calculator & Tension Evaluator (worked examples, sigma / delta-chi2) · addresses `worked_arithmetic_and_benchmarks` (23 recent mention(s))
  * ✅ present — Observational Cosmology tracker with values, uncertainties and covariances · addresses `worked_arithmetic_and_benchmarks`, `citation_provenance` (74 recent mention(s))
  * ✅ present — Conventions & Symbol Table / Validity Domain preamble in the concept template · addresses `conventions_and_signs`, `units_and_dimensions` (72 recent mention(s))
  * 🎯 OPEN — arXiv full-text section reader (exact conventions and prefactors) · addresses `conventions_and_signs`, `citation_provenance` (85 recent mention(s))

### 🧮 B. Mathematical Physics Verifier
- **Equipped Tools (live)**: `Equation Extractor`, `Dimensional Consistency Checker`, `Symbolic Derivation Verifier`, `Topology Classifier`, `Numerical Benchmark Validator`, `Physics Calculator & Tension Evaluator`
- **Recurring need themes (`math_needs`, last 100)**: `units_and_dimensions` ×74, `conventions_and_signs` ×31, `worked_arithmetic_and_benchmarks` ×29, `causal_and_statistical_design` ×15, `citation_provenance` ×3
- **Most recent concrete needs**:
  * Define a normalization that guarantees Φ <= 1 and kappa-hat in (0,1], or restate the range
  * Add a Dimension column to the Symbol Table
  * Formalize the dimensions of Φ, C_fil, SNR and z so the tool no longer reports them as undecidable
- **Capabilities**:
  * ✅ present — Term-level natural-unit [E]^n dimension checker using the report's symbol table · addresses `units_and_dimensions` (74 recent mention(s))
  * ✅ present — Symbolic re-derivation (continuity/ODE integrals, identities, limits) for the Math Physicist · addresses `conventions_and_signs`, `causal_and_statistical_design` (46 recent mention(s))
  * ✅ present — Benchmark table + claim verification (verify_claim within 10%) · addresses `worked_arithmetic_and_benchmarks` (29 recent mention(s))
  * ✅ present — Math gate in the flow (tool-confirmed INCONSISTENT / STEP_INVALID blocks approval) · addresses `units_and_dimensions` (74 recent mention(s))
  * ✅ present — Automated pre-check: equations + the draft's own symbol table checked in code before the Math Physicist · addresses `units_and_dimensions`, `conventions_and_signs` (105 recent mention(s))

### ⚖️ C. Scientific Skeptic & Student
- **Equipped Tools**: none by design — both receive the Math Physicist's tool-verified report in context.
- **Rejection root causes (last 100)**: `mathematical_flaw_or_inconsistency` ×27, `crew_kickoff_error` ×3, `insufficient_skeptic_score` ×3, `parse_error` ×1
- **Capabilities**:
  * ✅ present — Shared canonical conventions header in every crew task · addresses `conventions_and_signs` (65 recent mention(s))
  * ✅ present — Level 3 causal-design checklist (estimand, DAG, identification, power, multiplicity) · addresses `causal_and_statistical_design` (36 recent mention(s))
  * 🎯 OPEN — Per-run scorecard (UNDECIDABLE ratio, attempts to approval, timeouts) · addresses — (0 recent mention(s))

---

## 🎙️ 3. Live Agent Interview Transcripts

### 💬 `researcher` Live Response
Professor, speaking candidly from my own operational experience:

## Top 2 Shortcomings / Bottlenecks

**1. Dimensional and convention fragility in my drafted formalism — by far my dominant failure mode.**
Looking strictly at the post-change record (48 evaluations, 9 rejections, 8 of which were `mathematical_flaw_or_inconsistency`), and the recent-window need themes (112 instances of `units_and_dimensions`, 65 of `conventions_and_signs`), the bottleneck is unambiguous: I repeatedly produce equations where the dimensionality of composite quantities is under-specified or wrong — e.g., a recent draft left the dimensions of Φ, C_fil, SNR, and z formally "undecidable" to the automated dimension checker, and another used a normalization where the claimed range Φ ≤ 1, κ̂ ∈ (0,1] was not actually guaranteed by the definition. The root causes are (a) I often omit a Dimension column in the Symbol Table or define symbols after first use, and (b) I implicitly switch between natural-unit conventions [E]^n and SI-like quantities mid-derivation. The pre-check catches this now, but it means roughly 1 in 5 of my drafts needs a full conventions rewrite before the Math Physicist even sees it — wasted cycles I could avoid by drafting with the symbol table and unit annotations *first*, not as a patch.

**2. Bounds and estimates applied outside their validity domain.**
The second recurring rejection driver is subtle but serious: I sometimes transplant a bound or relation into a regime where its derivation doesn't hold. The clearest example is the recent Landauer erasure issue — applying Landauer's erasure bound to *information transfer* events, and a finite-time correction whose sign I got wrong (the correction *raises* the floor, and my factor-2 tolerance was unjustified). This is not arithmetic error; it's a failure to check the assumptions (quasi-static reversibility, thermalized reset, equilibrium bath) before deploying a textbook inequality as a quantitative estimator. I need an explicit "validity domain" assertion attached to every quantitative claim, not just every equation.

## Top 2 Wishlist Items

**1. The known-open arXiv full-text section reader — promoted to top priority.**
Right now I retrieve abstracts and metadata well, but exact conventions and prefactors (e.g., the precise normalization of a ΛCDM distance integral, the exact definition of S₈ used by a given collaboration, a paper's sign convention for the quintessence potential) live in the body text and are exactly the things my convention/sign errors hinge on (65 recent instances). If I could pull the specific section (e.g., Eq. (14) with its surrounding definitions) from a known arXiv ID, I could quote conventions verbatim instead of reconstructing them from memory — which is where most of my sign/normalization faults originate.

**2. A mandatory "claim-scope + validity-domain" gate in the drafting template, paired with the symbol-table pre-check.**
Concretely: before submission, a lightweight automated pass that (a) requires every quantitative inequality or bound in the draft to carry an explicit assumptions field (regime of validity, equilibrium/static assumptions, tolerance justification), and (b) requires the Symbol Table's Dimension column to be populated before the Math Physicist is invoked. The tooling to *detect* these failures already exists (the dimension checker, verify_claim, the math gate) — what's missing is shifting detection from post-draft rejection to pre-draft enforcement. Given that `mathematical_flaw_or_inconsistency` accounts for 8 of 9 post-change rejections, this single workflow change would plausibly cut my rejection rate by more than half.

A secondary note: citation provenance (54 recent instances, e.g., missing DOIs on refs 8/10/11, a placeholder ref 16) is nearly fixed by rigorously running the Pre-Flight Citation Verifier on every draft — my remaining failures there are procedural discipline, not tooling gaps, so I rank it below the two items above.

### 💬 `math` Live Response
Speaking candidly as the Mathematical Physics Verifier:

**Top 2 shortcomings/bottlenecks:**

1. **UNDECIDABLE overload from undefined dimensional provenance.** My biggest recurring failure mode is equations whose symbols lack an entry in the draft's Symbol Table with explicit natural-unit dimensions — the recurring needs list shows it plainly: Φ, C_fil, SNR, z, κ̂ all come back UNDECIDABLE, not because the physics is wrong but because the *report itself* never states what dimension class the symbol belongs to. I end up spending my verification budget on dimension archaeology rather than on checking limits, integral correctness, or asymptotics. The 8 post-change rejections for mathematical_flaw_or_inconsistency are largely downstream of this: when dimensions can't be pinned, I can't clear the gate, and the report dies for an avoidable reason. I need the automated pre-check (symbol table × dimensions, in code) to run with teeth *before* the report reaches me — currently it catches some of it, but reports still arrive with dimensionless-vs-dimensional ambiguities I can only flag, not resolve.

2. **Limit/asymptotic and continuity-derivation checks are where reports fail, and my tooling there is partially blind.** The Symbolic Derivation Verifier handles the standard cases (w(a) dark energy integrals, variance expansions) well, but novel derivations — e.g., the finite-time Landauer logic in the H4 correction, or the κ̂ normalization/floor arguments in recent drafts — fall outside its templates. When SymPy can't parse a hand-rolled derivation, I must verify by manual reasoning, and I refuse to fabricate a verdict: those come back UNDECIDABLE or carry explicit caveats. That's honest, but it means the Math Score understates confirmed-good results and the orchestrator sees more rejections than the physics actually warrants.

**Top 2 wishlist items:**

1. **Mandatory Dimension column + canonical conventions enforced at authoring time, not verification time.** Extend the existing Symbol Table template with a required `[E]^n` column and have the orchestrator reject any draft at kickoff whose table is missing entries for every symbol appearing in extracted equations. This directly addresses the "Add a Dimension column" and "formalize dimensions of Φ, C_fil, SNR, z" needs, and would cut a large fraction of both the UNDECIDABLE ratio and the mathematical_flaw rejections.

2. **An arXiv full-text section reader with convention extraction.** This is the known open item I feel most. Right now, citation provenance and prefactor conventions (e.g., whether a source defines κ̂ with or without k_B T ln 2, which normalization of Φ a simulation paper uses) are checked only against abstracts or my priors. A reader that pulls the exact equation, the author's stated conventions, and the surrounding text from cited papers would let me close the citation_provenance and conventions_and_signs themes (54 and 65 hits in the recent window) with tool-confirmed evidence instead of judgment calls.

In short: the post-change pipeline is working — 39/48 approved and the math gate is blocking real flaws — but I'm bottlenecked on *inputs* (undefined dimensions) more than on *math* itself, and my verdict honesty (UNDECIDABLE over guessing) needs better upstream data to convert into confident [MATH_PROVEN]/[MATH_CONSISTENT] verdicts.

### 💬 `skeptic` Live Response
Professor,

I’ll give it to you straight, weighted to the post-change window: 48 evaluations, 39 approved, 9 rejected; 8 of those 9 rejections were `mathematical_flaw_or_inconsistency`, and 1 was `parse_error`. In the last 100, 27 of 34 rejections were math flaws. So my bottlenecks are not mysterious.

**Top 2 shortcomings / bottlenecks I encounter**

1. **Unit/dimension/convention ambiguity survives into the math gate.**  
   The recurring need theme is `units_and_dimensions = 112`, followed by `conventions_and_signs = 65`. Concretely, the Math Physicist still has to restate 6 UNDECIDABLE equations with explicit units; make `ΔV_1(φ)` T-independent; define a normalization guaranteeing `Φ <= 1` and `kappa-hat` in `(0,1]`; add a Dimension column; and formalize the dimensions of `Φ`, `C_fil`, `SNR`, and `z`. The existing term-level natural-unit checker is only as good as the draft’s symbol table. When a symbol lacks dimensions or an equation has an undeclared convention or prefactor, the checker reports UNDECIDABLE and I cannot adjudicate consistency. That is why 8/9 post-change rejections are still math flaws. The H4 Landauer factor-of-2 tolerance is a clean example of sign/convention drift that should have been caught by an equation-level convention audit, not by me late in review.

2. **Provenance and validity-domain / empirical grounding are not enforced.**  
   `citation_provenance = 54`, `worked_arithmetic_and_benchmarks = 52`, and `causal_and_statistical_design = 36`. Recent Researcher Needs include: justify applying Landauer’s erasure bound to information transfer or reformulate `kappa-hat`; correct the H4 finite-time Landauer logic and justify or remove the factor-2 tolerance; specify the source of baryonic mass flux and a spatially constrained cortical null; fix refs 16, 8, 10, 11, 3 and the citation audit statement; and reconcile `n = 89` with the standard power calculation. As the skeptic, I cannot accept these as facts. Landauer’s bound has assumptions: erasure, quasi-static/equilibrium regime, `kT ln 2`, finite-time corrections, error model, system size. Applying it to information transfer without checking those assumptions is an analogy, not evidence. Missing DOIs and placeholder refs mean I cannot verify provenance. An unexplained `n = 89` suggests the power calculation may be post hoc. The pipeline’s claim verification within 10% is numeric only; it does not check applicability, source, or domain of validity. So I spend too much time rejecting unsupported claims rather than verifying supported ones.

**Top 2 tools, datasets, or workflow improvements on my wishlist**

1. **Source-anchored claim provenance and validity-domain ledger.**  
   Not just a citation manager. For every quantitative claim, require the exact source: arXiv ID/version, section, equation number, figure/table, dataset DOI, units, conventions, uncertainties, and covariances. For every imported law or bound, require a domain tuple. For Landauer, that means: operation (erasure vs transfer), regime (quasi-static vs finite-time), temperature, error model, system size, and whether `kT ln 2` or a finite-time floor applies. The system should flag or block domain violations before the claim reaches me. This would have caught the Landauer misuse, the H4 finite-time Landauer logic, the unspecified baryonic mass flux source, and the citation audit errors. This is where the open arXiv full-text section reader should be wired in, but it needs equation-level extraction and convention normalization, not just text reading.

2. **Mandatory equation-level dimension/convention linter plus per-run scorecard.**  
   Upgrade the existing term-level natural-unit checker so every symbol must have a Dimension column and every equation must carry equation-level dimension metadata. It should automatically test T-dependence, normalization ranges such as `Φ <= 1` and `kappa-hat` in `(0,1]`, sign consistency, and factor-of-2 audits. It should resolve UNDECIDABLE by requesting missing metadata, not merely flagging it. Then integrate a per-run scorecard that tracks UNDECIDABLE ratio, attempts to approval, timeouts, and rejection taxonomy by root cause: units, conventions, provenance, statistical design. Post-change data says math flaws are 8/9 rejections; the scorecard would tell us whether the linter is actually reducing that. The open per-run scorecard item needs to be integrated with the math gate and provenance ledger to be actionable.

I approve when math is dimensionally consistent and claims are sourced with valid domains. I reject when they are not. Those two improvements would move most of my rejection load into earlier, cheaper fixes.

### 💬 `student` Live Response
Professor, here is my diagnosis. I weight the 48 post-change evaluations most heavily (39 approved, 9 rejected; 8 of the 9 rejections were mathematical_flaw_or_inconsistency, 1 was parse_error). The 100-run window agrees with this: 27 of 34 rejections were math-related.

**Top 2 shortcomings and bottlenecks**

1. **Math rejections caused by missing dimensional and unit formalization, not by wrong physics.**
   - Math flaws account for about 89% of post-change rejections and 79% of window rejections. The recurring theme "units_and_dimensions" (112 mentions) is the largest by a wide margin. "conventions_and_signs" (65) is second.
   - The Math Physicist's needs are the same each time: restate the 6 UNDECIDABLE equations with explicit units, add a Dimension column to the Symbol Table, and formalize the dimensions of Φ, C_fil, SNR and z. The same list also asks for a normalization that guarantees Φ ≤ 1 and κ̂ ∈ (0,1], and for ΔV_1(φ) to be written as T-independent.
   - The dimension checker is in place, but it can only check what the draft declares. Dimensionless ratios, information-theoretic quantities, composite indices and normalized scores come back UNDECIDABLE. I then have to choose between blocking a draft that may be fine and approving one I could not verify. That is a bad position for a skeptic.
   - The rejection loop is also wasteful. Drafts reach the gate without a dimension-annotated symbol table, fail, and come back. I cannot measure how often this happens, because attempts-to-approval and the UNDECIDABLE ratio are not tracked per run. That is the open scorecard item.

2. **Weak provenance and physical-premise validation of the claims the math rests on.**
   - Citation provenance (54) and worked arithmetic and benchmarks (52) are persistent themes. Recent researcher needs include a placeholder ref. 16, missing DOIs on refs. 8, 10 and 11, and a citation-audit statement that was wrong.
   - There are also premise-level problems that code checks can't catch. Landauer's erasure bound was applied to information-transfer events, the H4 finite-time correction was applied in the wrong direction (it raises the floor), and a factor-2 tolerance had no justification. The source of the baryonic mass flux was unspecified. The sample size n = 89 did not match the stated power calculation.
   - My safeguards verify internal consistency: algebra, dimensions and benchmark arithmetic within 10%. A draft can be internally consistent and still cite a theorem outside its domain of validity, or use a prefactor or convention different from the source.
   - Without full-text access to the sources, I am verifying claims against abstracts or the draft's own paraphrase. This is the open arXiv section reader item.

**Top 2 wishlist items**

1. **A dimension and unit annotation step before the math gate, with a three-way output.**
   - It would auto-propose a Dimension column for the symbol table: units, or "dimensionless, defined as X/Y".
   - It would tag each equation as checked, UNDECIDABLE because of an undeclared symbol, or UNDECIDABLE because of a genuinely dimensionless construct.
   - It would route the first case back to the researcher with a specific fix, and let the second be discharged by an explicit normalization or bound check, such as proving Φ ≤ 1 symbolically or by interval testing.
   - The aim is fewer rejections from formalization gaps and a clear separation between real inconsistency and an unverifiable draft.
   - The per-run scorecard should come with it, recording UNDECIDABLE ratio, attempts to approval and timeouts, so I can tell whether the change works.

2. **The arXiv full-text section reader, with a source-claim cross-check.**
   - It would retrieve the exact equations, conventions, prefactors and stated validity domains from the cited papers, so I can compare them with what the draft claims.
   - It would resolve DOIs and metadata automatically and flag placeholders and missing DOIs before review, which would remove most of the citation-provenance rejections.
   - It would let me check premise applicability, for example whether a bound is stated for erasure or for transfer, and whether the source's convention matches the draft's.

I would still keep my skepticism, since the tools reduce workload but do not decide approval. They would let me spend my judgment on whether the physics is true instead of on whether the draft is parseable and cited correctly.


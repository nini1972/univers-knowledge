# Verification Protocol

For the Student Agent to accept any concept from the Researcher, the Skeptic must clear it based on the following **Verification Threshold**:

## 1. Source Consensus
- **Rule:** The research must originate from a minimum of **3 independent, peer-reviewed scientific sources**.
- **Action:** If the sources are missing or unreliable, the Skeptic rejects the claim.

## 2. Empirical Evidence vs. Theoretical Status
- **Rule:** The Skeptic must determine if the concept has been experimentally proven (e.g., standard model particles via accelerators) or remains theoretical (e.g., String theory, gravitons).
- **Action:**
  - Proven concepts are labeled as **[VERIFIED]**.
  - Unproven, mathematically consistent concepts are labeled as **[THEORETICAL]**.
  - Pseudoscience or logically flawed concepts are **[REJECTED]**.

## 3. Transparency of Debate
- **Rule:** If the scientific community has major competing theories, the Skeptic must highlight them.
- **Action:** The Student will not accept a single theory as absolute truth if mainstream consensus is divided.

## 4. Visual & Mathematical Grounding
- **Rule:** Complex phenomena must be grounded by mathematical equations (using KaTeX/LaTeX) and require a visual representation request (handled by the Visualizer agent in later phases).

## 5. Visual Grounding
- **Rule:** A detailed visual/image prompt description must be included in the research report.
- **Action:** The Visualizer Agent will use this to generate a concept image.

## 6. Mathematical Integrity *(New — Math Physicist Agent)*
- **Rule:** The Math Physicist Agent must run a Tier 1 automatic verification on every research report:
  - Extract all LaTeX equations
  - Check dimensional consistency (do units balance on both sides?)
  - Classify topological arguments (fiber bundles, Calabi-Yau, spin foams, etc.)
  - Validate numerical predictions against CODATA/PDG physical constants
  - Output a **Math Score (0–4)** and assign a **math_status** label
- **Action:**
  - `[MATH_PROVEN]` / `[MATH_CONSISTENT]` with Math Score ≥ 3/4 → Criterion 6 **PASSES**
  - `[MATH_TOPOLOGICAL]` with valid structural analysis → Criterion 6 **PASSES**
  - `[MATH_CONJECTURED]` with clear assumptions flagged → Criterion 6 **PASSES** (concept labeled [THEORETICAL])
  - `[MATH_FLAWED]` (dimensional inconsistency detected) → Criterion 6 **FAILS** — concept must be flagged or rejected
  - `[MATH_PENDING]` (no equations found) → Criterion 6 **PENDING** — Skeptic marks unchecked with note

## Verification Score Threshold
- **Passing score:** ≥ **5/6** for Student to approve a concept
- **Below 5/6:** Student must reject and request a retry
- **Exception:** Concepts that score 4/6 but have `[MATH_TOPOLOGICAL]` or `[MATH_CONJECTURED]` may still be approved as `[THEORETICAL]` at the Student's discretion if all other criteria are satisfied

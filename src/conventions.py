"""Shared Canonical Physics, Cosmology, and Causal-Design Conventions (P1).

Injected into Researcher, Math Physicist, Skeptic, Student, and Micro-Revision
tasks across Levels 1, 2, and 3 so every agent in a crew shares identical unit
definitions, metric signatures, thermal-history anchors, and claim-scope tags.
"""

from textwrap import dedent

CANONICAL_CONVENTIONS_HEADER = dedent("""
    CANONICAL PHYSICS & COSMOLOGY CONVENTIONS (SHARED CREW BASELINE):
    1. Natural Units & Conversions:
       - Default basis: hbar = c = k_B = 1 (all quantities expressed in mass/energy dimension [E]^n in GeV^n), unless SI/CGS units are explicitly declared for laboratory or astronomical observables.
       - Reduced Planck mass: M_Pl = (8*pi*G)^(-1/2) = 2.435e18 GeV (distinct from Planck mass m_Pl = G^(-1/2) = 1.221e19 GeV; 8*pi*G = 1/M_Pl^2). Never mix M_Pl and m_Pl without an explicit sqrt(8*pi) factor.
       - Exact conversions: 1 GeV^-1 = 1.97327e-16 m = 6.58212e-25 s; 1 Mpc = 3.08568e22 m = 1.5637e38 GeV^-1; H_0 = 100*h km s^-1 Mpc^-1 = 2.1331e-42*h GeV.
    2. Spacetime, Metric & Field Normalization:
       - Default metric signature: (-,+,+,+) ("mostly plus"). With this signature, the canonical scalar kinetic invariant is X = -(1/2) g^{mu nu} d_mu phi d_nu phi = +(1/2) dot(phi)^2 - (1/2) a^-2 (grad phi)^2 > 0 on a homogeneous background. (If citing a (+,-,-,-) source, state the sign flip explicitly.)
       - 4D Action & Mass Dimensions: S = int d^4x sqrt(-g) [ (M_Pl^2 / 2) R + L_matter ], where [L] = [E]^4, [d^4x] = [E]^-4, [g_{mu nu}] = [E]^0, [phi] = [A_mu] = [H] = [T] = [E]^1, [R] = [m^2] = [E]^2, [n] = [s] = [J^mu] = [E]^3, [rho] = [p] = [V(phi)] = [E]^4, [G] = [E]^-2.
       - Time-Varying Equation of State w(a): The continuity equation dot(rho) + 3*H*(1 + w(a))*rho = 0 integrates to rho(a) = rho_0 * exp(-3 * int_1^a [(1 + w(a')) / a'] da'). NEVER write rho(a) = rho_0 * a^(-3*(1 + w(a))) when w(a) is not constant.
    3. Thermal History & Relativistic Degrees of Freedom:
       - Present CMB temperature: T_0 = 2.7255 K = 2.3486e-13 GeV; present entropy density s_0 = (2*pi^2/45) * g_{*s}(T_0) * T_0^3 ≈ 2891 cm^-3 with g_{*s}(T_0) = 3.909 and g_*(T_0) = 3.383 (for N_eff = 3.044).
       - Standard Model g_*(T) ≈ g_{*s}(T) anchors: 106.75 (T >= 175 GeV), 86.25 (5 GeV <= T <= 80 GeV), 61.75 (T ~ 1 GeV), 10.75 (1 MeV <= T <= 100 MeV).
       - Scale-factor expansion across adiabatic epochs: a_0 / a_reh = [g_{*s}(T_reh) / g_{*s}(T_0)]^(1/3) * (T_reh / T_0) (multiplied by entropy-dilution factor Delta^(1/3) if a late-decaying scalar/flaton injects entropy).
""").strip()


LEVEL_1_2_PREAMBLE_REQUIREMENTS = dedent("""
    MANDATORY STRUCTURE INSIDE `## 3. Mathematical Framework`:
    To ensure full dimensional and convention verifiability across agents, open `## 3. Mathematical Framework` with these three sub-sections:
    - `### Conventions & Symbol Table`:
      * Explicitly state the metric signature, unit basis (e.g., natural units hbar = c = k_B = 1 vs SI), and Planck mass normalization (M_Pl vs m_Pl).
      * Provide a compact Markdown Symbol Table (`| Symbol | Meaning | Dimension |`) listing every field, coupling, and observable used in your equations (using `[E]^n` in natural units or SI units).
    - `### Validity Domain & Claim Scope`:
      * State the regime of validity for the equations (e.g., canonical vs k-essence kinetic sector, ghost-free/gradient stability conditions c_s^2 > 0, linear k << k_NL perturbation regime, or thermal equilibrium).
      * Tag every major theoretical conclusion or bound as either **`[GENERAL]`** (follows from conservation laws/symmetries alone) or **`[MODEL-DEPENDENT: <explicit assumptions>]`** (e.g., `[MODEL-DEPENDENT: canonical single-field quintessence with X = (1/2)dot(phi)^2 and V > 0]`).
    - `### Governing Equations & Observables`:
      * Present the numbered/labeled equations showing the explicit chain: **Assumptions -> Governing Equations -> Predicted Observable** (e.g., c_s^2, f*sigma_8(z), w_0-w_a, S_8, Delta N_eff, or present-day physical scale lambda_0 in meters).
""").strip()


LEVEL_3_PREAMBLE_REQUIREMENTS = dedent("""
    MANDATORY STRUCTURE INSIDE `## 3. Mathematical Framework` (LEVEL 3 EMERGENCE, CAUSAL & TOPOLOGICAL DESIGN):
    Open `## 3. Mathematical Framework` with these three sub-sections:
    - `### Conventions, Symbol Table & Estimand`:
      * Provide a compact Markdown Symbol Table (`| Symbol | Meaning | Dimension / Domain |`) for all physical, information-theoretic, topological, or statistical quantities.
      * Explicitly define the formal **Target Estimand** (e.g., interventional contrast, Controlled Direct Effect, transfer-entropy rate, or topological Betti-curve distance) and distinguish the **Theoretical Construct** (e.g., IIT integrated information Phi) from its **Operational Empirical Proxy** (e.g., Perturbational Complexity Index PCI or spectral Granger causality).
    - `### Validity Domain, Identification & Claim Scope`:
      * State the explicit **Identification Assumptions** or **Null-Model Conditions** required for valid inference (e.g., causal DAG structure, sequential ignorability, cross-world independence for natural indirect effects, or Gaussian random field / LambdaCDM N-body null realizations).
      * Tag every major conclusion as either **`[GENERAL]`** or **`[MODEL-DEPENDENT: <explicit assumptions>]`**.
    - `### Governing Equations, Variance Algebra & Decision Rule`:
      * Write out the formal equations, ensuring that any variance of a difference or contrast explicitly retains covariance terms: Var(A - B) = Var(A) + Var(B) - 2*Cov(A, B) (never drop covariance unless independence is proven).
      * Specify a preregistered **Decision Rule** derived from divergent formal model predictions, including sampling distribution, statistical power, and multiplicity control (e.g., Holm-Bonferroni or Benjamini-Hochberg FDR).
""").strip()


def get_conventions_prompt_block(level: int = 1) -> str:
    """Return the combined Canonical Conventions Header + Level-appropriate Preamble requirements."""
    preamble = LEVEL_3_PREAMBLE_REQUIREMENTS if level == 3 else LEVEL_1_2_PREAMBLE_REQUIREMENTS
    return f"\n\n{CANONICAL_CONVENTIONS_HEADER}\n\n{preamble}\n"

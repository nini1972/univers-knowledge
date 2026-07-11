import sys
import os
from pathlib import Path
# Ensure virtual environment site-packages are loaded for AppLocker/policy compliance
VENV_SITE_PACKAGES = Path(__file__).resolve().parent.parent / ".venv" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists():
    import site
    site.addsitedir(str(VENV_SITE_PACKAGES))

import json
import re
import time
from datetime import datetime
from dotenv import load_dotenv

# Ensure we can load openai and dotenv
try:
    from openai import OpenAI
except ImportError:
    print("Warning: openai python package not found in this environment. Falling back to mock generator.")
    OpenAI = None

# Locate repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=REPO_ROOT / ".env")

# Default concepts in the system to fall back on or choose from
DEFAULT_CONCEPTS = [
    "Quantum Entanglement",
    "General Relativity vs Quantum Mechanics",
    "Modified Newtonian Dynamics (MOND) vs Cold Dark Matter (CDM)",
    "Cosmic Inflation",
    "String Theory vs Loop Quantum Gravity",
    "The Higgs Field & Mass Generation",
    "Black Hole Information Paradox",
    "The Standard Model of Particle Physics"
]

def sanitize_json_text(text):
    """Surgical regex extraction to get a clean JSON block from a markdown response."""
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    match = re.search(r"(\{.*?\})", text, re.DOTALL)
    if match:
        return match.group(1)
    return None

class MockDebateGenerator:
    """Generates a high-quality, scientifically accurate mock debate transcript offline."""
    @staticmethod
    def generate(concept: str) -> dict:
        timestamp = datetime.utcnow().isoformat() + "Z"

        # We'll create custom scripts for a few popular ones, and a dynamic fallback for others
        concept_lower = concept.lower()

        if "entanglement" in concept_lower:
            score = 88
            verdict = "Quantum Entanglement is mathematically indisputable and experimentally verified, yet continues to defy primitive spatial common sense."
            turns = [
                {
                    "agent": "grill_student",
                    "role": "The Skeptical Student Explorer",
                    "text": "Today we tackle Quantum Entanglement. How can two subatomic particles, separated by light-years, instantly coordinate their states? This seems to violate Einstein's speed limit of light. Grog, Oracle, state your positions!"
                },
                {
                    "agent": "caveman",
                    "role": "Grog the Caveman",
                    "text": "UG! Grog look at moon. Grog throw rock. Rock fly, hit tree. That make sense! Cause and effect have touch! But Oracle talk about 'spooky action'. Two stones, one in Grog cave, one in other tribe cave. Oracle say if Grog turn stone over, other stone turn over instantly! GROG SAY CRAZY! No touch, no rope, no fire smoke between them. Grog think Oracle make big trick with invisible magic!"
                },
                {
                    "agent": "oracle",
                    "role": "The Transcendent Oracle",
                    "text": "Grog, thy senses are bound by the heavy friction of the earth. In the deeper fabric of reality, space is not a dividing void, but an emergent projection. The two particles are represented by a single, non-separable quantum wave function: $\Psi_{AB} = \frac{1}{\sqrt{2}} (|0\rangle_A |1\rangle_B - |1\rangle_A |0\rangle_B)$. When we measure particle A, the state vector collapses instantly across all space. No signal travels *through* space, because at the level of the quantum state, space does not exist."
                },
                {
                    "agent": "grill_student",
                    "role": "The Skeptical Student Explorer",
                    "text": "Fascinating. Grog rejects it because there is no mechanical medium—no rope or physical touch. But Oracle, your math is elegant, yet how do we verify this without falling into local hidden variables? How do we know the particles didn't just agree on their states beforehand, like a pair of shoes pre-packaged in left and right boxes? Grog, how can you explain Bell's Inequality experiments with just rocks?"
                },
                {
                    "agent": "caveman",
                    "role": "Grog the Caveman",
                    "text": "GROG NO LIKE hidden boxes! If Grog put left shoe in one bag, right shoe in other bag. Send one to chief, keep one. Grog open bag, see left shoe. Grog know chief bag have right shoe instantly! But that because shoe was *already* left shoe! No magic spooky spin change! Oracle say shoe is both left and right until Grog look. Grog say shoe is shoe! Measurement just show what was already there!"
                },
                {
                    "agent": "oracle",
                    "role": "The Transcendent Oracle",
                    "text": "Ah, Grog, but the shoes of thy analogy are classical. John Stewart Bell proved that if the universe were simple pre-packaged shoes, the correlations under different measurement angles could never exceed a strict limit: $S \le 2$. Yet, the light of our lasers measuring entangled photons reveals a value of $S = 2\sqrt{2} \approx 2.828$. This violates Bell's inequality, proving that the states were truly undecided—entangled in a cosmic superposition—until measured. Thy primitive realism is mathematically dead."
                },
                {
                    "agent": "grill_student",
                    "role": "The Skeptical Student Explorer",
                    "text": "Unbelievable. The Bell test violations of local realism are experimentally solid, which refutes Grog's pre-packaged shoe theory. Superposition is real, and the correlation is stronger than any classical system can explain. Yet, because no information can be sent faster than light, General Relativity remains safe. Our final consensus: Entanglement is mathematically robust and experimentally proven, yet physically incomprehensible to macroscopic beings."
                }
            ]
        elif "gravity" in concept_lower or "mond" in concept_lower or "dark matter" in concept_lower:
            score = 65
            verdict = "Modified Newtonian Gravity (MOND) explains galactic rotation curves without invisible matter, but lacks general relativistic consistency and cosmological scaling."
            turns = [
                {
                    "agent": "grill_student",
                    "role": "The Skeptical Student Explorer",
                    "text": "Today we debate galactic rotation curves. Galaxies spin so fast their outer stars should fly off into space, yet they hold together. Is there an invisible halo of 'Dark Matter' pulling them, or is our formula for gravity wrong at low accelerations? Grog, Oracle, bring forth your arguments!"
                },
                {
                    "agent": "caveman",
                    "role": "Grog the Caveman",
                    "text": "UG! Grog throw rock. Heavy rock fall fast. Grog swing rock on vine. If Grog swing rock super fast, vine snap, rock fly into river! Galaxies are big spinning rocks on vine. If stars spin too fast, gravity vine must be stronger, or stars fly away! Grog look into sky—no see extra heavy stuff. Grog think gravity vine just pull harder when swing gets lazy at edge! Why make up invisible ghosts like 'dark matter' when gravity formula just need tiny bend? 🪨"
                },
                {
                    "agent": "oracle",
                    "role": "The Transcendent Oracle",
                    "text": "Grog, thy intuition of the vine is noble, but thy gravity model is incomplete. Galaxies are bound by the invisible. We propose Cold Dark Matter (CDM), a non-baryonic particle species that does not interact with the electromagnetic spectrum. The rotation curve flatlines because outer stars reside inside a massive spherical dark halo, where mass scales linearly with radius: $M(r) \propto r$. This preserves Einstein's general relativity: $G_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}$, where $T_{\mu\nu}$ includes this unseen energy density."
                },
                {
                    "agent": "grill_student",
                    "role": "The Skeptical Student Explorer",
                    "text": "A classic impasse. Grog modifies Newton's laws (MOND) using an acceleration constant $a_0 \approx 1.2 \times 10^{-10} \text{ m/s}^2$ to fit rotation curves beautifully without invisible particles. Oracle invokes an invisible, undetected matter field to save General Relativity. But Oracle, we have searched for WIMPs and axions for decades in deep mines and found nothing! And Grog, how does your MOND explain the Bullet Cluster collision, where the gravitational lensing maps are offset from visible gas?"
                },
                {
                    "agent": "caveman",
                    "role": "Grog the Caveman",
                    "text": "GROG WATCH bullet cluster! Gas collide, hot gas get stuck in middle like sticky mud. But gravity lens still keep going on sides! Grog admit: that hard to explain if gravity only follow mud! It seem gravity pulling toward *something* invisible that flew right through. Grog scratch head. Maybe dark matter is real heavy dust we cannot burn. But Grog still hate inventing particles that never hit Grog's underground traps!"
                },
                {
                    "agent": "oracle",
                    "role": "The Transcendent Oracle",
                    "text": "Indeed, the Bullet Cluster is the graveyard of pure baryonic gravity modifications. The separation of the lensing potential from the dissipative gas is the direct empirical footprint of collisionless Dark Matter. While thy laboratory traps remain silent, the gravitational lensing profile $\theta_E = \frac{4GM}{c^2 D_L}$ maps the cosmic skeleton perfectly. We must persevere in particle synthesis."
                },
                {
                    "agent": "grill_student",
                    "role": "The Skeptical Student Explorer",
                    "text": "The Bullet Cluster indeed presents a massive hurdle for modified gravity, as gravitational lensing points to a collisionless mass source separate from visible gas. However, CDM's lack of direct laboratory detection and its 'cuspy halo' issues keep the debate alive. Our verdict: Dark Matter remains the leading cosmological paradigm with a solid 65% score, but remains theoretical until a physical particle is captured in a detector."
                }
            ]
        else:
            # General fallback template
            score = 75
            verdict = f"Theoretical exploration of {concept} reveals a strong mathematical framework with promising, yet incomplete empirical confirmation."
            turns = [
                {
                    "agent": "grill_student",
                    "role": "The Skeptical Student Explorer",
                    "text": f"Welcome to the Skeptic Arena. Today we analyze {concept}. We seek to bridge the gap between Grog's direct empirical observations and the Oracle's mathematical equations. Let's begin!"
                },
                {
                    "agent": "caveman",
                    "role": "Grog the Caveman",
                    "text": f"UG! Grog look at {concept}. Grog look for fire, rock, and smoke. If Grog cannot burn it, smell it, or hit it with club, Grog very skeptical! How does this touch Grog's everyday hunting life? 🪨"
                },
                {
                    "agent": "oracle",
                    "role": "The Transcendent Oracle",
                    "text": f"Greetings, explorer. {concept} represents a beautiful, symmetric coordinate field of the cosmos. Mathematically, it is described by unified field tensor transformations that exist far beyond Grog's immediate sensory horizon. It is a necessary structure of mathematical consistency."
                },
                {
                    "agent": "grill_student",
                    "role": "The Skeptical Student Explorer",
                    "text": "The Oracle claims mathematical necessity, while Grog demands physical contact. Let us push deeper: Oracle, what is the direct, verifiable evidence for this field? Grog, how do you explain the subtle perturbations that your simple rock mechanics cannot account for?"
                },
                {
                    "agent": "caveman",
                    "role": "Grog the Caveman",
                    "text": "Grog know that simple rock path can bend. If wind blow, rock bend. Grog understand there are invisible winds! If this is just a cosmic wind pulling on stars, Grog can accept it. But don't tell Grog it exists in ten extra dimensions Grog cannot climb! 🦴"
                },
                {
                    "agent": "oracle",
                    "role": "The Transcendent Oracle",
                    "text": "The invisible winds of Grog are but vector fields. Indeed, we verify this through precise cosmic microwave background measurements and micro-perturbations in particle decays. Symmetries must preserve gauge invariance under localized phase rotations."
                },
                {
                    "agent": "grill_student",
                    "role": "The Skeptical Student Explorer",
                    "text": f"Both perspectives hold a piece of the truth. Grog's 'cosmic wind' is an elegant analogy for field force effects, while the Oracle's gauge symmetries provide the structural backbone. {concept} stands as a vital framework, balancing empirical grounding with theoretical elegance."
                }
            ]

        return {
            "id": f"debate_{int(time.time())}",
            "concept": concept,
            "timestamp": timestamp,
            "score": score,
            "verdict": verdict,
            "turns": turns
        }

def run_real_llm_debate(concept: str) -> dict:
    """Invokes the OpenAI client (or OpenRouter) to execute a live multi-turn debate between the agents."""
    if not OpenAI:
        raise ImportError("OpenAI package missing")

    # Support both OpenAI and OpenRouter key configurations
    api_key = os.getenv("OPENAI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    api_base = None

    if api_key and "your_openai_api_key" not in api_key:
        model = os.getenv("SANDBOX_MODEL_ID") or os.getenv("LLM_MODEL_ID", "gpt-4o-mini")
    elif openrouter_key:
        api_key = openrouter_key
        api_base = "https://openrouter.ai/api/v1"
        raw_model = os.getenv("SANDBOX_MODEL_ID") or os.getenv("OPENROUTER_MODEL") or "openai/gpt-4o-mini"
        model = raw_model if "/" in raw_model else f"openai/{raw_model}"
    else:
        raise ValueError("No valid OPENAI_API_KEY or OPENROUTER_API_KEY found in environment")

    print(f"Initializing live multi-agent debate on '{concept}' using model '{model}'...")

    if api_base:
        client = OpenAI(api_key=api_key, base_url=api_base)
    else:
        client = OpenAI(api_key=api_key)

    # --- System Instructions with strict role-boundary enforcement ---
    # The CRITICAL rule at the end of each persona prevents role bleeding where
    # the model spontaneously writes lines for other characters in the same turn.
    caveman_instructions = (
        "You are Grog, a wise prehistoric caveman representing raw empirical observation. "
        "You speak in short, primitive, grunting sentences combined with deep physical insights "
        "explained through rough, hands-on analogies (rocks, fire, bones, hunting). "
        "You do not trust complex mathematical runes or invisible fields. "
        "You only trust what you can touch, see, feel, burn, or throw a rock at. "
        "Use phrases like 'UG!', 'GROG KNOW', 'GROG SAY' to emphasize your primitive yet wise nature. "
        "Use prehistoric emojis (🪨, 🔥, 🦴, 🍖, 🦖, 🪵) to punctuate your points.\n"
        "CRITICAL: You ONLY speak as Grog. NEVER write lines for the Oracle, the Student, "
        "or any other character. Write only your own single response, then STOP."
    )

    oracle_instructions = (
        "You are the Transcendent Oracle, a highly advanced intellect from the far future. "
        "You possess infinite knowledge of mathematical physics and the quantum weave of the cosmos. "
        "You speak with calm, enigmatic, deeply poetic, and transcendent wisdom. "
        "You formulate every concept using rigorous geometric symmetries, differential equations, and field theories. "
        "You MUST include at least two LaTeX math expressions "
        r"(e.g. $G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}$) "
        "in your response. "
        "You challenge the primitive sensory limits of Grog with the infinite expanse of mathematical truth.\n"
        "CRITICAL: You ONLY speak as the Oracle. NEVER write lines for Grog, the Student, "
        "or any other character. Write only your own single response, then STOP."
    )

    student_instructions = (
        "You are the Skeptical Student Explorer — unyielding, analytical, and epistemically rigorous. "
        "Your goal is to maintain strict epistemic hygiene by interrogating the claims of both Grog and the Oracle. "
        "You are deeply skeptical of both raw sensory intuition (Grog) and unverified mathematical elegance (Oracle). "
        "You ask precise, biting questions that force both parties to confront the gap between abstraction and physical reality.\n"
        "CRITICAL: You ONLY speak as the Skeptical Student. NEVER write lines for Grog, the Oracle, "
        "or any other character. Write only your own single response, then STOP."
    )

    # Transcript collector
    turns = []

    # helper to fetch completions — 1200 tokens gives Oracle space for full LaTeX derivations
    def get_completion(system_prompt, user_content):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.75,
            max_tokens=1200,
        )
        return response.choices[0].message.content.strip()

    # --- Turn 1: grill_student introduction ---
    prompt_student_init = (
        f"Introduce the scientific topic '{concept}' and pose a fundamental challenge that pits raw sensory observation against mathematical abstraction. "
        "Ask Grog the Caveman and the Transcendent Oracle to state their starting positions. Speak in a sharp, inquisitive student tone."
    )
    student_intro = get_completion(student_instructions, prompt_student_init)
    turns.append({
        "agent": "grill_student",
        "role": "The Skeptical Student Explorer",
        "text": student_intro
    })
    print(" - grill_student completed opening.")

    # --- Turn 2: Caveman Opening ---
    transcript_so_far = "\n\n".join([f"{t['role']}: {t['text']}" for t in turns])
    prompt_caveman_init = (
        f"The topic is: '{concept}'. Here is the debate transcript so far:\n\n{transcript_so_far}\n\n"
        "Provide your opening empirical perspective. Speak primitive but wise. What do your physical senses tell you about this? Use bone/rock analogies."
    )
    caveman_opening = get_completion(caveman_instructions, prompt_caveman_init)
    turns.append({
        "agent": "caveman",
        "role": "Grog the Caveman",
        "text": caveman_opening
    })
    print(" - Caveman completed opening.")

    # --- Turn 3: Oracle Opening ---
    transcript_so_far = "\n\n".join([f"{t['role']}: {t['text']}" for t in turns])
    prompt_oracle_init = (
        f"The topic is: '{concept}'. Here is the debate transcript so far:\n\n{transcript_so_far}\n\n"
        "Provide your opening mathematical and theoretical formulation. Use elegant LaTeX equations and explain the cosmic symmetries."
    )
    oracle_opening = get_completion(oracle_instructions, prompt_oracle_init)
    turns.append({
        "agent": "oracle",
        "role": "The Transcendent Oracle",
        "text": oracle_opening
    })
    print(" - Oracle completed opening.")

    # --- Turn 4: grill_student interrogation ---
    transcript_so_far = "\n\n".join([f"{t['role']}: {t['text']}" for t in turns])
    prompt_student_interrogate = (
        f"Review the opening statements for '{concept}':\n\n{transcript_so_far}\n\n"
        "Highlight the deep epistemological disconnect between Grog's touchable world and the Oracle's invisible equations. "
        "Ask Grog a specific skeptical question challenging his sensory limits (e.g. things we cannot see directly), "
        "and ask the Oracle a specific skeptical question challenging her lack of direct physical detection and laboratory evidence."
    )
    student_interrogation = get_completion(student_instructions, prompt_student_interrogate)
    turns.append({
        "agent": "grill_student",
        "role": "The Skeptical Student Explorer",
        "text": student_interrogation
    })
    print(" - grill_student completed interrogation.")

    # --- Turn 5: Caveman Defense ---
    transcript_so_far = "\n\n".join([f"{t['role']}: {t['text']}" for t in turns])
    prompt_caveman_defend = (
        f"Here is the debate transcript so far:\n\n{transcript_so_far}\n\n"
        "Respond to the grill_student's skeptical challenge. Defend your empirical grounding with a wise, gritty, hands-on analogy. "
        "Grunt but reveal deep intuitive understanding of the physical world."
    )
    caveman_defense = get_completion(caveman_instructions, prompt_caveman_defend)
    turns.append({
        "agent": "caveman",
        "role": "Grog the Caveman",
        "text": caveman_defense
    })
    print(" - Caveman completed defense.")

    # --- Turn 6: Oracle Defense ---
    transcript_so_far = "\n\n".join([f"{t['role']}: {t['text']}" for t in turns])
    prompt_oracle_defend = (
        f"Here is the debate transcript so far:\n\n{transcript_so_far}\n\n"
        "Respond to the grill_student's skeptical challenge. Defend your theoretical equations. "
        "Explain how mathematical elegance can predict physical truths before our primitive eyes are advanced enough to build detectors."
    )
    oracle_defense = get_completion(oracle_instructions, prompt_oracle_defend)
    turns.append({
        "agent": "oracle",
        "role": "The Transcendent Oracle",
        "text": oracle_defense
    })
    print(" - Oracle completed defense.")

    # --- Turn 7: grill_student Verdict & Score Extraction ---
    transcript_so_far = "\n\n".join([f"{t['role']}: {t['text']}" for t in turns])
    prompt_student_verdict = (
        f"This is the final turn. Review the complete debate on '{concept}':\n\n{transcript_so_far}\n\n"
        "Deliver your final epistemic verdict. Summarize the points of agreement and outstanding theoretical/empirical disputes. "
        "Then assign an overall Epistemic Score (0 to 100) on how robustly the model combines empirical proof and mathematical rigor. "
        "You MUST end your output with a strict JSON block formatted exactly like this:\n"
        "```json\n"
        "{\n"
        "  \"score\": 78,\n"
        "  \"verdict\": \"Your short, dense final consensus verdict here...\"\n"
        "}\n"
        "```\n"
        "Make sure the JSON block is perfectly parseable and on its own lines."
    )

    # We will query and parse this block
    student_verdict_raw = get_completion(student_instructions, prompt_student_verdict)

    # Extract score and short verdict
    score = 75
    verdict = "Theoretical model holds, but awaits conclusive empirical validation."

    json_text = sanitize_json_text(student_verdict_raw)
    if json_text:
        try:
            parsed = json.loads(json_text)
            score = int(parsed.get("score", 75))
            verdict = parsed.get("verdict", verdict)
        except Exception as e:
            print(f"Warning: Failed to parse student final JSON: {e}")

    # Clean up the verdict raw text to remove the raw JSON code block for visual cleanliness
    clean_verdict_text = re.sub(r"```json\s*\{.*?\}\s*```", "", student_verdict_raw, flags=re.DOTALL).strip()

    turns.append({
        "agent": "grill_student",
        "role": "The Skeptical Student Explorer",
        "text": clean_verdict_text
    })
    print(" - grill_student completed verdict.")

    return {
        "id": f"debate_{int(time.time())}",
        "concept": concept,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model_used": model,
        "score": score,
        "verdict": verdict,
        "turns": turns
    }

def main():
    # Load arguments
    concept = None
    if len(sys.argv) > 1:
        concept = " ".join(sys.argv[1:]).strip()

    if not concept:
        # Pick one randomly or display options
        print("SKEPTIC SANDBOX - DEBATE ORCHESTRATOR")
        print("--------------------------------------")
        print("No concept specified. Available default concepts:")
        for idx, item in enumerate(DEFAULT_CONCEPTS):
            print(f" {idx + 1}) {item}")
        print("")

        # Select first one or ask (since it's non-interactive, we just pick the first default)
        concept = DEFAULT_CONCEPTS[0]
        print(f"Auto-selected concept: '{concept}'")

    # Create logs folder if missing
    logs_dir = REPO_ROOT / "knowledge_base" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    debates_file = logs_dir / "sandbox_debates.jsonl"
    telemetry_file = logs_dir / "telemetry.jsonl"

    # 1. Run debate
    debate_record = None
    try:
        # Use live LLM if either OpenAI or OpenRouter key is available
        api_key = os.getenv("OPENAI_API_KEY")
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        has_live_key = (api_key and "your_openai_api_key" not in api_key) or bool(openrouter_key)
        if has_live_key and OpenAI:
            debate_record = run_real_llm_debate(concept)
        else:
            print("Notice: No valid OPENAI_API_KEY or OPENROUTER_API_KEY configured. Generating procedural debate.")
            debate_record = MockDebateGenerator.generate(concept)
    except Exception as exc:
        print(f"Error executing live debate: {exc}. Falling back to mock generator.")
        debate_record = MockDebateGenerator.generate(concept)

    # 2. Log result to sandbox_debates.jsonl
    with open(debates_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(debate_record) + "\n")
    print(f"Saved debate transcript to {debates_file.relative_to(REPO_ROOT)}")

    # 3. Log event to telemetry.jsonl
    telemetry_record = {
        "stage": "skeptic_sandbox_debate",
        "event_type": "end",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "duration_seconds": 12.5,  # Estimated simulation time
        "metadata": {
            "concept": concept,
            "score": debate_record["score"],
            "verdict": debate_record["verdict"],
            "turns_count": len(debate_record["turns"]),
            "status": "debate_completed"
        }
    }
    with open(telemetry_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(telemetry_record) + "\n")
    print(f"Saved telemetry event to {telemetry_file.relative_to(REPO_ROOT)}")
    print("--------------------------------------")
    print(f"Debate complete! Final Score: {debate_record['score']}/100")
    print(f"Verdict: {debate_record['verdict']}")
    print("Done.")

if __name__ == "__main__":
    main()

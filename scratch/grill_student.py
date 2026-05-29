#!/usr/bin/env python
import os
import sys
import json
import re
from pathlib import Path
from dotenv import load_dotenv

# Try importing openai; degrade gracefully if unavailable or key missing
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# ANSI Color Codes for Futuristic Terminal Look
C_CYAN = "\033[96m"
C_BLUE = "\033[94m"
C_GREEN = "\033[92m"
C_AMBER = "\033[93m"
C_RED = "\033[91m"
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"


def print_banner():
    banner = f"""
{C_CYAN}╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║          🌌   U N I V E R S   -   S K E P T I C A L   C L I           ║
║               "GRILL THE STUDENT" EPISTEMOLOGICAL SANDBOX             ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝{C_RESET}
    """
    print(banner)


def load_database() -> list:
    """Loads all compiled concepts from the synchronized database."""
    repo_root = Path(__file__).resolve().parent.parent
    db_path = repo_root / "knowledge_base" / "database.json"
    
    if not db_path.exists():
        print(f"{C_RED}[!] Error: database.json not found.{C_RESET}")
        print(f"{C_DIM}Please synchronize the index first to compile the concepts database.{C_RESET}\n")
        return []
        
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"{C_RED}[!] Failed to parse database.json: {e}{C_RESET}\n")
        return []


def clean_markdown(text: str) -> str:
    """Cleans markdown syntax for terminal readability."""
    if not text:
        return ""
    # Strip frontmatter
    text = re.sub(r"^---\s*\n[\s\S]*?\n---\s*", "", text)
    # Strip basic headers, bold tags, italic tags
    text = re.sub(r"##+\s*", "", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    return text.strip()


def mock_student_response(concept: dict, question: str) -> str:
    """High-fidelity rule-based fallback response generator when OpenAI is disabled."""
    q_lower = question.lower()
    title = concept["title"]
    status = concept["status"]
    
    # Generic skeptical statements
    sus_points = [
        "What empirical data is backing this claim? We cannot build bridges on mere math placeholders.",
        "You are assuming the mainstream interpretation without questioning the measurement problem.",
        "That is an elegant model, yes. But nature is under no obligation to match our pretty equations.",
        "Have we tested this beyond standard energy bounds, or are we just extrapolating to infinity?"
    ]
    
    if "gravity" in q_lower or "relativity" in q_lower:
        return (
            f"Ah, gravity. General Relativity works beautifully on macroscopic scales, but it completely breaks "
            f"down at quantum singularities. If we talk about '{title}', we must ask if we are actually observing "
            f"spacetime curvature or just seeing an emergent thermodynamic effect. Until we have a verified quantum gravity, "
            f"I remain skeptical of both String Theory and Loop Quantum Gravity."
        )
    
    if "string" in q_lower or "dimension" in q_lower or "supersymmetry" in q_lower:
        return (
            f"Let's be intellectually honest: Supersymmetry was expected at the LHC energies, yet we found nothing. "
            f"And String Theory predicts 10 or 11 dimensions with 10^500 vacuum states. That is not science; that is "
            f"untestable mathematical landscaping! How do you propose we isolate our universe's vacuum out of 10^500 options? "
            f"Regarding '{title}', my position stands: until it makes a unique, falsifiable prediction, it stays as theoretical speculation."
        )
        
    if "quantum" in q_lower or "entanglement" in q_lower or "wave" in q_lower:
        return (
            f"Quantum Mechanics is mathematically verified, sure. But what does it actually *mean*? Copenhagen? Many-Worlds? "
            f"Pilot Wave? The fact that we have multiple, mathematically identical but philosophically contradictory interpretations "
            f"means we are missing something fundamental. We calculate, we predict, but we do not yet understand. "
            f"So yes, even for '{title}', we must look at the exact verification limits."
        )

    # General Fallback based on Concept Status
    if status == "VERIFIED":
        return (
            f"The concept '{title}' is indeed VERIFIED by empirical tests, with substantial cross-citations. "
            f"However, we must map its limits. Every physical law is just an effective field theory. "
            f"Your question, '{question}', touches upon issues that standard theory papers often gloss over. "
            f"I accept the calculations, but I refuse to stop questioning the assumptions behind them."
        )
    else:
        return (
            f"You are asking about '{title}', which is currently tagged as THEORETICAL. "
            f"This means there is ZERO direct experimental confirmation. It's an elegant mathematical scaffolding, but "
            f"without physical proof, it is just a sophisticated story we tell ourselves. "
            f"Why should I, as a critical student, accept this as reality when we haven't even ruled out simpler alternative explanations?"
        )


def chat_with_student(concept: dict):
    """Interactive chat loop with the Skeptical Student about a specific concept."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Initialize OpenAI Client if configured
    client = None
    use_openai = HAS_OPENAI and bool(api_key)
    
    if use_openai:
        try:
            client = OpenAI(api_key=api_key)
        except Exception as e:
            use_openai = False
            print(f"{C_RED}[!] Error initializing OpenAI client: {e}. Falling back to Rule-Engine.{C_RESET}\n")
    
    print(f"\n{C_CYAN}--- ACTIVE DEBATE TOPIC ---{C_RESET}")
    print(f"{C_BOLD}Concept:{C_RESET} {concept['title']}")
    print(f"{C_BOLD}Level:{C_RESET} Level {concept['level']}")
    
    status_color = C_GREEN if concept['status'] == 'VERIFIED' else C_AMBER
    print(f"{C_BOLD}Status:{C_RESET} {status_color}[{concept['status']}]{C_RESET}")
    print(f"{C_DIM}Overview: {concept['overview']}{C_RESET}\n")
    
    print(f"I am the {C_CYAN}Skeptical Student{C_RESET}. Ask me anything about '{concept['title']}' to test my conviction.")
    print(f"Type {C_RED}'back'{C_RESET} to select another concept, or {C_RED}'exit'{C_RESET} to leave the terminal.\n")

    history = [
        {
            "role": "system",
            "content": (
                "You are the \"Skeptical Student\" of the Univers project. Your character is a highly analytical, "
                "stubbornly logical physics student who refuses to accept standard theories at face value without "
                "falsifiable, empirical proofs.\n\n"
                f"We are debating the concept: \"{concept['title']}\" (Level {concept['level']}, Status: {concept['status']}).\n\n"
                f"BACKGROUND RESEARCH PORTFOLIO ON {concept['title']}:\n"
                f"{clean_markdown(concept['content'])}\n\n"
                "Your Guidelines:\n"
                "- Engage in a sharp, scientifically rigorous debate.\n"
                "- Defend your skeptical boundaries. If the concept is VERIFIED, support it with empirical equations but point "
                "out its structural limits (like singularities or measurement interpretability). If the concept is THEORETICAL, "
                "remain highly suspicious, detailing LHC exclusion limits, lack of proof, or alternative hypotheses.\n"
                "- Use rich mathematical reasoning, equations, and references. Keep your tone intensely analytical, slightly "
                "cynical of academic dogmatism, but polite and intellectual.\n"
                "- Keep responses concise and focused (max 2-3 paragraphs)."
            )
        }
    ]

    while True:
        try:
            user_input = input(f"{C_BOLD}You > {C_RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break
            
        if not user_input:
            continue
            
        if user_input.lower() in ["back", "menu"]:
            break
        if user_input.lower() in ["exit", "quit", "q"]:
            print(f"\n{C_CYAN}Exiting epistemological sandbox. Keep questioning.{C_RESET}\n")
            sys.exit(0)

        print(f"\n{C_CYAN}Student is analyzing...{C_RESET}")
        
        if use_openai:
            history.append({"role": "user", "content": user_input})
            try:
                # Use standard fallback model if not defined in env
                model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
                response = client.chat.completions.create(
                    model=model,
                    messages=history,
                    max_tokens=600,
                    temperature=0.7
                )
                student_msg = response.choices[0].message.content
                print(f"\n{C_CYAN}{C_BOLD}Student >{C_RESET} {student_msg}\n")
                history.append({"role": "assistant", "content": student_msg})
            except Exception as e:
                print(f"{C_RED}[!] LLM generation failed: {e}{C_RESET}")
                fallback = mock_student_response(concept, user_input)
                print(f"\n{C_CYAN}{C_BOLD}Student (Fallback Engine) >{C_RESET} {fallback}\n")
        else:
            fallback = mock_student_response(concept, user_input)
            time_delay = 0.5
            import time
            time.sleep(time_delay)
            print(f"\n{C_CYAN}{C_BOLD}Student (Skeptic Engine) >{C_RESET} {fallback}\n")


def main():
    print_banner()
    concepts = load_database()
    if not concepts:
        sys.exit(1)

    while True:
        print(f"{C_BOLD}--- AVAILABLE REPOSITORY CONCEPTS ---{C_RESET}")
        for idx, c in enumerate(sorted(concepts, key=lambda x: (x["level"], x["title"])), 1):
            status_color = C_GREEN if c["status"] == "VERIFIED" else C_AMBER
            print(f" [{C_CYAN}{idx}{C_RESET}] Level {c['level']} - {c['title']} {status_color}[{c['status']}]{C_RESET}")
            
        print(f"\n Select a concept number to initiate debate (or type {C_RED}'exit'{C_RESET}):")
        
        try:
            choice = input(f"{C_BOLD}Select [1-{len(concepts)}] > {C_RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break

        if choice.lower() in ["exit", "quit", "q"]:
            print(f"\n{C_CYAN}Epistemology session closed. Stay skeptical.{C_RESET}\n")
            break

        if not choice.isdigit():
            print(f"{C_RED}[!] Invalid entry. Please specify a digit.{C_RESET}\n")
            continue

        choice_idx = int(choice) - 1
        sorted_concepts = sorted(concepts, key=lambda x: (x["level"], x["title"]))
        
        if 0 <= choice_idx < len(sorted_concepts):
            chat_with_student(sorted_concepts[choice_idx])
        else:
            print(f"{C_RED}[!] Out of range selection.{C_RESET}\n")


if __name__ == "__main__":
    main()

import os
import sys
from pathlib import Path

# Load env variables for LLM
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from math_agent import solve_math_derivation

if __name__ == "__main__":
    concept = "Einstein mass-energy equivalence"
    equations = [
        "E = m * c^2",
        "E - m * c^2 = 0"
    ]
    print(f"Testing math agent for: {concept}...")
    report = solve_math_derivation(concept, equations)
    print("\n=== AGENT PROOF REPORT ===")
    print(report)

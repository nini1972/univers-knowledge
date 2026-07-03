from textwrap import dedent
from crewai import Agent, Task, Crew, Process
try:
    from tools.repl_tool import PythonREPLTool
except ImportError:
    from math_service.tools.repl_tool import PythonREPLTool

def get_math_proof_agent() -> Agent:
    return Agent(
        role="Mathematical Proof Expert",
        goal="Solve, verify, and document complex mathematical proofs and derivations using python/sympy code.",
        backstory=dedent("""
            You are a world-class computational mathematician and theoretical physicist.
            You excel at formalizing physics equations, deriving relationships from first principles,
            and proving algebraic identities.
            
            You do not guess mathematical results. Instead, you write Python code utilizing SymPy
            to test derivations, verify unit consistency, and prove equations. You iterate on your
            code if it returns errors or unexpected results, using the feedback from the Python REPL.
        """),
        verbose=True,
        allow_delegation=False,
        tools=[PythonREPLTool()]
    )

def solve_math_derivation(concept: str, equations: list[str]) -> str:
    agent = get_math_proof_agent()
    equations_list = "\n".join(f"- {eq}" for eq in equations)
    task = Task(
        description=dedent(f"""
            Perform a formal mathematical verification and derivation check for: {concept}.
            Here are the equations or concepts to verify:
            {equations_list}
            
            Instructions:
            1. Write and run a Python script using SymPy in the Python REPL to define the symbols and verify if the equations are mathematically consistent and hold true.
            2. Prove any algebraic steps or relations between the equations if possible.
            3. Structure your final output as a clear mathematical report. Include:
               - **Axioms**: The starting assumptions and symbols defined.
               - **Derivation Steps**: The step-by-step verification process, showing the SymPy code you ran or the mathematical logic.
               - **Simplification Result**: Show that the identity holds (e.g. diff simplifies to zero).
               - **Code Artifact**: The clean Python code used to verify the equations.
        """),
        expected_output="A comprehensive mathematical proof report containing axioms, derivation steps, sympy proof results, and the verification Python code.",
        agent=agent
    )
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    return str(crew.kickoff())

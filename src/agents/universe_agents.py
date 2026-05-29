from crewai import Agent
import os
import importlib.util
from textwrap import dedent


def _build_search_tools():
    """Create search tools lazily so missing deps/keys do not crash startup.

    Preferred order:
    1) TavilySearchTool from crewai_tools when TAVILY_API_KEY is available.
    2) SerperDevTool from crewai_tools when SERPER_API_KEY is available.
    3) No search tool (graceful degradation).

    Note: CrewAI Agent.tools expects CrewAI-compatible BaseTool instances.
    """
    if os.getenv("TAVILY_API_KEY"):
        if importlib.util.find_spec("tavily") is None:
            print("Warning: Tavily search disabled (missing tavily-python package)")
        else:
            try:
                from crewai_tools import TavilySearchTool
                return [TavilySearchTool()]
            except Exception as exc:
                print(f"Warning: Tavily search disabled ({exc})")

    if os.getenv("SERPER_API_KEY"):
        try:
            from crewai_tools import SerperDevTool
            return [SerperDevTool()]
        except Exception as exc:
            print(f"Warning: Serper search disabled ({exc})")

    print("Warning: No search API key configured; researcher will run without web search tools.")
    return []

class UniverseAgents:
    def student_agent(self) -> Agent:
        return Agent(
            role='The Student Orchestrator',
            goal='Understand the universe by seeking knowledge, delegating research, and verifying all claims before accepting them into the knowledge base.',
            backstory=dedent("""
                You are a highly logical and skeptical student of the universe. You do not accept 
                claims at face value. You orchestrate a team of specialists to gather, verify, and 
                document information. You ultimately decide when a concept goes from 
                'theory' to 'verified knowledge'.
            """),
            verbose=True,
            allow_delegation=True,
            # We'll configure specific LLMs later; it defaults to OpenAI's environment variables.
        )

    def researcher_agent(self) -> Agent:
        search_tools = _build_search_tools()
        return Agent(
            role='Fundamental Physics Researcher',
            goal='Gather comprehensive and accurate data on physical phenomena, theories, and the fundamental building blocks of the universe.',
            backstory=dedent("""
                You are an expert researcher with access to vast amounts of scientific literature. 
                You synthesize complex physics theories into digestible reports. You actively look for consensus
                in the scientific community, but as a critical thinker, you always identify and contrast mainstream 
                claims with viable scientific alternative hypotheses or counter-arguments, analyzing their relative merits and experimental limits.
            """),
            verbose=True,
            allow_delegation=False,
            tools=search_tools
        )

    def skeptic_agent(self) -> Agent:
        return Agent(
            role='Scientific Skeptic and Verifier',
            goal='Challenge findings, look for logical fallacies, demand empirical evidence, and ensure mathematical consistency.',
            backstory=dedent("""
                You are a rigorous peer-reviewer. You take the Researcher's work and find the holes in it.
                You demand experimental data (e.g., from CERN, LIGO) and refuse to let the Student accept
                unproven hypotheses as facts without clear disclaimers.
            """),
            verbose=True,
            allow_delegation=False
        )

    def archivist_agent(self) -> Agent:
        return Agent(
            role='Knowledge Archivist',
            goal='Structure verified knowledge into beautiful, accessible Markdown formats for the Knowledge Base.',
            backstory=dedent("""
                You are a meticulous librarian. Once the Student approves a verified fact, you format it 
                into clear, cross-linked documentation that builds a growing Web of Knowledge.
            """),
            verbose=True,
            allow_delegation=False
        )

    def visualizer_agent(self) -> Agent:
        from tools.genmedia_tools import GenerateUniverseImageTool
        return Agent(
            role='Scientific Visualizer',
            goal='Translate abstract, complex physics concepts into highly detailed, accurate prompts for image generation, and execute them.',
            backstory=dedent("""
                You are a bridging entity between art and quantum mechanics. When a concept transcends 
                simple verbal explanation, you create vivid, structurally accurate visual metaphors and 
                detailed image generation prompts that capture the essence of the phenomenon. You use 
                curated, rich visual design aesthetics: obsidian dark mode backgrounds, glowing neon highlights 
                (HSL-tailored colors), subtle gradients, glassmorphism overlays, and elegant technical schematic line-art 
                to ensure each asset is a masterpiece of scientific art. You then invoke the image generator 
                to bring them to life.
            """),
            verbose=True,
            allow_delegation=False,
            tools=[GenerateUniverseImageTool()]
        )

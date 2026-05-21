from crewai import Task
from textwrap import dedent

class UniverseTasks:
    def determine_next_topic_task(self, agent, current_index):
        return Task(
            description=dedent(f"""
                Review the current knowledge graph index below:
                ---
                {current_index}
                ---
                Based on what is already known, identify ONE logical next concept in fundamental physics 
                or cosmology that is currently missing and should form the foundation of our next learning step.
                Do NOT suggest a topic that is already explicitly listed in the index.
                Your response must ONLY be the name of the concept, so it can be passed directly to the Researcher.
                For example: "Dark Matter" or "The Higgs Boson".
            """),
            expected_output="A single string containing the exact name of the next concept to research.",
            agent=agent
        )

    def determine_next_level2_topic_task(self, agent, current_index):
        return Task(
            description=dedent(f"""
                Review the full knowledge graph index below, including all Level 1 and Level 2 entries:
                ---
                {current_index}
                ---
                Choose the NEXT Level 2 debate topic that builds on existing Level 1 foundations and is not already in the index.
                Select exactly two competing theories/frameworks that should be compared in a rigorous debate.
                Return ONLY valid JSON with these keys:
                {{
                  "theory_a": "...",
                  "theory_b": "...",
                  "concept_name": "..."
                }}
                Constraints:
                - Do not reuse a concept already listed in the index.
                - concept_name should be a concise debate title for the two selected theories.
            """),
            expected_output='A JSON object containing theory_a, theory_b, and concept_name.',
            agent=agent
        )

    def research_concept_task(self, agent, concept, async_execution=False):
        return Task(
            description=dedent(f"""
                Research the following concept thoroughly: {concept}.
                You must gather information from at least 3 independent scientific sources.
                Synthesize the current understanding, proposed mechanisms, and any mathematical 
                frameworks associated with this concept.
            """),
            expected_output="A comprehensive research report detailing the concept, citing at least 3 scientific sources.",
            agent=agent,
            async_execution=async_execution
        )

    def verify_research_task(self, agent, concept):
        return Task(
            description=dedent(f"""
                Review the research report on: {concept}.
                Apply the strict Verification Threshold:
                1. Are there at least 3 independent, credible sources?
                2. Is there experimental/empirical evidence, or is this purely theoretical?
                3. Are there competing theories or contradictions? 
                
                If the concept relies on unproven hypotheses, explicitly flag it as [THEORETICAL].
                If there are logical fallacies or lack of consensus, return a failure report to the student.
            """),
            expected_output="A verification report indicating whether the concept meets the threshold to be accepted as 'Verified Knowledge' or 'Theoretical Knowledge', along with critiques.",
            agent=agent
        )

    def student_evaluation_task(self, agent, concept):
        return Task(
            description=dedent(f"""
                Assess the Researcher's report and the Skeptic's verification on: {concept}.
                Decide if this concept has passed the Verification Threshold.
                If it passes, formulate a clear directive for the Archivist to document it. 
                If it fails, dictate what specific fallback questions the Researcher must explore next.
            """),
            expected_output="A final ruling on the concept. If approved, a structured summary for the archivist. If rejected, detailed follow-up questions.",
            agent=agent
        )

    def debate_theories_task(self, agent, theory_a, theory_b):
        return Task(
            description=dedent(f"""
                Conduct a rigorous comparative debate between "{theory_a}" and "{theory_b}".
                Evaluate both theories based on:
                1. Mathematical consistency.
                2. Alignment with existing empirical data (e.g., General Relativity and Quantum Mechanics).
                3. Major flaws or unprovable assumptions in each.
                Highlight which theory (if either) has stronger current consensus, and clearly flag both as [THEORETICAL].
            """),
            expected_output="A structured debate report comparing both theories, highlighting strengths, weaknesses, and current scientific consensus.",
            agent=agent
        )

    def generate_visual_concept_task(self, agent, concept):
        return Task(
            description=dedent(f"""
                Read the final verified summary for the concept: {concept}.
                Create a highly detailed, 1-paragraph image generation prompt that accurately 
                visualizes the core mechanisms of this concept. 
                
                You MUST use the 'Generate Universe Image' tool to actually create the image. 
                Pass your detailed prompt to the tool.
                
                If the tool returns a normal file path, your final output must be exactly:
                `![{concept}](<the path returned by the tool>)`

                If the tool returns a value that starts with `GENMEDIA_UNAVAILABLE:`, do NOT fabricate a file path.
                In that case, your final output must be exactly:
                `[VISUAL_PENDING: <the full tool message>]`
            """),
            expected_output="Either a markdown image tag with a real generated path, or a VISUAL_PENDING marker with a concrete unavailability reason.",
            agent=agent
        )

    def document_knowledge_task(self, agent, output_path, include_visual=True, approved_summary=None):
        summary_source = "Take the final approved summary from the Student."
        if approved_summary:
            summary_source = dedent(f"""
                Use the following approved Student summary as the authoritative final content:
                ---
                {approved_summary}
                ---
            """).strip()

        visual_source = "and the generated image tag from the Visualizer"
        visual_insert = "and INSERT the Markdown image tag generated by the Visualizer directly into the document where appropriate."
        if not include_visual:
            visual_source = ""
            visual_insert = "If no image tag is available, omit the visual section cleanly without placeholders."

        return Task(
            description=dedent(f"""
                {summary_source} {visual_source}
                Format the final output strictly following the template found in 'knowledge_base/templates/concept_template.md'.
                Include proper sections, citations, mathematical formulas (LaTeX/KaTeX), {visual_insert}
                Do NOT include markdown formatting wrappers like "```markdown" in the final output text,
                just output the raw markdown text so it saves properly.
            """),
            expected_output=f"A fully formatted Markdown document saved directly to {output_path}.",
            agent=agent,
            output_file=output_path # CrewAI will save the output of this task directly to the file
        )

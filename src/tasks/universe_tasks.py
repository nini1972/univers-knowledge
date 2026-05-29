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
                
                CRITICAL REQUIREMENTS - Your research report MUST satisfy these 5 criteria:
                1. Cite at least 3 independent scientific/academic sources with clear references.
                2. Highlight skepticism, empirical gaps, limitations, and contradictions of this concept.
                3. Include mathematical grounding, equations, or LaTeX formulas (e.g. $E=mc^2$) explaining the underlying physics.
                4. Classify the status clearly as either [VERIFIED] or [THEORETICAL] with rigorous justification.
                5. Include a "Visual Grounding" section with a highly detailed, 1-paragraph visual description or image generation prompt for a schematic diagram representing the concept.
            """),
            expected_output="A comprehensive research report detailing the concept, citing at least 3 scientific sources, including math formulas, status, limitations, and a visual description.",
            agent=agent,
            async_execution=async_execution
        )

    def verify_research_task(self, agent, concept, context=None):
        return Task(
            description=dedent(f"""
                Review the research report on: {concept}.
                Apply the strict Verification Protocol to evaluate the findings.
                
                You MUST fill out and include this exact markdown checklist and score at the end of your report:
                
                Verification Checklist:
                - [ ] Criterion 1: Source Consensus (at least 3 independent sources cited)
                - [ ] Criterion 2: Skepticism & Gaps (limitations/contradictions highlighted)
                - [ ] Criterion 3: Mathematical Grounding (concept is grounded in mathematical formulas or LaTeX equations)
                - [ ] Criterion 4: Status Classification (clearly classified as [VERIFIED] or [THEORETICAL])
                - [ ] Criterion 5: Visual Grounding (detailed visual/image prompt description included)

                Verification Score: X/5
                
                Replace [ ] with [x] for each criterion that is successfully met. Compute and output the final score (e.g., Score: 4/5 or 5/5).
                If the concept relies on unproven hypotheses, explicitly flag it as [THEORETICAL] and do not let the Student accept it as [VERIFIED].
            """),
            expected_output="A comprehensive verification report concluding with the completed 5-point Verification Checklist and final Verification Score.",
            agent=agent,
            context=context
        )

    def student_evaluation_task(self, agent, concept, context=None):
        return Task(
            description=dedent(f"""
                Assess the Researcher's report and the Skeptic's verification on: {concept}.
                Decide if this concept has passed the Verification Threshold.
                
                CRITICAL RULE: Check the Skeptic's Verification Score. If the score is less than 4 out of 5 (4/5), you MUST reject the concept and set "status" to "rejected" and "reason_code" to "insufficient_skeptic_score".
                
                Return ONLY valid JSON with this exact schema:
                {{
                  "status": "approved" | "rejected",
                  "reason_code": "short_snake_case_reason",
                  "summary_for_archivist": "non-empty when approved",
                  "follow_up_questions": ["question 1", "question 2"]
                }}
                Rules:
                - If approved: status must be "approved" and summary_for_archivist must be non-empty.
                - If rejected: status must be "rejected" and follow_up_questions must contain at least one concrete question.
                - Per protocol, unproven but mathematically consistent concepts can still be approved as [THEORETICAL].
                - Do NOT reject solely because experimental confirmation is absent.
                - Do not include markdown code fences or extra commentary.
            """),
            expected_output="A strict JSON object containing status, reason_code, summary_for_archivist, and follow_up_questions.",
            agent=agent,
            context=context
        )

    def student_level2_debate_evaluation_task(self, agent, concept, context=None):
        return Task(
            description=dedent(f"""
                Assess the comparative Level 2 debate report and skeptic review on: {concept}.
                
                CRITICAL RULE: Check the Skeptic's Verification Score. If the score is less than 4 out of 5 (4/5), you MUST reject the concept and set "status" to "rejected" and "reason_code" to "insufficient_skeptic_score".
                
                Return ONLY valid JSON with this exact schema:
                {{
                  "status": "approved" | "rejected",
                  "reason_code": "short_snake_case_reason",
                  "summary_for_archivist": "non-empty when approved",
                  "follow_up_questions": ["question 1", "question 2"]
                }}
                Decision policy for Level 2 debates:
                - Approve when the report is rigorous, source-grounded, mathematically coherent, and transparent about uncertainty.
                - If there is no direct experimental confirmation, classify the outcome as [THEORETICAL] inside summary_for_archivist.
                - Reject ONLY for quality failures (insufficient sources, logical inconsistencies, missing critical comparisons, or non-rigorous claims).
                - "lack_of_experimental_confirmation" alone is NOT a valid rejection reason for Level 2.
                - If approved: status must be "approved" and summary_for_archivist must be non-empty.
                - If rejected: status must be "rejected" and follow_up_questions must contain at least one concrete question.
                - Do not include markdown code fences or extra commentary.
            """),
            expected_output="A strict JSON object containing status, reason_code, summary_for_archivist, and follow_up_questions.",
            agent=agent,
            context=context
        )

    def debate_theories_task(self, agent, theory_a, theory_b, context=None):
        return Task(
            description=dedent(f"""
                Conduct a rigorous comparative debate between "{theory_a}" and "{theory_b}".
                Evaluate both theories based on:
                1. Mathematical consistency.
                2. Alignment with existing empirical data (e.g., General Relativity and Quantum Mechanics).
                3. Major flaws or unprovable assumptions in each.
                Highlight which theory (if either) has stronger current consensus, and clearly flag both as [THEORETICAL].
                
                You MUST include this exact markdown checklist and score at the end of your debate report:
                
                Verification Checklist:
                - [ ] Criterion 1: Multi-source Integration (at least 3 independent sources compared)
                - [ ] Criterion 2: Mathematical Consistency (rigorous comparative math review in LaTeX)
                - [ ] Criterion 3: Empirical Core (empirical data alignment and gaps scrutinized)
                - [ ] Criterion 4: Transparency & Gaps (unprovable assumptions flagged)
                - [ ] Criterion 5: Comparative Consensus (clear statement of current consensus status)

                Verification Score: X/5
                
                Replace [ ] with [x] for each criterion that is successfully met. Compute and output the final score.
            """),
            expected_output="A structured debate report comparing both theories, concluding with the completed 5-point Verification Checklist and final Verification Score.",
            agent=agent,
            context=context
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
            agent=agent
        )

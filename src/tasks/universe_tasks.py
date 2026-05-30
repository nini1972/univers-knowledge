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
                
                SEARCH STRATEGY & SPECIFICITY INSTRUCTIONS:
                - When searching, generate highly specific queries. Append terms like "review article", "recent advances", "experimental constraints", or "mathematical framework" (e.g., "{concept} experimental constraints" or "{concept} review article").
                - Prioritize peer-reviewed journals, institutional PDFs (.edu/.ac), and open-access preprint portals (like arXiv.org).
                
                CRITICAL REQUIREMENTS - Your research report MUST satisfy these 5 criteria:
                1. Cite at least 3 independent scientific/academic sources with clear references.
                2. Highlight skepticism, empirical gaps, limitations, and contradictions of this concept, explicitly comparing the mainstream model with at least one unorthodox or alternative counter-hypothesis (e.g. MOND vs. Dark Matter; loop quantum gravity or non-commutative geometry vs. String Theory) and describing the current experimental bounds.
                3. Include mathematical grounding, equations, or LaTeX formulas (e.g. $E=mc^2$) explaining the underlying physics.
                4. Classify the status clearly as either [VERIFIED] or [THEORETICAL] with rigorous justification.
                5. Include a "Visual Grounding" section with a highly detailed, 1-paragraph visual description or image generation prompt for a schematic diagram representing the concept.
            """),
            expected_output="A comprehensive research report detailing the concept, citing at least 3 scientific sources, including alternative hypotheses, math formulas, status, limitations, and a visual description.",
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
                visualizes the core physical mechanisms of this concept. 
                
                VISUAL STYLING GUIDELINES:
                - Use a cinematic deep-space aesthetic with a premium dark mode obsidian backdrop.
                - Use vibrant, curated neon HSL highlights (e.g. quantum cyan, stellar ultraviolet, glowing nebular violet, and supernova orange).
                - Use technical schematic line-art, glassmorphism lenses, and geometric overlay patterns to give a premium, scientific look.
                - Avoid generic flat designs; make the scene feel immersive, layered, and multi-dimensional.
                - Create a vivid, structurally accurate visual metaphor representing the quantum/cosmological phenomenon.
                
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
        from pathlib import Path
        repo_root = Path(__file__).resolve().parent.parent
        template_file = repo_root / "knowledge_base" / "templates" / "concept_template.md"
        template_content = ""
        if template_file.exists():
            template_content = template_file.read_text(encoding="utf-8")
        else:
            template_content = dedent("""
                ---
                title: "{Concept Name}"
                level: 1
                status: "[VERIFIED] or [THEORETICAL]"
                sources:
                  - Source 1
                  - Source 2
                  - Source 3
                ---

                # {Concept Name}

                ## 1. Overview
                ...
                ## 2. Detailed Explanation
                ...
                ## 3. Mathematical Framework
                ...
                ## 4. Skeptical Perspectives & Alternative Hypotheses
                ...
                ## 5. Verification & Skeptic's Notes
                ...
                ## 6. Visual Representation
                ...
                ## 7. Related Concepts
                ...
            """).strip()

        summary_source = "Take the final approved summary from the Student."
        if approved_summary:
            summary_source = dedent(f"""
                Use the following approved Student summary as the authoritative final content:
                ---
                {approved_summary}
                ---
            """).strip()

        visual_source = "and the generated image tag from the Visualizer"
        visual_insert = "and INSERT the Markdown image tag generated by the Visualizer directly into section '## 5. Visual Representation'."
        if not include_visual:
            visual_source = ""
            visual_insert = "If no image tag is available, section '## 5. Visual Representation' must contain either a text description of the visualization or the raw image placeholder."

        return Task(
            description=dedent(f"""
                {summary_source} {visual_source}
                
                You MUST format the final output strictly following this exact template. Fill in all placeholder values (such as {{Concept Name}}, the level, the status, and sources list).
                
                CRITICAL STRUCTURE INSTRUCTIONS:
                1. You must include the complete YAML frontmatter block starting and ending with '---' containing: title, level, status, and sources.
                2. You must use the EXACT headings, numbering, and titles as defined in the template below. Do NOT omit any headings, and do NOT alter their names/numbers.
                3. {visual_insert}
                4. Do NOT wrap the entire output in markdown code fences like '```markdown'. Output raw markdown content directly.
                
                TEMPLATE LAYOUT TO STRICTLY ADHERE TO:
                {template_content}
            """),
            expected_output=f"A fully formatted Markdown document saved directly to {output_path} following the exact template layout, starting with '---' frontmatter.",
            agent=agent
        )


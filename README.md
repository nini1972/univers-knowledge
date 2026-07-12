# 🌌 Univers Knowledge Builder

An autonomous, self-growing system powered by CrewAI that continuously learns, verifies, and visually documents the fundamental physics and cosmology of our universe.

## 🚀 Overview
The Univers Knowledge Builder is designed as an autonomous multi-agent workflow. It iterates dynamically to incrementally expand a verified base of knowledge about the universe. It features rigorous scientific skepticism and integrates **Google Genmedia MCP Servers (Vertex AI Gemini)** to automatically generate high-definition visual representations of complex phenomena (like quantum entanglement, black holes, and string theory).

## 🤖 The Specialist Agents

- 🎓 **The Student Orchestrator**: Reviews current knowledge, dictates the curriculum, and chooses the next logical topic to understand.
- 🔬 **The Fundamental Physics Researcher**: Explores scientific literature, gathers data, and synthesizes complex theories.
- ⚖️ **The Scientific Skeptic**: Cross-examines findings for logical fallacies, math consistency, and empirical evidence (e.g., CERN, LIGO data).
- 🎨 **The Scientific Visualizer**: Uses the Google NanoBanana MCP (Gemini Image Generation) to create precise visual representations of verified physics concepts.
- 📚 **The Knowledge Archivist**: Formats, links, and documents approved findings into beautifully structured Markdown files.

## 📈 Auto-Learning Workflow Visualized

When the script kicks off, the agents collaborate in this sequence to securely expand the knowledge base:

```mermaid
graph TD
    classDef agent fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef data fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff;
    classDef mcp fill:#7f1d1d,stroke:#f87171,stroke-width:2px,color:#fff;
    classDef eval fill:#701a75,stroke:#fb7185,stroke-width:2px,color:#fff;

    A[(Knowledge Base Index)] --->|Reads proven concepts| B(🎓 Student Agent):::agent
    B -->|Selects new Uncharted Topic| C(🔬 Researcher Agent):::agent
    C -->|Web Search & Literature Review| D(⚖️ Skeptic Agent):::agent
    D -->|Verification Threshold Check| E{Student Evaluates}:::eval

    E -->|Fails Verification| C

    E -->|Passes Verification| F(🎨 Visualizer Agent):::agent

    F -.->|Tool Call via Langchain| G[[Genmedia MCP Server (NanoBanana)]]:::mcp
    G -.->|Saves Image File| F

    F -->|Markdown Image Tag| H(📚 Archivist Agent):::agent
    E -->|Verified Topic Summary| H

    H -->|Saves Structured Format| I[Concept Markdown File]:::data
    H -->|Commits New Entry| A
```

## 🛠 Setup & Installation

### Prerequisites
1. **Python 3.11+**
2. **Google Cloud CLI** authenticated (`gcloud auth application-default login`) with Vertex AI permissions on your project.
3. The **mcp-genmedia-go** binaries installed inside the `.mcp-servers/` directory.

### 1. Initialize the Environment
```powershell
pip install -r requirements.txt
```

### 2. Configure MCP settings
Ensure `mcp-config.json` inside the root tree is updated with your correct GCP `PROJECT_ID` and `LOCATION`.

### 3. Run the Core Loop
Execute the main workflow sequence:
```powershell
cd src
python main.py
```

### 4. Serve the Project Locally
In a separate terminal from the project root, serve the repository dynamically over HTTP (which automatically finds an open port if 8000 is taken, and opens your browser):
```powershell
python serve.py
```
*(Windows users facing corporate policy/AppLocker blocks on the virtual environment can use the trusted Python launcher instead)*:
```powershell
py serve.py
```

Alternatively, run the standard python HTTP server manually:
```powershell
python -m http.server 8000
```
or
```powershell
py -m http.server 8000
```

## 📂 Data Structure
The generated learning artifacts are preserved cleanly in the `knowledge_base` directory:
- `_index.md`: The running table of contents.
- `images/`: The output directory for the Gemini 2.5 flash generated visuals.
- `level_X_.../`: Folders segregating physical mechanics by complexity (e.g., fundamental models vs theoretical physics).
- `logs/equations.jsonl`: Structured database of all mathematical equations discovered across concepts (see Roadmap).

## 🗺️ Roadmap

### 🧮 Equation Database & Discovery Agent
**Status:** Data collection active · Agent planned

Every workflow run now logs all discovered LaTeX equations to `knowledge_base/logs/equations.jsonl`, linking each equation to its concept, level, math verification status, and timestamp. This builds a growing structured index across the entire knowledge base.

**Future: Equation Archaeologist Agent** — A specialized agent that queries the equation database to discover:
- 🔗 **Cross-concept bridges** — shared variables/constants appearing across unrelated domains
- 🧬 **Structural homologies** — equations with identical operator structures in different physics areas
- 📊 **Equation genealogies** — tracing which equations derive from which axioms
- 🔍 **Gap detection** — inconsistent definitions of the same variable across debates

### 🔬 A2A Math Verification Service
**Status:** Testing · Integration planned

An Agent-to-Agent (A2A) math verification service running on Google Cloud Run. Currently force-triggered as a test case during L1 runs. Will be integrated as an optional agent tool once stability is confirmed across diverse scenarios.

### 🌌 Level 3: Cosmology & Astrophysics
**Status:** Directory ready · Workflow not started

The `level_3_cosmology_and_astrophysics/` directory exists but no workflow step produces L3 content yet. Planned as the third knowledge tier building on L1 fundamentals and L2 debates.

### 📝 Math Enrichment Pipeline
**Status:** Standalone tool · Integration optional

`src/math_enrichment.py` can retroactively add detailed step-by-step derivations (Section 8) and permanent math audit reports (Section 9) to existing documents. Currently run on-demand via CLI.

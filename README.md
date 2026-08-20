# Automotive Process Intelligence Agent (APIA)

> A production-grade multi-agent AI system that automates BMW Z4 vehicle defect analysis and technical report generation - reducing a 90-180 minute manual engineering workflow to under 2 minutes.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-green?style=flat-square)
![Claude](https://img.shields.io/badge/Claude-Haiku%20%7C%20Sonnet-orange?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-teal?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

---

<!-- PLACEHOLDER: Add a banner image or demo GIF here -->
<!-- Recommended: A screen recording of the full workflow — defect submission → agent trace → report approval -->
<!-- ![APIA Demo](assets/demo.gif) -->

## Overview

Vehicle defect analysis is a knowledge-intensive process performed daily across automotive service and quality assurance operations. An experienced engineer currently spends 90–180 minutes per defect case manually searching through Technical Service Bulletins (TSBs), factory repair manuals, and quality standards before producing a structured report.

APIA replaces that process with a four-agent AI pipeline:

1. A **Classifier** categorises the defect and generates targeted search keywords
2. A **Documentation Researcher** retrieves relevant procedures from a BMW Z4 knowledge base using RAG
3. A **Standards Validator** checks compliance against IATF 16949 and ISO 9001
4. A **Report Writer** synthesises all findings into a structured defect report

A human engineer reviews and approves the report before it is saved — ensuring oversight is preserved while the research and writing is fully automated.

**Target vehicle:** BMW Z4 (E89: 2009–2016, G29: 2019–present)

---

## Architecture

<!-- PLACEHOLDER: Replace with your actual architecture diagram -->
<!-- Recommended tool: draw.io, Excalidraw, or Mermaid -->
<!-- ![Architecture Diagram](assets/architecture.png) -->

```
┌─────────────────────────────────────────────────────────────┐
│                     OFFLINE PIPELINE                        │
│                                                             │
│  PDFs (TSBs / Manuals / Standards)                         │
│       │                                                     │
│       ▼                                                     │
│  parser.py ──── PyMuPDF + pdfplumber + OCR                  │
│       │                                                     │
│       ▼                                                     │
│  chunker.py ─── 512-token overlapping chunks                │
│       │                                                     │
│       ▼                                                     │
│  embedder.py ── BAAI/bge-m3 (local, no API cost)           │
│       │                                                     │
│       ├──► ChromaDB  (3 typed vector collections)           │
│       └──► SQLite    (raw chunks + metadata)                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     RUNTIME PIPELINE                        │
│                                                             │
│  Streamlit UI ──► FastAPI ──► LangGraph Graph               │
│                                    │                        │
│                          ┌─────────▼──────────┐            │
│                          │  classify          │  Haiku      │
│                          │  research          │  Sonnet     │
│                          │  validate          │  Sonnet     │
│                          │  write_report      │  Sonnet     │
│                          │  human_checkpoint  │  interrupt  │
│                          │  save_report       │             │
│                          └─────────┬──────────┘            │
│                                    │                        │
│                          SQLite + Langfuse                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Pipeline

| Agent | Model | Tools | Input | Output |
|---|---|---|---|---|
| **Classifier** | claude-haiku-4-5 | None | Raw defect submission | Category, severity, search keywords |
| **Researcher** | claude-sonnet-4-6 | `search_tsb`, `search_manual`, `fetch_document_section` | Keywords + defect details | Root cause, procedure, parts, sources |
| **Validator** | claude-sonnet-4-6 | `search_standards`, `web_search` | Procedure + severity | Compliance status, warnings, escalation flag |
| **Report Writer** | claude-sonnet-4-6 | None | All upstream outputs | Structured JSON report → Word document |

Each agent has a single responsibility. The **Classifier** converts vague symptom descriptions into precise technical search terms. The **Researcher** retrieves and synthesises documentation using RAG across three typed ChromaDB collections. The **Validator** checks regulatory compliance independently of the repair logic. The **Report Writer** combines all outputs into a consistently formatted deliverable.

After the report is generated, a **human-in-the-loop checkpoint** pauses the graph for engineer review. The engineer can approve the report or request a revision with structured feedback - the graph loops back to the Researcher with that feedback injected into the prompt.

<!-- PLACEHOLDER: Add an agent flow diagram here -->
<!-- ![Agent Flow](assets/agent_flow.png) -->

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Anthropic Claude (claude-haiku-4-5, claude-sonnet-4-6) |
| Agent Orchestration | LangGraph |
| Embeddings | Sentence Transformers — BAAI/bge-m3 (local, no API cost) |
| Vector Store | ChromaDB (persistent, file-based) |
| Document Store | SQLite via SQLAlchemy (file-based, no server) |
| PDF Parsing | PyMuPDF + pdfplumber + pytesseract (OCR) |
| Web Search | Anthropic's websearch tool |
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Observability | Langfuse (self-hosted) |
| Document Output | python-docx (Word reports) |
| Testing | pytest + golden test set |


---

## Getting Started

### Prerequisites

- Python 3.11+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/automotive-intelligence-agent.git
cd automotive-intelligence-agent
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `sentence-transformers` will download the `BAAI/bge-m3` model (~500MB) on first use. This is a one-time download stored in your local model cache.

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key
TAVILY_API_KEY=your_tavily_api_key

# Database — SQLite, no server needed
DATABASE_URL=sqlite:///./data/apia.db

# Langfuse observability (optional — skip if not using)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
```

Get your keys here:
- Anthropic API key → [console.anthropic.com](https://console.anthropic.com)
- Tavily API key → [tavily.com](https://tavily.com)
- Langfuse (optional, self-hosted) → see [Langfuse docs](https://langfuse.com/docs)


## Running the Ingestion Pipeline

The ingestion pipeline processes your PDF documents into a searchable knowledge base. Run it once before starting the application.

---

## Running the Application

Start the API and frontend in two separate terminals.

**Terminal 1 — FastAPI backend:**

```bash
uvicorn api.main:app --reload --port 8000
```

**Terminal 2 — Streamlit frontend:**

```bash
streamlit run frontend/main.py
```

Open your browser:

| Interface | URL |
|---|---|
| Streamlit UI | http://localhost:8501 |
| FastAPI docs | http://localhost:8000/docs |
| Langfuse (if running) | http://localhost:3000 |

---


## Screenshots


**Defect Submission Form**
![Defect Tab](assets/screenshots/submit.png)


**Live Agent Trace**
![Trace Tab](assets/screenshots/trace.png)

**Report Review and Approval**
![Review Tab](assets/screenshots/review.png)

<!-- **Generated Word Report**
![Word Report](assets/screenshots/report_docx.png) -->

<!-- **Langfuse Trace Dashboard** -->
<!-- ![Langfuse](assets/screenshots/langfuse.png) -->

---


## Acknowledgements

- [Anthropic](https://anthropic.com) — Claude API and prompt engineering guidance
- [LangChain](https://langchain.com) — LangGraph orchestration framework
- [NHTSA](https://www.nhtsa.gov) — Public BMW Z4 Technical Service Bulletin database
- [BAAI](https://huggingface.co/BAAI/bge-m3) — BGE-M3 embedding model
- [Langfuse](https://langfuse.com) — Open-source LLM observability

---

*Built as a portfolio project demonstrating production-grade multi-agent AI engineering. Domain: automotive quality assurance and defect analysis.*

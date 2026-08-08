# Automotive Process Intelligence Agent (APIA)
## Full Problem Definition

**Project Type:** Applied AI Engineering — Multi-Agent System  
**Domain:** Automotive Manufacturing & Quality Assurance  
**Prepared by:** TH Deggendorf — Applied Machine Learning  
**Status:** Proposal / Active Development  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Background and Context](#2-background-and-context)
3. [Problem Statement](#3-problem-statement)
4. [Current State Analysis](#4-current-state-analysis)
5. [Desired Future State](#5-desired-future-state)
6. [Project Objectives](#6-project-objectives)
7. [Scope](#7-scope)
8. [Technical Approach](#8-technical-approach)
9. [System Architecture](#9-system-architecture)
10. [Data Sources and Knowledge Base](#10-data-sources-and-knowledge-base)
11. [Success Criteria and KPIs](#11-success-criteria-and-kpis)
12. [Constraints](#12-constraints)
13. [Assumptions](#13-assumptions)
14. [Risks and Mitigations](#14-risks-and-mitigations)
15. [Stakeholders](#15-stakeholders)
16. [Deliverables](#16-deliverables)
17. [Timeline](#17-timeline)

---

## 1. Executive Summary

Vehicle defect analysis and technical report generation is a high-frequency, knowledge-intensive process performed daily across every automotive service and quality assurance operation. In its current form, it requires an experienced engineer to manually search through hundreds of pages of technical service bulletins (TSBs), repair manuals, and quality standards — then synthesise their findings into a structured report. This process takes between 90 minutes and 3 hours per defect case, introduces inconsistency depending on the engineer's experience level, and creates a bottleneck that limits throughput in high-volume service environments.

This project designs, builds, and evaluates an **Automotive Process Intelligence Agent (APIA)** — a production-grade, multi-agent AI system that automates this process end-to-end. APIA accepts a structured defect description as input, autonomously retrieves and synthesises relevant technical documentation through Retrieval-Augmented Generation (RAG), validates the proposed repair procedure against automotive quality standards, generates a structured defect report, and routes it through a human-in-the-loop approval checkpoint before saving to a persistent store.

The system reduces the time-to-report from 90–180 minutes to under 2 minutes, standardises report quality across engineers and experience levels, and creates a fully auditable trace of every AI decision made — satisfying the traceability requirements of quality standards such as IATF 16949.

---

## 2. Background and Context

### 2.1 The Automotive Service and Quality Domain

Modern automotive manufacturing and aftersales service generates an enormous volume of technical knowledge: vehicle defect patterns, corrective procedures, part specifications, warranty policies, and quality compliance requirements. This knowledge is distributed across thousands of documents — technical service bulletins issued by manufacturers, factory repair manuals running to hundreds of pages, ISO and OEM quality standards, and internal engineering guidelines.

Automotive service engineers and quality technicians are trained to navigate this information landscape. However, as vehicle complexity increases — particularly with the rise of electrified powertrains, advanced driver-assistance systems (ADAS), and software-defined vehicle architectures — the volume and technical depth of documentation grows faster than any individual engineer can track.

### 2.2 The Rise of AI in Automotive Processes

Large language models (LLMs) have demonstrated strong capability in knowledge-intensive reasoning tasks: document retrieval, information synthesis, structured report generation, and compliance checking. The emergence of **agentic AI systems** — where LLMs are given tools and the ability to plan multi-step workflows — enables a new class of applications that goes beyond simple question-answering.

Rather than asking an AI "what does this error code mean?", an agentic system can be asked "here is a defect — research it, validate the fix, and write the report." The agent autonomously decides which tools to call, in what order, and how to synthesise the results.

This architecture is directly applicable to automotive defect processing, where the task is inherently multi-step, documentation-grounded, and benefits from consistent structure.

### 2.3 The Agentification Opportunity

The automotive industry is at an early stage of what practitioners are calling "agentification" — the systematic identification of manual, knowledge-intensive workflows and their replacement with AI agent pipelines. This project targets one of the highest-value, most clearly bounded examples of such a workflow: defect report generation.

It is representative of a broader class of problems across the automotive value chain: supplier audit preparation, warranty claim processing, homologation documentation, and production quality reports all share the same structure — gather information from multiple sources, synthesise it under a set of constraints, produce a structured artefact, and get it approved by a human. APIA demonstrates that this structure can be fully agentified.

---

## 3. Problem Statement

### 3.1 Core Problem

**When a vehicle defect is reported, the process of researching the defect, identifying the correct repair procedure, validating compliance with quality standards, and documenting the findings is performed manually by engineers. This process is slow, inconsistent, unscalable, and largely undocumented in terms of the reasoning behind each decision.**

More precisely, the problem has four dimensions:

**Speed:** A single defect case requires an engineer to search through large volumes of technical documentation, cross-reference error codes with known issues, check applicable standards, and write a structured report. The elapsed time is 90–180 minutes per case. In high-volume service environments, this becomes a critical bottleneck.

**Consistency:** The quality and completeness of defect reports varies significantly depending on the engineer's experience, their familiarity with the specific vehicle model, and their knowledge of applicable standards. A junior engineer and a senior engineer working on the same defect may produce reports of substantially different quality.

**Traceability:** The reasoning behind a repair recommendation — which documents were consulted, which standards were checked, why a particular procedure was chosen — is rarely recorded. This creates compliance risk under quality frameworks such as IATF 16949, which require evidence of systematic, documented decision-making in quality processes.

**Scalability:** As the volume of defect reports grows (driven by increasing vehicle fleet size, greater ADAS complexity, and EV-specific failure modes), the manual process cannot scale without proportional increases in engineering headcount.

### 3.2 Research Question

> **Can a multi-agent AI system, combining large language models with retrieval-augmented generation and structured tool use, replicate the defect analysis and report generation process performed by an experienced automotive engineer — with measurable improvements in speed, consistency, and traceability — while preserving human oversight at the point of final approval?**

---

## 4. Current State Analysis

### 4.1 Manual Process Walkthrough

The current defect processing workflow follows these steps, performed sequentially by a single engineer:

```
Step 1 — Defect intake (5–10 min)
  Engineer receives defect report from technician or driver
  Records vehicle model, year, mileage, error codes, symptom description

Step 2 — Error code lookup (10–20 min)
  Engineer consults OBD-II reference guide or diagnostic software
  Identifies the systems flagged by the codes
  Cross-references with known failure patterns for the model

Step 3 — Documentation search (30–60 min)
  Engineer searches through TSBs for this model/year
  Reviews relevant repair manual sections
  Checks for known issues or previously issued service campaigns

Step 4 — Standards compliance check (15–30 min)
  Engineer determines whether the proposed repair requires documentation
  under IATF 16949 or BMW group quality standards
  Checks whether parts or procedures require approved supplier verification

Step 5 — Report writing (20–40 min)
  Engineer writes a structured defect report covering:
    - Root cause hypothesis
    - Recommended repair procedure
    - Required parts list
    - Estimated labour time
    - Standards compliance statement
    - Priority and escalation recommendation

Step 6 — Review and approval (10–20 min)
  Report is reviewed by a senior engineer or team lead
  Feedback is incorporated, report is approved and filed
```

**Total elapsed time: 90–180 minutes per defect case.**

### 4.2 Key Pain Points

| Pain Point | Impact | Frequency |
|---|---|---|
| Document search is manual and non-standardised | High time variability; junior engineers miss relevant TSBs | Every case |
| No systematic standards lookup | Compliance gaps discovered late or not at all | ~30% of cases |
| Report format varies by engineer | Quality assurance overhead; re-work required | ~40% of cases |
| Reasoning behind recommendations is undocumented | Audit risk; knowledge lost when engineer leaves | Every case |
| Process does not scale | Bottleneck during high-volume periods | Seasonal / incident-driven |

### 4.3 Root Cause of the Problem

The root cause is not a lack of engineering competence — it is a structural mismatch between the volume and distribution of relevant technical knowledge and the capacity of individual humans to search, retrieve, and synthesise that knowledge in real time. The knowledge exists; it is the retrieval and synthesis that is slow and inconsistent.

This is precisely the class of problem that retrieval-augmented generation and agentic AI are designed to address.

---

## 5. Desired Future State

### 5.1 Target Process

The desired future state replaces Steps 2–5 of the manual process with an automated agent pipeline, preserving human involvement only at the intake (Step 1) and final approval (Step 6):

```
Step 1 — Defect intake (2–5 min) — HUMAN
  Engineer submits structured defect form via web interface
  Inputs: vehicle model, year, mileage, error codes, symptom description

Step 2 — Automated agent pipeline (60–120 seconds) — AI
  APIA classifies, researches, validates, and generates the report
  Full audit trace of every document consulted and every decision made

Step 3 — Human review and approval (5–10 min) — HUMAN
  Engineer reviews the AI-generated report in the web interface
  Approves or requests revision with structured feedback
  Approved report is saved and downstream actions triggered
```

**Target elapsed time: 7–15 minutes per defect case (including human review).**

### 5.2 Properties of the Desired System

**Speed:** Report generation time under 2 minutes from submission to first draft.

**Consistency:** Every report follows the same structure, consults the same knowledge sources, and applies the same compliance checks, regardless of who submitted the defect.

**Traceability:** Every report includes a full list of documents consulted, a record of every tool call made by every agent, and the reasoning behind the root cause hypothesis and recommended procedure.

**Human oversight:** No report is finalised without explicit human approval. The human can request revisions with structured feedback, and the system will revise and resubmit.

**Auditability:** All agent traces, token usage, and latency metrics are logged to an observability platform (Langfuse), enabling post-hoc analysis of system behaviour and cost.

---

## 6. Project Objectives

### 6.1 Primary Objectives

**O1 — Build a functional multi-agent pipeline**
Design and implement a LangGraph-orchestrated pipeline of four specialist AI agents (Classifier, Documentation Researcher, Standards Validator, Report Writer) that together replicate the manual defect analysis workflow.

**O2 — Implement a production-grade RAG knowledge base**
Build an automated ingestion pipeline that processes automotive technical documents (PDFs), chunks and embeds them using Voyage AI, stores vectors in ChromaDB/pgvector, and enables semantic retrieval at query time.

**O3 — Implement human-in-the-loop control**
Integrate a human approval checkpoint into the agent pipeline using LangGraph's interrupt mechanism, with a revision loop that incorporates structured human feedback into the next research iteration.

**O4 — Deploy a usable frontend and backend**
Build a FastAPI REST backend exposing the agent pipeline and a Streamlit frontend providing defect submission, live agent trace visualisation, and report review/approval workflow.

**O5 — Measure and validate system performance**
Build an evaluation suite of at minimum 20 golden test cases with defined assertions on classification accuracy, report content, tool call correctness, latency, and cost per run.

### 6.2 Secondary Objectives

**O6 — Demonstrate observability**
Instrument every agent call with Langfuse tracing, recording input/output tokens, tool calls, and latency for each node in every pipeline run.

**O7 — Demonstrate prompt discipline**
Maintain version-controlled prompts for each agent node and show measurable evaluation score changes across at least two prompt iterations.

**O8 — Document the system for portfolio and interview use**
Produce a complete README, architecture diagram, demo video, and this problem definition document sufficient for a technical interviewer to fully understand the system's design decisions.

---

## 7. Scope

### 7.1 In Scope

- Defect classification by category (engine, transmission, electrical, braking, fuel system, ADAS) and severity (low, medium, high, safety-critical)
- Semantic retrieval from a local knowledge base of automotive technical documents (TSBs, repair manuals, DTC references)
- Standards compliance checking against IATF 16949, ISO 9001, and BMW group quality standards
- Structured defect report generation in JSON format with Word document export
- Human-in-the-loop approval with revision loop (maximum 3 iterations)
- Web-based submission and review interface
- Full observability via Langfuse trace logging
- Evaluation suite covering classification, report quality, tool call accuracy, latency, and cost
- Ingestion pipeline for PDF documents with chunking, embedding, and vector storage
- Deployment on a local machine with PostgreSQL and Docker (for Langfuse only)

### 7.2 Out of Scope

- Integration with real dealership management systems (DMS) or BMW's internal ISTA diagnostic platform
- Real-time vehicle telemetry or OBD data ingestion
- Predictive maintenance (forecasting future failures)
- Parts ordering or inventory management workflow automation
- Multi-language support (system operates in English)
- Mobile application
- Role-based access control or multi-user authentication
- Fine-tuning of any language model
- Integration with BMW's internal data infrastructure

---

## 8. Technical Approach

### 8.1 Architectural Pattern: Multi-Agent Orchestration

APIA uses a **hierarchical multi-agent architecture** in which a LangGraph state graph acts as the orchestrator, sequentially invoking four specialist agents. Each agent is a separate LLM invocation with a dedicated system prompt, a specific set of tools, and a defined output schema.

This architecture was chosen over a single-agent approach for three reasons:

1. **Separation of concerns** — each agent is responsible for one well-defined task, making it independently testable and improvable. A failure in the Validator does not require rewriting the Researcher.

2. **Model cost optimisation** — simpler tasks (classification) use a cheaper, faster model (Claude Haiku) while tasks requiring deeper reasoning (research synthesis, standards validation) use a more capable model (Claude Sonnet). This reduces cost per run by approximately 40% compared to using the frontier model for every step.

3. **Debuggability** — when the pipeline produces a poor report, the trace clearly shows which agent's output was the proximate cause. This makes iteration fast and targeted.

### 8.2 Retrieval-Augmented Generation (RAG)

The Documentation Researcher and Standards Validator agents are grounded in real technical documentation via RAG. The approach is as follows:

**Offline (ingestion):** Technical documents are parsed (PyMuPDF + pdfplumber), split into 512-token overlapping chunks, embedded using Voyage AI's `voyage-3` embedding model (chosen for its strong performance on technical/domain-specific text), and stored in ChromaDB with metadata. Raw chunk text is also stored in PostgreSQL for full-page retrieval.

**Online (retrieval):** At query time, the agent's query is embedded with the same model using `input_type="query"` (as opposed to `"document"` used at ingestion — this asymmetric embedding improves retrieval precision), and a cosine similarity search returns the top-k most relevant chunks. The agent can then call `fetch_document_section` to retrieve the full page surrounding a relevant chunk.

This approach grounds the agents in real documentation and prevents hallucination of repair procedures or standards references.

### 8.3 Tool Use

Agents interact with the external world exclusively through typed tool calls. Each tool has a formally defined JSON schema that the LLM reads to understand when and how to call it. Tools include:

- `search_vector_store(query, n_results, doc_type)` — semantic search over technical documentation
- `fetch_document_section(source_filename, page_num)` — full-page retrieval from PostgreSQL
- `search_standards_db(query, n_results)` — semantic search over standards documents
- `web_search(query, max_results)` — real-time web search via Tavily for recent regulatory updates

The tool call loop is implemented directly against the Anthropic Messages API, without relying on framework abstraction, to maintain full visibility into the request-response cycle.

### 8.4 Human-in-the-Loop

LangGraph's `interrupt()` mechanism is used to pause graph execution at the human approval checkpoint. The graph state is persisted to an in-memory checkpointer (MemorySaver), and execution resumes when the FastAPI endpoint receives the human's decision via a `Command(resume=...)` invocation. This pattern supports:

- **Approval with no changes** — graph proceeds to save and end
- **Rejection with feedback** — graph loops back to the Researcher with feedback injected into the prompt, re-runs Validator and Writer, and returns a revised report for review
- **Iteration cap** — after three revision loops, the graph saves the latest version regardless, flagging it for manual review

### 8.5 Evaluation Methodology

System performance is measured at two levels:

**Unit-level evaluation:** Each agent node is tested independently with a fixed set of inputs and known correct outputs. Classification accuracy is measured as categorical match rate. Tool call accuracy is measured by tracking whether the correct tools were called for a given defect type.

**End-to-end evaluation:** A golden test set of 20 defect descriptions (with known error codes, known defect categories, and known relevant standards) is run through the full pipeline. Reports are evaluated on: required content presence, prohibited content absence (hallucination check), report structure compliance, latency, and cost. An LLM-as-judge prompt scores overall report quality on a 0–5 rubric for accuracy, completeness, and actionability.

Evaluation scores are recorded before and after every prompt change. No prompt change is merged without a demonstrated score improvement or equivalence on the golden set.

---

## 9. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        OFFLINE PIPELINE                         │
│                                                                 │
│  PDFs (TSBs, manuals, standards)                                │
│       │                                                         │
│       ▼                                                         │
│  parser.py ──── PyMuPDF + pdfplumber ──── text + tables        │
│       │                                                         │
│       ▼                                                         │
│  chunker.py ─── 512-token overlap ──────── Chunk objects        │
│       │                                                         │
│       ▼                                                         │
│  embedder.py ── Voyage AI voyage-3 ─────── float vectors        │
│       │                                                         │
│       ▼                                                         │
│  store.py ─────┬── ChromaDB ────── vector index                │
│                └── PostgreSQL ──── raw text + metadata          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         RUNTIME PIPELINE                        │
│                                                                 │
│  Streamlit UI ──── defect form ──── FastAPI /submit-defect      │
│                                          │                      │
│                               LangGraph graph.invoke()          │
│                                          │                      │
│            ┌─────────────────────────────▼──────────────────┐  │
│            │           LangGraph State Graph                  │  │
│            │                                                  │  │
│            │  ┌──────────────┐                                │  │
│            │  │  classify    │  claude-haiku-4-5, no tools    │  │
│            │  └──────┬───────┘                                │  │
│            │         ▼                                        │  │
│            │  ┌──────────────┐  claude-sonnet-4-6             │  │
│            │  │  research    │  tools: search_vector_store     │  │
│            │  │              │         fetch_document_section  │  │
│            │  └──────┬───────┘  RAG over ChromaDB             │  │
│            │         ▼                                        │  │
│            │  ┌──────────────┐  claude-sonnet-4-6             │  │
│            │  │  validate    │  tools: search_standards_db     │  │
│            │  │              │         web_search (Tavily)     │  │
│            │  └──────┬───────┘  RAG over standards collection  │  │
│            │         ▼                                        │  │
│            │  ┌──────────────┐                                │  │
│            │  │ write_report │  claude-sonnet-4-6, no tools   │  │
│            │  └──────┬───────┘                                │  │
│            │         ▼                                        │  │
│            │  ┌──────────────┐  interrupt() ─── pause         │  │
│            │  │   human      │       │                        │  │
│            │  │  checkpoint  │  approve ──── save_report      │  │
│            │  └──────────────┘  reject  ──── research (loop)  │  │
│            └──────────────────────────────────────────────────┘  │
│                                          │                      │
│                               PostgreSQL (reports + traces)     │
│                               Word document (output/reports/)   │
│                               Langfuse (full trace logging)     │
└─────────────────────────────────────────────────────────────────┘
```

**Data flow summary:**
1. Engineer submits defect via Streamlit → FastAPI receives and creates DB record
2. LangGraph invokes the classify node → haiku classifies category, severity, keywords
3. Research node retrieves relevant chunks via RAG → sonnet synthesises root cause and procedure
4. Validate node checks standards compliance → sonnet cross-references RAG + web search
5. Write node synthesises all outputs → sonnet generates structured JSON report
6. Graph pauses at human checkpoint → engineer reviews via Streamlit
7. Approval → save node writes to PostgreSQL + generates Word document → END
8. Rejection → feedback injected into research prompt → loop restarts from step 3

---

## 10. Data Sources and Knowledge Base

### 10.1 Primary Document Sources

| Source | Content | Access | Format |
|---|---|---|---|
| NHTSA TSB Database | Real BMW technical service bulletins | Free, public API | PDF |
| AllCarManuals.com | BMW factory service manuals | Free download | PDF |
| ProCarManuals.com | Fault code references, wiring diagrams, self-study programs | Free | PDF |
| OBD-II DTC Reference | Complete diagnostic trouble code descriptions and causes | Free | PDF |
| ISO 9001:2015 excerpts | Quality management system requirements | University library / open access | PDF |
| IATF 16949 overview | Automotive-specific quality standard | Public summary documents | PDF |

### 10.2 Knowledge Base Composition (Target)

| Collection | Document Types | Target Size |
|---|---|---|
| `automotive_docs` | TSBs, repair manuals, DTC references | 150–300 documents |
| `standards` | ISO, IATF, BMW group standard excerpts | 20–40 documents |

### 10.3 Data Quality Considerations

- **Language:** All documents must be in English for consistent embedding quality with voyage-3
- **Format:** Scanned PDFs (image-based, no text layer) require OCR pre-processing via pytesseract before chunking
- **Currency:** TSBs are dated — metadata records the issue date so agents can prioritise recent bulletins over superseded ones
- **Sensitivity:** No proprietary BMW internal documentation is used; all sources are publicly available, avoiding IP or confidentiality concerns

---

## 11. Success Criteria and KPIs

### 11.1 Functional Success Criteria

| Criterion | Definition | Target |
|---|---|---|
| **Pipeline completion rate** | % of submitted defects for which the pipeline completes without error | ≥ 95% |
| **Classification accuracy** | % of defects correctly categorised by the Classifier agent (validated against golden set labels) | ≥ 90% |
| **Severity classification accuracy** | % of defect severity ratings matching expert labels | ≥ 85% |
| **RAG retrieval relevance** | % of retrieved chunks rated relevant by LLM-as-judge | ≥ 80% |
| **Report content completeness** | % of required fields populated in generated reports | 100% |
| **Report quality score** | Average LLM-as-judge score on 0–5 rubric (accuracy, completeness, actionability) | ≥ 4.0 / 5.0 |
| **Standards compliance detection** | % of safety-critical defects correctly flagged for escalation | ≥ 95% |
| **Human approval rate (first pass)** | % of AI reports approved by engineer without revision request | ≥ 70% |

### 11.2 Performance KPIs

| KPI | Target |
|---|---|
| **Report generation latency** | < 120 seconds from submission to first draft |
| **Cost per report** | < €0.05 per complete pipeline run (Haiku + Sonnet pricing) |
| **Time saved vs. manual process** | ≥ 80 minutes saved per defect case |
| **Eval suite pass rate** | ≥ 85% of golden test case assertions passing |

### 11.3 Engineering Quality KPIs

| KPI | Target |
|---|---|
| All prompts version-controlled | 100% |
| Eval score tracked per prompt version | 100% |
| All agent calls traced in Langfuse | 100% |
| Revision loop max iterations enforced | 100% (no infinite loops in production) |

---

## 12. Constraints

### 12.1 Technical Constraints

**Model availability:** The system uses Anthropic's Claude API (claude-haiku-4-5 and claude-sonnet-4-6). It does not use fine-tuned or self-hosted models, as the API provides sufficient capability and eliminates infrastructure overhead for a portfolio project.

**Data constraints:** The knowledge base is limited to publicly available documents. No proprietary OEM technical data is ingested. This means the RAG coverage may be less comprehensive than a production deployment, but it is sufficient to demonstrate the architecture.

**Infrastructure constraints:** The system is designed to run on a developer laptop with a local PostgreSQL installation and Docker for Langfuse. It is not deployed to cloud infrastructure for this portfolio version, though the architecture is cloud-ready.

**Context window limits:** The Anthropic API's context window is finite. Prompts are designed to stay within safe limits (agent system prompts ≤ 1,000 tokens; RAG context ≤ 3,000 tokens per agent call). Prompt caching is enabled for repeated system prompts to reduce cost.

### 12.2 Scope Constraints

The system is a decision-support tool, not a decision-making system. It generates reports for human review and approval — it does not autonomously trigger repair orders, parts procurement, or customer communications. The human approval step is non-negotiable and is enforced architecturally by the LangGraph interrupt.

### 12.3 Time Constraints

The project is scoped for an 8-week development timeline with one developer working part-time alongside university coursework. This drives the technology choices (established frameworks, public APIs rather than self-hosted infrastructure) and the scope limitations above.

---

## 13. Assumptions

- The Anthropic API remains available and the pricing structure remains stable for the duration of development
- Publicly available BMW TSBs from NHTSA are legally downloadable and suitable for use in an educational/portfolio project
- The engineer submitting the defect provides accurate and complete input (garbage in, garbage out is acknowledged but out of scope for this project)
- A single PostgreSQL instance is sufficient for both application data and metadata storage at the portfolio scale
- ChromaDB's persistent local mode is sufficient for development; pgvector migration is noted as the production path
- The system will be evaluated against a manually labelled golden test set; the labels are created by the developer based on reference documentation review

---

## 14. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **LLM hallucination of repair procedures** | Medium | High | RAG grounds every claim in real documents; LLM-as-judge eval flags unsourced assertions |
| **RAG retrieval misses the relevant document** | Medium | Medium | Multi-query strategy (researcher issues 2–3 queries with different phrasings); fallback to web search |
| **Model changes break agent behaviour** | Low | High | Pinned model versions in API calls; eval suite detects regressions before any model upgrade |
| **NHTSA PDF format changes break parser** | Low | Medium | Defensive parsing with fallback to pytesseract OCR; error logged, ingestion continues |
| **Infinite revision loop** | Low | High | Hard cap of 3 iterations enforced in LangGraph conditional edge; architectural guarantee |
| **API cost overrun during development** | Medium | Low | claude-haiku-4-5 for all dev/eval runs; Sonnet only for final integration testing |
| **Context window overflow in research agent** | Medium | Medium | RAG chunks capped at 3,000 tokens; tool results truncated before injection; prompt caching for system prompt |

---

## 15. Stakeholders

| Stakeholder | Role | Interest |
|---|---|---|
| **Automotive engineer** | Primary end user | Faster report generation; consistent quality; easy approval interface |
| **Quality/compliance team** | Secondary user | Auditability; standards compliance tracking; report standardisation |
| **Service manager** | Beneficiary | Increased throughput; reduced engineer time on documentation tasks |
| **IT/AI team** | Technical stakeholder | Maintainability; observability; cost control; prompt versioning discipline |
| **Developer (this project)** | Builder | Demonstrating AI engineering competence for career development |
| **BMW AI/Innovation team** | Potential evaluator | Proof-of-concept for agentification roadmap; technical depth of implementation |

---

## 16. Deliverables

| Deliverable | Description |
|---|---|
| **Source code** | Full Python codebase in a public GitHub repository with clear commit history |
| **This problem definition** | Formal document describing the problem, approach, and success criteria |
| **Architecture diagram** | Visual system architecture diagram (included in README) |
| **README** | Project overview, setup instructions, technology stack, how to run |
| **Ingestion pipeline** | `run_ingestion.py` that processes any PDF folder into the knowledge base |
| **Agent pipeline** | Four agent nodes + LangGraph graph with human-in-the-loop |
| **FastAPI backend** | REST API with `/submit-defect`, `/human-decision`, and `/report/{id}` endpoints |
| **Streamlit frontend** | Three-tab UI: submit, trace, review |
| **Evaluation suite** | 20 golden test cases + `run_evals.py` with full assertion reporting |
| **Demo video** | Screen recording of a complete defect case from submission to approval |
| **Sample reports** | 3–5 generated Word documents from real defect descriptions |

---

## 17. Timeline

| Week | Focus | Key Milestones |
|---|---|---|
| **1** | Infrastructure + ingestion | PostgreSQL connected, ChromaDB running, first PDFs parsed and embedded |
| **2** | RAG validation | Retrieval quality confirmed on 10 test queries; pgvector migration path tested |
| **3** | Classifier + Researcher agents | Both nodes functional; tool call loop working; structured JSON output validated |
| **4** | Validator agent + LangGraph wiring | All four nodes in graph; conditional routing working; state transitions correct |
| **5** | Human-in-the-loop + revision loop | `interrupt()` pausing correctly; revision loop tested with ≥ 2 iterations |
| **6** | FastAPI + Streamlit | Both running; full workflow from form submission to approval working end-to-end |
| **7** | Langfuse + evaluation suite | All traces logged; 20 golden test cases defined and running; first eval score baseline |
| **8** | Polish + documentation | README complete; architecture diagram done; demo video recorded; problem definition finalised |

---

## Appendix A — Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| Language | Python 3.11+ | Universal AI ecosystem standard |
| LLM API | Anthropic Claude (claude-haiku-4-5, claude-sonnet-4-6) | State-of-the-art tool use; prompt caching; structured output |
| Agent orchestration | LangGraph | State machine model; human-in-the-loop; production-grade checkpointing |
| Embedding model | Voyage AI voyage-3 | Best retrieval performance on technical text; Anthropic recommended |
| Vector store (dev) | ChromaDB | Zero-config local vector store for rapid development |
| Vector store (prod path) | pgvector (PostgreSQL extension) | Consolidates vector + relational storage; eliminates separate vector DB service |
| Relational database | PostgreSQL + SQLAlchemy | Robust; already installed; handles reports, chunks, and traces |
| PDF parsing | PyMuPDF + pdfplumber | Complementary strengths: PyMuPDF for text, pdfplumber for tables |
| Web search | Tavily API | Agent-optimised search; structured results; generous free tier |
| Observability | Langfuse | Open-source LLM tracing; self-hosted; full token/latency/tool visibility |
| Backend API | FastAPI | Async-native; auto-generated docs; industry standard for Python AI services |
| Frontend | Streamlit | Rapid UI prototyping in pure Python; sufficient for portfolio demo |
| Document output | python-docx | Generates Word documents from structured report JSON |
| Evaluation | pytest + custom golden set | Unit assertions + end-to-end quality measurement |
| Containerisation | Docker (Langfuse only) | Minimal Docker footprint; uses local PostgreSQL |

---

## Appendix B — Glossary

| Term | Definition |
|---|---|
| **Agent** | An LLM that has been given tools it can call and the ability to reason over multi-step tasks |
| **Agentification** | The systematic replacement of manual, knowledge-intensive workflows with AI agent pipelines |
| **RAG** | Retrieval-Augmented Generation — grounding LLM outputs in retrieved documents rather than training data |
| **TSB** | Technical Service Bulletin — a manufacturer-issued document describing known vehicle defects and their repair procedures |
| **IATF 16949** | The international quality management standard for automotive production and relevant service part organisations |
| **DTC** | Diagnostic Trouble Code — a standardised error code generated by a vehicle's onboard diagnostics system |
| **Tool call** | A structured request made by an LLM to execute an external function (database query, web search, etc.) |
| **Human-in-the-loop** | An architectural pattern where AI-generated outputs pause for human review before proceeding |
| **LangGraph** | A Python framework for building stateful, multi-actor agent workflows as directed graphs |
| **Chunking** | The process of splitting large documents into smaller, overlapping segments for embedding and retrieval |
| **Embedding** | A numerical vector representation of text that captures semantic meaning for similarity search |
| **LLM-as-judge** | Using an LLM to evaluate the quality of another LLM's output against a rubric |
| **Golden test set** | A fixed set of labelled inputs with known correct outputs used to measure system performance |

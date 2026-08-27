# Zycus AI Support System

## Overview

Zycus AI Support System is a prototype AI-powered customer support system that combines Retrieval-Augmented Generation (RAG), automated ticket triage, and TAM (Technical Account Manager) account health analysis. The system uses a knowledge base retrieval pipeline backed by ChromaDB and the Google Gemini LLM to answer product questions, classify support tickets, and generate account health briefs.

This project was built as a technical assignment and is a **prototype**, not a production-ready system.

## Features

- **Knowledge Base Q&A** — Retrieval-Augmented Generation over a local knowledge base to answer product questions with grounded context.
- **Intelligent Ticket Triage** — Classifies incoming support tickets using retrieved knowledge base context and the Gemini LLM, producing structured triage output.
- **TAM Account Health Analysis** — Combines account and ticket data to generate an account health brief with risks, evidence, and recommended talking points.
- **Evaluation Harness** — Deterministic test suite covering ticket triage and account health logic.
- **Streamlit UI** — Interactive interface exposing all three core workflows.

## Architecture

### RAG Pipeline

```
Knowledge Base Documents
        ↓
  Document Loading
        ↓
   Text Splitting
        ↓
    Embeddings
        ↓
     ChromaDB
        ↓
Similarity Retrieval
        ↓
 Relevant Context
        ↓
    Gemini LLM
        ↓
  Grounded Answer
```

### Ticket Triage Pipeline

```
Incoming Ticket
        ↓
   Ticket Text
        ↓
Knowledge Base Retrieval
        ↓
 Relevant KB Context
        ↓
    Gemini LLM
        ↓
  Structured JSON
        ↓
   Triage Result
```

## Project Structure

```
Zycus_Project_ass/
│
├── data/
│   ├── accounts.json
│   └── tickets.json
│
├── knowledge-base/
│   ├── analyticshub.md
│   ├── databridge-pro.md
│   └── performance-and-integrations.md
│
├── src/
│   ├── retrieval.py
│   ├── rag.py
│   ├── llm.py
│   ├── ticket_triage.py
│   ├── account_health.py
│   ├── evaluation.py
│   └── app.py
│
├── evaluation_results/
│   └── eval_report.json
│
├── .env
├── requirements.txt
├── design_note.md
└── README.md
```

### File Responsibilities

| File | Responsibility |
|---|---|
| `retrieval.py` | Loads the knowledge base, creates embeddings, uses ChromaDB, and retrieves relevant documents. |
| `rag.py` | Implements the RAG workflow — sends the question to retrieval, builds context, and generates a grounded answer. |
| `llm.py` | Handles Gemini LLM interaction; reads `GOOGLE_API_KEY` from `.env` and generates answers using the configured Gemini model. |
| `ticket_triage.py` | Loads tickets from `data/tickets.json`, retrieves relevant KB context, and uses Gemini to classify/triage tickets into structured JSON. |
| `account_health.py` | Loads accounts and tickets, matches account IDs, calculates 90-day ticket history, and generates an Account Health Brief. |
| `evaluation.py` | Deterministic evaluation harness for Task 1 (Ticket Triage) and Task 2 (Account Health). |
| `app.py` | Streamlit application exposing Knowledge Base Q&A, Ticket Triage, and Account Health. |

## Technology Stack

- Python
- LangChain
- LangChain Community
- LangChain HuggingFace
- ChromaDB
- Sentence Transformers
- Hugging Face
- Google Gemini
- Streamlit
- FastAPI
- NumPy
- Pandas
- Scikit-learn
- python-dotenv

## Setup

The project uses a Python virtual environment (Windows setup shown below).

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Configuration

The application requires a Gemini API key, provided via a `.env` file:

```
GOOGLE_API_KEY=your_actual_gemini_api_key
```

**Note:** The actual API key must never be committed to GitHub. Use the placeholder above locally and keep `.env` out of version control.

## Running the Application

Start the Streamlit application:

```bash
python -m streamlit run src\app.py
```

The sidebar provides three sections:

- **Knowledge Base Q&A** — Enter a question; the system retrieves relevant knowledge base context and generates an answer.
- **Ticket Triage** — Select a real ticket and run ticket triage.
- **Account Health** — Select an account shared between `accounts.json` and `tickets.json` to generate an Account Health Brief.

## Running Individual Modules

Ticket triage:

```bash
python src\ticket_triage.py
```

Account health:

```bash
python src\account_health.py
```

Evaluation:

```bash
python src\evaluation.py
```

## Task 1 — Intelligent Ticket Triage

Given an incoming ticket, the system retrieves relevant knowledge base context and uses the Gemini LLM to produce a structured triage result containing:

- Product area
- Issue category
- Urgency
- Reasoning
- Known issue
- Knowledge base source
- Responder team
- First response
- Retrieved sources

**Urgency categories:**

| Level | Meaning |
|---|---|
| P1 | Critical / major business impact |
| P2 | High impact / significant functionality affected |
| P3 | Moderate impact / limited users or workaround exists |
| P4 | Low impact / general question or minor issue |

**Tested example:** Ticket `TKT-10078` was triaged and produced a DataBridge Pro performance-related result.

## Task 2 — TAM Account Health

The account health system combines `accounts.json` and `tickets.json` to calculate ticket history over a 90-day window.

**Note on dates:** The dataset does not contain current real-world dates for evaluation logic. The implementation therefore uses the latest ticket timestamp in `tickets.json` as the dataset reference date.

The system produces:

- Executive summary
- Open risks and flagged issues
- Risk severity
- Evidence
- Ticket quotes when available
- Recommended TAM talking points
- Ticket count for the last 90 days
- Dataset reference date

**Tested example:** Account `ACC-1785` had one matching ticket within the calculated 90-day window.

## Task 3 — Evaluation Harness

The evaluation harness covers:

- Task 1 (Ticket Triage): 5 tests
- Task 2 (Account Health): 5 tests
- **Total: 10 tests**

Current deterministic evaluation result:

```
Total tests: 10
Passed: 10
Failed: 0
Overall pass rate: 1.00
```

The report is generated at `evaluation_results/eval_report.json`.

The evaluation harness uses deterministic dataset/logic checks and avoids unnecessary Gemini API calls where possible, keeping evaluation fast and repeatable.

## Task 4 — Design Note

A separate design note, [`design_note.md`](./design_note.md), covers:

1. Production failure modes and mitigations
2. Latency versus quality trade-offs
3. Data sensitivity and PII handling
4. Scaling to 10× volume

Refer to `design_note.md` for the full discussion of these topics.

## Security

- API keys are loaded from `.env` and are never hard-coded in source files.
- `.env` should not be committed to version control.
- Support and account data may contain sensitive information and should be handled accordingly.
- A production deployment should apply data minimization, access control, secure logging, and appropriate PII handling.

## Limitations

This project is a **prototype** built for a technical assignment. It is not production-ready. A production deployment would additionally require:

- Authentication/authorization
- Secure secrets management
- API rate limiting
- Retry and timeout handling
- Strong structured-output validation
- Monitoring and observability
- Persistent production vector infrastructure
- Asynchronous processing
- Horizontal scaling
- Continuous evaluation
- Data quality monitoring

None of the above production features are currently implemented; they are noted here as future considerations only.

## Conclusion

Zycus AI Support System demonstrates a working prototype of an AI-assisted support workflow — combining RAG-based knowledge retrieval, LLM-driven ticket triage, and account health analysis — along with a deterministic evaluation harness and a Streamlit interface for interactive use.

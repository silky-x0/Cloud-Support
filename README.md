# CloudDash Multi-Agent Customer Support System

> A production-grade prototype of a multi-agent AI system for handling end-to-end customer support for **CloudDash** — a cloud infrastructure monitoring SaaS. Built with Python, FastAPI, and a hybrid RAG pipeline.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Architecture Overview](#architecture-overview)
- [Knowledge Base](#knowledge-base)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Environment Variables](#environment-variables)
- [Design Decisions](#design-decisions)
- [Known Limitations](#known-limitations)

---

## Overview

CloudDash Support is a **multi-agent customer support system** that:

1. Accepts customer queries via a REST API (or optional CLI)
2. Classifies intent and routes to the correct specialist agent
3. Grounds responses in a real knowledge base using a hybrid RAG pipeline
4. Preserves full context during cross-agent handovers
5. Escalates to human operators (simulated) when AI cannot resolve
6. Enforces input/output guardrails for safety and accuracy
7. Emits structured JSON logs with per-conversation trace IDs

---

## Features

| Category | Capability |
|----------|------------|
| **Agents** | Triage · Technical Support · Billing · Escalation |
| **RAG** | Dense vector search + BM25 keyword + RRF fusion + cross-encoder re-ranking |
| **Knowledge Base** | 20+ articles across FAQ, Troubleshooting, Billing, API Docs, Account |
| **Handovers** | Full context preservation, entity transfer, fallback routing, audit logging |
| **Guardrails** | Prompt injection detection · PII redaction · Hallucination check |
| **Observability** | Structured JSON logs · trace_id propagation · optional Langfuse tracing |
| **Config** | YAML-driven agent definitions — add new agents without touching core code |
| **Interface** | REST API with auto-generated OpenAPI docs at `/docs` |

---

## Quick Start

### Prerequisites

- Python 3.11+
- An OpenAI API key (or configure a local model — see [Configuration](#configuration))

### 1. Clone and set up environment

```bash
git clone https://github.com/your-org/cloud-support.git
cd cloud-support

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (and optionally LANGFUSE keys)
```

### 3. Ingest the knowledge base

```bash
python -m retrieval.ingest
# This chunks, embeds, and indexes all KB articles into ChromaDB
# Persisted to ./chroma_db/ — only needs to run once (or after KB updates)
```

### 4. Start the API server

```bash
uvicorn main:app --reload --port 8000
```

The API is now live at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### 5. Test with curl

```bash
# Start a new conversation
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "cust-001"}'

# Send a message (replace {id} with the conversation_id from above)
curl -X POST http://localhost:8000/api/v1/conversations/{id}/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "My CloudDash alerts stopped firing after I updated my AWS credentials yesterday."}'
```

### 6. (Optional) CLI interface

```bash
python cli.py
# Interactive terminal chat session
```

---

## Project Structure

```
cloud-support/
│
├── main.py                   # FastAPI application entrypoint
├── requirements.txt
├── .env.example              # Environment variable template
├── README.md
├── ARCHITECTURE.md           # Detailed architecture document
│
├── agents/                   # Agent implementations
│   ├── base_agent.py         # Abstract BaseAgent class
│   ├── orchestrator.py       # Central coordinator & state manager
│   ├── triage_agent.py       # Intent classification & routing
│   ├── technical_agent.py    # Technical support resolution
│   ├── billing_agent.py      # Billing inquiries & plan management
│   └── escalation_agent.py   # Human handover packaging
│
├── api/                      # HTTP interface layer
│   ├── routes.py             # FastAPI routers & endpoint definitions
│   └── dependencies.py       # Dependency injection wiring
│
├── retrieval/                # RAG pipeline
│   ├── ingest.py             # KB ingestion: parse → chunk → embed → index
│   ├── embeddings.py         # Embedding model wrapper (OpenAI / local)
│   ├── vector_store.py       # ChromaDB / FAISS abstraction
│   └── retriever.py          # Query rewrite → dense+BM25 → RRF → rerank
│
├── handover/                 # Agent handover protocol
│   ├── handover_manager.py   # Payload building, dispatch, fallback
│   ├── summarizer.py         # Conversation compression (<500 tokens)
│   └── audit_logger.py       # JSONL audit log for every handover event
│
├── guardrails/               # Safety layer
│   ├── input_guard.py        # Injection detection · off-topic filter
│   └── output_guard.py       # PII redaction · hallucination check
│
├── models/                   # Pydantic data models
│   ├── conversation.py       # ConversationState
│   ├── message.py            # Message, Citation
│   ├── agent_response.py     # AgentResponse
│   └── handover.py           # HandoverPayload, HandoverLog
│
├── config/                   # Configuration files
│   ├── agents.yaml           # Per-agent: class, prompt, LLM params
│   ├── routing.yaml          # Intent → agent mapping & thresholds
│   └── settings.py           # Pydantic Settings (reads .env)
│
├── knowledge_base/           # Knowledge base articles
│   ├── faq/                  # General FAQ articles (JSON)
│   ├── troubleshooting/      # Step-by-step guides (JSON)
│   ├── billing/              # Pricing & policy docs (JSON)
│   ├── api_docs/             # API reference articles (JSON)
│   └── account/              # SSO, RBAC, team management (JSON)
│
├── utils/                    # Shared utilities
│   ├── logger.py             # Structured JSON logger + trace_id propagation
│   └── llm_client.py         # OpenAI wrapper with retry & timeout
│
└── tests/                    # Test suite
    ├── unit/
    │   ├── test_triage.py
    │   ├── test_retriever.py
    │   ├── test_guardrails.py
    │   └── test_handover.py
    └── integration/
        ├── test_single_agent_flow.py
        ├── test_cross_agent_handover.py
        └── test_escalation_flow.py
```

---

## Architecture Overview

```
Client
  │
  ▼
FastAPI (api/)
  │  Input Guardrail → reject injection / off-topic
  ▼
Orchestrator (agents/orchestrator.py)
  │  Loads ConversationState · routes · dispatches
  ├──► Triage Agent      → classify intent, extract entities
  ├──► Technical Agent   → RAG + LLM troubleshooting
  ├──► Billing Agent     → RAG + mock account lookup
  └──► Escalation Agent  → summarize + package for human
           │
           ▼ (when cross-domain)
       HandoverManager (handover/)
           │  build payload · validate · audit log
           ▼
       Target Agent (resumes with full context)
           │
           ▼
     Output Guardrail → PII redact · hallucination check
           │
           ▼
     Structured JSON Response (with citations)
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full component breakdown, data models, RAG pipeline diagram, and handover state machine.

---

## Knowledge Base

The KB contains **20 articles** across five categories:

| Category | Count | Examples |
|----------|-------|---------|
| FAQ | 5 | API key reset, supported cloud providers, team invitations |
| Troubleshooting | 6 | Alerts not firing, AWS integration failure, dashboard latency |
| Billing & Pricing | 4 | Plan comparison, refund policy, invoice explanation, payment methods |
| API Docs | 3 | Authentication, rate limits, webhook setup |
| Account & Access | 2 | SSO / SAML setup, RBAC configuration |

Each article follows this schema:

```json
{
  "id": "KB-001",
  "title": "How to Configure Alert Thresholds",
  "category": "troubleshooting",
  "tags": ["alerts", "configuration", "thresholds"],
  "content": "...",
  "last_updated": "2026-04-15",
  "applies_to": ["Pro", "Enterprise"]
}
```

To add new KB articles, place them in the appropriate `knowledge_base/<category>/` directory (as JSON files) and re-run `python -m retrieval.ingest`.

---

## API Reference

Full interactive docs available at `http://localhost:8000/docs` (Swagger UI).

### Start a Conversation

```http
POST /api/v1/conversations
Content-Type: application/json

{ "customer_id": "cust-001" }
```

**Response:**
```json
{
  "conversation_id": "conv-abc123",
  "trace_id": "tr-xyz789",
  "current_agent": "triage",
  "created_at": "2026-05-14T10:30:00Z"
}
```

### Send a Message

```http
POST /api/v1/conversations/{conversation_id}/messages
Content-Type: application/json

{ "content": "My alerts stopped firing after updating AWS credentials." }
```

**Response:**
```json
{
  "agent": "technical",
  "content": "This is typically caused by IAM permission changes... [KB-007]",
  "citations": [
    {
      "kb_id": "KB-007",
      "title": "AWS Integration Troubleshooting",
      "snippet": "When credentials are rotated, the IAM role must include...",
      "score": 0.91
    }
  ],
  "handover_occurred": false,
  "trace_id": "tr-xyz789"
}
```

### Get Conversation History

```http
GET /api/v1/conversations/{conversation_id}/history
```

### Health Check

```http
GET /api/v1/health
```

---

## Configuration

### Agent Configuration (`config/agents.yaml`)

Define agents declaratively — no code changes needed to add new ones:

```yaml
agents:
  triage:
    class: agents.triage_agent.TriageAgent
    system_prompt_file: prompts/triage.txt
    max_tokens: 512
    temperature: 0.2
    retriever_enabled: false

  technical:
    class: agents.technical_agent.TechnicalAgent
    system_prompt_file: prompts/technical.txt
    max_tokens: 1024
    temperature: 0.3
    retriever_enabled: true
    retrieval_top_k: 5
```

### Routing Rules (`config/routing.yaml`)

```yaml
routing:
  intents:
    technical_issue:
      target: technical
      confidence_threshold: 0.70
    billing_inquiry:
      target: billing
      confidence_threshold: 0.75
  fallback:
    low_confidence: triage
    agent_error: escalation
    max_handovers: 3
```

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests (requires OPENAI_API_KEY)
pytest tests/integration/ -v

# With coverage report
pytest tests/ --cov=. --cov-report=html
```

### Test Scenarios Covered

| Scenario | Test File |
|----------|-----------|
| Single-agent technical resolution | `test_single_agent_flow.py` |
| Cross-agent handover (Tech → Billing) | `test_cross_agent_handover.py` |
| Escalation to human | `test_escalation_flow.py` |
| KB retrieval failure + graceful fallback | `test_retriever.py` |
| Input guardrail (injection attempt) | `test_guardrails.py` |
| Output guardrail (PII in response) | `test_guardrails.py` |
| Handover failure + fallback routing | `test_handover.py` |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
# ── LLM ──────────────────────────────────────────────────────
OPENAI_API_KEY=sk-...              # Required
OPENAI_MODEL=gpt-4o-mini           # Default model
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# ── Vector Store ──────────────────────────────────────────────
CHROMA_PERSIST_DIR=./chroma_db     # ChromaDB persistence directory
USE_FAISS=false                    # Set true to use FAISS instead

# ── State Store ───────────────────────────────────────────────
REDIS_URL=                         # Optional — leave empty for in-memory state

# ── Observability (optional) ──────────────────────────────────
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com

# ── Guardrails ────────────────────────────────────────────────
ENABLE_INPUT_GUARDRAIL=true
ENABLE_OUTPUT_GUARDRAIL=true
PII_REDACTION_ENABLED=true

# ── Server ────────────────────────────────────────────────────
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
LOG_FORMAT=json                    # json | text
```

---

## Design Decisions

### Why a custom Orchestrator instead of LangGraph / CrewAI?

LangGraph and CrewAI are powerful, but they introduce significant framework complexity and vendor lock-in. For this prototype, a custom async Orchestrator gives us:
- Full control over routing logic and state management
- No hidden graph execution semantics to debug
- A cleaner separation of concerns across modules
- Easier to explain in a live discussion

The trade-off: we write more boilerplate. For a production system with 10+ agents, adopting LangGraph's stateful graph model would be the right call.

### Why ChromaDB over Pinecone / Qdrant?

ChromaDB runs locally with zero infrastructure — no account needed, no cost, persists to disk. The `VectorStore` abstraction in `retrieval/vector_store.py` makes swapping to Pinecone a single config change for production.

### Why hybrid retrieval (dense + BM25)?

Pure vector search misses exact-match queries for technical terms like "SSO", "SAML", "BM25", "webhook". BM25 excels at these. RRF fusion captures the best of both, and cross-encoder re-ranking (using `cross-encoder/ms-marco-MiniLM-L-6`) significantly improves precision on the final top-k.

### Why pull-based handover?

The target agent must explicitly `acknowledge()` the handover payload before the source agent releases ownership. This enables the target to validate context completeness and trigger a fallback if something is wrong, rather than blindly accepting a broken state.

---

## Known Limitations

- **In-memory state** is lost on restart unless `REDIS_URL` is set.
- **No streaming** — responses are complete JSON payloads; SSE would reduce perceived latency.
- **Billing is simulated** — mock `AccountLookup` uses fixture data; no real CRM integration.
- **Single-instance only** — horizontal scaling requires Redis-backed session state.
- **Hallucination check** is overlap-heuristic-based; a dedicated NLI model (e.g., `roberta-large-mnli`) would be more reliable.
- **No authentication** on the API — suitable for prototype demo; would need JWT/API-key auth for production.

---

## Live Demo

🌐 **Deployed at:** `https://cloud-support.your-domain.com`  
📖 **Swagger UI:** `https://cloud-support.your-domain.com/docs`

> Deployed on Render free tier. Cold starts may take ~30s.

---

*Assessment submission for CloudDash Multi-Agent Support — AI Engineering Intern Role.*
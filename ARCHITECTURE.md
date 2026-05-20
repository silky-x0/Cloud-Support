# CloudDash Multi-Agent Support System — Architecture

## Table of Contents
1. [High-Level Overview](#1-high-level-overview)
2. [Request Lifecycle](#2-request-lifecycle)
3. [Component Deep-Dives](#3-component-deep-dives)
4. [Agent Architecture](#4-agent-architecture)
5. [RAG Pipeline](#5-rag-pipeline)
6. [Handover Protocol](#6-handover-protocol)
7. [Guardrails & Safety](#7-guardrails--safety)
8. [Data Models](#8-data-models)
9. [Observability](#9-observability)
10. [Configuration System](#10-configuration-system)
11. [Design Decisions & Trade-offs](#11-design-decisions--trade-offs)

---

## 1. High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│              HTTP REST API  /  CLI  /  Web UI                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API LAYER (FastAPI)                        │
│   POST /conversations          POST /conversations/{id}/messages │
│   GET  /conversations/{id}     GET  /conversations/{id}/history  │
│                                                                 │
│   ┌─────────────────┐   ┌─────────────────┐                     │
│   │  Input Guardrail│   │ Output Guardrail │                     │
│   │  - Injection    │   │ - PII Redaction  │                     │
│   │  - Off-topic    │   │ - Hallucination  │                     │
│   └────────┬────────┘   └────────▲─────────┘                     │
└────────────┼────────────────────┼────────────────────────────────┘
             │                    │
             ▼                    │
┌────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                               │
│                                                                │
│  ┌──────────────┐   Routing Decision   ┌────────────────────┐  │
│  │ Conversation │ ──────────────────► │  Agent Registry    │  │
│  │    State     │                      │  (from YAML config)│  │
│  │  (in-memory  │ ◄────────────────── │                    │  │
│  │  + Redis opt)│   Aggregates Resps   └────────────────────┘  │
│  └──────────────┘                                              │
└──────────┬────────────────────────────────────────────────────┘
           │ dispatches to
           ▼
┌──────────────────────────────────────────────────────────────────┐
│                        AGENT LAYER                               │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────┐ │
│  │    Triage    │  │  Technical   │  │   Billing    │  │ Esc. │ │
│  │    Agent     │  │    Agent     │  │    Agent     │  │Agent │ │
│  │              │  │              │  │              │  │      │ │
│  │ • Intent     │  │ • KB Retriev │  │ • KB Retriev │  │• Ctx │ │
│  │   classify   │  │ • Troubl.    │  │ • Plan mgmt  │  │  Sum │ │
│  │ • Entity ext │  │ • Code snips │  │ • Policy cit │  │• Pri │ │
│  │ • Routing    │  │              │  │              │  │  ority│ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──┬───┘ │
└─────────┼─────────────────┼─────────────────┼─────────────┼──────┘
          │                 │                 │             │
          └─────────────────┴────────┬────────┘─────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────┐
│                      HANDOVER LAYER                             │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                 HandoverManager                          │  │
│  │  • Packages full conversation context                    │  │
│  │  • Transfers extracted entities                          │  │
│  │  • Validates target agent acceptance                     │  │
│  │  • Falls back to Triage/Escalation on failure            │  │
│  │  • Emits structured audit log event                      │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌────────────────────────────────────────────────────────────────┐
│                       RAG / RETRIEVAL LAYER                     │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Embeddings  │  │ Vector Store │  │   Retrieval Chain    │  │
│  │  (OpenAI /   │  │  (ChromaDB / │  │                      │  │
│  │   Sentence   │  │   FAISS)     │  │  1. Query rewrite    │  │
│  │   Transf.)   │  │              │  │  2. Dense search     │  │
│  └──────────────┘  └──────────────┘  │  3. BM25 keyword     │  │
│                                       │  4. RRF fusion       │  │
│  ┌──────────────────────────────┐    │  5. Cross-encoder re-│  │
│  │    Knowledge Base (JSON)     │    │     rank              │  │
│  │  FAQs / Troubleshooting /    │    │  6. Citation attach  │  │
│  │  Billing / API Docs / Acct   │    └──────────────────────┘  │
│  └──────────────────────────────┘                              │
└────────────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────────────┐
│                        LLM LAYER                                │
│  OpenRouter API (openai-compatible)                             │
│  Chat model:  nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free │
│  System prompt loaded from agents.yaml per-agent                │
└────────────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────────────┐
│                     OBSERVABILITY LAYER                         │
│  Structured JSON logs  ·  Trace ID propagation  ·  Langfuse    │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. Request Lifecycle

### Single-Turn Happy Path

```
1. Client  ──POST /conversations/{id}/messages──►  API Layer
2. API     ──apply Input Guardrail─────────────►  (rejects injection / off-topic)
3. API     ──dispatch(conversation_id, query)──►  Orchestrator
4. Orch.   ──load ConversationState────────────►  State Store
5. Orch.   ──route() → active_agent────────────►  Agent Registry
6. Agent   ──query_rewrite(history + query)────►  Retriever
7. Retriev.──dense_search + BM25 + rerank──────►  Vector Store + BM25 Index
8. Agent   ──build_prompt(context + chunks)────►  LLM Client
9. LLM     ──completion────────────────────────►  Agent
10. Agent  ──AgentResponse(text, citations)────►  Orchestrator
11. Orch.  ──apply Output Guardrail────────────►  (PII redact / hallucination check)
12. Orch.  ──persist ConversationState─────────►  State Store
13. Orch.  ──emit structured log───────────────►  Logger / Langfuse
14. API    ──JSON response──────────────────────►  Client
```

### Cross-Agent Handover Path (additional steps after step 10)

```
10b. Agent ──handover_required? YES─────────────►  Orchestrator
10c. Orch. ──persists current response──────────►  State Store
10d. Orch. ──delegates to HandoverManager───────►  HandoverManager
10e. HM    ──emits HandoverAuditLog─────────────►  Audit Logger
10f. Orch. ──invoke(target_agent, query)────────►  Target Agent
10g. Target──resolves new intent (step 6+)──────►  Target Agent
10h. Orch. ──aggregates responses───────────────►  Orchestrator
     fallback: HM ──route back to Triage──────►  (if target fails)
```

---

## 3. Component Deep-Dives

### 3.1 API Layer (`api/`)

| File | Responsibility |
|------|---------------|
| `routes.py` | FastAPI router — conversation CRUD + message endpoints |
| `dependencies.py` | DI wiring — injects Orchestrator, Guardrails, Logger |

**Implemented endpoints:**

```
POST   /api/v1/conversations                  → Start new conversation → {conversation_id, trace_id}
POST   /api/v1/conversations/{id}/messages    → Send message → {agent, content, citations}
GET    /api/v1/conversations/{id}             → (via history) Fetch conversation state
GET    /api/v1/conversations/{id}/history     → Full message history → List[Message]
POST   /api/v1/chat                          → Legacy stub endpoint (returns STUB: … for integration tests)
GET    /api/v1/health                         → Liveness check → {"status": "ok"}
```

Input guardrail (`check_input`) runs inside `POST …/messages` before the orchestrator is called.
Output guardrail (`redact_pii`) is applied inside the orchestrator after the final agent response.

### 3.2 Orchestrator (`agents/orchestrator.py`)

The Orchestrator is the central coordinator. It is **stateless itself** — all mutable state lives in `ConversationState`. Responsibilities:

- Load/save `ConversationState` from the state store
- Call `AgentRegistry.resolve(intent)` to get the correct agent
- Invoke the agent's `handle()` method
- Delegate handovers to `HandoverManager`
- Apply input and output guardrails
- Emit per-turn structured logs with `trace_id`

The Orchestrator does **not** implement routing logic — that lives in `config/routing.yaml` and the `Triage Agent`. This separation means new routing rules never require code changes.

### 3.3 Agent Registry

Agents are registered at startup by loading `config/agents.yaml`. The registry is a simple dict: `{agent_name → AgentInstance}`. Adding a new agent type requires:
1. Adding an entry to `config/agents.yaml`
2. Placing a new `*_agent.py` file in `agents/`
3. Zero changes to `orchestrator.py`

---

## 4. Agent Architecture

### 4.1 BaseAgent (Abstract)

```python
class BaseAgent(ABC):
    name: str
    llm_client: LLMClient
    retriever: Optional[Retriever]
    config: AgentConfig          # loaded from agents.yaml

    @abstractmethod
    async def handle(self, query: str, state: ConversationState) -> AgentResponse:
        ...

    async def _retrieve(self, query: str) -> list[RetrievedChunk]:
        """Shared RAG invocation — rewrites query with history first."""
        ...

    async def _call_llm(self, system_prompt: str, messages: list) -> str:
        """Thin LLM wrapper with retry + timeout."""
        ...
```

### 4.2 Agent Responsibilities

#### Triage Agent
- **Input**: Raw customer query + prior context
- **Output**: `AgentResponse` with `routing_decision` field set
- **How**: LLM call with a classification prompt (intent list in `routing.yaml`). Extracts entities (customer_id, plan, product, urgency). Writes entities into `ConversationState.extracted_entities`.
- **Does NOT** resolve the issue — it routes and hands off immediately.

#### Technical Support Agent
- **Input**: Query + `ConversationState` (entities already extracted by Triage)
- **Output**: Step-by-step resolution with KB citation
- **How**: RAG retrieval → builds `[SYSTEM][KB_CONTEXT][USER]` prompt structure → LLM completion. Includes source KB article IDs in response.
- **Escalation trigger**: If after 2 retrieval attempts no relevant chunk found (score < threshold), sets `escalate=True`.

#### Billing Agent
- **Input**: Query + state
- **Output**: Policy explanation / plan change confirmation (simulated)
- **How**: RAG retrieval focused on billing/pricing category. Mock `AccountLookup` tool returns hardcoded plan/invoice data keyed on `customer_id` from entities. Cites billing policy KB articles.
- **Escalation trigger**: Refund requests, disputed amounts, or sentiment < -0.5 (from guardrail).

#### Escalation Agent
- **Input**: Full `ConversationState`
- **Output**: `EscalationPackage` — structured handover to human
- **How**: Calls `ConversationSummarizer` to compress history to <500 tokens. Classifies priority (P1–P3) based on urgency and sentiment. Logs to `handover/audit_log.jsonl`. Returns human-readable ticket stub.

### 4.3 Agent Configuration (`config/agents.yaml`)

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

  billing:
    class: agents.billing_agent.BillingAgent
    system_prompt_file: prompts/billing.txt
    max_tokens: 1024
    temperature: 0.2
    retriever_enabled: true
    retrieval_top_k: 3

  escalation:
    class: agents.escalation_agent.EscalationAgent
    system_prompt_file: prompts/escalation.txt
    max_tokens: 800
    temperature: 0.1
    retriever_enabled: false
```

---

## 5. RAG Pipeline

```
Raw KB JSON
     │
     ▼
┌──────────────┐
│   Ingestor   │  Parses KB JSON, validates schema, splits into chunks
│ (ingest.py)  │  Strategy: recursive character splitting (512 tokens,
└──────┬───────┘  64 token overlap) — preserves sentence boundaries
       │
       ▼
┌──────────────┐
│  Embeddings  │  text-embedding-3-small (OpenAI) or
│(embeddings.py│  all-MiniLM-L6-v2 (local, free tier fallback)
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│            Vector Store (vector_store.py) │
│  Primary: ChromaDB (persistent, local)    │
│  Fallback: FAISS (in-memory)              │
│  Metadata stored: kb_id, category, tags   │
└──────────────────────────────────────────┘
       │
       ▼ (at query time)
┌──────────────────────────────────────────┐
│          Retrieval Chain (retriever.py)   │
│                                          │
│  1. Query Rewrite                        │
│     • Condenses last 3 turns + query     │
│     • LLM rewrites to standalone question│
│                                          │
│  2. Dense Retrieval (vector similarity)  │
│     • top_k = configurable per agent     │
│                                          │
│  3. BM25 Keyword Retrieval (BONUS)       │
│     • rank_bm25 library on raw text      │
│                                          │
│  4. Reciprocal Rank Fusion               │
│     • Merges dense + sparse rankings     │
│                                          │
│  5. Cross-Encoder Re-Ranking (BONUS)     │
│     • cross-encoder/ms-marco-MiniLM-L-6  │
│     • Rescores top-10 → returns top-k    │
│                                          │
│  6. Citation Packaging                   │
│     • Returns List[RetrievedChunk] with  │
│       kb_id, title, score, snippet       │
└──────────────────────────────────────────┘
```

### Chunk Schema

```json
{
  "chunk_id":   "KB-001-chunk-0",
  "kb_id":      "KB-001",
  "title":      "How to Configure Alert Thresholds",
  "category":   "troubleshooting",
  "tags":       ["alerts", "configuration", "thresholds"],
  "text":       "...",
  "embedding":  [0.123, ...],
  "score":      0.91
}
```

---

## 6. Handover Protocol

### 6.1 HandoverPayload Model

```python
class HandoverPayload(BaseModel):
    handover_id:      str            # UUID
    timestamp:        datetime
    source_agent:     str
    target_agent:     str
    reason:           str
    conversation_id:  str
    trace_id:         str
    conversation_summary: str        # ≤500 tokens
    full_history:     list[Message]
    extracted_entities: dict[str, Any]
    priority:         Literal["P1", "P2", "P3"]
    sentiment:        float          # -1.0 to 1.0
```

### 6.2 Handover State Machine (Orchestrator-driven)

```
INITIATED
    │
    ▼
ORCHESTRATOR DETECTS HANDOVER_REQUIRED == True
    │
    ├──► 1. Orchestrator captures current agent response & citations
    │
    ├──► 2. HandoverManager.execute()
    │       • Builds Payload
    │       • Logs Audit Event
    │
    ├──► 3. Orchestrator invokes target_agent
    │
    ├──► 4. Orchestrator aggregates new response with previous
    │
    └──► 5. Returns combined message to user
```

### 6.3 Audit Log Entry (JSONL)

```json
{
  "event":          "HANDOVER",
  "handover_id":    "h-uuid-...",
  "timestamp":      "2026-05-14T10:30:00Z",
  "trace_id":       "tr-uuid-...",
  "source_agent":   "technical",
  "target_agent":   "billing",
  "reason":         "customer_intent_billing_upgrade",
  "status":         "ACCEPTED",
  "context_tokens": 312
}
```

---

## 7. Guardrails & Safety

### 7.1 Input Guardrail (`guardrails/input_guard.py`)

| Check | Method | Action on Fail |
|-------|--------|----------------|
| Prompt Injection | Regex (6 patterns: ignore instructions, act as, disregard, jailbreak, DAN mode) | HTTP 400 + `GUARDRAIL_TRIGGERED` log |
| Message Length | `len(text) > 2048` characters | HTTP 400 `length_exceeded` |

Returns a `GuardrailResult(passed: bool, reason: Optional[str])` Pydantic model.
Called inside `POST /conversations/{id}/messages` **before** the orchestrator.

### 7.2 Output Guardrail (`guardrails/output_guard.py`)

| Check | Method | Action on Fail |
|-------|--------|----------------|
| PII Redaction | Regex (email, phone `\d{3}-\d{3}-\d{4}`, credit card `\d{4}-\d{4}-\d{4}-\d{4}`) | Inline replacement with `[REDACTED_EMAIL]` / `[REDACTED_PHONE]` / `[REDACTED_CC]` |

Called inside the orchestrator **after** the final agent response, before history persistence.
The `redact_pii(text: str) -> str` function is stateless and idempotent.

### 7.3 KB Grounding Rule

Agents are instructed via system prompt: **"If the answer is not supported by the retrieved context, say so explicitly and offer to escalate."** The output guardrail enforces this by comparing factual claims in the response against retrieved chunk text.

---

## 8. Data Models

### ConversationState

```python
class ConversationState(BaseModel):
    conversation_id:   str
    trace_id:          str
    current_agent:     str = "triage"
    messages:          list[Message]
    extracted_entities: dict[str, Any]   # customer_id, plan, issue_type …
    handover_history:  list[HandoverLog]
    created_at:        datetime
    updated_at:        datetime
```

### Message

```python
class Message(BaseModel):
    role:       Literal["user", "assistant", "system"]
    content:    str
    agent:      str
    timestamp:  datetime
    citations:  list[Citation] = []
```

### AgentResponse

```python
class AgentResponse(BaseModel):
    agent:              str
    content:            str
    citations:          list[Citation]
    routing_decision:   Optional[str]    # set by Triage only
    handover_required:  bool = False
    handover_target:    Optional[str]
    escalate:           bool = False
    confidence:         float            # 0.0 – 1.0
```

### Citation

```python
class Citation(BaseModel):
    kb_id:    str
    title:    str
    snippet:  str
    score:    float
```

---

## 9. Observability

### Structured Log Format (JSON)

```json
{
  "timestamp":       "2026-05-14T10:30:01.123Z",
  "level":           "INFO",
  "trace_id":        "tr-abc123",
  "conversation_id": "conv-xyz789",
  "event":           "AGENT_INVOCATION",
  "agent":           "technical",
  "query_tokens":    47,
  "retrieval_top_k": 5,
  "retrieval_scores": [0.91, 0.87, 0.83, 0.79, 0.71],
  "llm_model":       "gpt-4o-mini",
  "prompt_tokens":   612,
  "completion_tokens": 284,
  "latency_ms":      1423
}
```

### Log Events

| Event | Trigger |
|-------|---------|
| `CONVERSATION_STARTED` | New conversation created |
| `AGENT_INVOCATION` | Any agent `handle()` call |
| `KB_RETRIEVAL` | Each retrieval chain call |
| `HANDOVER` | Every agent-to-agent transfer |
| `ESCALATION` | Human handover triggered |
| `GUARDRAIL_INPUT` | Input guard check fired |
| `GUARDRAIL_OUTPUT` | Output guard check fired |
| `LLM_CALL` | Every LLM completion request |

### Langfuse Integration (Bonus)

Each `AGENT_INVOCATION` is wrapped in a Langfuse trace span, capturing: agent name, prompt, completion, token counts, latency, and retrieval context. This enables end-to-end visibility across multi-hop conversations.

---

## 10. Configuration System

### Configuration Files

```
config/
├── agents.yaml      # Per-agent: class path, system prompt, LLM params, retriever settings
├── routing.yaml     # Intent-to-agent mapping, confidence thresholds, fallback rules
└── settings.py      # Pydantic Settings — reads .env for API keys, feature flags
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
    account_management:
      target: technical        # handled by technical with account KB category
      confidence_threshold: 0.65
    general_inquiry:
      target: triage
      confidence_threshold: 0.50

  fallback:
    low_confidence: triage
    agent_error:    escalation
    max_handovers:  3           # force escalation after 3 handovers
```

### Extensibility Contract

To add a new **Onboarding Agent** (example):
1. Create `agents/onboarding_agent.py` extending `BaseAgent`
2. Add entry to `config/agents.yaml` with its system prompt and LLM params
3. Add routing rule to `config/routing.yaml` for `onboarding` intent
4. **Zero changes to `orchestrator.py` or any existing agent**

---

## 11. Design Decisions & Trade-offs

| Decision | Choice | Rejected Alternative | Rationale |
|----------|--------|----------------------|-----------|
| Orchestration Pattern | Custom async Orchestrator | LangGraph / CrewAI | Full control; no framework lock-in; lighter for prototype |
| Vector Store | ChromaDB | Pinecone / Qdrant | Local-first, zero cost, persistent; easy swap via adapter |
| Embeddings | OpenRouter `nvidia/llama-nemotron-embed-vl-1b-v2:free` | OpenAI `text-embedding-3-small` | Zero cost on free tier; OpenRouter wrapper reuses same HTTP client |
| LLM | OpenRouter `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | GPT-4o-mini / Gemini Flash | Free tier; configurable via `OPENAI_MODEL` env var — swap without code changes |
| LLM Client | `openai.AsyncOpenAI` pointed at OpenRouter base URL | `httpx` direct | OpenAI SDK handles retry, timeout, streaming; OpenRouter is OpenAI-compatible |
| State Storage | In-memory dict + optional Redis | Full DB (PostgreSQL) | Fast for prototype; Redis optional for persistence |
| Handover Strategy | Orchestrated Aggregation + Audit Log | Push/Pull target acknowledgement | Orchestrator aggregates responses in a single turn, providing a cohesive multi-intent reply without client-side looping. |
| Retrieval | Dense vector search (ChromaDB similarity) | Hybrid dense + BM25 + rerank | MVP scope; architecture designed so hybrid can be layered in without API changes |
| Agent Config | YAML-driven class loading | Hardcoded factories | Adding agent = add YAML + file, no core code changes |
| API Framework | FastAPI | Flask / Django | Native async, auto-OpenAPI docs, Pydantic integration |
| Guardrails | Regex-based (input) + Regex-based PII (output) | LLM-based classifiers | Zero latency, zero cost, deterministic; LLM-based checks are a named limitation |

### Known Limitations

- **State is ephemeral** — in-memory store resets on server restart unless Redis is configured.
- **No streaming** — responses are returned as complete JSON; streaming (SSE) would reduce perceived latency.
- **Simulated billing** — `AccountLookup` uses mock data; no real CRM/billing system integration.
- **Single-instance** — no horizontal scaling support without Redis-backed sessions.
- **Hallucination check** — the overlap-based check is heuristic; a dedicated NLI model would be more precise.

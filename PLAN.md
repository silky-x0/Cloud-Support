# CloudDash Multi-Agent Support — 5-Day MVP Plan

> **Scope:** This is an internship MVP, not a production system. Working code with clear design decisions beats over-engineered code that doesn't run. Every day ends with something you can demo.

---

## Background & Why This Stack

You already built an LLM orchestrator (LLM-Orc-Station) with classifier → router → model routing, key rotation, and concurrent session handling. **That's the hard part.** This assignment is the same mental model, just in Python with a knowledge base layer on top.

Direct translation from your existing project:

| LLM-Orc-Station | This Assignment |
|---|---|
| `classifier.ts` | Triage Agent (intent classification) |
| `router.ts` | Orchestrator routing logic |
| `orchestrator.ts` | Orchestrator + HandoverManager |
| `registry.ts` | AgentRegistry loaded from `agents.yaml` |
| Multi-provider routing | Multi-agent routing |

**FastAPI** = Express with decorators. `@router.post('/chat')` instead of `app.post('/chat', handler)`. You'll feel at home within an hour.

---

## Technology Choices

| Concern | Choice | Why not the alternative |
|---|---|---|
| Web framework | FastAPI | Native async (like Express), auto-docs at `/docs`, Pydantic baked in |
| LLM | OpenAI GPT-4o-mini | Cheapest capable model; configurable |
| RAG library | LangChain (chunking + embeddings only) | Gives ChromaDB + splitter + embeddings for free — ~20 lines vs ~200 |
| Vector store | ChromaDB | Runs locally, persists to disk, zero infra. Pinecone needs an account |
| Data models | Pydantic v2 | Free validation + JSON serialization. Like Zod in TypeScript |
| State | In-memory dict | Redis is overkill for an MVP. Add it later if needed |
| Config | YAML (`agents.yaml`, `routing.yaml`) | Adding a new agent = add YAML entry, zero code changes |
| Logging | Python `logging` (JSON format) | Simple and sufficient. Langfuse is a bonus if time allows |
| Deploy | Render free tier | Persistent disk for ChromaDB, free HTTPS, zero config |

### What we're skipping (and why it's fine)

| Skipped | Why it's okay for MVP |
|---|---|
| BM25 + hybrid retrieval | Dense vector search alone scores >0.85 relevance on a 20-doc KB |
| Cross-encoder re-ranking | Overkill for 20 articles. Add later if retrieval is bad |
| Query rewriting | Direct embedding search works fine for clear support queries |
| Redis state | In-memory dict resets on restart — fine for a demo |
| Hallucination NLI check | A guardrail prompt + disclaimer covers this for MVP |
| Langfuse tracing | Bonus only — standard JSON logs are enough |
| Docker / CI/CD | Assessment explicitly says not required |

---

## Day 1 — RAG Pipeline (The Only "New" Thing)

**Goal:** By end of day, you can query your knowledge base and get relevant chunks back with citations.

### What RAG actually is (plain English)

```
1. Ingest:  Read KB JSON files → split into ~500-token chunks → call OpenAI
            embeddings API → store vectors in ChromaDB
2. Retrieve: Embed the user query → find the most similar chunks → return them
3. Use:     Paste those chunks into the LLM prompt as context
```

That's it. LangChain handles steps 1 and 2 almost entirely.

### Tasks

**1.1 — Write 20 KB articles** (`knowledge_base/`)

Create JSON files across 5 categories (4 per category):

```json
{
  "id": "KB-001",
  "title": "How to Configure Alert Thresholds",
  "category": "troubleshooting",
  "tags": ["alerts", "configuration", "thresholds"],
  "content": "Step 1: Navigate to Alerts → Settings...",
  "last_updated": "2026-04-15",
  "applies_to": ["Pro", "Enterprise"]
}
```

Categories: `faq` · `troubleshooting` · `billing` · `api_docs` · `account`

> Use AI to generate the content — the assessment only checks that articles exist and retrieval works. 15 minutes with a good prompt.

**1.2 — Ingestion script** (`retrieval/ingest.py`)

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import json, glob

def ingest():
    docs = []
    for path in glob.glob("knowledge_base/**/*.json", recursive=True):
        article = json.load(open(path))
        docs.append(Document(
            page_content=article["content"],
            metadata={"kb_id": article["id"], "title": article["title"],
                      "category": article["category"]}
        ))

    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    chunks = splitter.split_documents(docs)

    Chroma.from_documents(
        chunks,
        OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory="./chroma_db"
    )
    print(f"Indexed {len(chunks)} chunks from {len(docs)} articles")

if __name__ == "__main__":
    ingest()
```

**1.3 — Retriever wrapper** (`retrieval/retriever.py`)

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from models.message import Citation

class Retriever:
    def __init__(self):
        self.store = Chroma(
            persist_directory="./chroma_db",
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
        )

    def retrieve(self, query: str, k: int = 5) -> tuple[str, list[Citation]]:
        results = self.store.similarity_search_with_score(query, k=k)
        context_parts = []
        citations = []
        for doc, score in results:
            context_parts.append(f"[{doc.metadata['kb_id']}] {doc.page_content}")
            citations.append(Citation(
                kb_id=doc.metadata["kb_id"],
                title=doc.metadata["title"],
                snippet=doc.page_content[:200],
                score=round(1 - score, 3)
            ))
        return "\n\n".join(context_parts), citations
```

### Day 1 Deliverable

```bash
python -m retrieval.ingest
# → "Indexed 87 chunks from 20 articles"

python -c "
from retrieval.retriever import Retriever
ctx, cites = Retriever().retrieve('alerts not firing after AWS update')
print(cites[0].kb_id, cites[0].score)
"
# → KB-007  0.91
```

---

## Day 2 — Agents

**Goal:** All 4 agents return real responses. Triage correctly classifies the 4 test scenarios.

### Core pattern (same as your orchestrator.ts)

Every agent is a class with `async def handle(query, state) -> AgentResponse`. The Triage agent returns a `routing_decision` field. Others return content + citations.

**2.1 — BaseAgent** (`agents/base_agent.py`)

```python
from abc import ABC, abstractmethod
from models.conversation import ConversationState
from models.agent_response import AgentResponse

class BaseAgent(ABC):
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config

    @abstractmethod
    async def handle(self, query: str, state: ConversationState) -> AgentResponse:
        pass

    def _build_history(self, state: ConversationState) -> list[dict]:
        """Convert ConversationState messages to OpenAI chat format."""
        return [{"role": m.role, "content": m.content} for m in state.messages[-6:]]
```

**2.2 — Triage Agent** (`agents/triage_agent.py`)

The Triage agent calls GPT-4o-mini with a structured output prompt that returns `{"intent": "...", "entities": {...}, "route_to": "..."}`. This is your `classifier.ts` in Python.

Intents to classify: `technical_issue` · `billing_inquiry` · `account_management` · `general_inquiry`

**2.3 — Technical Agent** (`agents/technical_agent.py`)

1. Call `retriever.retrieve(query)`
2. Build system prompt: `"You are a CloudDash technical support agent. Use ONLY the following KB articles to answer: {context}. Always cite the KB ID."`
3. Call OpenAI with history + context
4. If no relevant chunks found (all scores < 0.5): set `escalate=True`

**2.4 — Billing Agent** (`agents/billing_agent.py`)

Same as Technical but:
- Retrieves from billing KB category only
- Has a mock `account_lookup(customer_id)` dict that returns plan/invoice data
- Escalates on: "refund", "speak to manager", "duplicate charge" keywords

**2.5 — Escalation Agent** (`agents/escalation_agent.py`)

No retrieval needed. Takes the full `ConversationState`, asks GPT to summarize it in 3 sentences, classifies priority (P1/P2/P3) based on keywords, and returns a human-handover package.

**2.6 — Agent config** (`config/agents.yaml`)

```yaml
agents:
  triage:
    class: agents.triage_agent.TriageAgent
    temperature: 0.2
    max_tokens: 512
    retriever_enabled: false

  technical:
    class: agents.technical_agent.TechnicalAgent
    temperature: 0.3
    max_tokens: 1024
    retriever_enabled: true
    retrieval_top_k: 5

  billing:
    class: agents.billing_agent.BillingAgent
    temperature: 0.2
    max_tokens: 1024
    retriever_enabled: true
    retrieval_top_k: 3

  escalation:
    class: agents.escalation_agent.EscalationAgent
    temperature: 0.1
    max_tokens: 800
    retriever_enabled: false
```

### Day 2 Deliverable

```bash
python -c "
import asyncio
from agents.triage_agent import TriageAgent
from models.conversation import ConversationState
import uuid

state = ConversationState(conversation_id=str(uuid.uuid4()), trace_id=str(uuid.uuid4()))
agent = TriageAgent('triage', {})
result = asyncio.run(agent.handle('My alerts stopped firing after I updated AWS credentials', state))
print(result.routing_decision)  # → 'technical'
"
```

---

## Day 3 — Orchestrator + FastAPI Routes

**Goal:** A running API at `localhost:8000` that handles the full conversation loop.

### The Orchestrator (your router.ts equivalent)

```python
# agents/orchestrator.py  — simplified mental model
class Orchestrator:
    def __init__(self):
        self.agents = AgentRegistry.from_yaml("config/agents.yaml")
        self.retriever = Retriever()
        self.sessions: dict[str, ConversationState] = {}   # in-memory state

    async def chat(self, conversation_id: str, query: str) -> AgentResponse:
        state = self.sessions.setdefault(conversation_id, new_state())

        # 1. Always go through Triage first if no active agent
        if state.current_agent == "triage":
            triage_response = await self.agents["triage"].handle(query, state)
            state.current_agent = triage_response.routing_decision

        # 2. Dispatch to specialist agent
        agent = self.agents[state.current_agent]
        response = await agent.handle(query, state)

        # 3. Handle handover
        if response.handover_required:
            self._do_handover(state, response.handover_target)
            agent = self.agents[state.current_agent]
            response = await agent.handle(query, state)

        # 4. Handle escalation
        if response.escalate:
            response = await self.agents["escalation"].handle(query, state)

        # 5. Save turn to history
        state.messages.append(Message(role="user", content=query, agent="user"))
        state.messages.append(Message(role="assistant", content=response.content, agent=agent.name))
        self.sessions[conversation_id] = state

        return response
```

### FastAPI routes (this is just Express, different syntax)

```python
# Express                                  # FastAPI
app.post('/conversations', handler)    →   @router.post('/api/v1/conversations')
app.post('/conversations/:id/messages') →   @router.post('/api/v1/conversations/{id}/messages')
app.get('/conversations/:id/history')  →   @router.get('/api/v1/conversations/{id}/history')
req.body.content                       →   request.content  (Pydantic model)
res.json({...})                        →   return {...}
```

**Endpoints to implement:**

```
POST /api/v1/conversations              → create conversation, return {conversation_id, trace_id}
POST /api/v1/conversations/{id}/messages → send message, get {agent, content, citations}
GET  /api/v1/conversations/{id}/history → full message list
GET  /api/v1/health                     → {"status": "ok"}
```

### Day 3 Deliverable

```bash
uvicorn main:app --reload
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Content-Type: application/json" -d '{"customer_id": "cust-001"}'
# → {"conversation_id": "conv-abc", "trace_id": "tr-xyz"}

curl -X POST http://localhost:8000/api/v1/conversations/conv-abc/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "My alerts stopped firing after I updated AWS credentials"}'
# → {"agent": "technical", "content": "...[KB-007]...", "citations": [...]}
```

---

## Day 4 — Handover Protocol + Guardrails

**Goal:** Cross-agent handovers work with an audit trail. Basic input/output safety is in place.

### Handover (3–4 hours)

The handover is simple: when an agent sets `handover_required=True` and `handover_target="billing"`, the Orchestrator:

1. Builds a `HandoverPayload` (conversation summary + entities + timestamp)
2. Writes one line to `handover/audit.jsonl`
3. Switches `state.current_agent` to the target
4. Calls the target agent with the same query + full context

```python
# handover/handover_manager.py
class HandoverManager:
    def execute(self, state: ConversationState, target: str, reason: str) -> HandoverPayload:
        payload = HandoverPayload(
            handover_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            source_agent=state.current_agent,
            target_agent=target,
            reason=reason,
            conversation_id=state.conversation_id,
            trace_id=state.trace_id,
            extracted_entities=state.extracted_entities,
            full_history=state.messages
        )
        self._audit_log(payload)          # append to audit.jsonl
        state.current_agent = target
        state.handover_history.append(payload.model_dump())
        return payload

    def _audit_log(self, payload: HandoverPayload):
        with open("handover/audit.jsonl", "a") as f:
            f.write(payload.model_dump_json() + "\n")
```

**Fallback rule:** If the target agent raises an exception → fall back to `triage`. If Triage also fails → route to `escalation`. Max 3 handovers per conversation → force escalation.

### Guardrails (2–3 hours)

**Input guardrail** (`guardrails/input_guard.py`) — two checks:

```python
INJECTION_PATTERNS = [
    r"ignore (previous|all) instructions",
    r"act as (a|an|if)",
    r"disregard (your|the) (system|previous)",
    r"jailbreak", r"DAN mode",
]

def check_input(text: str) -> GuardrailResult:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return GuardrailResult(passed=False, reason="prompt_injection")
    return GuardrailResult(passed=True)
```

**Output guardrail** (`guardrails/output_guard.py`) — PII redaction:

```python
PII_PATTERNS = {
    "email":   r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone":   r'\b(\+\d{1,3}[\s-])?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b',
    "cc":      r'\b\d{4}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}\b',
}

def redact_pii(text: str) -> str:
    for label, pattern in PII_PATTERNS.items():
        text = re.sub(pattern, f"[REDACTED_{label.upper()}]", text)
    return text
```

**KB grounding rule** — add this to every agent's system prompt:
> *"If the answer is not found in the provided KB articles, say: 'I don't have verified information on this. Would you like me to escalate to our team?' Never make up pricing, plan details, or feature availability."*

### Structured logging (1 hour)

Add trace_id to every log line using Python's `logging` with a JSON formatter:

```python
# utils/logger.py
import logging, json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "event": record.getMessage(),
            **getattr(record, "extra", {})
        })
```

Log these events at minimum: `AGENT_INVOCATION`, `KB_RETRIEVAL`, `HANDOVER`, `ESCALATION`, `GUARDRAIL_TRIGGERED`.

### Day 4 Deliverable

```bash
# Test Scenario 2: Cross-agent handover
curl -X POST .../conversations/conv-abc/messages \
  -d '{"content": "I want to upgrade from Pro to Enterprise, but first check my SSO issue"}'
# → Technical agent responds about SSO, then hands over to Billing for upgrade

cat handover/audit.jsonl | python -m json.tool
# → {"handover_id": "...", "source_agent": "technical", "target_agent": "billing", ...}
```

---

## Day 5 — Knowledge Base Polish + Tests + Deploy

**Goal:** All 4 assessment test scenarios pass. System is live at a public URL.

### Morning: Knowledge base completeness check

Verify you have articles that cover all 4 scenarios:

| Scenario | Required KB articles |
|---|---|
| Scenario 1 (AWS alerts) | AWS integration troubleshooting, alert threshold config |
| Scenario 2 (SSO + upgrade) | SSO/SAML setup, Pro→Enterprise plan comparison |
| Scenario 3 (double charge) | Refund policy, billing dispute process |
| Scenario 4 (Datadog) | *(intentionally absent — tests graceful failure)* |

### Tests (2–3 hours)

Write 6 focused tests — not 100% coverage, just the key flows:

```
tests/
├── unit/
│   ├── test_triage.py        # intent classification for all 4 scenarios
│   ├── test_retriever.py     # KB retrieval returns relevant results
│   └── test_guardrails.py    # injection detected, PII redacted
└── integration/
    ├── test_scenario_1.py    # single-agent technical resolution
    ├── test_scenario_2.py    # cross-agent handover (Tech → Billing)
    └── test_scenario_3.py    # escalation to human
```

Use `pytest-asyncio` for async tests. Mock the OpenAI calls in unit tests (`unittest.mock.patch`) to avoid API costs.

### Deploy (1–2 hours)

**Render (recommended):**
1. Push to GitHub
2. Create a new Web Service on render.com → connect repo
3. Build command: `pip install -r requirements.txt && python -m retrieval.ingest`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add `OPENAI_API_KEY` as environment variable
6. Disk: mount at `/app/chroma_db` (so ChromaDB persists across deploys)

### Day 5 Deliverable

```bash
# All 4 scenarios pass
pytest tests/ -v

# Live URL works
curl https://your-app.onrender.com/api/v1/health
# → {"status": "ok"}

curl https://your-app.onrender.com/docs
# → Swagger UI with all endpoints interactive
```

---

## All 4 Test Scenarios — Quick Reference

### Scenario 1 — Single-agent technical resolution
```
User: "My CloudDash alerts stopped firing after I updated my AWS integration credentials yesterday."
Flow: Triage → technical_issue → Technical Agent → retrieves KB-007 (AWS integration)
      → step-by-step fix with citation [KB-007]
```

### Scenario 2 — Cross-agent handover
```
User: "I want to upgrade from Pro to Enterprise, but first check my SSO issue."
Flow: Triage → technical_issue (primary) + billing_inquiry (secondary)
      → Technical Agent handles SSO → handover_required=True, target="billing"
      → HandoverManager logs handover → Billing Agent has full context, handles upgrade
```

### Scenario 3 — Escalation
```
User: "I've been charged twice for April. I need an immediate refund and I want to speak to a manager."
Flow: Triage → billing_inquiry → Billing Agent → detects "refund" + "speak to manager"
      → escalate=True → Escalation Agent → summarizes context, priority=P1 → human handover package
```

### Scenario 4 — KB retrieval failure
```
User: "Does CloudDash support integration with Datadog?"
Flow: Triage → general_inquiry → Technical Agent → retrieves KB → all scores < 0.5
      → "I don't have verified information on Datadog integration. I can escalate this to our
         product team or log a feature request — would you like me to do that?"
```

---

## Day-by-Day Summary

| Day | Focus | End State |
|---|---|---|
| 1 | RAG pipeline | 20 KB articles indexed, retrieval returning cited chunks |
| 2 | 4 Agents | All agents handle their domain, Triage routes correctly |
| 3 | Orchestrator + API | Running FastAPI server, full conversation loop working |
| 4 | Handover + Guardrails | Audit log populating, PII redacted, injection blocked |
| 5 | Tests + Deploy | All 4 scenarios automated, live URL up |

---

## What Scores Points (Prioritized)

| Weight | Item | MVP approach |
|---|---|---|
| 25% | System Design | Clean module separation + YAML-driven agent registry |
| 25% | KB Integration | LangChain ChromaDB + citations in every response |
| 20% | Handover | HandoverManager + audit.jsonl + fallback rule |
| 15% | Code Quality | Pydantic models + typed signatures + 6 tests |
| 15% | Guardrails | Regex injection guard + PII redaction + KB grounding prompt |

# Graph Report - Cloud-Support  (2026-05-20)

## Corpus Check
- 74 files · ~24,865 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 621 nodes · 654 edges · 75 communities (62 shown, 13 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 64 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `83ec5c43`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Base Agent Framework|Base Agent Framework]]
- [[_COMMUNITY_Specialist Agents & Responses|Specialist Agents & Responses]]
- [[_COMMUNITY_Data Models & API Interface|Data Models & API Interface]]
- [[_COMMUNITY_Orchestration & Session Management|Orchestration & Session Management]]
- [[_COMMUNITY_Technical Support & Retrieval Subsystem|Technical Support & Retrieval Subsystem]]
- [[_COMMUNITY_Logging & Tracing|Logging & Tracing]]
- [[_COMMUNITY_Billing & Strategic MVP Concepts|Billing & Strategic MVP Concepts]]
- [[_COMMUNITY_Application Configuration|Application Configuration]]
- [[_COMMUNITY_Gemini Tool Configuration|Gemini Tool Configuration]]
- [[_COMMUNITY_Web Framework Components|Web Framework Components]]
- [[_COMMUNITY_Core Agent Capabilities|Core Agent Capabilities]]
- [[_COMMUNITY_Handover Tests|Handover Tests]]
- [[_COMMUNITY_Retrieval Tests|Retrieval Tests]]
- [[_COMMUNITY_Output Guardrails|Output Guardrails]]
- [[_COMMUNITY_Input Guardrails|Input Guardrails]]
- [[_COMMUNITY_Processing Logic|Processing Logic]]
- [[_COMMUNITY_Conversation Summarization|Conversation Summarization]]
- [[_COMMUNITY_Knowledge Ingestion|Knowledge Ingestion]]
- [[_COMMUNITY_Agent Messaging Models|Agent Messaging Models]]
- [[_COMMUNITY_Request Lifecycle|Request Lifecycle]]
- [[_COMMUNITY_System Safety Principles|System Safety Principles]]
- [[_COMMUNITY_Project Documentation|Project Documentation]]
- [[_COMMUNITY_Vector Database Infrastructure|Vector Database Infrastructure]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 77|Community 77]]

## God Nodes (most connected - your core abstractions)
1. `BaseAgent` - 16 edges
2. `CloudDash Multi-Agent Customer Support System` - 15 edges
3. `ConversationState` - 13 edges
4. `AgentResponse` - 13 edges
5. `CloudDash Multi-Agent Support System — Architecture` - 13 edges
6. `chat()` - 12 edges
7. `BillingAgent` - 12 edges
8. `Citation` - 11 edges
9. `Retriever` - 11 edges
10. `CloudDash Multi-Agent Support — 5-Day MVP Plan` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Settings` --semantically_similar_to--> `FastAPI`  [INFERRED] [semantically similar]
  config/settings.py → requirements.txt
- `BillingAgent` --implements--> `CloudDash 5-Day MVP Plan`  [INFERRED]
  agents/billing_agent.py → PLAN.md
- `BillingAgent` --conceptually_related_to--> `Handover Protocol`  [INFERRED]
  agents/billing_agent.py → ARCHITECTURE.md
- `BillingAgent` --references--> `Agent Registry`  [INFERRED]
  agents/billing_agent.py → config/agents.yaml
- `Retriever` --implements--> `RAG Pipeline Concept`  [INFERRED]
  retrieval/retriever.py → PLAN.md

## Hyperedges (group relationships)
- **Agent Orchestration Flow** — agents_orchestrator_chat, agents_triage_agent_triageagent, agents_technical_agent_technicalagent, agents_escalation_agent_escalationagent [EXTRACTED 1.00]
- **Core Support Data Models** — models_conversation_conversationstate, models_agent_response_agent_response, models_message_message [INFERRED 0.85]
- **Contextual Observability Stack** — utils_trace_trace_context, utils_logger_jsonformatter, api_routes_chat_stub [INFERRED 0.85]
- **Agent Orchestration System** — agents_billing_agent_billingagent, config_agents_registry, architecture_handover_protocol_details, architecture_request_lifecycle [INFERRED 0.95]
- **RAG Retrieval Subsystem** — retrieval_embeddings_get_embeddings, retrieval_retriever_retriever, requirements_chromadb, plan_rag_pipeline_concept [INFERRED 0.95]

## Communities (75 total, 13 thin omitted)

### Community 0 - "Base Agent Framework"
Cohesion: 0.05
Nodes (34): ABC, BaseAgent, get_openai_client(), Return a safe, user-friendly response when something goes wrong internally., Return a safe, user-friendly response when something goes wrong internally., Return a safe, user-friendly response when something goes wrong internally., Shared singleton so every agent reuses the same HTTP connection pool., Shared singleton so every agent reuses the same HTTP connection pool. (+26 more)

### Community 1 - "Specialist Agents & Responses"
Cohesion: 0.07
Nodes (37): chat(), create_conversation(), _do_handover(), get_agents(), get_conversation(), _load_agents(), Switch the active agent and write an audit log entry., Load agent configurations from YAML and instantiate agent classes dynamically. (+29 more)

### Community 2 - "Data Models & API Interface"
Cohesion: 0.04
Nodes (46): All 4 Test Scenarios — Quick Reference, Background & Why This Stack, CloudDash Multi-Agent Support — 5-Day MVP Plan, code:python (# Express                                  # FastAPI), code:block11 (POST /api/v1/conversations              → create conversatio), code:bash (uvicorn main:app --reload), code:python (# handover/handover_manager.py), code:python (INJECTION_PATTERNS = [) (+38 more)

### Community 3 - "Orchestration & Session Management"
Cohesion: 0.05
Nodes (38): Agent Configuration (`config/agents.yaml`), API Reference, Architecture Overview, CloudDash Multi-Agent Customer Support System, code:http (POST /api/v1/conversations), code:json ({), code:http (POST /api/v1/conversations/{conversation_id}/messages), code:json ({) (+30 more)

### Community 4 - "Technical Support & Retrieval Subsystem"
Cohesion: 0.21
Nodes (6): OpenAIEmbeddings, get_embeddings(), OpenRouterEmbeddings, Returns the embeddings model.     Uses OpenRouter and nvidia/llama-nemotron-embe, Returns the OpenAI embeddings model.     Uses text-embedding-3-small for cost/pe, ingest()

### Community 5 - "Logging & Tracing"
Cohesion: 0.14
Nodes (17): Check for context, code:block1 (┌─────────────────────────────────────────┐), code:bash (openspec list --json), code:block3 (User: I'm thinking about adding real-time collaboration), code:block4 (User: The auth system is a mess), code:block5 (User: /opsx:explore add-auth-system), code:block6 (User: Should we use Postgres or SQLite?), code:block7 (## What We Figured Out) (+9 more)

### Community 6 - "Billing & Strategic MVP Concepts"
Cohesion: 0.14
Nodes (14): 1. Clone and set up environment, 2. Configure environment variables, 3. Ingest the knowledge base, 4. Start the API server, 5. Test with curl, 6. (Optional) CLI interface, code:bash (git clone https://github.com/your-org/cloud-support.git), code:bash (cp .env.example .env) (+6 more)

### Community 7 - "Application Configuration"
Cohesion: 0.4
Nodes (4): BaseSettings, Application settings powered by Pydantic Settings.     Environment variables are, Settings, FastAPI

### Community 13 - "Handover Tests"
Cohesion: 0.24
Nodes (4): HandoverManager, Executes a handover from source agent to target agent.         Builds the Handov, HandoverPayload, test_handover_execution()

### Community 14 - "Retrieval Tests"
Cohesion: 0.22
Nodes (9): code:block1 (1. Ingest:  Read KB JSON files → split into ~500-token chunk), code:json ({), code:python (from langchain_community.vectorstores import Chroma), code:python (from langchain_community.vectorstores import Chroma), code:bash (python -m retrieval.ingest), Day 1 Deliverable, Day 1 — RAG Pipeline (The Only "New" Thing), Tasks (+1 more)

### Community 15 - "Output Guardrails"
Cohesion: 0.5
Nodes (4): 7.1 Input Guardrail (`guardrails/input_guard.py`), 7.2 Output Guardrail (`guardrails/output_guard.py`), 7.3 KB Grounding Rule, 7. Guardrails & Safety

### Community 24 - "Knowledge Ingestion"
Cohesion: 0.17
Nodes (11): Check for context, code:block1 (┌─────────────────────────────────────────┐), code:bash (openspec list --json), Ending Discovery, Guardrails, OpenSpec Awareness, The Stance, What You Don't Have To Do (+3 more)

### Community 31 - "Community 31"
Cohesion: 0.2
Nodes (10): 4.1 BaseAgent (Abstract), 4.2 Agent Responsibilities, 4.3 Agent Configuration (`config/agents.yaml`), 4. Agent Architecture, Billing Agent, code:python (class BaseAgent(ABC):), code:yaml (agents:), Escalation Agent (+2 more)

### Community 32 - "Community 32"
Cohesion: 0.22
Nodes (9): 8. Data Models, AgentResponse, Citation, code:python (class ConversationState(BaseModel):), code:python (class Message(BaseModel):), code:python (class AgentResponse(BaseModel):), code:python (class Citation(BaseModel):), ConversationState (+1 more)

### Community 34 - "Community 34"
Cohesion: 0.29
Nodes (6): Capabilities, Impact, Modified Capabilities, New Capabilities, What Changes, Why

### Community 35 - "Community 35"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 36 - "Community 36"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 37 - "Community 37"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 38 - "Community 38"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 39 - "Community 39"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 40 - "Community 40"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 41 - "Community 41"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 42 - "Community 42"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 43 - "Community 43"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 44 - "Community 44"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 45 - "Community 45"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 46 - "Community 46"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 47 - "Community 47"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 48 - "Community 48"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 49 - "Community 49"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 50 - "Community 50"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 51 - "Community 51"
Cohesion: 0.18
Nodes (10): ADDED Requirements, knowledge-base Specification, Purpose, Requirement: Support Article Categories, Requirement: Support Article Fields, Requirement: Total Size and Volume, Requirements, Scenario: Check combined file size (+2 more)

### Community 52 - "Community 52"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 53 - "Community 53"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 54 - "Community 54"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 55 - "Community 55"
Cohesion: 0.25
Nodes (7): applies_to, category, content, id, last_updated, tags, title

### Community 56 - "Community 56"
Cohesion: 0.18
Nodes (10): ADDED Requirements, Purpose, rag-ingestion Specification, Requirement: JSON Support Articles Loading, Requirement: Text Chunking, Requirement: Vector DB Storage, Requirements, Scenario: Index chunks into ChromaDB (+2 more)

### Community 57 - "Community 57"
Cohesion: 0.48
Nodes (5): code:bash (openspec status --change "<name>" --json), code:bash (openspec instructions apply --change "<name>" --json), code:block3 (## Implementing: <change-name> (schema: <schema-name>)), code:block4 (## Implementation Complete), code:block5 (## Implementation Paused)

### Community 58 - "Community 58"
Cohesion: 0.29
Nodes (6): code:bash (mkdir -p openspec/changes/archive), code:bash (mv openspec/changes/<name> openspec/changes/archive/YYYY-MM-), code:block3 (## Archive Complete), code:block4 (## Archive Complete), code:block5 (## Archive Complete (with warnings)), code:block6 (## Archive Failed)

### Community 59 - "Community 59"
Cohesion: 0.29
Nodes (6): 11. Design Decisions & Trade-offs, 1. High-Level Overview, CloudDash Multi-Agent Support System — Architecture, code:block1 (┌───────────────────────────────────────────────────────────), Known Limitations, Table of Contents

### Community 60 - "Community 60"
Cohesion: 0.29
Nodes (7): 6.1 HandoverPayload Model, 6.2 Handover State Machine, 6.3 Audit Log Entry (JSONL), 6. Handover Protocol, code:block10 (INITIATED), code:json ({), code:python (class HandoverPayload(BaseModel):)

### Community 61 - "Community 61"
Cohesion: 0.29
Nodes (6): Capabilities, Impact, Modified Capabilities, New Capabilities, What Changes, Why

### Community 62 - "Community 62"
Cohesion: 0.53
Nodes (4): code:bash (openspec new change "<name>"), code:bash (openspec status --change "<name>" --json), code:bash (openspec instructions <artifact-id> --change "<name>" --json), code:bash (openspec status --change "<name>")

### Community 63 - "Community 63"
Cohesion: 0.33
Nodes (5): code:bash (openspec status --change "<name>" --json), code:bash (openspec instructions apply --change "<name>" --json), code:block3 (## Implementing: <change-name> (schema: <schema-name>)), code:block4 (## Implementation Complete), code:block5 (## Implementation Paused)

### Community 64 - "Community 64"
Cohesion: 0.33
Nodes (6): 10. Configuration System, code:block17 (config/), code:yaml (routing:), Configuration Files, Extensibility Contract, Routing Rules (`config/routing.yaml`)

### Community 65 - "Community 65"
Cohesion: 0.6
Nodes (3): code:bash (mkdir -p openspec/changes/archive), code:bash (mv openspec/changes/<name> openspec/changes/archive/YYYY-MM-), code:block3 (## Archive Complete)

### Community 66 - "Community 66"
Cohesion: 0.4
Nodes (4): code:bash (openspec new change "<name>"), code:bash (openspec status --change "<name>" --json), code:bash (openspec instructions <artifact-id> --change "<name>" --json), code:bash (openspec status --change "<name>")

### Community 67 - "Community 67"
Cohesion: 0.4
Nodes (5): 2. Request Lifecycle, code:block2 (1. Client  ──POST /conversations/{id}/messages──►  API Layer), code:block3 (10b. Agent ──handover_required? YES─────────────►  HandoverM), Cross-Agent Handover Path (additional steps after step 10), Single-Turn Happy Path

### Community 68 - "Community 68"
Cohesion: 0.4
Nodes (5): 3.1 API Layer (`api/`), 3.2 Orchestrator (`agents/orchestrator.py`), 3.3 Agent Registry, 3. Component Deep-Dives, code:block4 (POST   /api/v1/conversations                  → Start new co)

### Community 69 - "Community 69"
Cohesion: 0.4
Nodes (5): 9. Observability, code:json ({), Langfuse Integration (Bonus), Log Events, Structured Log Format (JSON)

### Community 70 - "Community 70"
Cohesion: 0.4
Nodes (4): Context, Decisions, Goals / Non-Goals, Risks / Trade-offs

### Community 71 - "Community 71"
Cohesion: 0.5
Nodes (4): 5. RAG Pipeline, Chunk Schema, code:block7 (Raw KB JSON), code:json ({)

### Community 72 - "Community 72"
Cohesion: 0.4
Nodes (4): Context, Decisions, Goals / Non-Goals, Risks / Trade-offs

### Community 73 - "Community 73"
Cohesion: 0.5
Nodes (3): 1. Create Knowledge Base Articles, 2. Ingestion Script Implementation, 3. Verification

### Community 77 - "Community 77"
Cohesion: 0.5
Nodes (3): 1. Create Knowledge Base Articles, 2. Ingestion Script Implementation, 3. Verification

## Knowledge Gaps
- **308 isolated node(s):** `id`, `title`, `category`, `tags`, `content` (+303 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConversationState` connect `Specialist Agents & Responses` to `Base Agent Framework`, `Conversation Summarization`, `Handover Tests`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `BaseAgent` connect `Base Agent Framework` to `Specialist Agents & Responses`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Why does `Retriever` connect `Base Agent Framework` to `Specialist Agents & Responses`, `Technical Support & Retrieval Subsystem`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `BaseAgent` (e.g. with `ConversationState` and `AgentResponse`) actually correct?**
  _`BaseAgent` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `ConversationState` (e.g. with `Message` and `TechnicalAgent`) actually correct?**
  _`ConversationState` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AgentResponse` (e.g. with `Citation` and `TechnicalAgent`) actually correct?**
  _`AgentResponse` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Temporary stub endpoint for initial integration testing.     Returns a hardcoded`, `Structured logging formatter that outputs logs in JSON format.     Merges extra`, `Load agent configurations from YAML and instantiate agent classes dynamically.` to the rest of the system?**
  _346 weakly-connected nodes found - possible documentation gaps or missing edges._
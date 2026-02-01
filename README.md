# AI Knowledge Assistant (RAG-Based Enterprise Q&A System)
An end-to-end Retrieval-Augmented Generation (RAG) system that answers questions over internal documents with grounded, explainable, and secure AI responses.
This project is built with production-grade engineering practices, including structured prompting, guardrails against hallucinations, regression evaluation, security controls, CI/CD, and Dockerized deployment.

## Key Features
    •	Retrieval-Augmented Generation (RAG) with document grounding
    •	Citation-aware answers (every answer is tied to real sources)
    •	“I don’t know” safety behavior when no reliable context exists
    •	Prompt-injection detection & blocking
    •	LLM output guardrails (source validation, grounding enforcement)
    •	Regression evaluation framework for LLM outputs
    •	API key authentication & rate limiting
    •	Metrics & observability endpoints
    •	Fully Dockerized (multi-stage build)
    •	CI with GitHub Actions
    •	Config-driven (dev / CI / prod ready)

## Architecture Overview
    User Question
         ↓
    FastAPI API (/api/v1/ask)
         ↓
    Retriever (Vector Search + Threshold)
         ↓
    ┌───────────────────────────────┐
    │ No relevant sources found?    │->"I don’t know"
    └───────────────────────────────┘
         ↓
    Prompt Builder (with citations)
         ↓
    LLM (OpenAI / Stub / Pluggable)
         ↓
    Guardrails & Validation
        ↓
    Structured API Response

## Project Structure
    AI-Knowledge-Assistant/
    |── app/
    │   |── api/
    │   │   └── v1/
    │   │       |── routes/
    │   │       │   |── ask.py
    │   │       │   |── metrics.py
    │   │       │   |── version.py
    │   │       └── router.py
    │   |── core/
    │   │   |── config.py
    │   │   |── security.py
    │   │   |── rate_limit.py
    │   │   |── metrics.py
    │   │   └── logging.py
    │   |── rag/
    │   │   |── loaders.py
    │   │   |── chunking.py
    │   │   |── vector_store.py
    │   │   |── index_builder.py
    │   │   └── prompting.py
    │   |── llm/
    │   │   |── client.py
    │   │   └── stub.py
    │   |── services/
    │   │   └── ask_service.py
    │   └── main.py
    |── data/
    │   └── docs/
    │       |── policy_access.txt
    │       |── policy_passwords.txt
    │       └── policy_incident.txt
    |── tests/
    │   |── test_ask.py
    │   |── test_rag_api.py
    │   |── test_grounded_output.py
    │   |── test_eval_regression.py
    │   |── test_security.py
    │   |── test_metrics.py
    │   |── test_health.py
    │   └── test_version.py
    |── .github/workflows/ci.yml
    |── dockerfile
    |── requirements.txt
    └── README.md


## Architecture Diagram
                  ┌──────────────────────────┐
                  │       User / Client      │
                  └─────────────┬────────────┘
                                │  POST /api/v1/ask
                                ▼
                     ┌───────────────────────┐
                     │       FastAPI API     │
                     └─────────────┬─────────┘
                                   │
                ┌──────────────────┴──────────────────┐
                │                                     │
                ▼                                     ▼
       ┌──────────────────┐                 ┌──────────────────┐
       │ Security Controls│                 │   Metrics Store  │
       │ - API Key (opt)  │                 │ - latency/tokens │
       │ - Trusted Hosts  │                 │ - counts         │
       │ - CORS           │                 └──────────────────┘
       └─────────┬────────┘
                 │
                 ▼
       ┌──────────────────┐
       │ Rate Limiter     │
       │ (per IP/API key) │
       └─────────┬────────┘
                 │
                 ▼
       ┌──────────────────────────┐
       │ Prompt Injection Detector│
       └─────────┬────────────────┘
                 │ allowed
                 ▼
       ┌──────────────────────────┐
       │ Retriever (Top-K search) │
       │ - embed query            │
       │ - vector similarity      │
       └─────────┬────────────────┘
                 │
                 ▼
       ┌──────────────────────────┐
       │ Vector Store (FAISS)     │
       └─────────┬────────────────┘
                 │ chunks + scores
                 ▼
       ┌──────────────────────────┐
       │ Threshold filter         │
       │ (RAG_MIN_SCORE)          │
       └───────┬───────────┬──────┘
               │ no sources│ sources
               ▼           ▼
     ┌────────────────┐   ┌──────────────────────────┐
     │ "I don't know" │   │ Prompt Builder           │
     │ sources=[]     │   │ (grounded with citations)│
     └────────────────┘   └─────────┬────────────────┘
                                    │
                                    ▼
                           ┌──────────────────────┐
                           │ LLM Client           │
                           │ (OpenAI / Stub)      │
                           └─────────┬────────────┘
                                     │ structured output
                                     ▼
                           ┌──────────────────────────┐
                           │ Guardrails / Validation  │
                           │ - used_sources subset    │
                           │ - must cite if not IDK   │
                           └─────────┬────────────────┘
                                     ▼
                           ┌──────────────────────────┐
                           │ API Response             │
                           │ - answer                 │
                           │ - sources + used_sources │
                           │ - meta (latency/model)   │
                           └──────────────────────────┘

## Observability:
      GET /api/v1/metrics
      GET /api/v1/metrics/summary


## How the RAG Pipeline Works
    1.	Document Ingestion
        •	Documents are loaded from data/docs
        •	Chunked with overlap to preserve semantic context
        •	Embedded and indexed into a vector store
    2.	Query Handling
        •	User question hits /api/v1/ask
        •	Vector search retrieves top-K chunks
        •	Low-confidence matches are filtered via RAG_MIN_SCORE
    3.	Safety First
        •	If no reliable chunks remain → return "I don’t know"
        •	LLM is not called when retrieval fails
    4.	Prompt + LLM
        •	Prompt explicitly restricts the LLM to provided sources
        •	LLM returns structured output:
            o	answer
            o	used_sources
    5.	Post-LLM Guardrails
        •	Used sources must match retrieved chunks
        •	Non-IDK answers must cite at least one source
        •	Violations → forced "I don’t know"

## Security Controls
    •	API Key Authentication
        o	Enabled when API_KEY + REQUIRE_API_KEY=true
        o	Applied to sensitive endpoints (/metrics, etc.)
    •	Rate Limiting
        o	Per-IP or API-key based
        o	Disabled in CI via DISABLE_RATE_LIMIT=true
    •	Prompt Injection Detection
        o	Detects malicious instructions attempting to override system behavior
        o	Blocks unsafe prompts before LLM execution

## Metrics & Observability
    Endpoints:
        •	GET /api/v1/metrics
        •	GET /api/v1/metrics/summary
    Tracked:
        •	Request counts
        •	Latency
        •	Token usage
        •	LLM model metadata

## Testing Strategy
    This project treats LLMs as non-deterministic systems and tests accordingly.
    Test Coverage Includes:
        •	API behavior & validation
        •	RAG correctness
        •	“I don’t know” behavior
        •	Citation enforcement
        •	Prompt-injection blocking
        •	Rate limiting
        •	API key enforcement
        •	Regression evaluation suite

## Deterministic CI Testing
LLM_PROVIDER=stub
RAG_MIN_SCORE=0.12
DISABLE_RATE_LIMIT=true

## Run Tests Locally
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

LLM_PROVIDER=stub DISABLE_RATE_LIMIT=true python -m pytest -q

## Docker Usage
Build Test Image
docker build --target test -t ai-knowledge-assistant:test .

## Run Tests in Docker
docker run --rm ai-knowledge-assistant:test

## Build Runtime Image
docker build --target runtime -t ai-knowledge-assistant:runtime .

## Run API
docker run --rm -p 8000:8000 ai-knowledge-assistant:runtime

## CI/CD
    •	GitHub Actions runs:
        o	Unit tests
        o	RAG regression tests
        o	Docker test stage
    •	PRs cannot be merged unless CI passes
    •	Release tags created after stable merges

## Configuration (via Environment Variables)
    LLM_PROVIDER -> openai or stub
    RAG_MIN_SCORE -> Similarity threshold
    API_KEY -> API key value
    REQUIRE_API_KEY	-> Enable API key enforcement
    DISABLE_RATE_LIMIT -> Disable rate limiting (CI/dev)
    ENVIRONMENT -> dev / test / prod

## Why This Project Matters
    This project demonstrates:
        •	Real-world LLM system design
        •	Treating AI as a controlled component, not magic
        •	Engineering rigor around safety, evaluation, and reliability
        •	Production readiness (CI, Docker, security)

## Future Improvements:
    •	Caching frequent queries
    •	Async/background document ingestion
    •	Swappable vector stores (FAISS → pgvector)
    •	Observability dashboards
    •	Agent-based workflows (if needed)


## Author
Ashish Sunuwar  
AI / Software Engineer  
LinkedIn: https://www.linkedin.com/in/ashish-sunuwar-810314206/

Email: ashish.a.sun@gmail.com

For questions or collaboration, feel free to reach out via LinkedIn or Email.

## Disclaimer
This project is a demonstration system built for learning and portfolio purposes. It is not intended for production use without additional security hardening, compliance review, and operational validation.

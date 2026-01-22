# AI-Knowledge-Assistant
An enterprise-grade AI system that answers user questions using internal documents via Retrieval-Augmented Generation (RAG), with strong guardrails, automated testing, and production-ready deployment.

## Key Features
- FastAPI backend
- RAG-based LLM pipeline
- Guardrails & hallucination prevention
- Automated LLM testing
- CI/CD & Docker deployment

## Tech Stack
- Python
- FastAPI
- Pydantic
- PyTest
- Vector Databases (FAISS/pgvector)
- OpenAI/Azure OpenAI

## Running Locally
```bash
uvicorn app.main:app --reload




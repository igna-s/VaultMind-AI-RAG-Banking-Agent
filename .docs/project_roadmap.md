# 🗺️ Project Roadmap

Current Status: **Phase 1 Complete (Backend Core)**

## Phase 1: Foundation (✅ Done)

- [x] Backend architecture migration to FastAPI.
- [x] Database migration to SQLModel (Relational + Vector).
- [x] Voyage AI integration (Embeddings + Rerank).
- [x] Basic Auth and RAG logic in place.

## Phase 2: Frontend Integration (🚧 Next)

- [ ] Connect React Frontend to `POST /chat` endpoint.
- [ ] Connect File Upload to `POST /upload`.
- [ ] Implement Login/Signup UI.

## Phase 3: Advanced RAG

- [ ] Implement "Hybrid Search" (Keyword + Vector) using `pgvector` hybrid search features or simple SQL LIKE fallback.
- [ ] Add conversation history memory window (currently sends full history or just last message?).
- [ ] Multi-document summarization.

## Phase 4: Production Readiness

- [ ] Dockerize the application (Dockerfile already exists but needs update for FastAPI).
- [ ] CI/CD Pipeline (GitHub Actions) to deploy to Azure App Service.
- [ ] Monitoring (Azure Application Insights).

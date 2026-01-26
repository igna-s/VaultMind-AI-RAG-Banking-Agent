# Task: Configure Azure Database Connection

- [x] Analyze backend configuration (`config.py`, `database.py`) <!-- id: 0 -->
- [x] Create `.env` in `Database` folder using credentials from backend <!-- id: 1 -->
- [x] Create and run script to apply `init.sql` to Azure PostgreSQL <!-- id: 2 -->
- [x] Verify FastAPI connection and ensure it uses `.env` <!-- id: 3 -->
- [x] Explain how to verify database via FastAPI <!-- id: 4 -->

# Task: Implement Role-Based Access Control (RBAC)

- [x] Add `role` column to `users` table via migration script <!-- id: 5 -->
- [x] Update `User` model in `models.py` <!-- id: 6 -->
- [x] Implement Admin logic and endpoints in `main.py` <!-- id: 7 -->
- [x] Verify Admin vs User access <!-- id: 8 -->

# Task: Refine Database Schema (Cleanup)

- [x] Update `init.sql` with final schema (remove legacy tables, include `role`) <!-- id: 9 -->
- [x] Create script to DROP ALL tables in Azure DB (`reset_db.py`) <!-- id: 10 -->
- [x] Reset and Re-initialize Database <!-- id: 11 -->
- [x] Verify final clean schema <!-- id: 12 -->

# Task: Verify End-to-End RAG Workflow

- [x] Update `rag.py` to use Voyage AI (real embeddings) <!-- id: 13 -->
- [x] Migrate DB vector dimension to 1024 <!-- id: 14 -->
- [x] Fix Groq model deprecation (Updating to Llama 3.3) <!-- id: 15 -->
- [x] Run full RAG test (`test_rag_flow.py`) <!-- id: 16 -->

# Task: Enhance API Security

- [x] Install `slowapi` and update requirements <!-- id: 17 -->
- [x] Implement Password Hashing in `main.py` <!-- id: 18 -->
- [x] Run migration to hash legacy admin password (`hash_legacy_passwords.py`) <!-- id: 19 -->
- [x] Implement Rate Limiting on critical endpoints <!-- id: 20 -->
- [x] Verify Rate Limiting and Login Access <!-- id: 21 -->

# Task: Securing Database and Connection for Production

- [x] Audit `rag.py` and other services for SQL Injection vulnerabilities <!-- id: 22 -->
- [x] Implement SSL/TLS enforcement in `database.py` for PROD mode <!-- id: 23 -->
- [x] Fix `config.py` PROD validation and settings <!-- id: 24 -->
- [x] Create explanation artifact for SQLi, DoS, and Production Readiness <!-- id: 25 -->

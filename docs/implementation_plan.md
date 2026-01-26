# Implementation Plan - Production Readiness

Secure the database and API connection for production deployment.

## User Review Required
> [!IMPORTANT]
> **DoS Protection**: I have implemented application-level rate limiting (`slowapi`). For full **DDoS** protection, you MUST use Azure's built-in protections (Azure Front Door, Application Gateway, or DDoS Protection Standard). I will document this.

## Proposed Changes

### 1. Database Connection Security (SSL/TLS)
#### [MODIFY] [database.py](file:///workspace/TheDefinitiveProyect/backend/app/database.py)
- **Change**: Pass `connect_args={"sslmode": "require"}` to `create_engine` to enforce encrypted connections to Azure PostgreSQL.

### 2. Configuration Validation
#### [MODIFY] [config.py](file:///workspace/TheDefinitiveProyect/backend/app/config.py)
- **Fix**: Correct the validation check `DB_PASSWORD` -> `POSTGRES_PASSWORD`.
- **Add**: Validate `DATABASE_URL` presence.

### 3. Documentation & Explanations
#### [NEW] [production_readiness.md](file:///home/vscode/.gemini/antigravity/brain/3297a6a5-f453-458b-b114-a971b7eeee95/production_readiness.md)
- **SQL Injection**: Explanation of how SQLModel/SQLAlchemy protects you (Audit results).
- **DoS/DDoS**: Explanation of Application vs Network layer protection.
- **Production Checklist**: List of things to do in Azure (Key Vault, etc).

## Verification Plan
1. **Run API**: Ensure it still connects locally (Local Postgres usually supports SSL or we make it optional for DEV).
    - *Correction*: For local DEV with `postgres` container, `sslmode=require` might fail if not configured. I will make this conditional on `APP_MODE != "DEV"`.
2. **Review Code**: Manual check of the changes.

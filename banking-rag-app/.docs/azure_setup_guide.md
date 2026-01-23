# ☁️ Azure Setup Guide (Free Tier / Student Focus)

This guide documents how to replicate the infrastructure using **Azure for Students** credits or free tier options properly.

## 1. Resource Group

- **Name**: `REDACTED_RG`
- **Region**: `East US 2` or `Central US` (Avoid regions with high quota usage like East US).

## 2. Database (PostgreSQL Flexible Server)

- **Service**: Azure Database for PostgreSQL - Flexible Server
- **Version**: 16
- **Workload Type**: Development
- **Compute Tier**: `Burstable` (B1MS)
  - _Note_: B1MS is often free for 12 months (750 hours/month).
- **Storage**: 32 GB (Included in free tier).
- **Networking**:
  - Enable "Allow public access from any Azure service within Azure to this server".
  - Add your client IP to the firewall rules.
- **Extensions**:
  - Once created, go to **Server parameters** -> Search for `azure.extensions` -> Select `vector`. Save.

## 3. App Service (Backend & Frontend)

For Azure for Students, you can use **Azure App Service (Linux)**.

- **Plan**: `F1 (Free)` (Shared infrastructure).
- **Runtime Stack**: Python 3.10+
- **Startup Command**: `gunicorn -w 2 -k uvicorn.workers.UvicornWorker backend.app.main:app` (Adjust path as needed).

## 4. Environment Variables

Configure these in your App Service **Configuration** -> **Application settings**:

| Key                           | Value Description                                             |
| :---------------------------- | :------------------------------------------------------------ |
| `DATABASE_URL`                | `postgresql://user:pass@host:5432/postgres?sslmode=require`   |
| `VOYAGE_API_KEY`              | Your Voyage AI API Key                                        |
| `SECRET_KEY`                  | Generated random string for JWT (e.g. `openssl rand -hex 32`) |
| `ALGORITHM`                   | `HS256`                                                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                                                          |

## 5. Storage (PDFs)

- **Service**: Azure Blob Storage
- **Redundancy**: LRS (Locally-redundant storage) - Cheapest.
- **Access Tier**: Hot.
- Create a container named `documents`.

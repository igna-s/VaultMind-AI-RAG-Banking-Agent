# 🚀 Deployment & Replication Guide

This guide explains how to set up the **Banking RAG Agent** project from scratch. The project is split into three components:

1.  **Database** (Azure PostgreSQL)
2.  **Backend** (Python/FastAPI)
3.  **Frontend** (React + Static Web App)

---

## 1. Database Setup (Azure PostgreSQL)

_For a step-by-step guide with screenshots and Free Tier details, see [.docs/azure_setup_guide.md](.docs/azure_setup_guide.md)._

Due to Azure Student policies, we recommend creating the database manually or following our detailed guide.

1.  **Log in to Azure Portal** and search for **"Azure Database for PostgreSQL - Flexible Server"**.
    - _Note_: Ensure `vector` extension is enabled.

---

## 2. Backend Setup (The Brain)

Located in `backend/`. Contains the LangGraph agent and API logic.

### Prerequisites

- Python 3.10+
- Pip

### Installation

1.  Navigate to the backend:
    ```bash
    cd backend
    ```
2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # venv\Scripts\activate   # Windows
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  Create a `.env` file in `backend/` (copy from example or start new):

    ```ini
    # Database
    DATABASE_URL=postgresql://user:pass@host:5432/postgres?sslmode=require

    # APIs
    VOYAGE_API_KEY=vy-...       # Voyage AI
    SECRET_KEY=...              # JWT Secret
    ```

### Execution

Run the API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

_The app will automatically create the required database tables on first run._

---

## 3. Frontend Setup (The Face)

Located in `frontend/`. A modern React application.

### Prerequisites

- Node.js 18+
- npm

### Installation

1.  Navigate to the frontend:
    ```bash
    cd frontend
    ```
2.  Install packages:
    ```bash
    npm install
    ```

### Execution

Start the development server:

```bash
npm run dev
```

---

## ☁️ Deployment (CI/CD)

The project includes automated deployment scripts for Azure Free Tier.

### 1. Provision Infrastructure

Run this script to create the **App Service (Backend)** and **Static Web App (Frontend)** automatically:

```bash
chmod +x scripts/provision_hosting.sh
./scripts/provision_hosting.sh
```

_This will output two critical secrets:_ `AZURE_WEBAPP_PUBLISH_PROFILE` and `AZURE_STATIC_WEB_APPS_API_TOKEN`.

### 2. Configure GitHub Actions

Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions**.
Add the following secrets:

- `AZURE_WEBAPP_PUBLISH_PROFILE` (From script output)
- `AZURE_STATIC_WEB_APPS_API_TOKEN` (From script output)
- `DATABASE_URL` (From Database Setup)
- `VOYAGE_API_KEY`

### 3. Deploy

Just push to your `main` branch!

- Changes in `backend/**` trigger Backend Deploy.
- Changes in `frontend/**` trigger Frontend Deploy.

---

_Verified Working on 2026-01-23_

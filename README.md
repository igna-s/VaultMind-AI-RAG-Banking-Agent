# 🧠 VaultMind AI - RAG Banking Agent

![VaultMind AI](docs/screenshots/vaultmind_banner.png)

This project is a **full-stack AI-powered RAG (Retrieval-Augmented Generation) application** designed for banking and financial knowledge management. It demonstrates the practical integration of **FastAPI** (Python) for the backend, **React + Vite** for the frontend, and **PostgreSQL with pgvector** for vector storage. The system includes a **LangGraph-based Deep Research Agent** capable of web search, database queries, and multi-step reasoning.

> **🎓 Educational Purpose**: This project serves as a comprehensive guide for building production-ready AI agents with full-stack web development.

> **🛡️ Security Note**: This project implements multiple security layers including bcrypt password hashing, JWT authentication, rate limiting, SQL injection protection, and CORS configuration. See the [Security Features](#-security-features) section for details.

---

## 🚀 Technologies

### Backend
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![SQLModel](https://img.shields.io/badge/SQLModel-009688?style=for-the-badge&logo=sqlite&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Google OAuth](https://img.shields.io/badge/Google%20OAuth-4285F4?style=for-the-badge&logo=google&logoColor=white)

### AI & RAG
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-FF6B6B?style=for-the-badge&logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-FF6600?style=for-the-badge&logo=groq&logoColor=white)
![Llama 3](https://img.shields.io/badge/Llama%203-0467DF?style=for-the-badge&logo=meta&logoColor=white)
![Voyage AI](https://img.shields.io/badge/Voyage%20AI-7B68EE?style=for-the-badge&logoColor=white)
![PGVector](https://img.shields.io/badge/PGVector-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Tavily](https://img.shields.io/badge/Tavily%20Search-00C853?style=for-the-badge&logoColor=white)

### Frontend
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![React Router](https://img.shields.io/badge/React_Router-CA4245?style=for-the-badge&logo=react-router&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Framer Motion](https://img.shields.io/badge/Framer_Motion-0055FF?style=for-the-badge&logo=framer&logoColor=white)
![Lucide](https://img.shields.io/badge/Lucide_Icons-F56565?style=for-the-badge&logoColor=white)

### ☁️ Cloud / Deployment
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Azure App Service](https://img.shields.io/badge/Azure%20App%20Service-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Azure Static Web Apps](https://img.shields.io/badge/Azure%20Static%20Web%20Apps-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Azure PostgreSQL](https://img.shields.io/badge/Azure%20PostgreSQL-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

---

## 📖 Project Structure

```
TheDefinitiveProyect/
├── backend/                  # FastAPI Backend
│   ├── app/                  # Main application
│   │   ├── main.py           # FastAPI entry point
│   │   ├── auth.py           # JWT & bcrypt authentication
│   │   ├── database.py       # SQLModel + PostgreSQL connection
│   │   ├── models.py         # Database models (User, Document, ChatSession)
│   │   ├── routers/          # API route handlers
│   │   └── services/         # Business logic (RAG, LLM)
│   ├── agent/                # LangGraph Deep Research Agent
│   │   ├── agents/           # Agent definitions
│   │   ├── tools/            # Search, filesystem, TODO tools
│   │   ├── rag/              # Retrieval & ingestion logic
│   │   └── prompts/          # System prompts
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React + Vite Frontend
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Application pages (Chat, Dashboard, Admin)
│   │   ├── context/          # Auth context provider
│   │   └── services/         # API service layer
│   └── package.json          # Node.js dependencies
├── Database/                 # Database initialization scripts
├── docs/                     # Project documentation
├── .github/workflows/        # CI/CD GitHub Actions
└── docker-compose.yml        # Local development with Docker
```

---


### Test Users

If you want to try the app, you can use the following test accounts:

- **Email:** admin@bank.com (Admin)  
  **Password:** Admin123!

- **Email:** hua@gmail.com  
  **Password:** Admin123!

---

## ☁️ Deployment

This project is configured to be deployed on **Azure Free Tier**:

- **Frontend** – [Azure Static Web Apps (F1 Plan)](https://salmon-smoke-0337ed810.6.azurestaticapps.net/)
- **Backend** – [Azure App Service (Free Plan)](https://banking-rag-auth-api.azurewebsites.net)
- **Database** – Azure Database for PostgreSQL (with pgvector extension)

👉 **[Read the Deployment Guide](docs/AZURE_DEPLOY_GUIDE.md)** for step-by-step instructions.

👉 **[See the Setup Guide](docs/SETUP.md)** for complete installation and replication instructions.

---

## 🛠️ Installation and Configuration

Follow these steps to set up the project locally.

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+
- **PostgreSQL** with `pgvector` extension (or use Docker)

### Option A: Using Docker (Recommended)

The easiest way to run the entire stack locally:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/VaultMind-AI.git
cd VaultMind-AI

# 2. Start all services (Backend, Frontend, PostgreSQL)
docker-compose up --build
```

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432

### Option B: Manual Setup

#### 1. Database (PostgreSQL with pgvector)

```bash
# Using Docker for the database only:
docker run -d \
  --name vaultmind_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=rag_db \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

#### 2. Backend (FastAPI)

Navigate to the `backend/` folder:

```bash
cd backend

# 1. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env with your API keys and database credentials

# 4. Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at `http://localhost:8000`.

#### 3. Frontend (React + Vite)

Navigate to the `frontend/` folder:

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

### 🌍 Local vs Cloud Execution

The project uses **Environment Variables** to automatically switch the Backend URL:

| Environment | Config File | API URL |
|-------------|-------------|---------|
| **Local** | `.env.development` | `http://localhost:8000` |
| **Production** | `.env.production` | `https://banking-rag-auth-api.azurewebsites.net` |

You don't need to change any code. Just run `npm run dev` for local development, or `npm run build` for production deployment.

---

## 🔧 Configuration

### Required Environment Variables (Backend)

Create a `.env` file in `backend/` with these values:

```ini
# App Mode (DEV, PROD, TEST)
APP_MODE=DEV

# Security
SECRET_KEY=your_super_secret_jwt_key_here

# AI APIs (Required for RAG functionality)
TAVILY_API_KEY=tvly-...        # Web Search
GROQ_API_KEY=gsk_...           # LLM (Llama 3)
VOYAGE_API_KEY=vy-...          # Embeddings

# Database (PostgreSQL)
DATABASE_URL=postgresql://postgres:password@localhost:5432/rag_db

# CORS (Comma separated list)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Email (Optional - for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your_google_client_id
```

👉 **[See Security Map](docs/SECURITY_MAP.md)** for the complete list of environment variables across all environments.

---

## ✨ Main Features

### 🤖 AI Chat with RAG
- **Retrieval-Augmented Generation**: Queries your private knowledge base using vector similarity search
- **LangGraph Agent**: Multi-step reasoning with tool use (web search, database queries)
- **Streaming Responses**: Real-time status updates and reasoning steps

### 📚 Knowledge Base Management
- **Document Upload**: PDF and text file ingestion with automatic vectorization
- **Voyage AI Embeddings**: 1024-dimensional embeddings for high-quality retrieval
- **Per-User Access Control**: Users only see documents from their assigned knowledge bases

### 👥 User Management (Admin)
- **Role-Based Access**: Admin and user roles
- **User Assignment**: Assign users to specific knowledge bases
- **Statistics Dashboard**: Track usage and system metrics

### 🔐 Authentication
- **JWT Tokens**: Secure stateless authentication
- **Google OAuth**: Social login integration
- **Password Reset**: Email-based password recovery

---

## 🔒 Security Features

This project implements multiple layers of security (verified from codebase):

### 1. Password Hashing (Bcrypt)
- **Implementation**: `passlib.context.CryptContext` with `bcrypt` scheme
- **Location**: [`backend/app/auth.py`](backend/app/auth.py) línea 18
- **Code**: `pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")`

### 2. Password Strength Validation
- **Requirements**: Mínimo 10 caracteres, mayúscula, minúscula, número y carácter especial
- **Location**: [`backend/app/routers/auth.py`](backend/app/routers/auth.py) función `validate_password_strength()`
- **Applied**: En registro y cambio de contraseña

### 3. SQL Injection Protection
- **Mechanism**: **SQLModel** (built on **SQLAlchemy**) con queries parametrizadas
- **Example**: `session.exec(select(User).where(User.email == email))` - el input nunca se concatena al SQL
- **Verified**: No se encontraron f-strings con input de usuario en queries SQL

### 4. Rate Limiting (SlowAPI)
- **Implementation**: `slowapi` library en [`app/limiter.py`](backend/app/limiter.py)
- **Limits verificados en el código**:
  - `POST /auth/register`: **30/minute**
  - `POST /auth/resend-verification-code`: **5/minute** 
  - `POST /auth/google`: **30/minute**
  - `POST /auth/forgot-password`: **10/minute**
  - `POST /auth/reset-password`: **10/minute**
  - `POST /chat`: **30/minute**

### 5. HttpOnly Cookies (XSS Protection)
- **Implementation**: JWT tokens almacenados en cookies HttpOnly
- **Location**: [`backend/app/routers/auth.py`](backend/app/routers/auth.py) líneas 212-219, 312-319
- **Code**:
  ```python
  response.set_cookie(
      key="access_token",
      value=access_token,
      httponly=True,                                    # Previene XSS
      secure=settings.APP_MODE != "DEV",               # HTTPS en producción
      samesite="none" if settings.APP_MODE != "DEV" else "lax",  # CSRF protection
      max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
  )
  ```

### 6. CORS (Cross-Origin Resource Sharing)
- **Configuration**: Whitelist de origins en `settings.CORS_ORIGINS`
- **Location**: [`backend/app/main.py`](backend/app/main.py) líneas 85-94
- **Code**:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=origins,           # Whitelist, no "*"
      allow_credentials=True,          # Para cookies
      max_age=3600                      # Cache preflight 1 hora
  )
  ```

### 7. SSL/TLS Enforcement (Database)
- **Production**: Automáticamente fuerza `sslmode=require` cuando `APP_MODE != "DEV"`
- **Location**: [`backend/app/database.py`](backend/app/database.py) líneas 18-19
- **Effect**: Tráfico encriptado entre backend y PostgreSQL

### 8. JWT Token Security
- **Algorithm**: HS256
- **Secret Key**: Configurable via `SECRET_KEY` environment variable
- **Expiration**: 30 minutos (`ACCESS_TOKEN_EXPIRE_MINUTES = 30`)

### 9. Email Enumeration Prevention
- **Implementation**: Respuestas genéricas que no revelan si un email existe
- **Location**: [`backend/app/routers/auth.py`](backend/app/routers/auth.py)
- **Example**: `"If email exists, a reset link has been sent."` (línea 363)

### 10. Secure Random Token Generation
- **Implementation**: `secrets` module (criptográficamente seguro)
- **Usage**:
  - Verification codes: `secrets.choice(string.digits)` (línea 94)
  - Reset tokens: `secrets.token_urlsafe(32)` (línea 366)
  - Google OAuth random passwords: `secrets.token_urlsafe(16)` (línea 297)

### 11. Email Verification
- **Flow**: Código de 6 dígitos enviado por email antes de permitir login
- **Blocking**: Usuarios no verificados con código pendiente no pueden hacer login (líneas 199-203)

👉 **[Read the Production Readiness Guide](docs/production_readiness.md)** for detailed security recommendations.

👉 **[See the Security Walkthrough](docs/walkthrough.md)** for implementation details and test results.

---

## 🚀 Replicating on Azure

### Quick Start

1. **Provision Infrastructure**:
   ```bash
   chmod +x scripts/provision_hosting.sh
   ./scripts/provision_hosting.sh
   ```

2. **Configure GitHub Secrets**:
   - `AZURE_WEBAPP_PUBLISH_PROFILE`
   - `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - `DATABASE_URL`, `VOYAGE_API_KEY`, `GROQ_API_KEY`, `TAVILY_API_KEY`

3. **Push to main** – Changes automatically deploy via GitHub Actions

### Detailed Guides

| Guide | Description |
|-------|-------------|
| [Setup Guide](docs/SETUP.md) | Complete installation and deployment instructions |
| [Azure Deploy Guide](docs/AZURE_DEPLOY_GUIDE.md) | Azure-specific configuration (App Service, Static Web Apps) |
| [Security Map](docs/SECURITY_MAP.md) | Environment variables for all environments |
| [Versions](docs/VERSIONS.md) | Exact library versions for reproducibility |

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│    React + Vite + TailwindCSS + Framer Motion                   │
│    (Azure Static Web Apps)                                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS (REST API)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                 │
│    FastAPI + SQLModel + LangGraph                               │
│    (Azure App Service)                                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Auth API   │  │   Chat API   │  │  Admin API   │           │
│  │  (JWT/OAuth) │  │   (RAG)      │  │  (CRUD)      │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                           │                                     │
│                           ▼                                     │
│  ┌────────────────────────────────────────────────────┐         │
│  │          LangGraph Deep Research Agent             │         │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────────────┐    │          │
│  │  │ Web     │  │ DB      │  │ Knowledge Base  │    │          │
│  │  │ Search  │  │ Query   │  │ RAG Retrieval   │    │          │
│  │  │(Tavily) │  │         │  │ (Voyage AI)     │    │          │
│  │  └─────────┘  └─────────┘  └─────────────────┘    │          │
│  └────────────────────────────────────────────────────┘         │
└─────────────────────────┬───────────────────────────────────────┘
                          │ SSL/TLS
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE                                 │
│    PostgreSQL + pgvector                                        │
│    (Azure Database for PostgreSQL)                              │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │    Users     │  │  Documents   │  │ Chat History │           │
│  │  & Sessions  │  │  & Chunks    │  │  & Messages  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Setup Guide](docs/SETUP.md) | Installation and local development |
| [Azure Deploy Guide](docs/AZURE_DEPLOY_GUIDE.md) | Cloud deployment instructions |
| [Production Readiness](docs/production_readiness.md) | Security measures and production checklist |
| [Security Walkthrough](docs/walkthrough.md) | Implementation details of security features |
| [Security Map](docs/SECURITY_MAP.md) | Environment variables across environments |
| [Project Roadmap](docs/project_roadmap.md) | Future development plans |
| [Versions](docs/VERSIONS.md) | Exact library versions |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Groq** for ultra-fast LLM inference
- **Voyage AI** for high-quality embeddings
- **Tavily** for web search capabilities
- **LangChain** and **LangGraph** for agent orchestration
- **Azure** for free-tier hosting services

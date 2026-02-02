# Security Map & Secrets Management

This document outlines the environment variables and secrets required to run the `banking-rag-app` in different environments.

| Variable | Propósito | Entorno Local (`.env`) | Entorno GitHub (Actions Secrets) | Entorno Azure (App Service Config) |
| :--- | :--- | :--- | :--- | :--- |
| **APP_MODE** | Define el modo de ejecución (DEV, TEST, PROD). | `APP_MODE=DEV` | N/A (Inyectado por script en CI) | `APP_MODE=PROD` |
| **USE_MOCK_LLM** | Flag para usar mocks de LLM y ahorrar créditos. | `USE_MOCK_LLM=False` | `USE_MOCK_LLM=True` (Inyectado en CI) | `USE_MOCK_LLM=False` |
| **OPENAI_API_KEY** | API Key para Azure OpenAI Service. | Definir en `.env` | `OPENAI_API_KEY` | `OPENAI_API_KEY` |
| **GEMINI_API_KEY** | API Key para Google Gemini Pro. | Definir en `.env` | `GEMINI_API_KEY` | `GEMINI_API_KEY` |
| **DB_PASSWORD** | Contraseña de la base de datos PostgreSQL. | Definir en `.env` | `DB_PASSWORD` (Mock para tests) | `DB_PASSWORD` |
| **POSTGRES_USER** | Usuario de la base de datos. | `user` | Usado en Service Container | `POSTGRES_USER` |
| **POSTGRES_HOST** | Host de la base de datos. | `localhost` | `localhost` | Host de Azure Database for PostgreSQL |
| **POSTGRES_DB** | Nombre de la base de datos. | `banking_db` | `test_db` | `banking_db` |
| **JWT_SECRET_KEY** | Clave secreta para firmar tokens JWT. | Generar string seguro | `JWT_SECRET_KEY` | `JWT_SECRET_KEY` |
| **AZURE_CREDENTIALS** | JSON con credenciales de Service Principal para deploy. | N/A | `AZURE_CREDENTIALS` | N/A |
| **ACR_LOGIN_SERVER** | Dirección del Azure Container Registry (ej: `myregistry.azurecr.io`). | N/A | `ACR_LOGIN_SERVER` | N/A |
| **ACR_USERNAME** | Usuario administrador del ACR. | N/A | `ACR_USERNAME` | N/A |
| **ACR_PASSWORD** | Contraseña del ACR. | N/A | `ACR_PASSWORD` | N/A |
| **AZURE_WEBAPP_NAME** | Nombre del App Service en Azure. | N/A | `AZURE_WEBAPP_NAME` | N/A |

> [!IMPORTANT]
> Nunca comitear valores reales en archivos `.env` o en el código fuente. Usar siempre `local.env.example` como plantilla.

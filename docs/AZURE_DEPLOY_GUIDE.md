# Guía de Despliegue en Azure

Este repositorio está configurado para desplegarse automáticamente en Azure usando GitHub Actions.

## Recursos de Azure

*   **Frontend (Static Web App):** [`banking-rag-web`](https://salmon-smoke-0937ed810.6.azurestaticapps.net)
*   **Backend (App Service):** [`banking-rag-auth-api`](https://banking-rag-auth-api.azurewebsites.net)
*   **Base de Datos:** Azure Database for PostgreSQL (Central US)

## Configuración Requerida

### 1. Variables de Entorno en Azure App Service

Ve a **Azure Portal** -> **banking-rag-auth-api** -> **Settings** -> **Environment variables** y asegúrate de tener configuradas las siguientes variables:

#### Generales
*   `APP_MODE`: `PROD`
*   `SECRET_KEY`: *[Tu clave secreta segura]*
*   `CORS_ORIGINS`: `https://salmon-smoke-0937ed810.6.azurestaticapps.net`

#### Base de Datos
*   `DATABASE_URL`: *[Connection string de postgresql]*
    *   Ejemplo: `postgresql://user:password@host:5432/dbname?sslmode=require`

#### APIs Externas (LLM & Search)
*   `TAVILY_API_KEY`: *[Tu API Key]*
*   `GROQ_API_KEY`: *[Tu API Key]*
*   `VOYAGE_API_KEY`: *[Tu API Key]*

#### Email (SMTP)
*   `SMTP_HOST`: `smtp.gmail.com`
*   `SMTP_PORT`: `587`
*   `SMTP_USER`: *[Tu email]*
*   `SMTP_PASSWORD`: *[Tu contraseña de aplicación]*
*   `FRONTEND_URL`: `https://salmon-smoke-0937ed810.6.azurestaticapps.net` (Usado para links en emails)

#### Auth
*   `GOOGLE_CLIENT_ID`: *[Tu Client ID de Google]*

### 2. Secretos en GitHub

En tu repositorio de GitHub, ve a **Settings** -> **Secrets and variables** -> **Actions** y configura:

*   `AZURE_WEBAPP_PUBLISH_PROFILE`: El contenido del archivo de perfil de publicación descargado desde el App Service ("Get publish profile").
*   `AZURE_STATIC_WEB_APPS_API_TOKEN`: El token de despliegue de la Static Web App ("Manage deployment token").

## Cambios Realizados en el Código

1.  **Limpieza:** Se eliminaron `print()` de debug y archivos temporales. Los errores críticos se registran en logs.
2.  **Frontend Build:** Se inyecta `VITE_API_URL` y `VITE_GOOGLE_CLIENT_ID` durante el build en GitHub Actions.
3.  **Backend Config:** Se agregó `gunicorn` para producción y se configuró CORS para aceptar peticiones desde el dominio de la Static Web App.
4.  **Static Web App Config:** Se agregó `staticwebapp.config.json` para manejar el routing de la SPA (evitar errores 404 de Azure).

## Verificación

1.  Hacer push a la rama `main`.
2.  Verificar que los workflows `Deploy Backend` y `Deploy Frontend` en la pestaña **Actions** de GitHub finalicen en verde.
3.  Acceder al Frontend y probar Login/Chat.

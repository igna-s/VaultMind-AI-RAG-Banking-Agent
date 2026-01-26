# Versiones del Sistema

Este documento lista las versiones exactas de las herramientas y librerías instaladas para garantizar la estabilidad del sistema.

## Entorno Base

- **Node.js**: v24.13.0
- **NPM**: 11.6.2
- **Python**: 3.14.2

## Backend (Python)

Las dependencias están fijadas estrictamente en `requirements.txt`:

- `fastapi==0.128.0`
- `pydantic-settings==2.12.0`
- `pytest==9.0.2`
- `uvicorn==0.40.0`
- `sqlalchemy==2.0.45`
- `asyncpg==0.31.0`
- `httpx==0.28.1`

> **Nota**: Para instalar exactamente estas versiones, ejecuta:
>
> ```bash
> pip install -r backend/requirements.txt
> ```

## Frontend (React + Vite)

Las versiones principales de las dependencias directas son:

- **React**: ^19.2.0
- **React DOM**: ^19.2.0
- **Vite**: ^7.2.4

> **Importante**: El archivo `package-lock.json` asegura que se instalen siempre las mismas sub-versiones dependientes. No lo borres ni ignores en git.

#!/bin/bash

# Azure App Service startup script for Python FastAPI
# Works with Azure Oryx which extracts the app to a temp directory

# Get the directory where this script is located (should be the app root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Working directory: $(pwd)"
echo "Contents:"
ls -la

# Add site-packages to PYTHONPATH if present
if [ -d "site-packages" ]; then
    export PYTHONPATH="$(pwd)/site-packages:$PYTHONPATH"
fi

echo "Starting Gunicorn with Uvicorn workers..."
echo "PYTHONPATH: $PYTHONPATH"

# Start the application
exec gunicorn --bind=0.0.0.0:8000 --workers=2 --timeout=120 -k uvicorn.workers.UvicornWorker app.main:app

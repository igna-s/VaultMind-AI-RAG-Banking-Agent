#!/bin/bash

# Azure App Service startup script for Python FastAPI
# Dependencies are pre-packaged in site-packages/ directory

cd /home/site/wwwroot

# Add site-packages to PYTHONPATH
export PYTHONPATH="/home/site/wwwroot/site-packages:$PYTHONPATH"

echo "Starting Gunicorn with Uvicorn workers..."
echo "PYTHONPATH: $PYTHONPATH"

# Start the application
exec gunicorn --bind=0.0.0.0:8000 --workers=2 -k uvicorn.workers.UvicornWorker app.main:app

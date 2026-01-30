#!/bin/bash

# Azure App Service startup script for Python FastAPI

# Navigate to the app directory
cd /home/site/wwwroot

# Create virtual environment if it doesn't exist
if [ ! -d "antenv" ]; then
    echo "Creating virtual environment..."
    python -m venv antenv
fi

# Activate virtual environment
source antenv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Start the application with Gunicorn + Uvicorn workers
echo "Starting Gunicorn with Uvicorn workers..."
exec gunicorn --bind=0.0.0.0:8000 --workers=2 -k uvicorn.workers.UvicornWorker app.main:app

# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (e.g. for potential pg_config)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app

# Expose port (Documentation only, Compose maps it)
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

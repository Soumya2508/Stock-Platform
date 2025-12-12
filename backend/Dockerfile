"""
Dockerfile for Stock Intelligence Dashboard Backend.

This creates a containerized version of the FastAPI backend.

Build: docker build -t stock-dashboard-backend .
Run: docker run -p 8000:8000 stock-dashboard-backend

Challenges:
- Managing Python dependencies in container
- Data persistence for SQLite database
- Container size optimization

Future Improvements:
- Multi-stage build for smaller image
- Add health checks
- Use non-root user
"""

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data /app/ml_models

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

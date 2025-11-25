# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Bind CRA dev server to all interfaces and use port 3000
ARG APP_HOST=api.smchitfund.local
ARG APP_PORT=8000

ENV HOST=${APP_HOST}
ENV PORT=${APP_PORT}

#RUN echo "127.0.0.1 api.smchitfund.local" >> /etc/hosts
# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://api.smchitfund.local/health || exit 1

# Production command with Gunicorn
CMD ["gunicorn", "app:app", "-c", "gunicorn.conf.py"]
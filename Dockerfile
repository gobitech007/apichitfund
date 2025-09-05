# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file if exists
COPY requirements.txt ./

# Install dependencies if requirements.txt is present
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy application code
COPY . .

# Default command to run your app (replace app.py with your entrypoint)
CMD ["python", "app.py"]
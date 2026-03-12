# Stage 1: Runtime Environment
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
# .dockerignore will handle excluding tests, source docs, and .env
COPY . .

# Expose the port (Cloud Run uses 8080 by default)
EXPOSE 8080

# Launch the application using uvicorn
# We use host 0.0.0.0 to allow traffic from outside the container
CMD ["python", "main.py"]

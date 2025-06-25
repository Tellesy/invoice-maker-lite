# Invoice Maker Lite Dockerfile
# --------------------------------
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port (Flask default)
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
# Production secret key (can override with -e SECRET_KEY at runtime)
ENV SECRET_KEY=ZyA5u4s3cG8nV6kP1wR2bL0qFt9hXs7e

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' flaskuser
USER flaskuser

# Entrypoint: Use Gunicorn for production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

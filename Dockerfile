# Use an official Python runtime as a parent image
# Pinned to a specific digest for security and stability
FROM python:3.12-slim@sha256:cdaac40248bb4e4487dda52f63c14112447ee5a2ed4c5c80c9b9965d04a8caeb

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV DEBUG=False

# Set work directory
WORKDIR /app

# Install system dependencies
# Update packages and install security updates
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        postgresql-client \
        netcat-traditional \
        libpq-dev \
        ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
# Update pip and install dependencies with version pinning
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn==21.2.0 uvicorn==0.27.1

# Copy project with appropriate permissions
COPY --chown=1000:1000 . .

# Set up a non-root user for better security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

# Collect static files
RUN python manage.py collectstatic --noinput

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8080

# Run gunicorn with Uvicorn worker for handling ASGI applications including WebSockets
CMD exec gunicorn project_chatbot.asgi:application -b 0.0.0.0:$PORT -w 1 -k uvicorn.workers.UvicornWorker --timeout 300

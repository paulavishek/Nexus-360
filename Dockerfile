# Use an official Python runtime as a parent image
# Using Alpine Linux for a minimal image with reduced attack surface
FROM python:3.12-alpine@sha256:9c51ecce261773a684c8345b2d4673700055c513b4d54bc0719337d3e4ee552e

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV DEBUG=False

# Set work directory
WORKDIR /app

# Install system dependencies
# Alpine uses apk instead of apt-get and has different package names
RUN apk update \
    && apk upgrade \
    && apk add --no-cache \
        gcc \
        g++ \
        musl-dev \
        linux-headers \
        postgresql-dev \
        mysql-client \
        mysql-dev \
        postgresql-client \
        libffi-dev \
        netcat-openbsd \
        curl \
        bash \
    && rm -rf /var/cache/apk/*

# Install Python dependencies
COPY requirements.txt .
# Update pip and install dependencies with version pinning and security checks
RUN pip install --no-cache-dir --upgrade pip==24.0 \
    && pip install --no-cache-dir pip-audit \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn==21.2.0 uvicorn==0.27.1 \
    && pip-audit \
    && pip uninstall -y pip-audit

# Copy project with appropriate permissions
COPY --chown=1000:1000 . .

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set up a non-root user for better security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup \
    && chown -R appuser:appgroup /app

# Collect static files
RUN python manage.py collectstatic --noinput

# Switch to non-root user
USER appuser

# Add metadata as labels
LABEL maintainer="Avishek Paul"
LABEL org.opencontainers.image.title="Nexus360"
LABEL org.opencontainers.image.description="AI-powered project management assistant"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.created="2025-05-21"
LABEL org.opencontainers.image.vendor="Nexus360"

# Expose the port
EXPOSE 8080

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/health/ || exit 1

# Run gunicorn with Uvicorn worker for handling ASGI applications including WebSockets
# Note: We keep the module path as project_chatbot for code compatibility
# CMD ["gunicorn", "project_chatbot.asgi:application", "-b", "0.0.0.0:8080", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--timeout", "300"]
ENTRYPOINT ["/app/entrypoint.sh"]

#!/bin/sh
# entrypoint.sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Start Gunicorn server
echo "Starting Gunicorn server..."
exec gunicorn project_chatbot.asgi:application -b 0.0.0.0:8080 -w 1 -k uvicorn.workers.UvicornWorker --timeout 300

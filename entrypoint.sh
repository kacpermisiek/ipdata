#!/bin/sh
set -e  # Stop script on error

# Wait until db is ready
until nc -z db 5432; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Run migration
alembic upgrade head

# Run the application
exec uvicorn ipdata.app.main:app --host 0.0.0.0 --port 8000
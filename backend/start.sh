#!/bin/bash

# Set error handling
set -e

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "Warning: DATABASE_URL not set. Skipping migration."
else
    # Run database migrations
    echo "Running database migrations..."
    python run_migration.py || echo "Migration failed or no migration needed"
fi

# Start the application
echo "Starting application on port $PORT..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

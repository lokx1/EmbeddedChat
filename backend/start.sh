#!/bin/bash

# Run database migrations
echo "Running database migrations..."
python run_migration.py

# Start the application
echo "Starting application..."
uvicorn main:app --host 0.0.0.0 --port $PORT

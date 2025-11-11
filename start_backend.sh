#!/bin/bash
cd "$(dirname "$0")/backend"

# Load environment variables
export $(cat ../.env | grep -v '^#' | xargs)

# Start backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

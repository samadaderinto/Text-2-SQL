#!/bin/bash

# Source the .env file if it exists
if [ -f .env ]; then
    # Export all environment variables defined in .env
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found"
    exit 1
fi

# Check and execute based on the value of ENV
if [ "$ENV" = "local" ]; then
    pipenv run python3 manage.py runserver 0.0.0.0:8000
elif [ "$ENV" = "dev" ]; then
    pipenv run gunicorn backend.asgi:application --bind 0.0.0.0:8000 --workers=1 --threads=1 --worker-connections=10 -k uvicorn.workers.UvicornWorker
else
    pipenv run gunicorn backend.asgi:application --bind 0.0.0.0:8000 --workers=5 --threads=2 --worker-connections=1000 -k uvicorn.workers.UvicornWorker
fi

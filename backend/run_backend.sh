#!/bin/bash

export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8001}
export APP_MODULE=routes:app
export CORS_ORIGIN=${CORS_ORIGIN:-'http://localhost:3002'}


# run uvicorn
uvicorn --host $HOST --port $PORT $APP_MODULE 

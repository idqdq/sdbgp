#!/bin/bash

export HOST=0.0.0.0
export PORT=8001
export APP_MODULE=routes:app
export CORS_ORIGIN='http://localhost:3002'

source ./venv/bin/activate

# run gunicorn
# exec gunicorn --bind $HOST:$PORT "$APP_MODULE" -k uvicorn.workers.UvicornWorker  # 5

# run uvicorn
uvicorn --host $HOST --port $PORT $APP_MODULE 

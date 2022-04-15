# 
FROM python:3.8

WORKDIR /code

COPY ./run_backend.sh .

ENV CORS_ORIGIN=$CORS_ORIGIN

COPY ./backend backend

RUN pip install --no-cache-dir --upgrade -r backend/requirements.txt

CMD ["sh","-c","./run_backend.sh"]
#CMD ["uvicorn", "routes:app", "--host", "0.0.0.0", "--port", "8000"]
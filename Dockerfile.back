# 
FROM python:3.8

WORKDIR /code

ENV CORS_ORIGIN=$CORS_ORIGIN

COPY ./backend backend

WORKDIR /code/backend

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["sh","-c","./run_backend.sh"]
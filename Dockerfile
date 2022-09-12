FROM python:3.8-slim-buster

RUN python -m pip install --upgrade pip

WORKDIR  /code

COPY . .

RUN pip install -r requirements.txt

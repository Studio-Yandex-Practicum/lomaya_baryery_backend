FROM python:3.8-slim-buster

RUN python -m pip install --upgrade pip

WORKDIR  /LOMAYA_BARYERY_BACKEND

COPY . .

RUN pip install -r requirements.txt

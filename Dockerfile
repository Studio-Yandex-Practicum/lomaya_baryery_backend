FROM python:3.9-slim-buster

RUN python -m pip install --upgrade pip
RUN apt-get update
RUN apt-get -y install gcc

WORKDIR  /code

# устанавливаем зависимости в отдельном слое
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# CMD uvicorn run:app --host 0.0.0.0 --port 8000 --reload
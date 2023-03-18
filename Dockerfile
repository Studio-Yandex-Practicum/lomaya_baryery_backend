FROM python:3.10-slim-buster

RUN python -m pip install --upgrade pip

WORKDIR  /LOMAYA_BARYERY_BACKEND

# устанавливаем зависимости в отдельном слое
COPY poetry.lock pyproject.toml ./
RUN pip install poetry==1.3.2
RUN poetry config virtualenvs.create false
RUN poetry install --without dev

COPY . .

CMD uvicorn run:app --host 0.0.0.0 --port 8000 --reload

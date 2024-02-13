FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

COPY ../pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY .. ./

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

CMD ["poetry", "run", "flask", "run", "--cert=cert.pem", "--key=key.pem"]

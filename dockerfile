FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pandas
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -source $HOME/.poetry/env
RUN poetry install --no-root
WORKDIR /app
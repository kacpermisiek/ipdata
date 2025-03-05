FROM python:3.13

WORKDIR /ipdata

COPY pyproject.toml poetry.lock README.md /ipdata/
COPY ./ipdata /ipdata/ipdata

COPY ./tests /ipdata/tests

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install && \
    apt-get update && \
    apt-get install -y netcat-openbsd


COPY ./alembic/. /ipdata/alembic/.
COPY alembic-db.ini /ipdata/alembic.ini

COPY entrypoint.sh /ipdata/entrypoint.sh
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
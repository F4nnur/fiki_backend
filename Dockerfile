FROM python:3.10 as requirements-stage
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10
WORKDIR /fiki
COPY --from=requirements-stage /tmp/requirements.txt /fiki/requirements.txt
COPY .env /fiki/.env
RUN pip install --no-cache-dir --upgrade -r /fiki/requirements.txt
COPY ./src /fiki/src
COPY ./alembic.ini /fiki/alembic.ini
COPY ./alembic /fiki/alembic
CMD ["uvicorn", "src:init_app", "--host", "0.0.0.0", "--port", "80"]
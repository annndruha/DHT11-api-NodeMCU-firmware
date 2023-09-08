FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
ARG APP_VERSION=prod
ENV APP_VERSION=${APP_VERSION}
ENV APP_NAME=temperature_monitor_api
ENV APP_MODULE=${APP_NAME}.routes.base:app

COPY ./requirements.txt /app/
RUN pip install -U -r /app/requirements.txt

COPY ./alembic.ini /app/alembic.ini
COPY ./migrations /app/migrations/
ADD static /app/static/
WORKDIR /app

RUN echo '#!/bin/bash \nalembic upgrade head' > /app/prestart.sh && chmod +x /app/prestart.sh

COPY ./${APP_NAME} /app/${APP_NAME}

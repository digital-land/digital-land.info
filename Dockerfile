FROM python:3.13-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /src
WORKDIR /src
RUN pip install --user -U pip
RUN pip install --user --no-cache-dir -r requirements/requirements.txt

EXPOSE 80

ENV PATH=/root/.local/bin:$PATH
ENV MODULE_NAME=application.app
ENV VARIABLE_NAME=app
ENV GUNICORN_CONF=/src/gunicorn_conf.py
ENV PRE_START_PATH=/src/prestart.sh
ARG RELEASE_TAG
ENV RELEASE_TAG=${RELEASE_TAG}

CMD ["/bin/sh", "-c", "if [ -f ${PRE_START_PATH} ]; then . ${PRE_START_PATH}; fi && exec gunicorn -k uvicorn.workers.UvicornWorker -c ${GUNICORN_CONF} ${MODULE_NAME}:${VARIABLE_NAME}"]

FROM production AS dev
WORKDIR /src
RUN pip install --user --no-cache-dir -r requirements/dev-requirements.txt

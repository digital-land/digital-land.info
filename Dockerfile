FROM tiangolo/uvicorn-gunicorn:python3.9 AS production

COPY . /src
WORKDIR /src
RUN pip install --user -U pip
RUN pip install --user --no-cache-dir -r requirements/requirements.txt

EXPOSE 80

ENV PATH=/root/.local/bin:$PATH
ENV MODULE_NAME=application.app
ENV GUNICORN_CONF=/src/gunicorn_conf.py
ENV PRE_START_PATH=/src/prestart.sh
ARG RELEASE_TAG
ENV RELEASE_TAG=${RELEASE_TAG}

FROM production AS dev
WORKDIR /src
RUN pip install --user --no-cache-dir -r requirements/dev-requirements.txt

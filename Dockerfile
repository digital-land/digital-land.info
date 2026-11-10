# Stage 1: build the frontend static assets.
# Self-contained, so a bare `docker build` produces a working image without a
# separate `make frontend-all` step in CI. Mirrors the `frontend` make target.
FROM node:26-slim AS assets
RUN apt-get update && apt-get install -y --no-install-recommends rsync \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY . .
RUN npm ci \
    && mkdir -p static/stylesheets static/javascripts \
    && npm run build \
    && rsync -r assets/javascripts static/ \
    && npx nps build.stylesheets \
    && npx nps copy.govukAssets \
    && rsync -r assets/images static/ \
    && cp node_modules/maplibre-gl/dist/maplibre-gl.css static/stylesheets/maplibre-gl.css \
    && mkdir -p static/govuk/assets \
    && cp -r node_modules/govuk-frontend/dist/govuk/* static/govuk

# Stage 2: production (runs as a non-root user).
FROM python:3.13-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Run as a non-root user. Source is owned by the user so the app can write its
# runtime dirs and pip installs to the user's home.
RUN useradd --create-home --uid 1000 appuser
COPY --chown=appuser:appuser . /src
# Bring in the static assets built in the assets stage.
COPY --from=assets --chown=appuser:appuser /src/static /src/static
WORKDIR /src
USER appuser
RUN pip install --user -U pip
RUN pip install --user --no-cache-dir -r requirements/requirements.txt

EXPOSE 80

ENV PATH=/home/appuser/.local/bin:$PATH
ENV MODULE_NAME=application.app
ENV VARIABLE_NAME=app
ENV GUNICORN_CONF=/src/gunicorn_conf.py
ENV PRE_START_PATH=/src/prestart.sh
ARG RELEASE_TAG
ENV RELEASE_TAG=${RELEASE_TAG}

CMD ["/bin/sh", "-c", "if [ -f ${PRE_START_PATH} ]; then . ${PRE_START_PATH}; fi && exec gunicorn -k uvicorn.workers.UvicornWorker -c ${GUNICORN_CONF} ${MODULE_NAME}:${VARIABLE_NAME}"]

FROM production AS dev
WORKDIR /src
USER appuser
RUN pip install --user --no-cache-dir -r requirements/dev-requirements.txt

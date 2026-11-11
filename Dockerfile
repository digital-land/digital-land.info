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
    && cp node_modules/maplibre-gl/dist/maplibre-gl.css static/stylesheets/maplibre-gl.css

# Stage 2: build Python wheels.
# psycopg2 is built from source, as its maintainers recommend for production,
# so it links against Debian's libpq and OpenSSL and picks up their security
# fixes when the base image is rebuilt. The compiler and headers needed to do
# that stay in this stage, which is thrown away after the build. The official
# Python image already includes Python's headers, so Debian's python3-dev
# isn't needed.
FROM python:3.13-slim AS python-build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements/requirements.txt /tmp/requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r /tmp/requirements.txt

# Wheels for the dev stage. Only built when the dev target is requested.
FROM python-build AS python-build-dev
COPY requirements/dev-requirements.txt /tmp/dev-requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r /tmp/dev-requirements.txt

# Stage 3: production.
# Starts from a clean base image rather than from python-build, so none of the
# build tools are inherited. It only takes the compiled wheels (see below).
# Everything is installed as root, so the app user can't change installed
# packages or app code, then we switch to a non-root user at the end.
FROM python:3.13-slim AS production

# Ignore ~/.local, so packages installed there by the app user never load.
ENV PYTHONNOUSERSITE=1

# libpq5 is the only system library needed at runtime (for psycopg2).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install from python-build's wheels. The bind mount makes /wheels available
# only for this command, so the wheel files aren't stored in the image.
COPY requirements/requirements.txt /tmp/requirements.txt
RUN --mount=type=bind,from=python-build,source=/wheels,target=/wheels \
    pip install --no-cache-dir --no-index --find-links=/wheels \
    --root-user-action=ignore -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# App code and static assets are owned by root and read-only to the app user.
# The app doesn't write to /src at runtime.
COPY . /src
COPY --from=assets /src/static /src/static
WORKDIR /src
# Compile bytecode now, so Python never needs to write __pycache__ at runtime.
RUN python -m compileall -q /src

RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 80

ENV MODULE_NAME=application.app
ENV VARIABLE_NAME=app
ENV GUNICORN_CONF=/src/gunicorn_conf.py
ENV PRE_START_PATH=/src/prestart.sh
ARG RELEASE_TAG
ENV RELEASE_TAG=${RELEASE_TAG}

CMD ["/bin/sh", "-c", "if [ -f ${PRE_START_PATH} ]; then . ${PRE_START_PATH}; fi && exec gunicorn -k uvicorn.workers.UvicornWorker -c ${GUNICORN_CONF} ${MODULE_NAME}:${VARIABLE_NAME}"]

FROM production AS dev
WORKDIR /src
USER root
RUN --mount=type=bind,from=python-build-dev,source=/wheels,target=/wheels \
    pip install --no-cache-dir --no-index --find-links=/wheels \
    --root-user-action=ignore -r requirements/dev-requirements.txt
USER appuser

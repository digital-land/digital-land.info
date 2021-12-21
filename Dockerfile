FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY . /src
WORKDIR /src
RUN pip install -U pip
RUN pip install --no-cache-dir  -r requirements.txt

EXPOSE 80

ENV PATH=/root/.local:$PATH
ENV MODULE_NAME=dl_web.app
ENV GUNICORN_CONF=/src/gunicorn_conf.py

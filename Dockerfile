FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY . /src
RUN pip install --user /src/

WORKDIR /src

EXPOSE 80

ENV PATH=/root/.local:$PATH
ENV MODULE_NAME=dl_web.app
ENV GUNICORN_CONF=/src/gunicorn_conf.py

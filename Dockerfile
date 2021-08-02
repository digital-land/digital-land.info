FROM python:3.8-slim as builder
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install git
RUN pip install --user fastapi uvicorn boto3 flask

COPY . /src
RUN pip install --user /src/
COPY ./frontend /src/frontend
RUN pip install --user /src/frontend/

FROM python:3.8-slim as app
COPY --from=builder /root/.local /root/.local
COPY --from=builder /src .

RUN pwd
# RUN pip install .

ENV PATH=/root/.local:$PATH
EXPOSE 5000

ENV FLASK_APP=dl_web/app.py
CMD ["python3", "dl_web/app.py"]

FROM python:3.12.4-slim


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /opt/tests/requirements.txt
RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r /opt/tests/requirements.txt

WORKDIR /opt

COPY . /opt/tests/functional
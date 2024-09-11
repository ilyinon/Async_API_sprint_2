FROM python:3.12.4-slim


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /opt/test
COPY requirements.txt /opt/app/requirements.txt
RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r /opt/app/requirements.txt

COPY . /opt/test

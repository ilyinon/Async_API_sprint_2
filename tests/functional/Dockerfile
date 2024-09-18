FROM python:3.12.4-slim


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /opt

COPY requirements.txt /opt/requirements.txt
RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r /opt/requirements.txt

COPY . /opt/tests/functional

ENTRYPOINT python3 -m pytest tests/ -vvv --disable-warnings

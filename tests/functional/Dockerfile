FROM python:3.12.4-slim


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH '/opt/tests/functional'

WORKDIR /opt

COPY requirements.txt /opt/requirements.txt
RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r /opt/requirements.txt

COPY . /opt/tests/functional

ENTRYPOINT find /opt &&  \
    python3 /opt/tests/functional/utils/wait_for_es.py && \
    python3 ./tests/functional/utils/wait_for_redis.py && \
    python3 -m pytest tests/ -vvv --disable-warnings

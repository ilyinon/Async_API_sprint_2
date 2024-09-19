FROM python:3.12.4-slim


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH '/opt/tests'


WORKDIR /opt

COPY requirements.txt /opt/requirements.txt
RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r /opt/requirements.txt

COPY . /opt/tests/functional
RUN mv /opt/tests/functional/conftest.py /opt/tests/conftest.py && \
    mv /opt/tests/functional/fixtures /opt/tests/


ENTRYPOINT \
    python3 tests/functional/utils/wait_for_es.py && \
    python3 tests/functional/utils/wait_for_redis.py && \
    python3 -m pytest tests -vvv --disable-warnings

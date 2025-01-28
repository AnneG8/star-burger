FROM python:3.10-slim

WORKDIR /star-burger

RUN apt-get update && apt-get install -y postgresql-client \
    && apt-get clean

RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --no-cache-dir -r /tmp/requirements.txt

COPY . .

EXPOSE 8000

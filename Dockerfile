# Image 1: image builder for Postgres
# Use the official Postgres image as a base image
FROM postgres:16.1-alpine3.19

# Install build dependencies and pgvector
RUN apk add --no-cache --virtual .build-deps \
    git \
    make \
    gcc \
    musl-dev \
    postgresql-dev \
    && cd /tmp \
    && git clone --branch v0.5.0 https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install \
    && rm -rf /tmp/pgvector \
    && apk del .build-deps
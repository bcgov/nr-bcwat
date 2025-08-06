FROM postgres:17-bookworm as pgclient

FROM python:3.12-slim

COPY --from=pgclient /usr/lib/postgresql/17/bin/pg_restore /usr/bin/pg_restore
COPY --from=pgclient /usr/lib/postgresql/17/bin/psql /usr/bin/psql
COPY --from=pgclient /usr/lib/x86_64-linux-gnu/libpq.so.5 /usr/lib/x86_64-linux-gnu/
COPY --from=pgclient /usr/lib/x86_64-linux-gnu/libssl.so.3 /usr/lib/x86_64-linux-gnu/
COPY --from=pgclient /usr/lib/x86_64-linux-gnu/libcrypto.so.3 /usr/lib/x86_64-linux-gnu/

RUN apt-get update && \
    apt-get install -y \
        curl \
        unzip \
        && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AWS_DEFAULT_REGION=ca-central-1 \
    AWS_RESPONSE_CHECKSUM_VALIDATION=when_required \
    AWS_REQUEST_CHECKSUM_CALCULATION=when_required

RUN useradd -m appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app
USER appuser

# Copy restore script
COPY --chown=appuser:appuser restore_database_from_s3.py .

CMD ["python3", "restore_database_from_s3.py"]

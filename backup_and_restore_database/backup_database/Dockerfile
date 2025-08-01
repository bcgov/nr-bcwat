FROM postgres:17-bookworm as pgclient
FROM python:3.12-slim

# Copy PostgreSQL binaries
COPY --from=pgclient /usr/lib/postgresql/17/bin/pg_dump /usr/bin/pg_dump
COPY --from=pgclient /usr/lib/postgresql/17/bin/pg_dumpall /usr/bin/pg_dumpall
COPY --from=pgclient /usr/lib/postgresql/17/bin/psql /usr/bin/psql

# Copy required shared libraries
COPY --from=pgclient /usr/lib/x86_64-linux-gnu/libpq.so.5 /usr/lib/x86_64-linux-gnu/
COPY --from=pgclient /usr/lib/x86_64-linux-gnu/libssl.so.3 /usr/lib/x86_64-linux-gnu/
COPY --from=pgclient /usr/lib/x86_64-linux-gnu/libcrypto.so.3 /usr/lib/x86_64-linux-gnu/
COPY --from=pgclient /usr/lib/x86_64-linux-gnu/libldap-2.5.so.0 /usr/lib/x86_64-linux-gnu/
COPY --from=pgclient /usr/lib/x86_64-linux-gnu/liblber-2.5.so.0 /usr/lib/x86_64-linux-gnu/
COPY --from=pgclient /usr/lib/x86_64-linux-gnu/libsasl2.so.2 /usr/lib/x86_64-linux-gnu/

# Install additional required libraries
RUN apt-get update && \
    apt-get install -y \
        libldap-2.5-0 \
        libsasl2-2 \
        && \
    pip install --no-cache-dir awscli && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AWS_DEFAULT_REGION=ca-central-1 \
    AWS_CLI_AUTO_PROMPT=off

# Create and switch to non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /usr/src/app
USER appuser

COPY --chown=appuser:appuser backup_and_upload_to_s3.py .

CMD ["python3", "backup_and_upload_to_s3.py"]

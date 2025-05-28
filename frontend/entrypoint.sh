#!/bin/sh
set -e

echo "Injecting runtime environment variables..."

# Replace placeholders in env.js
envsubst < /app/env.js.template > /app/env.js

# Replace log level in nginx.conf
envsubst '$LOG_LEVEL $BACKEND_URL' < /etc/nginx/nginx.conf

#!/bin/sh
set -e

echo "Injecting runtime environment variables..."

# Substitute env.js
envsubst < /app/env.js.template > /app/env.js

# Let the official docker-entrypoint.sh finish the rest (including nginx.conf.template substitution)
exec /docker-entrypoint.sh nginx -g "daemon off;"

#!/bin/sh
set -e

echo "Injecting runtime environment variables..."

# Render full config
envsubst '$LOG_LEVEL $BACKEND_URL' < /etc/nginx/templates/nginx.conf.template > /tmp/nginx.conf

# Produce Env.js at run time
envsubst < /app/env.js.template > /app/env.js

# Start NGINX with custom config path
exec nginx -g "daemon off;" -c /tmp/nginx.conf

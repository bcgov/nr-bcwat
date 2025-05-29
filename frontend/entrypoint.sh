#!/bin/sh
set -e

echo "Injecting runtime environment variables..."

# # Render full config
envsubst '$LOG_LEVEL $BACKEND_URL' < /etc/nginx/templates/default.conf.template > /etc/nginx/nginx.conf

# Produce Env.js at run time
envsubst '$VITE_BASE_API_URL $VITE_APP_MAPBOX_TOKEN' < /app/env.js.template > /app/env.js

# Start NGINX with custom config path
exec nginx -g "daemon off;"

FROM node:23-slim AS build-stage
WORKDIR /client

COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# Production Stage
FROM nginx:1.27.4-alpine3.21-slim AS production-stage
USER root

RUN mkdir /app

# Static files
COPY --from=build-stage /client/dist/ /app

# Templates
COPY env.js.template /app/env.js.template
COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 3000 3001

ENTRYPOINT ["/entrypoint.sh"]

USER 1001

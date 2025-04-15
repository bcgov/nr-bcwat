FROM node:23-slim AS build-stage
WORKDIR /client

ARG VITE_BASE_API_URL
ENV VITE_BASE_API_URL=$VITE_BASE_API_URL

COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# Production Stage
FROM nginx:1.27.4-alpine3.21-slim AS production-stage
RUN mkdir /app
COPY --from=build-stage /client/dist/ /app
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

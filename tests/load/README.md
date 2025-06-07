# Load Tests

Load tests evaluate the system’s performance and stability under high traffic or concurrent usage. These tests are designed to simulate real-world load scenarios on both the backend and frontend services to identify bottlenecks, response time issues, and failure points.

You can run these tests locally; however, the primary purpose of this suite is to run via .github/workflows/.system-tests.yaml, targeting a live deployment to gather metrics on application performance.

This README provides instructions for running the tests locally — useful when adding new routes or making changes that impact performance behavior.

## Prerequisites

- [k6](https://grafana.com/docs/k6/latest/set-up/install-k6/) must be installed locally.
- A `.env` file should be created based on `.env.example`, with all necessary variables such as the backend base URL, Mapbox token, etc.
- Both frontend and backend services must be running before executing the tests.

## Setup

You can start the frontend and backend services in one of two ways:

### Option 1: Run services manually

```bash
# Terminal 1 - Frontend
cd client
npm install
npm run dev
```

```bash
# Terminal 2 - Backend
cd backend
chmod +777 ./startup.sh
./startup.sh
```

This will expose:

- Frontend at [http://localhost:5173](http://localhost:5173)
- Backend at [http://localhost:8000](http://localhost:8000)

### Option 2: Run services with Docker Compose

```bash
docker compose build
docker compose up
```

Ensure that all required environment variables (e.g., `VITE_APP_MAPBOX_TOKEN`) are declared in the `.env` block of `docker-compose.yaml`.

## Running Load Tests

With services running, use the following commands to execute k6 load tests:

```bash
# Test backend performance
BACKEND_URL=http://localhost:8000 k6 run backend-test.js
```

```bash
# Test frontend performance
FRONTEND_URL=http://localhost:5173 k6 run client-test.js
```

## Notes

- You can configure the number of virtual users, duration, and thresholds directly in the test files or by passing additional flags to `k6 run`.
- Test results include response times, request failures, and other performance metrics.
- It's recommended to run these tests against a staging or non-production environment.

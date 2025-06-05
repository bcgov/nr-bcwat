# Integration Tests

Integration tests validate the interactions between major components of the system — including the frontend, backend, and database — to ensure they work together as expected. These tests focus on end-to-end data flow and system behavior across service boundaries, catching issues that unit tests may miss.

You can run these tests locally; however, the primary purpose of this suite is to run via .github/workflows/.system-tests.yaml, targeting a live deployment to ensure proper integration between the client, backend, and database of our running application.

## Prerequisites

To run the tests locally, first create a `.env` file based on the provided `.env.example`. This should include all required environment variables, including your Mapbox access token.

### Option 1: Run services manually

In two separate terminals from the project root:

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

This will start:

- Frontend at [http://localhost:5173](http://localhost:5173)
- Backend at [http://localhost:8000](http://localhost:8000)

### Option 2: Run services with Docker Compose

```bash
docker compose build
docker compose up
```

Ensure that all required environment variables (e.g., `VITE_APP_MAPBOX_TOKEN`) are defined in the `.env` section of your `docker-compose.yaml`.

## Running the Tests

Once the frontend and backend are running:

```bash
cd tests/integration
npm install
npm test
```

## Maintenance

There should be an entry within the test block of our `test_suites/backend.flask.json` per API route.

As this application does not require authentication, nor does it allow `PUT`, `POST`, or `DELETE` requests, maintaining and adding to this test suite should be trivial.

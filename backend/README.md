# Backend Documentation

## Contents

1. [API](#api)
    1. [Local Deploy](#running-the-api-locally)
    2. [Manual](#manual)
    3. [Start-Up Script](#start-up-script)
    4. [Dockerized](#dockerized)
2. [Unit Tests](#unit-tests)
    1. [Running the Tests](#running-the-tests)
3. [Database](#database)

## API

The backend is a RESTful API built using [Flask](https://flask.palletsprojects.com/), a lightweight Python web framework.

### Running the API Locally

The following commands assume you are within the `backend` directory. __It is dockerized using Python3.12. Ensure your local python version is the same.__

### Manual

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m gunicorn -w 4 wsgi:app
```

### Start Up Script

The `startup.sh` script performs the creation of a virtual environment, and installs all packages required for the API to run.

```bash
#!/bin/bash
chmod +777 ./startup.sh
./startup.sh
```

### Dockerized

```bash
docker build -t bcwat-api:local .
docker run -p 8000:8000 bcwat-api:local
```

## Unit Tests

[PyTest](https://docs.pytest.org/en/stable/contents.html) is used for unit testing of the API. Please adhere to this documentation for creating unit tests for utility functions and API routes.

### Running the tests

The `run_unit_tests.sh` script performs the creation of a virtual environment, and installs all packages required for the API to run.

```bash
chmod +777 ./run_unit_tests.sh
./run_unit_tests.sh
```

The above command runs all of the unit tests.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

The above command runs all of the unit tests.

To run specific tests, use the following command for;

- running all tests within test file

```bash
pytest tests/test_hello_world.py
```

- running specific test in file

```bash
pytest tests/test_hello_world.py::test_hello_world
```

## Database

Please see the README in the `database_initialization` for information on what is in that directory

## Swagger Documentation

Each route contains detailed information regarding the schema of the response. To view this documentation, run the API, and go to `localhost:8000/docs`. No authorization is needed to execute any of the routes.

# BC WAT Frontend

## How to Install and Run

navigate to /client
use `npm install` to install all dependencies
use `npm run dev` to launch the frontend

## Docker

```bash
docker build -t bcwat-client:init --build-arg VITE_BASE_API_URL=http://localhost:8000 .
docker run -p 5173:80 bcwat-client:init
```
## Running Tests
### End-to-End Tests
navigate to /client directory
use `npm run dev` to launch the frontend
use `npx cypress run` in a separate terminal to begin the end-to-end test run.

### Component Tests
navigate to /client directory
use `npx cypress run --component` in a separate terminal to begin the end-to-end test run.
component tests do not need the frontend application running to work. 

to specify a browser, run the npx command with the additional browser flag: `npx cypress run -b chrome`.
tests can also be run headed by using the cypress UI. use `npx cypress open` to initialize the testing UI. 

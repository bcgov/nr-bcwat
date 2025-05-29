# BC WAT Frontend

## How to Install and Run

navigate to /client
use `npm install` to install all dependencies
use `npm run dev` to launch the frontend

## Docker

```bash
docker build -t bcwat-frontend:init --build-arg VITE_BASE_API_URL=http://localhost:8000 .
docker run -p 5173:80 bcwat-frontend:init
```

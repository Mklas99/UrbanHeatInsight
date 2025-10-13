# UrbanHeatmap Starter Repository

## Overview

This is a full-stack starter for the UrbanHeatmap project, combining:

- React + Leaflet.js frontend
- FastAPI backend serving API and static frontend files
- MLflow tracking server with example logging
- VS Code DevContainer for consistent development environment
- Docker Compose for orchestration of backend, MLflow, and frontend (optional)

---

## Getting Started

### Prerequisites

- Docker & Docker Compose installed
- VS Code with Remote - Containers extension (optional but recommended)
- Node.js and npm (if not using DevContainer)
- Python 3.11+ (if not using DevContainer)

### Development with DevContainer (Recommended)

1. Open this project folder in VS Code.
2. When prompted, reopen in the DevContainer.
3. The container will build, installing dependencies for frontend and backend.
4. Open a terminal inside VS Code.
5. Run the backend FastAPI server:
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```
6. Run the frontend React app:
   ```bash
   npm start --prefix frontend
   ```
7. Access:
   - Frontend at [http://localhost:3000](http://localhost:3000)
   - Backend API at [http://localhost:8000/api/heatmap](http://localhost:8000/api/heatmap)
   - MLflow UI at [http://localhost:5000](http://localhost:5000) (if started with Docker Compose)

### Using Docker Compose

1. Run:
   ```bash
   docker-compose up --build
   ```
2. This starts backend and MLflow server.
3. Access:
   - Backend API: [http://localhost:8000/api/heatmap](http://localhost:8000/api/heatmap)
   - MLflow UI: [http://localhost:5000](http://localhost:5000)

_Note: Frontend dev server is not included by default in Compose; run it manually or build static files and serve via backend._

### Logging Dummy Data to MLflow

Run the example script to log sample experiment data:

```bash
python ml/log_dummy.py
```

### Project Structure

- `frontend/`: React + Leaflet frontend
- `backend/`: FastAPI backend app
- `ml/`: Example MLflow experiment scripts
- `.devcontainer/`: VS Code DevContainer configs
- `docker-compose.yml`: Compose config for backend and MLflow
- `README.md`, `.gitignore`: Project docs and ignore config

---

## Notes

- The backend serves static frontend files from `frontend/build` (run `npm run build` to create).
- Logging is configured for JSON structured logs.

---

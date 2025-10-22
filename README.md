# UrbanHeatInsight Prototype

## Overview

This is a full-stack prototype `UrbanHeatmap project`. It combines:

- `React + Leaflet.js frontend` that displays maps and the analysis. It also allows the user to view and edit the used data.
- `FastAPI backend` serving API and data management as well as data processing
- `MinIO` used as S3 compatable storage for the raw and processed data.
- `MLflow` tracking server with example logging
- DevContainer for consistent development environment
- Docker Compose for orchestration of backend, MLflow, and frontend (optional)

_Note: For mor Details refere to the services own Readme.md [Frontend](frontend/README.md), [Backend](backend/README.md)_
---

## Getting Started

### Prerequisites

- Docker & Docker Compose installed
- Node.js and npm (if not using DevContainer)
- Python 3.11+ (if not using DevContainer)

### Development with DevContainer (Recommended)
. Start dev container
. Starting Services:
   . In VS Code the [launch.json configuration](./.vscode/launch.json) file provides easy `one-click start` for each service.
   . Run the backend FastAPI server:
      ```bash
      uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
      ```
   . Run the frontend React app:
      ```bash
      cd frontend
      npm run dev
      ```
      Or use the NPM SCRIPTS in [package.json](./frontend/package.json)

. Access:
   - Frontend at [http://localhost:3000](http://localhost:3000)
   - Backend API at [http://localhost:8000/swagger](http://localhost:8000/swagger)
   - MLflow UI at [http://localhost:5000](http://localhost:5000) (if started with Docker Compose)
   - PgAdmin at [http://localhost:5050](http://localhost:5050) (if started with Docker Compose)

### Using Docker Compose

   ```bash
   docker-compose up --build
   ```

### Logging Dummy Data to MLflow

Run the example script to log sample experiment data:

```bash
python ml/log_dummy.py
```

### Project Structure
- `.devcontainer`: Configuration for the development container
- `frontend/`: React + Leaflet frontend
- `backend/`: FastAPI backend app
- `ml/`: Example MLflow experiment scripts
- `scripts`: trial scripts that may helpfull in the development process
- `docker-compose.yml`: Compose config for backend and MLflow
- `README.md`, `.env`, `.gitignore`: Project docs and ignore config

---

## Development Process

### Feature Branches

Direct commits to the masters are not permited and disabled.
Each branch must have a prefix depending on the implementation:
- `feature/`  ->     for new feature implementations
- `fix/`      ->     for fixes of defects
- 

### Commits

In this project every commit should follow the [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/#summary) convention.

### Pull Requests



---

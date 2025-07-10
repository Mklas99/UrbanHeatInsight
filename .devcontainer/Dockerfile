FROM python:3.11-slim-bullseye

# Set environment variables
ENV NODE_VERSION=18

# Install curl and nodejs
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@10.8.2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install MLflow and FastAPI dependencies
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn mlflow python-json-logger

# Set the working directory
WORKDIR /workspace
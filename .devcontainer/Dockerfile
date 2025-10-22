# Start with the base image
FROM python:3.11-slim-bookworm

# Set environment variables
ENV NODE_VERSION=18

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    g++ \
    make \
    gdal-bin \
    libgdal-dev \
    python3-dev \
    build-essential \
    wget \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@10.8.2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python GDAL bindings matching system GDAL version (Bookworm provides 3.6+)
RUN pip install GDAL==3.6

# Install pgAdmin4 via pip for standalone use
RUN pip install pgadmin4

# Set GDAL environment variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Upgrade pip and setuptools
RUN pip install --upgrade pip setuptools
# Install FastAPI and Uvicorn
RUN pip install --no-cache-dir fastapi "uvicorn[standard]"

# Set the working directory
WORKDIR /workspace

# Add pgAdmin repository and install pgAdmin4 (web version)
RUN curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | gpg --dearmor > /usr/share/keyrings/pgadmin-keyring.gpg \
    && sh -c 'echo "deb [signed-by=/usr/share/keyrings/pgadmin-keyring.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/bookworm pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list' \
    && apt-get update \
    && apt-get install -y pgadmin4-web \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
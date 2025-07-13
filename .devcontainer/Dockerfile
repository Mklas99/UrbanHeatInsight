# Start with the base image
FROM python:3.11-slim-bullseye

# Set environment variables
ENV NODE_VERSION=18

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    g++ \
    make \
    libgdal-dev \
    wget \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@10.8.2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh && \
    /opt/conda/bin/conda init bash

# Add Conda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Install GDAL using Conda
RUN conda install -c conda-forge gdal -y && conda clean -afy

# Set GDAL environment variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Upgrade pip and setuptools
RUN pip install --upgrade pip setuptools

# Set the working directory
WORKDIR /workspace
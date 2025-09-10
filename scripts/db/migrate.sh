#!/bin/bash

# Wait for the database to be ready
until pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}"; do
  echo "Waiting for database to be ready..."
  sleep 2
done

# Run the initialization SQL script
psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -f /scripts/db/init.sql

echo "Database migration completed."
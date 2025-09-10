#!/bin/bash

cat <<EOF > /pgadmin4/servers.json
{
  "Servers": {
    "1": {
      "Name": "Postgres Database",
      "Group": "Servers",
      "Host": "${POSTGRES_HOST}",
      "Port": ${POSTGRES_PORT},
      "Username": "${POSTGRES_USER}",
      "Password": "${POSTGRES_PASSWORD}",
      "SSLMode": "prefer",
      "MaintenanceDB": "postgres"
    }
  }
}
EOF
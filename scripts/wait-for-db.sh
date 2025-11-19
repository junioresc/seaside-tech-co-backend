#!/usr/bin/env sh
set -eu

HOST="${POSTGRES_HOST:-postgres}"
PORT="${POSTGRES_PORT:-5432}"

echo "Waiting for Postgres at ${HOST}:${PORT}..."
i=0
while [ "$i" -lt 60 ]; do
  if nc -z "${HOST}" "${PORT}" >/dev/null 2>&1; then
    echo "Postgres is up"
    exit 0
  fi
  i=$((i+1))
  sleep 1
done

echo "Timed out waiting for Postgres"
exit 1



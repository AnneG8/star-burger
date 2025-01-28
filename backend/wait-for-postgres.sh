#!/usr/bin/env bash

set -e

HOST=$(echo $1 | cut -d':' -f1)
PORT=$(echo $1 | cut -d':' -f2)
shift
CMD="$@"

until PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' &> /dev/null; do
  >&2 echo "$(date -u +"%Y-%m-%d %H:%M:%S:") PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "$(date -u +"%Y-%m-%d %H:%M:%S:") PostgreSQL is up - executing command"
exec sh -c "$CMD"

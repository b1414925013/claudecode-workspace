#!/bin/bash
set -e

# Wait for MySQL to be ready
if [ -n "$DB_HOST" ]; then
    echo "Waiting for MySQL at $DB_HOST:${DB_PORT:-3306}..."
    for i in $(seq 1 30); do
        if python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('$DB_HOST', ${DB_PORT:-3306})); s.close()" 2>/dev/null; then
            echo "MySQL is ready"
            break
        fi
        echo "Waiting... ($i/30)"
        sleep 2
    done
fi

# Initialize database
if [ "$SERVICE_NAME" = "api-gateway" ] || [ "$SERVICE_NAME" = "auth-service" ]; then
    echo "Running database init..."
    uv run python scripts/init_db.py || true
fi

exec "$@"

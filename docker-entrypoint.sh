#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Docker entrypoint: wait for MySQL → run migrations → start server
# ─────────────────────────────────────────────────────────────────────────────
set -e

echo "⏳ Waiting for MySQL to be ready at ${DB_HOST}:${DB_PORT}..."

until python - <<'EOF'
import pymysql, os, sys
try:
    conn = pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        connect_timeout=5,
    )
    conn.close()
    sys.exit(0)
except Exception as e:
    sys.exit(1)
EOF
do
    echo "  MySQL not ready — retrying in 3s..."
    sleep 3
done

echo "✅ MySQL is ready."

echo "⏳ Running Alembic migrations..."
alembic upgrade head
echo "✅ Migrations complete."

# Start the server based on environment
if [ "${APP_ENV}" = "production" ]; then
    echo "🚀 Starting production server (uvicorn, 4 workers)..."
    exec uvicorn main:app \
        --host "${HOST:-0.0.0.0}" \
        --port "${PORT:-8000}" \
        --workers 4 \
        --no-access-log
else
    echo "🚀 Starting development server (uvicorn, hot-reload enabled)..."
    exec uvicorn main:app \
        --host "${HOST:-0.0.0.0}" \
        --port "${PORT:-8000}" \
        --reload
fi

#!/usr/bin/env bash
# Run everything for the project on Linux/macOS:
# - Ensure Redis via Docker
# - Export env vars
# - Start FastAPI (uvicorn)
# - Open dashboard (best-effort)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DASHBOARD="$PROJECT_ROOT/dashboard/index.html"

# 1) Ensure Docker/Redis
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required but not installed. Aborting." >&2
  exit 1
fi

CONTAINER_NAME="pm_redis"
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "Starting new Redis container '${CONTAINER_NAME}' on port 6379..."
  docker run -d --name "${CONTAINER_NAME}" -p 6379:6379 redis:7 >/dev/null
elif ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "Starting existing Redis container '${CONTAINER_NAME}'..."
  docker start "${CONTAINER_NAME}" >/dev/null
else
  echo "Redis container '${CONTAINER_NAME}' is already running."
fi

# 2) Env vars
export STREAM_BACKEND=REDIS
export REDIS_URL="redis://localhost:6379/0"
: "${REDIS_STREAM_KEY:=ops_stream}"

# 3) Start API
( cd "$PROJECT_ROOT" && python -m uvicorn application.main:app --reload ) &

# 4) Open dashboard
if [ -f "$DASHBOARD" ]; then
  if command -v xdg-open >/dev/null 2>&1; then xdg-open "$DASHBOARD" &
  elif command -v open >/dev/null 2>&1; then open "$DASHBOARD" &
  else echo "Please open $DASHBOARD in your browser."
  fi
else
  echo "Dashboard not found at $DASHBOARD"
fi

wait

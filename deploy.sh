#!/usr/bin/env bash
# =============================================================================
# deploy.sh
#
# Deploy averias (glosario de averías) con Docker.
# Gestiona dos contenedores: averias-db (MariaDB) y averias (app web).
# =============================================================================
set -euo pipefail

# --------------- defaults ---------------
DEFAULT_CONTAINER_NAME="averias"
DEFAULT_DB_CONTAINER_NAME="averias-db"
DEFAULT_NETWORK_NAME="averias-net"
DEFAULT_WAIT_MAX_ATTEMPTS=15
DEFAULT_WAIT_DELAY=2
DEFAULT_IMAGE_TAG="ghcr.io/psotsan/averias:latest"
DEFAULT_HOST_PORT=8001
DEFAULT_ENV_FILE="$HOME/.env"
DEFAULT_DB_IMAGE="mariadb:11.4"

CONTAINER_NAME="$DEFAULT_CONTAINER_NAME"
DB_CONTAINER_NAME="$DEFAULT_DB_CONTAINER_NAME"
NETWORK_NAME="$DEFAULT_NETWORK_NAME"
WAIT_MAX_ATTEMPTS="$DEFAULT_WAIT_MAX_ATTEMPTS"
WAIT_DELAY="$DEFAULT_WAIT_DELAY"
IMAGE_TAG="$DEFAULT_IMAGE_TAG"
HOST_PORT="$DEFAULT_HOST_PORT"
ENV_FILE="$DEFAULT_ENV_FILE"
DB_IMAGE="$DEFAULT_DB_IMAGE"
SKIP_MIGRATIONS=false
SKIP_COLLECTSTATIC=false

# --------------- usage ---------------
usage() {
  cat <<EOF
Usage: $(basename "$0") [options]

Options:
  --container-name NAME     App container name (default: $DEFAULT_CONTAINER_NAME)
  --db-container-name NAME  DB container name (default: $DEFAULT_DB_CONTAINER_NAME)
  --network-name NAME       Docker network name (default: $DEFAULT_NETWORK_NAME)
  --wait-max-attempts N     Max attempts waiting (default: $DEFAULT_WAIT_MAX_ATTEMPTS)
  --wait-delay SEC          Seconds between attempts (default: $DEFAULT_WAIT_DELAY)
  --tag TAG                 App image tag (default: $DEFAULT_IMAGE_TAG)
  --port PORT               Host port mapping (default: $DEFAULT_HOST_PORT)
  --env-file PATH           Path to .env file (default: $DEFAULT_ENV_FILE)
  --skip-migrations         Skip Django migrations
  --skip-collectstatic      Skip Django collectstatic
  -h, --help                Show this help and exit
EOF
  exit 0
}

# --------------- parse args ---------------
parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --container-name)     CONTAINER_NAME="$2";     shift 2 ;;
      --db-container-name)  DB_CONTAINER_NAME="$2";  shift 2 ;;
      --network-name)       NETWORK_NAME="$2";        shift 2 ;;
      --wait-max-attempts)  WAIT_MAX_ATTEMPTS="$2";  shift 2 ;;
      --wait-delay)         WAIT_DELAY="$2";         shift 2 ;;
      --tag)                IMAGE_TAG="$2";           shift 2 ;;
      --port)               HOST_PORT="$2";           shift 2 ;;
      --env-file)           ENV_FILE="$2";            shift 2 ;;
      --skip-migrations)    SKIP_MIGRATIONS=true;    shift   ;;
      --skip-collectstatic) SKIP_COLLECTSTATIC=true; shift   ;;
      -h|--help)            usage                             ;;
      *) echo "[ERROR] Unknown option: $1"; usage            ;;
    esac
  done
}

# --------------- error handling ---------------
handle_error() {
  local exit_code=$?
  local line_no=$1
  echo "[ERROR] deploy.sh - line ${line_no}:"
  echo "       command ended with code ${exit_code}"
  exit "${exit_code}"
}
trap 'handle_error $LINENO' ERR

# --------------- helpers --------------------
read_env_value() {
  local key="$1"
  grep "^${key}=" "$ENV_FILE" | cut -d'=' -f2- | xargs | tr -d "'"
}

# --------------- preflight ---------------
preflight() {
  if [ ! -f "$ENV_FILE" ]; then
    echo "[ERROR] ${ENV_FILE} not found."
    echo "       Run setup-env.sh first to generate it."
    exit 1
  fi

  if ! command -v docker &> /dev/null; then
    echo "[ERROR] docker not found."
    exit 1
  fi
}

# --------------- wait helpers ---------------
wait_for_mariadb() {
  echo "[..] Waiting for MariaDB container '${DB_CONTAINER_NAME}' to be ready..."
  for i in $(seq 1 "${WAIT_MAX_ATTEMPTS}"); do
    if docker exec "${DB_CONTAINER_NAME}" mariadb-admin ping --silent 2>/dev/null; then
      echo "[OK] MariaDB ready."
      return 0
    fi
    if [ "$i" -eq "${WAIT_MAX_ATTEMPTS}" ]; then
      echo "[ERROR] MariaDB not ready after ${WAIT_MAX_ATTEMPTS} attempts."
      docker logs "${DB_CONTAINER_NAME}" --tail 20
      return 1
    fi
    sleep "${WAIT_DELAY}"
  done
}

wait_for_django() {
  local name="$1"
  echo "[..] Waiting for container '${name}' to be ready..."
  for i in $(seq 1 "${WAIT_MAX_ATTEMPTS}"); do
    if docker exec "${name}" python -c \
         "import django; django.setup(); print('ok')" 2>/dev/null; then
      echo "[OK] Container '${name}' ready."
      return 0
    fi
    if [ "$i" -eq "${WAIT_MAX_ATTEMPTS}" ]; then
      echo "[ERROR] Container '${name}' not ready after" \
           "${WAIT_MAX_ATTEMPTS} attempts."
      docker logs "${name}" --tail 20
      return 1
    fi
    sleep "${WAIT_DELAY}"
  done
}

# --------------- docker network ---------------
ensure_network() {
  if ! docker network inspect "$NETWORK_NAME" &>/dev/null; then
    echo "[..] Creating Docker network '${NETWORK_NAME}'..."
    docker network create "$NETWORK_NAME"
    echo "[OK] Network created."
  else
    echo "[OK] Network '${NETWORK_NAME}' already exists."
  fi
}

# --------------- MariaDB container ---------------
deploy_database() {
  local db_name db_user db_password db_root_password

  db_name=$(read_env_value "DB_NAME")
  db_user=$(read_env_value "DB_USER")
  db_password=$(read_env_value "DB_PASSWORD")
  db_root_password=$(read_env_value "DB_ROOT_PASSWORD" || true)
  [ -z "$db_root_password" ] && db_root_password="$db_password"

  echo "[..] Stopping existing DB container '${DB_CONTAINER_NAME}'..."
  docker stop "$DB_CONTAINER_NAME" 2>/dev/null || true
  docker rm "$DB_CONTAINER_NAME" 2>/dev/null || true

  echo "[..] Starting MariaDB container '${DB_CONTAINER_NAME}'..."
  docker run -d \
    --name "$DB_CONTAINER_NAME" \
    --network "$NETWORK_NAME" \
    --restart unless-stopped \
    -e MARIADB_ROOT_PASSWORD="$db_root_password" \
    -e MARIADB_DATABASE="$db_name" \
    -e MARIADB_USER="$db_user" \
    -e MARIADB_PASSWORD="$db_password" \
    -v "${DB_CONTAINER_NAME}-data:/var/lib/mysql" \
    "$DB_IMAGE"

  echo "[OK] MariaDB container started."
  wait_for_mariadb
}

# --------------- app container ---------------
deploy_app() {
  echo "[..] Pulling image ${IMAGE_TAG}..."
  docker pull "$IMAGE_TAG"

  echo "[..] Stopping existing container '${CONTAINER_NAME}'..."
  docker stop "$CONTAINER_NAME" 2>/dev/null || true
  docker rm "$CONTAINER_NAME" 2>/dev/null || true

  echo "[..] Starting app container '${CONTAINER_NAME}'..."
  docker run -d \
    --name "$CONTAINER_NAME" \
    --network "$NETWORK_NAME" \
    -p "${HOST_PORT}:8001" \
    --restart unless-stopped \
    --env-file "$ENV_FILE" \
    "$IMAGE_TAG"

  echo "[OK] App container started."
  wait_for_django "$CONTAINER_NAME"
}

# --------------- django management commands ---------------
django_migrate() {
  echo "[..] Running migrations..."
  docker exec "$CONTAINER_NAME" python manage.py migrate --noinput
}

django_createsuperuser() {
  echo "[..] Creating superuser..."
  docker exec \
    --env-file "$ENV_FILE" \
    "$CONTAINER_NAME" python manage.py createsuperuser --noinput \
    || echo "[WARN] Superuser already exists (or creation failed)"
}

django_collectstatic() {
  echo "[..] Collecting static files..."
  docker exec "$CONTAINER_NAME" python manage.py collectstatic --noinput
}

# --------------- smoke test ---------------
smoke_test() {
  echo "[..] Running smoke test..."
  curl -I "http://localhost:${HOST_PORT}"
  echo "[OK] Smoke test completed."
}

# ------------------ main ------------------
main() {
  parse_args "$@"

  echo "============================================="
  echo " deploy.sh — averias"
  echo " Glosario de averías — deploy con Docker"
  echo "============================================="

  preflight
  ensure_network
  deploy_database
  deploy_app

  if [ "$SKIP_MIGRATIONS" = false ]; then
    django_migrate
  fi

  django_createsuperuser

  if [ "$SKIP_COLLECTSTATIC" = false ]; then
    django_collectstatic
  fi

  smoke_test

  echo ""
  echo "============================================="
  echo " Deploy complete!"
  echo "============================================="
}

main "$@"

#!/usr/bin/env bash
# =============================================================================
# setup-env.sh
#
# Genera/actualiza interactivamente ~/.averias.env para averias.
# Ejecutar una vez al provisionar la instancia o al cambiar variables.
# =============================================================================
set -euo pipefail

# --------------- defaults ---------------
DEFAULT_ENV_FILE="$HOME/.averias.env"
ENV_FILE="$DEFAULT_ENV_FILE"

# --------------- usage ---------------
usage() {
  cat <<EOF
Usage: $(basename "$0") [--env-file PATH]

Options:
  --env-file PATH    Path to .env file (default: $DEFAULT_ENV_FILE)
  -h, --help         Show this help and exit
EOF
  exit 0
}

# --------------- parse args ---------------
parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --env-file)  ENV_FILE="$2";  shift 2 ;;
      -h|--help)   usage                    ;;
      *) echo "[ERROR] Unknown option: $1"; usage ;;
    esac
  done
}

# --------------- error handling ---------------
handle_error() {
  local exit_code=$?
  local line_no=$1
  echo "[ERROR] setup-env.sh - line ${line_no}:"
  echo "       command ended with code ${exit_code}"
  exit "${exit_code}"
}
trap 'handle_error $LINENO' ERR

# --------------- generate secret key ---------------
generate_secret_key() {
  python3 -c "
import secrets, string
chars = string.ascii_letters + string.digits + string.punctuation
print(''.join(secrets.choice(chars) for _ in range(50)))
"
}

# --------------- prompt helpers ---------------
prompt_required() {
  local var="$1"
  local val
  while true; do
    read -r -p "  ${var}: " val
    [ -n "$val" ] && break
    echo "  [WARN] cannot be empty"
  done
  printf "%s" "$val"
}

prompt_optional() {
  local var="$1"
  local default="$2"
  local val
  read -r -p "  ${var} [${default}]: " val
  printf "%s" "${val:-$default}"
}

prompt_password() {
  local var="$1"
  local val
  read -r -s -p "  ${var}: " val
  echo "" >&2      # ← stderr, no stdout
  printf "%s" "$val"
}

prompt_password_optional() {
  local var="$1"
  local val
  read -r -s -p "  ${var}: " val
  echo "" >&2      # ← idem
  printf "%s" "$val"
}

# --------------- write .env ---------------
write_env() {
  # Desactivar history expansion para que caracteres como ! no se expandan
  set +H

  local env_content=""

  echo ""
  echo "--- Django ---"

  local secret_key
  secret_key=$(generate_secret_key)
  env_content="${env_content}SECRET_KEY="
  env_content="${env_content}$(printf '%s' "${secret_key}")"$'\n'

  local allowed_hosts
  allowed_hosts=$(prompt_required "ALLOWED_HOSTS")
  env_content="${env_content}ALLOWED_HOSTS=${allowed_hosts}"$'\n'

  local debug
  debug=$(prompt_optional "DEBUG" "False")
  env_content="${env_content}DEBUG=${debug}"$'\n'

  local csrf
  csrf=$(prompt_required "CSRF_TRUSTED_ORIGINS")
  env_content="${env_content}CSRF_TRUSTED_ORIGINS=${csrf}"$'\n'

  echo ""
  echo "--- Base de datos (MariaDB/MySQL) ---"

  local db_name
  db_name=$(prompt_required "DB_NAME")
  env_content="${env_content}DB_NAME=${db_name}"$'\n'

  local db_user
  db_user=$(prompt_required "DB_USER")
  env_content="${env_content}DB_USER=${db_user}"$'\n'

  local db_password
  while true; do
    db_password=$(prompt_password "DB_PASSWORD")
    [ -n "$db_password" ] && break
    echo "  [WARN] cannot be empty"
  done
  env_content="${env_content}DB_PASSWORD="
  env_content="${env_content}$(printf '%s' "${db_password}")"$'\n'

  local db_host
  db_host=$(prompt_optional "DB_HOST" "localhost")
  env_content="${env_content}DB_HOST=${db_host}"$'\n'

  local db_port
  db_port=$(prompt_optional "DB_PORT" "3306")
  env_content="${env_content}DB_PORT=${db_port}"$'\n'

  local db_root_password
  db_root_password=$(prompt_password_optional "DB_ROOT_PASSWORD (dejar vacío para usar DB_PASSWORD)")
  if [ -n "$db_root_password" ]; then
    env_content="${env_content}DB_ROOT_PASSWORD="
    env_content="${env_content}$(printf '%s' "${db_root_password}")"$'\n'
  fi

  echo ""
  echo "--- AWS S3 (estáticos) ---"

  local use_s3
  use_s3=$(prompt_optional "USE_S3" "True")
  env_content="${env_content}USE_S3=${use_s3}"$'\n'

  if [ "$use_s3" = "True" ]; then
    local use_iam_role
    read -r -p "  ¿Usar IAM Role de EC2? [y/N]: " use_iam_role

    if [[ "$use_iam_role" =~ ^[yY]([eE][sS])?$ ]]; then
      echo "  [OK] Usando IAM Role — no se requieren AWS_ACCESS_KEY_ID ni AWS_SECRET_ACCESS_KEY"
    else
      local aws_key
      aws_key=$(prompt_required "AWS_ACCESS_KEY_ID")
      env_content="${env_content}AWS_ACCESS_KEY_ID=${aws_key}"$'\n'

      local aws_secret
      while true; do
        aws_secret=$(prompt_password "AWS_SECRET_ACCESS_KEY")
        [ -n "$aws_secret" ] && break
        echo "  [WARN] cannot be empty"
      done
      env_content="${env_content}AWS_SECRET_ACCESS_KEY="
      env_content="${env_content}$(printf '%s' "${aws_secret}")"$'\n'
    fi

    local bucket
    bucket=$(prompt_required "AWS_STORAGE_BUCKET_NAME")
    env_content="${env_content}AWS_STORAGE_BUCKET_NAME=${bucket}"$'\n'

    local region
    region=$(prompt_optional "AWS_S3_REGION_NAME" "eu-west-1")
    env_content="${env_content}AWS_S3_REGION_NAME=${region}"$'\n'

    local custom_domain
    default_domain="${bucket}.s3.${region}.amazonaws.com"
    custom_domain=$(prompt_optional "AWS_S3_CUSTOM_DOMAIN" "${default_domain}")
    env_content="${env_content}AWS_S3_CUSTOM_DOMAIN=${custom_domain}"$'\n'
  fi

  echo ""
  echo "--- Seguridad SSL/TLS ---"

  local hsts
  hsts=$(prompt_optional "SECURE_HSTS_SECONDS" "31536000")
  env_content="${env_content}SECURE_HSTS_SECONDS=${hsts}"$'\n'

  local ssl_redirect
  ssl_redirect=$(prompt_optional "SECURE_SSL_REDIRECT" "True")
  env_content="${env_content}SECURE_SSL_REDIRECT=${ssl_redirect}"$'\n'

  local session_secure
  session_secure=$(prompt_optional "SESSION_COOKIE_SECURE" "True")
  env_content="${env_content}SESSION_COOKIE_SECURE=${session_secure}"$'\n'

  local csrf_secure
  csrf_secure=$(prompt_optional "CSRF_COOKIE_SECURE" "True")
  env_content="${env_content}CSRF_COOKIE_SECURE=${csrf_secure}"$'\n'

  printf "%s" "$env_content" > "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  echo ""
  echo "[OK] .env created at: ${ENV_FILE}"

  # Restaurar history expansion (por si acaso)
  set -H 2>/dev/null || true
}

# ------------------ main ------------------
main() {
  parse_args "$@"

  echo "============================================="
  echo " setup-env.sh"
  echo " Generate interactive .env for fault_knowledge_base"
  echo "============================================="

  if [ -f "$ENV_FILE" ]; then
    echo ""
    echo "  [WARN] ${ENV_FILE} already exists."
    read -r -p "  Overwrite? [y/N] " reply
    case "$reply" in
      [yY]|[yY][eE][sS]) ;;
      *) echo "  Aborted."; exit 0 ;;
    esac
  fi

  write_env
}

main "$@"

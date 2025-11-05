#!/usr/bin/env bash

# Deploy updated application code on the self-hosted runner.
# Expected to be executed by GitHub Actions (or manually) on the runner VM.

set -Eeuo pipefail

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*"
}

APP_USER="${DEPLOY_USER:-$(id -un)}"
APP_DIR="${DEPLOY_APP_DIR:-${HOME}/pbl-app-2025}"
VENV_DIR="${DEPLOY_VENV_DIR:-${APP_DIR}/.venv}"
PYTHON_BIN="${DEPLOY_PYTHON_BIN:-${VENV_DIR}/bin/python}"
PID_FILE="${DEPLOY_PID_FILE:-/run/django-dev.pid}"
TARGET_BRANCH="${DEPLOY_BRANCH:-${GITHUB_REF_NAME:-main}}"
LOG_FILE="${DEPLOY_LOG_FILE:-${HOME}/pbl-app-2025-deploy.log}"
DJANGO_SETTINGS_MODULE="${DEPLOY_DJANGO_SETTINGS_MODULE:-pbl_project.settings}"

mkdir -p "$(dirname "${LOG_FILE}")"
touch "${LOG_FILE}"
exec > >(tee -a "${LOG_FILE}") 2>&1

log "Starting deployment"
log "Running as user ${APP_USER}"
log "Using APP_DIR=${APP_DIR} (branch ${TARGET_BRANCH})"

export DJANGO_SETTINGS_MODULE
export PYTHONPATH="${APP_DIR}:${PYTHONPATH:-}"

if [[ ! -d "${APP_DIR}/.git" ]]; then
  log "ERROR: ${APP_DIR} does not look like a git repository."
  exit 1
fi

if [[ ! -x "${PYTHON_BIN}" ]]; then
  log "ERROR: Python interpreter not found at ${PYTHON_BIN}."
  exit 1
fi

if command -v sudo >/dev/null 2>&1; then
  SUDO="sudo"
else
  SUDO=""
fi

log "Stopping existing Django process if running"
if ${SUDO} start-stop-daemon --stop --pidfile "${PID_FILE}" --retry=TERM/5/KILL/2; then
  log "Existing process stopped"
else
  log "No running process found (or stop not required)"
fi

log "Fetching latest code"
git -C "${APP_DIR}" fetch --prune origin "${TARGET_BRANCH}"
if ! git -C "${APP_DIR}" checkout "${TARGET_BRANCH}" 2>/dev/null; then
  git -C "${APP_DIR}" checkout -b "${TARGET_BRANCH}" "origin/${TARGET_BRANCH}"
fi
git -C "${APP_DIR}" reset --hard "origin/${TARGET_BRANCH}"
git -C "${APP_DIR}" clean -df

log "Synchronizing dependencies with uv (if available)"
if command -v uv >/dev/null 2>&1; then
  (cd "${APP_DIR}" && uv sync)
else
  log "uv not installed; skipping dependency sync"
fi

if [[ -n "${DEPLOY_DATABASES:-}" ]]; then
  read -r -a MIGRATION_DATABASES <<< "${DEPLOY_DATABASES}"
else
  log "Detecting database aliases from Django settings"
  mapfile -t MIGRATION_DATABASES < <("${PYTHON_BIN}" - <<'PY'
import django
django.setup()
from django.conf import settings
for alias in settings.DATABASES.keys():
    print(alias)
PY
)
fi

if [[ ${#MIGRATION_DATABASES[@]} -eq 0 ]]; then
  log "ERROR: No database aliases detected; aborting migrations"
  exit 1
fi

log "Applying database migrations"
log "Databases: ${MIGRATION_DATABASES[*]}"
for db in "${MIGRATION_DATABASES[@]}"; do
  if [[ -z "${db}" ]]; then
    continue
  fi
  log "Applying database migrations for database=${db}"
  "${PYTHON_BIN}" "${APP_DIR}/manage.py" migrate --database "${db}" --noinput
done

log "Starting Django application"
${SUDO} start-stop-daemon \
  --start \
  --quiet \
  --background \
  --make-pidfile \
  --pidfile "${PID_FILE}" \
  --chdir "${APP_DIR}" \
  --exec "${PYTHON_BIN}" -- \
  "${APP_DIR}/manage.py" runserver 0.0.0.0:80 --noreload

log "Deployment finished successfully"

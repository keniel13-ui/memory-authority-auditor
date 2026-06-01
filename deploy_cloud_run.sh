#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-memory-authority-auditor}"
ENV_VARS="${ENV_VARS:-}"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "PROJECT_ID is not set and no active gcloud project was found." >&2
  exit 1
fi

if [[ -n "${ENV_VARS}" ]]; then
  gcloud run deploy "${SERVICE_NAME}" \
    --project "${PROJECT_ID}" \
    --region "${REGION}" \
    --source . \
    --allow-unauthenticated \
    --set-env-vars "${ENV_VARS}"
else
  gcloud run deploy "${SERVICE_NAME}" \
    --project "${PROJECT_ID}" \
    --region "${REGION}" \
    --source . \
    --allow-unauthenticated
fi

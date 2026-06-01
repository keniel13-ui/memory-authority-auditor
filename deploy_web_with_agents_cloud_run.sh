#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-memory-authority-auditor-web}"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "PROJECT_ID is not set and no active gcloud project was found." >&2
  exit 1
fi

service_url() {
  gcloud run services describe "$1" \
    --project "${PROJECT_ID}" \
    --region "${REGION}" \
    --format='value(status.url)'
}

MEMORY_EXTRACTOR_URL="${MEMORY_EXTRACTOR_URL:-$(service_url memory-extractor-agent)}"
AUTHORITY_CLASSIFIER_URL="${AUTHORITY_CLASSIFIER_URL:-$(service_url authority-classifier-agent)}"
CONFLICT_DETECTOR_URL="${CONFLICT_DETECTOR_URL:-$(service_url conflict-detector-agent)}"
VERIFICATION_GATE_URL="${VERIFICATION_GATE_URL:-$(service_url verification-gate-agent)}"
AUTHORITY_MAPPER_URL="${AUTHORITY_MAPPER_URL:-$(service_url authority-mapper-agent)}"
REPORT_WRITER_URL="${REPORT_WRITER_URL:-$(service_url report-writer-agent)}"

ENV_VARS="USE_REMOTE_AGENTS=1"
ENV_VARS+=",MEMORY_EXTRACTOR_URL=${MEMORY_EXTRACTOR_URL}"
ENV_VARS+=",AUTHORITY_CLASSIFIER_URL=${AUTHORITY_CLASSIFIER_URL}"
ENV_VARS+=",CONFLICT_DETECTOR_URL=${CONFLICT_DETECTOR_URL}"
ENV_VARS+=",VERIFICATION_GATE_URL=${VERIFICATION_GATE_URL}"
ENV_VARS+=",AUTHORITY_MAPPER_URL=${AUTHORITY_MAPPER_URL}"
ENV_VARS+=",REPORT_WRITER_URL=${REPORT_WRITER_URL}"

gcloud run deploy "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --source . \
  --allow-unauthenticated \
  --set-env-vars "${ENV_VARS}"

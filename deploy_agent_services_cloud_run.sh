#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${REGION:-us-central1}"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "PROJECT_ID is not set and no active gcloud project was found." >&2
  exit 1
fi

deploy_agent() {
  local service_name="$1"
  local role="$2"

  gcloud run deploy "${service_name}" \
    --project "${PROJECT_ID}" \
    --region "${REGION}" \
    --source . \
    --allow-unauthenticated \
    --command python3 \
    --args agent_service.py \
    --set-env-vars "AGENT_ROLE=${role}"
}

deploy_agent "memory-extractor-agent" "memory_extractor"
deploy_agent "authority-classifier-agent" "authority_classifier"
deploy_agent "conflict-detector-agent" "conflict_detector"
deploy_agent "verification-gate-agent" "verification_gate"
deploy_agent "authority-mapper-agent" "authority_mapper"
deploy_agent "report-writer-agent" "report_writer"

echo
echo "Agent service URLs:"
for service in \
  memory-extractor-agent \
  authority-classifier-agent \
  conflict-detector-agent \
  verification-gate-agent \
  authority-mapper-agent \
  report-writer-agent
do
  url="$(gcloud run services describe "${service}" --project "${PROJECT_ID}" --region "${REGION}" --format='value(status.url)')"
  echo "${service}=${url}"
done

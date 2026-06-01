# Cloud Shell Deploy Runbook

Use this when deploying the AI Memory Authority Auditor from Google Cloud Shell.

Project:

```text
project-2f702c18-2e87-4bfe-847
```

Region:

```text
us-central1
```

## 1. Upload the Package

Upload `memory-authority-auditor.tar.gz` into Cloud Shell.

In Cloud Shell:

```bash
mkdir -p ~/memory-authority-auditor
tar -xzf ~/memory-authority-auditor.tar.gz -C ~/memory-authority-auditor --strip-components=1
cd ~/memory-authority-auditor
```

## 2. Confirm Project

```bash
gcloud config set project project-2f702c18-2e87-4bfe-847
gcloud config get-value project
```

Expected:

```text
project-2f702c18-2e87-4bfe-847
```

## 3. Confirm APIs

```bash
gcloud services list --enabled | grep -E "run.googleapis.com|cloudbuild.googleapis.com|artifactregistry.googleapis.com"
```

If any are missing:

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

## 4. Deploy Agent Services

This deploys six separate Cloud Run services:

```bash
bash deploy_agent_services_cloud_run.sh
```

Copy the printed service URLs.

## 5. Deploy Web App Wired to Agents

```bash
bash deploy_web_with_agents_cloud_run.sh
```

This deploys:

```text
memory-authority-auditor-web
```

with `USE_REMOTE_AGENTS=1` and the six agent URLs.

## 6. Test

Open the final Cloud Run URL.

Run the sample audit.

Confirm:

- Agent Trace shows six agents.
- Findings show stale/loose/conflict checks.
- Authority Map appears.
- Export Report downloads Markdown.

## 7. Cost Guard

After testing, check current Cloud Run services:

```bash
gcloud run services list --region us-central1
```

Cloud Run normally scales to zero, but keep the `$5` budget alert active.

If you want to clean up:

```bash
gcloud run services delete memory-authority-auditor-web --region us-central1
gcloud run services delete memory-extractor-agent --region us-central1
gcloud run services delete authority-classifier-agent --region us-central1
gcloud run services delete conflict-detector-agent --region us-central1
gcloud run services delete verification-gate-agent --region us-central1
gcloud run services delete authority-mapper-agent --region us-central1
gcloud run services delete report-writer-agent --region us-central1
```

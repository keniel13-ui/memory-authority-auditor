FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

COPY requirements.txt .
RUN if [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

COPY agents ./agents
COPY templates ./templates
COPY app.py agent_service.py audit_cli.py audit_pipeline.py item_proxy.py remote_pipeline.py ./
COPY samples ./samples

EXPOSE 8080

CMD ["python3", "app.py"]

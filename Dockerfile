# syntax=docker/dockerfile:1
FROM python:3.15.0-slim@sha256:f5b92f2a669a4c347044f29367f31983280b648250ca94dea66f98c53bc87e58

ARG VERSION=dev
ENV LOGWATCH_VERSION=${VERSION} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY requirements.txt .
# pip/setuptools/ensurepip aren't needed at runtime and carry most of the scanner findings.
RUN pip install --no-cache-dir -r requirements.txt \
    && pip uninstall -y pip setuptools \
    && python -c "import shutil, sysconfig; from pathlib import Path; shutil.rmtree(Path(sysconfig.get_path('stdlib')) / 'ensurepip', ignore_errors=True)"
COPY logwatch.py .

LABEL org.opencontainers.image.title="logwatcher" \
      org.opencontainers.image.description="Nightly Docker log analyzer with rule checks, bot detection and Claude-written HTML email reports" \
      org.opencontainers.image.source="https://github.com/dwightmulcahy/logwatcher" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${VERSION}"

# Runs as root: it needs the mounted /var/run/docker.sock to read container logs.
VOLUME ["/data"]
# The scheduler loop touches /data/heartbeat at least every HOME_IP_CHECK_MIN minutes.
HEALTHCHECK --interval=5m --timeout=15s --start-period=2m --retries=3 \
  CMD ["python", "/app/logwatch.py", "--healthcheck"]
CMD ["python", "/app/logwatch.py"]

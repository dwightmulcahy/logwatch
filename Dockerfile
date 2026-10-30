# syntax=docker/dockerfile:1
FROM python:3.14.9-slim@sha256:35caba83af2fe6da9a5d922f9b0156f21d1246a48278c58a08bd253303ba42e8

ARG VERSION=dev
ENV LOGWATCH_VERSION=${VERSION} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade "setuptools>=78.1.1" \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip check \
    && python -c 'from importlib.metadata import version; from packaging.version import Version; minimums = {"msgpack": "1.2.3", "urllib3": "2.8.0", "setuptools": "78.1.1"}; assert all(Version(version(name)) >= Version(minimum) for name, minimum in minimums.items()), {name: version(name) for name in minimums}'
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

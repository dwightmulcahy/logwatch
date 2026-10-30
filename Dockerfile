# syntax=docker/dockerfile:1
FROM python:3.15.0-slim@sha256:f5b92f2a669a4c347044f29367f31983280b648250ca94dea66f98c53bc87e58

ARG VERSION=dev
ENV LOGWATCH_VERSION=${VERSION} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade "setuptools>=78.1.1" "certifi>=2026.10.18" \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip check \
    && python -c 'from importlib.metadata import version; minimums = {"msgpack": (1, 2, 3), "urllib3": (2, 8, 0), "setuptools": (78, 1, 1), "certifi": (2026, 10, 18)}; actual = {name: tuple(map(int, version(name).split(".")[:3])) for name in minimums}; assert all(actual[name] >= minimum for name, minimum in minimums.items()), actual'
# Build tools are not needed at runtime. In particular, pip ships a third-party
# SPDX SBOM describing vendored libraries, which Trivy can otherwise mistake
# for the versions of independently installed runtime dependencies.
RUN python -m pip uninstall --yes setuptools pip \
    && python -c 'import importlib.util; assert importlib.util.find_spec("pip") is None; assert importlib.util.find_spec("setuptools") is None'

COPY logwatch.py .

# Remove stale package metadata left by the base image's Python installation.
RUN python - <<'PY'
from importlib.metadata import distributions
from pathlib import Path

minimums = {"msgpack": (1, 2, 3), "urllib3": (2, 8, 0), "setuptools": (78, 1, 1), "certifi": (2026, 10, 18)}
for dist in distributions():
    name = (dist.metadata.get("Name") or "").lower().replace("_", "-")
    if name not in minimums:
        continue
    parts = dist.version.split(".")[:3]
    try:
        version = tuple(map(int, parts))
    except ValueError:
        continue
    if version < minimums[name]:
        path = Path(str(dist._path))
        if path.is_dir() and path.name.endswith((".dist-info", ".egg-info")):
            import shutil
            shutil.rmtree(path)
PY

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

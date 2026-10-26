"""Scheduler liveness only; report/delivery failures remain visible in logs/email."""
import os
from pathlib import Path
import time

HEARTBEAT_FILE = os.getenv("HEARTBEAT_FILE", "/tmp/logwatch-heartbeat")


def healthy(path=HEARTBEAT_FILE, now=None, max_age=900):
    try:
        age = (time.time() if now is None else now) - Path(path).stat().st_mtime
        return 0 <= age <= max_age
    except OSError:
        return False


if __name__ == "__main__":
    raise SystemExit(0 if healthy() else 1)

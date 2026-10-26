import os
import time

import logwatch


def test_healthcheck_tracks_heartbeat_age(tmp_path, monkeypatch):
    beat = tmp_path / "heartbeat"
    monkeypatch.setattr(logwatch, "HEARTBEAT_FILE", str(beat))
    monkeypatch.setattr(logwatch, "HOME_IP_CHECK_MIN", 60)

    assert logwatch.healthcheck() == 1          # never written

    logwatch.heartbeat()
    assert beat.exists()
    assert logwatch.healthcheck() == 0

    stale = time.time() - (2 * 60 * 60 + 901)
    os.utime(beat, (stale, stale))
    assert logwatch.healthcheck() == 1


def test_heartbeat_never_raises(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(logwatch, "HEARTBEAT_FILE", str(tmp_path / "missing" / "heartbeat"))
    logwatch.heartbeat()
    assert "heartbeat failed" in capsys.readouterr().out

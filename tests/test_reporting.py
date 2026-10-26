import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import healthcheck
import logwatch
from scripts import release_notes


class ReportingTests(unittest.TestCase):
    def setUp(self):
        self.bot_patch = patch.object(logwatch, "BOTS", logwatch.BotDB({}, "test"))
        self.bot_patch.start()
        self.lan_patch = patch.object(logwatch, "AUTO_IGNORE_LAN", True)
        self.lan_patch.start()
        self.addCleanup(self.lan_patch.stop)
        self.addCleanup(self.bot_patch.stop)

    def request(self, **overrides):
        entry = dict(timestamp="2026-10-26T12:00:00+00:00", path="/", method="GET",
                               client="8.8.8.8", status_code=200, duration_ms=5,
                               user_agent="Mozilla/5.0")
        entry.update(overrides)
        return json.dumps(entry)

    def test_parser_preserves_errors_probes_and_ignores_own_traffic(self):
        entries = [self.request(), self.request(path="/.env", status_code=404),
                   self.request(client="192.168.27.50"), self.request(status_code=503),
                   "Traceback: failed", '{"level":"ERROR","message":"failed"}']
        summary, metrics, _ = logwatch.digest(entries)
        self.assertEqual(metrics["requests"], 3)
        self.assertEqual(metrics["errors_5xx"], 1)
        self.assertEqual(metrics["probes"], 1)
        self.assertEqual(metrics["non_json"], 2)
        self.assertEqual(summary["ignored_own_requests"], 1)

    def test_health_gaps_and_latency(self):
        entries = [self.request(path=logwatch.HEALTH_PATH, timestamp=f"2026-10-26T12:{minute}:00+00:00")
                   for minute in ("00", "01", "05")]
        summary, metrics, _ = logwatch.digest(entries)
        self.assertEqual(summary["health"]["healthy_checks"], 3)
        self.assertEqual(metrics["health_gaps"], 1)
        self.assertEqual(metrics["requests"], 0)

    def test_baseline_anomaly_is_flagged(self):
        summary, metrics, _ = logwatch.digest([self.request()])
        past = dict(metrics, requests=0)
        state = {"history": [{"metrics": past} for _ in range(logwatch.BASELINE_MIN_DAYS)]}
        metrics["requests"] = 100
        flags = logwatch.evaluate(summary, metrics, {"status": "running"}, state, 1)
        self.assertTrue(any(sev == "WARN" and "requests=100" in msg for sev, msg in flags))

    def test_claude_failure_sends_rules_and_saves_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            meta = {"status": "running", "started_at": None, "image": "test", "oom_killed": False}
            with patch.object(logwatch, "STATE_FILE", str(Path(tmp)/"state.json")), \
                 patch.object(logwatch, "MODE", "hybrid"), \
                 patch.object(logwatch, "load_bot_db", return_value=logwatch.BOTS), \
                 patch.object(logwatch, "refresh_home_ips"), \
                 patch.object(logwatch, "home_ips_for_window", return_value=set()), \
                 patch.object(logwatch, "collect", return_value=([self.request(status_code=503)], meta)), \
                 patch.object(logwatch, "claude_report", side_effect=RuntimeError("offline")), \
                 patch.object(logwatch, "send") as send:
                logwatch.run_once()
                self.assertIn("ATTENTION", send.call_args.args[0])
                self.assertIn("rule report follows", send.call_args.args[1])
                self.assertTrue(Path(logwatch.STATE_FILE).exists())

    def test_next_run_rolls_to_next_day(self):
        now = dt.datetime(2026, 10, 26, 23, 0, tzinfo=logwatch.TZ)
        with patch.object(logwatch.dt, "datetime") as clock, patch.object(logwatch, "RUN_AT", "06:00"):
            clock.now.return_value = now
            self.assertEqual(logwatch.next_run(), now.replace(hour=6) + dt.timedelta(days=1))

    def test_heartbeat_missing_stale_and_fresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"heartbeat"
            self.assertFalse(healthcheck.healthy(path))
            path.touch()
            stamp = path.stat().st_mtime
            self.assertTrue(healthcheck.healthy(path, now=stamp+60))
            self.assertFalse(healthcheck.healthy(path, now=stamp+901))

    def test_release_notes_group_changes_and_breaking_changes(self):
        with patch.object(release_notes, "tags", return_value=["v1.1.0", "v1.0.0"]), \
             patch.object(release_notes, "commits", return_value=[("fix: correct parser", ""), ("feat!: new schema", "")]):
            notes = release_notes.notes("v1.1.0")
        self.assertIn("Bug Fixes", notes)
        self.assertIn("**BREAKING:** New schema", notes)
        self.assertIn("v1.0.0...v1.1.0", notes)


if __name__ == "__main__":
    unittest.main()

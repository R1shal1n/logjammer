"""Unit tests for relative time template replacement."""

from datetime import datetime, timezone
import unittest
from logjammer.templates import (
    TimeTemplateService,
    replace_time_templates,
    replace_time_templates_in_logs,
)


class TimeTemplateTest(unittest.TestCase):

  def setUp(self):
    self.base_time = datetime(2026, 8, 24, 12, 0, 0, tzinfo=timezone.utc)
    self.service = TimeTemplateService(self.base_time)

  def test_iso_timestamp_subtraction(self):
    # 2 hours, 15 minutes before 12:00:00 -> 09:45:00
    raw_text = '{"event_time": "##$TimeStamp-0d2h15m0s$##"}'
    resolved = self.service.replace_templates(raw_text)
    self.assertIn("2026-08-24T09:45:00.000Z", resolved)

  def test_iso_timestamp_addition(self):
    # 1 day, 30 minutes after 12:00:00 -> 2026-08-25 12:30:00
    raw_text = "Timestamp: ##$TimeStamp+1d0h30m0s$##"
    resolved = self.service.replace_templates(raw_text)
    self.assertIn("2026-08-25T12:30:00.000Z", resolved)

  def test_epoch_replacement(self):
    raw_text = "event_epoch=##$Epoch-0d0h10m0s$##"
    resolved = self.service.replace_templates(raw_text)
    expected_epoch = int((self.base_time).timestamp()) - 600
    self.assertEqual(resolved, f"event_epoch={expected_epoch}")

  def test_syslog_time_replacement(self):
    raw_text = "##$SyslogTime-0d1h0m0s$## host1 sshd[1234]: Failed password"
    resolved = self.service.replace_templates(raw_text)
    self.assertTrue(resolved.startswith("Aug 24 11:00:00"))

  def test_nested_structure_replacement(self):
    log_dict = {
        "user": "alice",
        "events": [
            {"time": "##$TimeStamp-0d0h5m0s$##", "action": "login"},
            {"time": "##$TimeStamp-0d0h1m0s$##", "action": "escalate"},
        ],
    }
    resolved = replace_time_templates_in_logs(log_dict, self.base_time)
    self.assertIn("2026-08-24T11:55:00", resolved["events"][0]["time"])
    self.assertIn("2026-08-24T11:59:00", resolved["events"][1]["time"])


if __name__ == "__main__":
  unittest.main()

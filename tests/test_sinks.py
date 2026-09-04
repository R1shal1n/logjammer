"""Unit tests for output sinks."""

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from logjammer.models import GeneratedScenario, LogEntry, LogFormat
from logjammer.sinks.file import FileSink
from logjammer.sinks.secops import SecOpsSink
from logjammer.sinks.syslog import SyslogSink
from logjammer.sinks.webhook import WebhookSink


class SinksTest(unittest.TestCase):

  def setUp(self):
    self.temp_dir = tempfile.TemporaryDirectory()
    self.scenario = GeneratedScenario(
        title="Test Attack",
        description="A test scenario",
        logs={
            "CS_EDR": [
                LogEntry(
                    log_type="CS_EDR",
                    content='{"event_simpleName": "ProcessRollup2", "CommandLine": "powershell.exe -enc ..."}',
                    format=LogFormat.JSON,
                    timestamp=datetime.now(timezone.utc),
                ),
                LogEntry(
                    log_type="CS_EDR",
                    content='{"event_simpleName": "SyntheticProcessDoc", "FileName": "mimikatz.exe"}',
                    format=LogFormat.JSON,
                    timestamp=datetime.now(timezone.utc),
                ),
            ]
        },
    )

  def tearDown(self):
    self.temp_dir.cleanup()

  def test_file_sink_jsonl(self):
    out_file = Path(self.temp_dir.name) / "output.jsonl"
    sink = FileSink(output_path=out_file)
    count = sink.emit(self.scenario)

    self.assertEqual(count, 2)
    self.assertTrue(out_file.exists())
    with open(out_file, "r", encoding="utf-8") as f:
      lines = [json.loads(line) for line in f if line.strip()]
    self.assertEqual(len(lines), 2)
    self.assertEqual(lines[0]["log_type"], "CS_EDR")

  def test_file_sink_raw(self):
    out_file = Path(self.temp_dir.name) / "output.log"
    sink = FileSink(output_path=out_file)
    count = sink.emit(self.scenario)

    self.assertEqual(count, 2)
    with open(out_file, "r", encoding="utf-8") as f:
      content = f.read()
    self.assertIn("powershell.exe", content)

  @mock.patch("socket.socket")
  def test_syslog_sink(self, mock_socket_cls):
    mock_sock = mock.MagicMock()
    mock_socket_cls.return_value = mock_sock

    sink = SyslogSink(host="127.0.0.1", port=514, protocol="udp")
    count = sink.emit(self.scenario)

    self.assertEqual(count, 2)
    self.assertEqual(mock_sock.sendto.call_count, 2)

  @mock.patch("urllib.request.urlopen")
  def test_webhook_sink(self, mock_urlopen):
    mock_resp = mock.MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    sink = WebhookSink(url="https://siem-collector.corp.internal/hec")
    count = sink.emit(self.scenario)

    self.assertEqual(count, 2)
    self.assertTrue(mock_urlopen.called)

  @mock.patch("urllib.request.urlopen")
  def test_secops_sink_raw_logs(self, mock_urlopen):
    mock_resp = mock.MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    sink = SecOpsSink(
        customer_id="12345678-abcd-ef01-2345-6789abcdef01",
        project_number="288909297183",
        region="us",
        tag="test-tag-01",
    )
    with mock.patch.object(sink, "_get_auth_token", return_value="fake-token"):
      count = sink.emit(self.scenario)

    self.assertEqual(count, 2)
    self.assertTrue(mock_urlopen.called)

    # Check request URL and payload structure
    call_args = mock_urlopen.call_args
    req_obj = call_args[0][0]
    self.assertIn("https://us-chronicle.googleapis.com/v1alpha/projects/288909297183/locations/us/instances/12345678-abcd-ef01-2345-6789abcdef01/logTypes/CS_EDR/logs:import", req_obj.full_url)
    self.assertEqual(req_obj.headers["Authorization"], "Bearer fake-token")

    payload = json.loads(req_obj.data.decode("utf-8"))
    self.assertIn("inline_source", payload)
    logs = payload["inline_source"]["logs"]
    self.assertEqual(len(logs), 2)
    self.assertIn("data", logs[0])
    self.assertIn("SOURCE", logs[0]["labels"])
    self.assertIn("SCENARIO_ID", logs[0]["labels"])
    self.assertNotIn("SIMULATION", logs[0]["labels"])

  @mock.patch("urllib.request.urlopen")
  def test_secops_sink_udm_events(self, mock_urlopen):
    mock_resp = mock.MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    sink = SecOpsSink(
        customer_id="12345678-abcd-ef01-2345-6789abcdef01",
        project_number="288909297183",
        region="europe-west1",
        mode="events:import",
        tag="test-tag-01",
    )
    with mock.patch.object(sink, "_get_auth_token", return_value="fake-token"):
      count = sink.emit(self.scenario)

    self.assertEqual(count, 2)
    call_args = mock_urlopen.call_args
    req_obj = call_args[0][0]
    self.assertIn("https://europe-west1-chronicle.googleapis.com/v1alpha/projects/288909297183/locations/europe-west1/instances/12345678-abcd-ef01-2345-6789abcdef01/events:import", req_obj.full_url)

    payload = json.loads(req_obj.data.decode("utf-8"))
    self.assertIn("inlineSource", payload)
    events = payload["inlineSource"]["events"]
    self.assertEqual(len(events), 2)
    self.assertIn("udm", events[0])

  @mock.patch("urllib.request.urlopen")
  def test_secops_sink_custom_labels(self, mock_urlopen):
    mock_resp = mock.MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    sink = SecOpsSink(
        customer_id="12345678-abcd-ef01-2345-6789abcdef01",
        project_number="288909297183",
        scenario_name="office_worker_simulation",
        labels={"ENVIRONMENT": "staging", "TEAM": "blue_team"},
    )
    with mock.patch.object(sink, "_get_auth_token", return_value="fake-token"):
      count = sink.emit(self.scenario)

    self.assertEqual(count, 2)
    payload = json.loads(mock_urlopen.call_args[0][0].data.decode("utf-8"))
    log_record = payload["inline_source"]["logs"][0]
    self.assertEqual(log_record["labels"]["SCENARIO_TAG"]["value"], "office_worker_simulation")
    self.assertEqual(log_record["labels"]["ENVIRONMENT"]["value"], "staging")
    self.assertEqual(log_record["labels"]["TEAM"]["value"], "blue_team")


if __name__ == "__main__":
  unittest.main()

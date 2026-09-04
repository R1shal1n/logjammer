"""Unit tests for scenario persistence and replay functionality."""

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from logjammer.config import LogJammerConfig
from logjammer.models import GeneratedScenario, LogEntry, LogFormat
from logjammer.scenario import ScenarioService
from logjammer.client import LogJammer


class ScenarioServiceTest(unittest.TestCase):

  def setUp(self):
    self.temp_dir = tempfile.TemporaryDirectory()
    self.config = LogJammerConfig(
        scenarios_dir=Path(self.temp_dir.name) / "scenarios"
    )
    self.service = ScenarioService(self.config)

    self.sample_scenario = GeneratedScenario(
        title="Test Phishing",
        description="Phishing simulation for testing",
        logs={
            "OFFICE_365": [
                LogEntry(
                    log_type="OFFICE_365",
                    content='{"UserId": "user@corp.local", "Operation": "UserLoggedIn"}',
                    format=LogFormat.JSON,
                    timestamp=datetime.now(timezone.utc),
                )
            ]
        },
    )

  def tearDown(self):
    self.temp_dir.cleanup()

  def test_save_and_list_scenarios(self):
    saved_path = self.service.save_scenario(self.sample_scenario)
    self.assertTrue(saved_path.exists())

    scenarios = self.service.list_scenarios()
    self.assertEqual(len(scenarios), 1)
    self.assertEqual(scenarios[0].scenario_id, self.sample_scenario.scenario_id)
    self.assertEqual(scenarios[0].description, "Phishing simulation for testing")

  def test_get_scenario_by_id_and_prefix(self):
    self.service.save_scenario(self.sample_scenario)
    sc_id = self.sample_scenario.scenario_id

    # Get by full ID
    sc1 = self.service.get_scenario(sc_id)
    self.assertIsNotNone(sc1)

    # Get by prefix
    sc2 = self.service.get_scenario(sc_id[:8])
    self.assertIsNotNone(sc2)
    self.assertEqual(sc2.scenario_id, sc_id)

  def test_delete_scenario(self):
    self.service.save_scenario(self.sample_scenario)
    sc_id = self.sample_scenario.scenario_id

    deleted = self.service.delete_scenario(sc_id[:8])
    self.assertTrue(deleted)
    self.assertEqual(len(self.service.list_scenarios()), 0)

  @mock.patch("urllib.request.urlopen")
  def test_client_replay_without_llm(self, mock_urlopen):
    mock_resp = mock.MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    client = LogJammer()
    client.config.scenarios_dir = Path(self.temp_dir.name) / "scenarios"
    client.scenario_service = ScenarioService(client.config)

    client.save_scenario(self.sample_scenario)

    count = client.replay(
        scenario=self.sample_scenario.scenario_id[:8],
        destination="secops://12345678-abcd-ef01-2345-6789abcdef01@us",
        project="288909297183",
        scenario_name="replay_test",
    )
    self.assertEqual(count, 1)
    self.assertTrue(mock_urlopen.called)


if __name__ == "__main__":
  unittest.main()

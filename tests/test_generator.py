"""Unit tests for scenario generation engine."""

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from logjammer.config import LogJammerConfig
from logjammer.generator import ScenarioGenerator
from logjammer.models import LogFormat
from logjammer.playbook import PlaybookService
PATCH_TARGET = "logjammer.generator.get_genai_client"


class GeneratorTest(unittest.TestCase):

  def setUp(self):
    self.temp_dir = tempfile.TemporaryDirectory()
    self.guides_dir = Path(self.temp_dir.name)
    self.config = LogJammerConfig(api_key="fake-key", guides_dir=self.guides_dir)
    self.base_time = datetime(2026, 8, 24, 12, 0, 0, tzinfo=timezone.utc)

  def tearDown(self):
    self.temp_dir.cleanup()

  def test_generate_scenario(self):
    with mock.patch(PATCH_TARGET) as mock_get_client:
      mock_client = mock.MagicMock()
      mock_response = mock.MagicMock()
      mock_response.text = json.dumps({
          "title": "Credential Stuffing Attack",
          "logs": {
              "OKTA": [
                  '{"timestamp": "##$TimeStamp-0d1h0m0s$##", "user": "victim@corp.com", "event": "failed_login"}',
                  '{"timestamp": "##$TimeStamp-0d0h30m0s$##", "user": "victim@corp.com", "event": "successful_login"}',
              ]
          },
      })
      mock_client.models.generate_content.return_value = mock_response
      mock_get_client.return_value = mock_client

      mock_playbook = mock.MagicMock(spec=PlaybookService)
      mock_playbook.get_guide.return_value = "Schema guide for OKTA"

      generator = ScenarioGenerator(self.config, playbook_service=mock_playbook)
      scenario = generator.generate(
          scenario="Credential stuffing on corporate SSO portal",
          log_types=["OKTA"],
          base_time=self.base_time,
      )

      self.assertEqual(scenario.title, "Credential Stuffing Attack")
      self.assertEqual(scenario.total_log_count, 2)
      self.assertIn("OKTA", scenario.logs)

  @mock.patch("urllib.request.urlopen")
  def test_generate_with_gti_enrichment(self, mock_urlopen):
    # Mock GTI API response
    mock_gti_resp = mock.MagicMock()
    mock_gti_resp.status = 200
    mock_gti_resp.read.return_value = json.dumps({
        "data": {
            "type": "agentic_session",
            "id": "762c2f6d-74d1-44bb-94fe-b39f7eeeb364",
            "attributes": {
                "title": "BlackSuit Ransomware Threat Simulation",
                "events": [
                    {
                        "id": "msg-111",
                        "message_type": "AGENT_FINAL_RESPONSE",
                        "agent_final_response": {
                            "widgets": [
                                {
                                    "widget_type": "MARKDOWN_TEXT",
                                    "markdown_text_widget": {
                                        "text": "Adversary uses C2 domain amaswellybmi.com and IP 103.113.70.65 with BlackSuit encryptor."
                                    },
                                }
                            ]
                        },
                    }
                ],
            },
        }
    }).encode("utf-8")
    mock_gti_resp.__enter__.return_value = mock_gti_resp
    mock_urlopen.return_value = mock_gti_resp

    with mock.patch(PATCH_TARGET) as mock_get_client:
      mock_client = mock.MagicMock()
      mock_response = mock.MagicMock()
      mock_response.text = json.dumps({
          "title": "BlackSuit Ransomware",
          "logs": {
              "WINDOWS_SYSMON": [
                  '{"CommandLine": "blacksuit_encryptor.exe", "DestinationIp": "103.113.70.65"}'
              ]
          },
      })
      mock_client.models.generate_content.return_value = mock_response
      mock_get_client.return_value = mock_client

      mock_playbook = mock.MagicMock(spec=PlaybookService)
      mock_playbook.get_guide.return_value = "Schema guide for WINDOWS_SYSMON"

      self.config.gti_api_key = "fake-gti-key"
      generator = ScenarioGenerator(self.config, playbook_service=mock_playbook)
      scenario = generator.generate(
          scenario="File encryption on Windows endpoint and C2 beaconing",
          log_types=["WINDOWS_SYSMON"],
          enrich_gti=True,
          base_time=self.base_time,
      )

      self.assertEqual(scenario.title, "BlackSuit Ransomware")
      self.assertEqual(scenario.total_log_count, 1)
      self.assertIsNotNone(scenario.enriched_narrative)
      self.assertIn("amaswellybmi.com", scenario.enriched_narrative)

      # Verify the prompt passed to Gemini included the GTI enriched narrative
      call_args = mock_client.models.generate_content.call_args
      prompt_passed = call_args.kwargs.get("contents") or call_args[1].get("contents")
      self.assertIn("Google Threat Intelligence (GTI) Real-World Scenario", prompt_passed)
      self.assertIn("amaswellybmi.com", prompt_passed)


if __name__ == "__main__":
  unittest.main()

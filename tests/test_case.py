"""Unit tests for case report parsing, log type inference, and scenario expansion."""

from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from logjammer.config import LogJammerConfig
from logjammer.models import GeneratedScenario, LogEntry, LogFormat
from logjammer.generator import ScenarioGenerator
from logjammer.client import LogJammer


class CaseExpansionTest(unittest.TestCase):

  def setUp(self):
    self.config = LogJammerConfig()
    self.generator = ScenarioGenerator(self.config)

    self.sample_case = """
Case Overview
Case ID: 104984
Case Title: Series of AWS Glue discovery actions
Principal Actor: IAM User: Worker-ONLY-for-RDE
Source IP Address: 16.171.190.38
AWS Account ID: 306026247677
Target Cloud Resources: AWS Glue GetConnections, GetDatabases
"""

  def test_infer_log_types_heuristic(self):
    inferred = self.generator.infer_log_types(self.sample_case)
    self.assertIn("AWS_CLOUDTRAIL", inferred)
    self.assertIn("AWS_VPC_FLOW", inferred)

  @mock.patch.object(ScenarioGenerator, "generate")
  def test_generate_from_case(self, mock_generate):
    mock_sc = GeneratedScenario(
        title="Expanded AWS Glue Case",
        description="Expanded case scenario",
        logs={
            "AWS_CLOUDTRAIL": [
                LogEntry(
                    log_type="AWS_CLOUDTRAIL",
                    content='{"eventName": "GetConnections"}',
                    format=LogFormat.JSON,
                    timestamp=datetime.now(timezone.utc),
                )
            ]
        },
    )
    mock_generate.return_value = mock_sc

    res = self.generator.generate_from_case(
        case_text=self.sample_case,
        surround_before="30m",
        surround_after="30m",
        outcome="benign",
    )
    self.assertEqual(res.title, "Expanded AWS Glue Case")
    self.assertTrue(mock_generate.called)


if __name__ == "__main__":
  unittest.main()

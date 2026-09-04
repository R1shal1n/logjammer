"""Unit tests for schema playbook learning engine."""

from pathlib import Path
import tempfile
import unittest
from unittest import mock

from logjammer.config import LogJammerConfig
from logjammer.playbook import PlaybookService
PATCH_TARGET = "logjammer.playbook.get_genai_client"


class PlaybookTest(unittest.TestCase):

  def setUp(self):
    self.temp_dir = tempfile.TemporaryDirectory()
    self.guides_dir = Path(self.temp_dir.name)
    self.config = LogJammerConfig(api_key="fake-key", guides_dir=self.guides_dir)

  def tearDown(self):
    self.temp_dir.cleanup()

  def test_learn_from_samples(self):
    with mock.patch(PATCH_TARGET) as mock_get_client:
      mock_client = mock.MagicMock()
      mock_response = mock.MagicMock()
      mock_response.text = "# OKTA Guide\nThis is an OKTA guide."
      mock_client.models.generate_content.return_value = mock_response
      mock_get_client.return_value = mock_client

      service = PlaybookService(self.config)
      sample_log = '{"actor": {"alternateId": "admin@example.com"}, "eventType": "user.authentication.auth_via_mfa"}'

      result = service.learn("OKTA", sample_log)
      self.assertEqual(result.log_type, "OKTA")
      self.assertIn("OKTA Guide", result.guide_content)
      self.assertTrue(result.guide_path.exists())

      # Verify guide retrieval
      saved_guide = service.get_guide("OKTA")
      self.assertEqual(saved_guide, "# OKTA Guide\nThis is an OKTA guide.")

      # Verify list
      available = service.list_available_log_types()
      self.assertIn("OKTA", available)

  def test_learn_from_directory_samples(self):
    # Create sample directory with multiple event files and a README
    samples_dir = Path(self.temp_dir.name) / "okta_samples"
    samples_dir.mkdir()

    (samples_dir / "auth_success.json").write_text('{"event": "login_success"}')
    (samples_dir / "auth_fail.json").write_text('{"event": "login_failed"}')
    (samples_dir / "README.md").write_text("# Documentation to ignore")

    with mock.patch(PATCH_TARGET) as mock_get_client:
      mock_client = mock.MagicMock()
      mock_response = mock.MagicMock()
      mock_response.text = "# OKTA Directory Guide"
      mock_client.models.generate_content.return_value = mock_response
      mock_get_client.return_value = mock_client

      service = PlaybookService(self.config)
      result = service.learn("OKTA", samples_dir)

      self.assertEqual(result.log_type, "OKTA")
      self.assertEqual(result.files_analyzed, 2)
      self.assertEqual(result.sample_count, 2)
      self.assertTrue(result.guide_path.exists())

      # Verify the prompt passed to generate_content contained both sample files
      call_args = mock_client.models.generate_content.call_args
      prompt_passed = call_args.kwargs.get("contents") or call_args[1].get("contents")
      self.assertIn("--- Sample File: auth_success.json ---", prompt_passed)
  def test_learn_from_textproto_sample(self):
    # Simulate a textproto log file with batch.entries.data and escaped JSON
    textproto_content = """batch {
  entries {
    data: "{\\"published\\": 1785258308008, \\"actor\\": {\\"id\\": \\"00u123\\", \\"alternateId\\": \\"admin@example.com\\"}, \\"eventType\\": \\"user.session.start\\"}"
  }
  entries {
    data: "{\\"published\\": 1785258309000, \\"actor\\": {\\"id\\": \\"00u123\\", \\"alternateId\\": \\"admin@example.com\\"}, \\"eventType\\": \\"user.mfa.verify\\"}"
  }
}
"""
    proto_file = Path(self.temp_dir.name) / "okta_batch.textproto"
    proto_file.write_text(textproto_content)

    with mock.patch(PATCH_TARGET) as mock_get_client:
      mock_client = mock.MagicMock()
      mock_response = mock.MagicMock()
      mock_response.text = "# OKTA Textproto Guide"
      mock_client.models.generate_content.return_value = mock_response
      mock_get_client.return_value = mock_client

      service = PlaybookService(self.config)
      result = service.learn("OKTA", proto_file)

      self.assertEqual(result.log_type, "OKTA")
      self.assertEqual(result.sample_count, 2)

      # Verify the extracted and unescaped JSON was passed to Gemini (no batch/entries wrapper or escaped quotes)
      call_args = mock_client.models.generate_content.call_args
      prompt_passed = call_args.kwargs.get("contents") or call_args[1].get("contents")
      self.assertIn('"published": 1785258308008', prompt_passed)
      self.assertIn('"alternateId": "admin@example.com"', prompt_passed)
      self.assertNotIn('data: "', prompt_passed)
      self.assertNotIn('\\"published\\"', prompt_passed)

  def test_subdirectory_and_markdown_guides(self):
    aws_dir = self.guides_dir / "AWS"
    aws_dir.mkdir(parents=True)

    ct_content = "**Official SecOps Log Type:** `AWS_CLOUDTRAIL`\n# CloudTrail Reference"
    (aws_dir / "cloudtrail_log_format_reference.md").write_text(ct_content)
    (aws_dir / "vpc_flow_logs_format_reference.md").write_text("# VPC Flow Reference")

    service = PlaybookService(self.config)
    available = service.list_available_log_types()

    self.assertIn("AWS/cloudtrail_log_format_reference", available)
    self.assertIn("AWS/vpc_flow_logs_format_reference", available)

    # Retrieval via relative path
    self.assertEqual(service.get_guide("AWS/cloudtrail_log_format_reference"), ct_content)
    # Retrieval via Official SecOps Log Type
    self.assertEqual(service.get_guide("AWS_CLOUDTRAIL"), ct_content)
    # Retrieval via normalized alias
    self.assertEqual(service.get_guide("CLOUDTRAIL"), ct_content)
    # Retrieval for VPC Flow via normalized alias
    self.assertEqual(service.get_guide("AWS_VPC_FLOW"), "# VPC Flow Reference")
    self.assertEqual(service.get_guide("VPC_FLOW"), "# VPC Flow Reference")

  def test_learn_with_subfolder(self):
    with mock.patch(PATCH_TARGET) as mock_get_client:
      mock_client = mock.MagicMock()
      mock_response = mock.MagicMock()
      mock_response.text = "# Custom AWS Service Guide"
      mock_client.models.generate_content.return_value = mock_response
      mock_get_client.return_value = mock_client

      service = PlaybookService(self.config)
      result = service.learn("AWS/CUSTOM_APP", '{"msg": "test"}')

      self.assertTrue(result.guide_path.exists())
      self.assertEqual(result.guide_path, self.guides_dir / "AWS" / "CUSTOM_APP.txt")


if __name__ == "__main__":
  unittest.main()

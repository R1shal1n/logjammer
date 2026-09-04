"""Unit tests for pre-flight validation of environment variables and credentials."""

import os
import unittest
from unittest import mock

from logjammer.client import LogJammer
from logjammer.config import LogJammerConfig
from logjammer.sinks.secops import SecOpsSink


class PreflightValidationTest(unittest.TestCase):

  def test_blank_gemini_api_key_fails_preflight(self):
    config = LogJammerConfig(api_key="")
    client = LogJammer(api_key="")
    # Manually set api_key to None/empty
    client.config.api_key = None

    with self.assertRaises(ValueError) as ctx:
      client.validate_preflight(require_genai=True)

    self.assertIn("[Pre-flight Validation Failed]", str(ctx.exception))
    self.assertIn("GEMINI_API_KEY", str(ctx.exception))

  def test_blank_secops_customer_id_fails_preflight(self):
    client = LogJammer(api_key="test_key")

    with self.assertRaises(ValueError) as ctx:
      client.validate_preflight(
          require_genai=True,
          destination="secops://YOUR_SECOPS_CUSTOMER_ID@us",
          project="sdl-preview-americas",
      )

    self.assertIn("[Pre-flight Validation Failed]", str(ctx.exception))
    self.assertIn("Customer ID", str(ctx.exception))

  @mock.patch.dict(os.environ, {"SECOPS_CUSTOMER_ID": "a556547c-1cff-43ef-a2e4-cf5b12a865df"})
  def test_valid_secops_preflight_passes(self):
    client = LogJammer(api_key="test_key")
    # Should not raise any error
    client.validate_preflight(
        require_genai=True,
        destination="secops://a556547c-1cff-43ef-a2e4-cf5b12a865df@us",
        project="sdl-preview-americas",
    )


if __name__ == "__main__":
  unittest.main()

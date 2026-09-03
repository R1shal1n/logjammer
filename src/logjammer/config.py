"""Configuration management for Log Jammer OSS."""

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Optional


DEFAULT_MODEL = "gemini-3.7-flash"
DEFAULT_GUIDES_DIR = Path.home() / ".logjammer" / "guides"


@dataclass
class LogJammerConfig:
  """Configuration settings for Log Jammer."""

  api_key: Optional[str] = None
  gti_api_key: Optional[str] = None
  model: str = DEFAULT_MODEL
  temperature: float = 1.0
  top_p: float = 0.95
  thinking_budget: int = -1
  guides_dir: Path = field(default_factory=lambda: DEFAULT_GUIDES_DIR)

  def __post_init__(self):
    if not self.api_key:
      self.api_key = os.environ.get("GEMINI_API_KEY")

    if not self.gti_api_key:
      self.gti_api_key = (
          os.environ.get("GTI_API_KEY")
          or os.environ.get("VIRUSTOTAL_API_KEY")
          or os.environ.get("VT_API_KEY")
      )

    env_model = os.environ.get("LOGJAMMER_MODEL")
    if env_model:
      self.model = env_model

    env_guides = os.environ.get("LOGJAMMER_GUIDES_DIR")
    if env_guides:
      self.guides_dir = Path(env_guides)

    # Ensure guides directory exists
    self.guides_dir.mkdir(parents=True, exist_ok=True)


def get_genai_client(config: Optional[LogJammerConfig] = None):
  """Instantiate a Google GenAI client using configuration."""
  try:
    from google import genai
  except ImportError:
    raise ImportError(
        "The 'google-genai' package is required for AI generation. "
        "Install it via: pip install google-genai"
    )
  cfg = config or LogJammerConfig()
  try:
    if cfg.api_key:
      return genai.Client(api_key=cfg.api_key)
    return genai.Client()
  except Exception as e:
    raise ValueError(
        f"Missing or invalid Gemini API credentials ({e}).\n"
        "Please provide a valid API key via:\n"
        "  1. export GEMINI_API_KEY=\"your_key_here\"\n"
        "  2. Or pass --api-key \"your_key_here\" on the command line.\n"
        "Get an API key at: https://aistudio.google.com/app/apikey"
    ) from None

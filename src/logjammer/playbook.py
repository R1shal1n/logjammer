import re
from pathlib import Path
from typing import List, Optional, Tuple, Union
try:
  from google.genai import types
except ImportError:
  types = None

from .config import LogJammerConfig, get_genai_client
from .models import LearnResult


SYSTEM_PROMPT = """You are an expert security data engineer and detection engineering specialist.
Your task is to analyze real-world log samples for a security/system log type and generate an exhaustive, highly detailed AI generation guide (Playbook).

The guide will be used by an AI scenario generator to produce realistic, synthetically generated logs for security testing and SIEM rule validation.

Your generated guide must include:
1. **Overview & Log Purpose**: What device, application, or system produces this log? What activities are recorded?
2. **Format Specification**:
   - Classification: Is it JSON, CEF, Syslog (RFC 3164 / RFC 5424), Windows Event XML, Key-Value pairs, or custom delimiters?
   - Delimiters and quoting rules.
3. **Schema Breakdown & Fields**:
   - Header fields and metadata (facility, severity, hostname, process name, process ID).
   - Core body fields, types, and realistic distributions (IP addresses, ports, usernames, file paths, URIs, user agents).
   - Expected status codes, event IDs, action verbs (e.g. ALLOW/DENY, SUCCESS/FAILURE).
4. **Timestamp & Dynamic Time Templating**:
   - Explain the timestamp format used (e.g. ISO 8601, Epoch seconds, Syslog MMM DD HH:MM:SS).
   - Explicitly instruct using relative time template tags: `##$TimeStamp-0d2h15m0s$##`, `##$Epoch-0d1h0m0s$##`, `##$SyslogTime-0d0h30m0s$##`.
5. **Concrete Valid Examples**:
   - Provide 3 to 5 realistic, full log lines representing varied activities (normal user activity, failed login, privilege escalation, firewall block).
6. **Key Constraints & Pitfalls**:
   - Fields that MUST be present for parsers not to fail.
   - Escaping rules for nested strings or JSON.
"""


class PlaybookService:
  """Learns log schemas and manages prompt guides for log generation."""

  def __init__(self, config: Optional[LogJammerConfig] = None):
    self.config = config or LogJammerConfig()
    self._client = None

  @property
  def client(self):
    if self._client is None:
      self._client = get_genai_client(self.config)
    return self._client

  def _preprocess_sample_text(self, raw_text: str) -> str:
    """Unwraps and unescapes textproto/protobuf wrappers if detected.

    Extracts raw logs from `batch.entries.data` or `data: "..."` and unescapes
    JSON/Syslog strings so Gemini analyzes the real log payload.
    """
    cleaned = raw_text.strip()
    if ("data:" in cleaned or "entries {" in cleaned or "batch {" in cleaned) and not (
        cleaned.startswith("{") and cleaned.endswith("}")
    ):
      pattern = r'data:\s*"((?:[^"\\]|\\.)*)"'
      matches = re.findall(pattern, cleaned)
      if matches:
        extracted = []
        for m in matches:
          unescaped = (
              m.replace('\\"', '"')
              .replace("\\\\", "\\")
              .replace("\\n", "\n")
              .replace("\\r", "\r")
              .replace("\\t", "\t")
          )
          if unescaped.strip():
            extracted.append(unescaped.strip())
        if extracted:
          return "\n".join(extracted)
    return raw_text

  def _load_samples(
      self, sample_content: Union[str, Path, List[str]]
  ) -> Tuple[str, int, int]:
    """Load sample content from a file, directory, string, or list.

    Returns:
      Tuple of (formatted_samples_text, total_lines, files_analyzed_count)
    """
    if isinstance(sample_content, Path):
      if sample_content.is_dir():
        # Find all regular non-hidden files, ignoring documentation
        files = [
            f
            for f in sorted(sample_content.glob("**/*"))
            if f.is_file()
            and not f.name.startswith(".")
            and f.name.lower() not in ("readme.md", "metadata.json")
        ]
        if not files:
          raise ValueError(
              f"No valid sample files found in directory '{sample_content}'."
          )

        chunks = []
        total_lines = 0
        for f in files:
          with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            content = self._preprocess_sample_text(fp.read().strip())
          if content:
            total_lines += len(content.splitlines())
            rel_name = f.relative_to(sample_content)
            chunks.append(f"--- Sample File: {rel_name} ---\n{content}")

        if not chunks:
          raise ValueError(
              f"All sample files in directory '{sample_content}' were empty."
          )

        return "\n\n".join(chunks), total_lines, len(chunks)
      else:
        with open(sample_content, "r", encoding="utf-8", errors="ignore") as f:
          content = self._preprocess_sample_text(f.read().strip())
        lines = len(content.splitlines()) if content else 0
        return content, lines, 1
    elif isinstance(sample_content, list):
      text = self._preprocess_sample_text("\n".join(sample_content).strip())
      lines = len(text.splitlines()) if text else 0
      return text, lines, 1
    else:
      text = self._preprocess_sample_text(str(sample_content).strip())
      lines = len(text.splitlines()) if text else 0
      return text, lines, 1

  def learn(
      self,
      log_type: str,
      sample_content: Union[str, Path, List[str]],
      output_dir: Optional[Path] = None,
  ) -> LearnResult:
    """Analyze log samples and generate a comprehensive schema playbook."""
    samples_text, sample_lines, files_count = self._load_samples(sample_content)

    if not samples_text.strip():
      raise ValueError(f"Sample content for log type '{log_type}' is empty.")

    user_prompt = f"""Log Type Name: {log_type}

Here are representative log samples extracted from real systems:
```
{samples_text[:50000]}
```

Generate the comprehensive AI log playbook guide for '{log_type}' following the required structure."""

    try:
      from google.genai import types as genai_types
      gen_config = genai_types.GenerateContentConfig(
          system_instruction=SYSTEM_PROMPT,
          temperature=self.config.temperature,
          top_p=self.config.top_p,
          thinking_config=genai_types.ThinkingConfig(
              thinking_budget=self.config.thinking_budget,
          ),
      )
    except (ImportError, AttributeError):
      gen_config = None

    response = self.client.models.generate_content(
        model=self.config.model,
        contents=user_prompt,
        config=gen_config,
    )

    guide_content = response.text or ""

    # Save to guides directory
    target_dir = output_dir or self.config.guides_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    guide_path = target_dir / f"{log_type}.txt"

    with open(guide_path, "w", encoding="utf-8") as f:
      f.write(guide_content)

    return LearnResult(
        log_type=log_type,
        guide_content=guide_content,
        guide_path=guide_path,
        sample_count=sample_lines,
        files_analyzed=files_count,
    )

  def get_guide(self, log_type: str, guides_dir: Optional[Path] = None) -> Optional[str]:
    """Retrieve the guide text for a specific log type."""
    search_dir = guides_dir or self.config.guides_dir
    guide_file = search_dir / f"{log_type}.txt"
    if guide_file.exists():
      with open(guide_file, "r", encoding="utf-8") as f:
        return f.read()
    return None

  def list_available_log_types(self, guides_dir: Optional[Path] = None) -> List[str]:
    """List all available log types that have guides."""
    search_dir = guides_dir or self.config.guides_dir
    if not search_dir.exists():
      return []
    return sorted(p.stem for p in search_dir.glob("*.txt"))

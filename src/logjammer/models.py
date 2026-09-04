"""Data models for Log Jammer OSS."""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid


class LogFormat(str, Enum):
  """Format of the generated or parsed log."""

  JSON = "json"
  RAW = "raw"
  SYSLOG = "syslog"
  CSV = "csv"


@dataclass
class LogEntry:
  """Represents a single log event."""

  log_type: str
  content: str
  format: LogFormat = LogFormat.RAW
  timestamp: Optional[datetime] = None
  metadata: Dict[str, Any] = field(default_factory=dict)

  def to_dict(self) -> Dict[str, Any]:
    return {
        "log_type": self.log_type,
        "content": self.content,
        "format": self.format.value,
        "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        "metadata": self.metadata,
    }

  @classmethod
  def from_dict(cls, data: Dict[str, Any]) -> "LogEntry":
    ts = None
    if data.get("timestamp"):
      try:
        ts = datetime.fromisoformat(data["timestamp"])
      except Exception:
        ts = None
    fmt_str = data.get("format", "raw")
    try:
      fmt = LogFormat(fmt_str)
    except Exception:
      fmt = LogFormat.RAW
    return cls(
        log_type=data.get("log_type", "UNKNOWN"),
        content=data.get("content", ""),
        format=fmt,
        timestamp=ts,
        metadata=data.get("metadata", {}),
    )


@dataclass
class LogTypeGuide:
  """Schema guide and formatting instructions for a log type."""

  log_type: str
  guide_content: str
  source_file: Optional[Path] = None
  description: Optional[str] = None


@dataclass
class GeneratedScenario:
  """A complete multi-source synthetic log scenario."""

  description: str
  title: str = "Synthetic Attack Scenario"
  scenario_id: str = field(default_factory=lambda: str(uuid.uuid4()))
  created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
  logs: Dict[str, List[LogEntry]] = field(default_factory=dict)
  raw_response: Optional[str] = None
  enriched_narrative: Optional[str] = None

  @property
  def total_log_count(self) -> int:
    """Return the total number of log events across all log types."""
    return sum(len(entries) for entries in self.logs.values())

  def get_flattened_logs(self) -> List[LogEntry]:
    """Return all logs flattened into a single list."""
    all_logs = []
    for entries in self.logs.values():
      all_logs.extend(entries)
    return all_logs

  def to_dict(self) -> Dict[str, Any]:
    return {
        "scenario_id": self.scenario_id,
        "title": self.title,
        "description": self.description,
        "created_at": self.created_at.isoformat(),
        "total_logs": self.total_log_count,
        "enriched_narrative": self.enriched_narrative,
        "logs": {
            k: [entry.to_dict() for entry in v] for k, v in self.logs.items()
        },
    }

  def to_json(self, indent: int = 2) -> str:
    return json.dumps(self.to_dict(), indent=indent)

  @classmethod
  def from_dict(cls, data: Dict[str, Any]) -> "GeneratedScenario":
    logs_dict = {}
    for log_type, entries_data in data.get("logs", {}).items():
      logs_dict[log_type] = [LogEntry.from_dict(e) for e in entries_data]

    created_at = datetime.now(timezone.utc)
    if data.get("created_at"):
      try:
        created_at = datetime.fromisoformat(data["created_at"])
      except Exception:
        pass

    return cls(
        scenario_id=data.get("scenario_id", str(uuid.uuid4())),
        title=data.get("title", "Synthetic Attack Scenario"),
        description=data.get("description", ""),
        created_at=created_at,
        logs=logs_dict,
        raw_response=data.get("raw_response"),
        enriched_narrative=data.get("enriched_narrative"),
    )

  @classmethod
  def from_json(cls, json_str: str) -> "GeneratedScenario":
    return cls.from_dict(json.loads(json_str))

  @classmethod
  def from_file(cls, filepath: Any) -> "GeneratedScenario":
    path = Path(filepath)
    with open(path, "r", encoding="utf-8") as f:
      return cls.from_json(f.read())


@dataclass
class LearnResult:
  """Result of learning a log schema from sample files."""

  log_type: str
  guide_content: str
  guide_path: Optional[Path] = None
  sample_count: int = 0
  files_analyzed: int = 1

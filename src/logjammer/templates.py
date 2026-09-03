"""Relative time template parser and dynamic timestamp generator."""

from datetime import datetime, timedelta, timezone
import re
from typing import Any, Dict, List, Optional, Union


# Regex to match relative timestamp templates:
# Examples: ##$TimeStamp-0d2h15m0s$##, ##$Epoch-0d0h5m0s$##, ##$SyslogTime-0d1h0m0s$##
TEMPLATE_PATTERN = re.compile(
    r"##\$(TimeStamp|Epoch|EpochMillis|Date|SyslogTime)([+-])(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?\$##"
)


class TimeTemplateService:
  """Resolves relative timestamp templates into real date/time strings."""

  def __init__(self, base_time: Optional[datetime] = None):
    self.base_time = base_time or datetime.now(timezone.utc)

  def parse_offset(
      self,
      sign: str,
      days: Optional[str],
      hours: Optional[str],
      minutes: Optional[str],
      seconds: Optional[str],
  ) -> timedelta:
    """Parse regex match groups into a timedelta object."""
    d = int(days) if days else 0
    h = int(hours) if hours else 0
    m = int(minutes) if minutes else 0
    s = int(seconds) if seconds else 0
    delta = timedelta(days=d, hours=h, minutes=m, seconds=s)
    return delta if sign == "+" else -delta

  def format_timestamp(self, template_type: str, target_dt: datetime) -> str:
    """Format the target datetime according to the template type."""
    if template_type == "Epoch":
      return str(int(target_dt.timestamp()))
    elif template_type == "EpochMillis":
      return str(int(target_dt.timestamp() * 1000))
    elif template_type == "Date":
      return target_dt.strftime("%Y-%m-%d")
    elif template_type == "SyslogTime":
      # Traditional syslog timestamp format: Aug 24 09:15:30 (handles single digit day spacing)
      day_str = f"{target_dt.day:2d}"
      return target_dt.strftime(f"%b {day_str} %H:%M:%S")
    else:  # Default "TimeStamp" -> ISO 8601 UTC format
      return target_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"

  def replace_templates(self, text: str) -> str:
    """Replace all ##$...$## templates in a text string."""
    def _replacer(match: re.Match) -> str:
      template_type, sign, d, h, m, s = match.groups()
      offset = self.parse_offset(sign, d, h, m, s)
      target_dt = self.base_time + offset
      return self.format_timestamp(template_type, target_dt)

    return TEMPLATE_PATTERN.sub(_replacer, text)


def replace_time_templates(
    text: str, base_time: Optional[datetime] = None
) -> str:
  """Helper function to replace time templates in a string."""
  service = TimeTemplateService(base_time)
  return service.replace_templates(text)


def replace_time_templates_in_logs(
    logs_data: Union[Dict[str, Any], List[Any], str],
    base_time: Optional[datetime] = None,
) -> Any:
  """Recursively replaces time templates across nested dictionaries, lists, and strings."""
  service = TimeTemplateService(base_time)

  if isinstance(logs_data, str):
    return service.replace_templates(logs_data)
  elif isinstance(logs_data, list):
    return [replace_time_templates_in_logs(item, base_time) for item in logs_data]
  elif isinstance(logs_data, dict):
    return {
        key: replace_time_templates_in_logs(value, base_time)
        for key, value in logs_data.items()
    }
  return logs_data

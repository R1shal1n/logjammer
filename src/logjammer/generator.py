"""AI-powered scenario log generation service."""

from datetime import datetime, timezone
import json
import re
from typing import Dict, List, Optional
try:
  from google.genai import types
except ImportError:
  types = None

from .config import LogJammerConfig, get_genai_client
from .gti import GTIClient
from .models import GeneratedScenario, LogEntry, LogFormat
from .playbook import PlaybookService
from .templates import replace_time_templates


SCENARIO_SYSTEM_PROMPT = """You are an elite Red Team Operator and Security Telemetry Architect.
Your task is to generate highly authentic, realistic, multi-source synthetic logs depicting a security scenario.

You will be given:
1. A natural language scenario narrative (e.g., "Phishing email leading to Cobalt Strike beacon and ransomware encryption").
2. The requested log types (e.g. OKTA, CS_EDR, BIND_DNS, PAN_FIREWALL).
3. Detailed Schema Guides for each log type detailing required fields, delimiters, headers, and timestamp formats.

CRITICAL RULES:
1. **Schema Fidelity**: Strictly follow the provided Schema Guides for each log type. Every log line must conform to real-world format expectations.
2. **Cohesive Narrative**: Ensure all events across different log sources correlate coherently:
   - Usernames, internal IP addresses, external C2 IPs, and hostnames must match across different log types.
   - The timeline must progress logically (initial recon -> delivery -> execution -> persistence -> lateral movement -> exfiltration/impact).
3. **Relative Time Templating**:
   - Never hardcode static timestamps!
   - Use relative template tags:
     * ISO 8601: `##$TimeStamp-0d2h15m0s$##` (e.g. 2 hours 15 minutes before trigger)
     * Unix Epoch: `##$Epoch-0d1h30m0s$##`
     * Syslog: `##$SyslogTime-0d0h45m0s$##`
4. **Output Format**:
   Return a single valid JSON object with the following structure:
   ```json
   {
     "title": "Short descriptive title of the attack scenario",
     "summary": "2-3 sentence overview of the simulated attack chain",
     "logs": {
       "<LOG_TYPE_1>": [
         "log line 1 or JSON string",
         "log line 2 or JSON string"
       ],
       "<LOG_TYPE_2>": [
         "log line 1",
         "log line 2"
       ]
     }
   }
   ```
   Do not include any conversational preamble outside the JSON markdown block.
"""


class ScenarioGenerator:
  """Generates multi-source synthetic logs for arbitrary security scenarios."""

  def __init__(
      self,
      config: Optional[LogJammerConfig] = None,
      playbook_service: Optional[PlaybookService] = None,
      gti_client: Optional[GTIClient] = None,
  ):
    self.config = config or LogJammerConfig()
    self.playbook_service = playbook_service or PlaybookService(self.config)
    self.gti_client = gti_client or GTIClient(api_key=self.config.gti_api_key)
    self._client = None

  @property
  def client(self):
    if self._client is None:
      self._client = get_genai_client(self.config)
    return self._client

  def _build_prompt(
      self,
      scenario: str,
      log_types: List[str],
      custom_system_prompt: Optional[str] = None,
  ) -> str:
    """Construct the full generation prompt including schema guides."""
    guides_section = []
    for lt in log_types:
      guide = self.playbook_service.get_guide(lt)
      if guide:
        guides_section.append(f"### Schema Guide for {lt}:\n{guide}\n")
      else:
        guides_section.append(
            f"### Schema Guide for {lt}:\n(No saved guide found. Use standard industry format for {lt}.)\n"
        )

    guides_text = "\n".join(guides_section)

    return f"""## Scenario Description:
{scenario}

## Requested Log Types:
{', '.join(log_types)}

## Log Type Schema Guides:
{guides_text}

Generate the complete attack scenario logs as specified."""

  def generate(
      self,
      scenario: str,
      log_types: List[str],
      base_time: Optional[datetime] = None,
      custom_system_prompt: Optional[str] = None,
      enrich_gti: bool = False,
  ) -> GeneratedScenario:
    """Generate synthetic logs for the specified scenario."""
    if not log_types:
      raise ValueError("At least one log type must be provided.")
    if not scenario or len(scenario.strip()) < 10:
      raise ValueError("Scenario description must be at least 10 characters.")

    enriched_text = None
    actual_scenario = scenario
    if enrich_gti:
      enriched_text = self.gti_client.enrich_scenario(scenario)
      actual_scenario = f"""### User High-Level Intent:
{scenario}

### Google Threat Intelligence (GTI) Real-World Scenario & Indicators:
{enriched_text}
"""

    prompt = self._build_prompt(actual_scenario, log_types, custom_system_prompt)
    system_instruction = custom_system_prompt or SCENARIO_SYSTEM_PROMPT

    try:
      from google.genai import types as genai_types
      gen_config = genai_types.GenerateContentConfig(
          system_instruction=system_instruction,
          temperature=self.config.temperature,
          top_p=self.config.top_p,
          response_mime_type="application/json",
          thinking_config=genai_types.ThinkingConfig(
              thinking_budget=self.config.thinking_budget,
          ),
      )
    except (ImportError, AttributeError):
      gen_config = None

    response = self.client.models.generate_content(
        model=self.config.model,
        contents=prompt,
        config=gen_config,
    )

    raw_text = response.text or "{}"
    return self._parse_response(
        raw_text, scenario, base_time, enriched_narrative=enriched_text
    )

  def _parse_response(
      self,
      raw_text: str,
      scenario_description: str,
      base_time: Optional[datetime] = None,
      enriched_narrative: Optional[str] = None,
  ) -> GeneratedScenario:
    """Parse Gemini's JSON response and resolve time templates."""
    # Strip optional markdown code fence
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
      cleaned = cleaned[7:]
    if cleaned.startswith("```"):
      cleaned = cleaned[3:]
    if cleaned.endswith("```"):
      cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
      data = json.loads(cleaned)
    except json.JSONDecodeError:
      # Fallback: extract json using regex
      match = re.search(r"\{.*\}", cleaned, re.DOTALL)
      if match:
        data = json.loads(match.group(0))
      else:
        data = {"title": "Generated Scenario", "logs": {}}

    title = data.get("title", "Synthetic Attack Scenario")
    raw_logs = data.get("logs", {})

    parsed_logs: Dict[str, List[LogEntry]] = {}

    for log_type, entries in raw_logs.items():
      parsed_logs[log_type] = []
      for entry in entries:
        # Convert dict to JSON string if needed
        if isinstance(entry, (dict, list)):
          entry_str = json.dumps(entry)
          fmt = LogFormat.JSON
        else:
          entry_str = str(entry)
          fmt = LogFormat.JSON if entry_str.strip().startswith(("{", "[")) else LogFormat.RAW

        # Resolve relative timestamps into real dates
        resolved_content = replace_time_templates(entry_str, base_time)

        parsed_logs[log_type].append(
            LogEntry(
                log_type=log_type,
                content=resolved_content,
                format=fmt,
                timestamp=base_time or datetime.now(timezone.utc),
            )
        )

    return GeneratedScenario(
        title=title,
        description=scenario_description,
        logs=parsed_logs,
        raw_response=raw_text,
        enriched_narrative=enriched_narrative,
    )

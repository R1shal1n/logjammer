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

  def infer_log_types(self, case_text: str) -> List[str]:
    """Analyze a case report and infer the appropriate SIEM log types from available playbooks."""
    available_types = self.playbook_service.list_available_log_types()
    available_str = (
        ", ".join(available_types)
        if available_types
        else "AWS_CLOUDTRAIL, AWS_VPC_FLOW, GUARDDUTY, OKTA, WINDOWS_SYSMON, GCP_CLOUDAUDIT"
    )

    prompt = f"""Given the following Security Case Report / Incident Alert Summary, identify the most relevant SIEM log types required to generate full surrounding telemetry (Pre-incident setup, Core alert events, and Post-incident outcome).

Available Log Jammer Playbook Schemas:
{available_str}

Case Report:
{case_text}

Return a valid JSON array of 1 to 5 matching log type strings (e.g. ["AWS_CLOUDTRAIL", "AWS_VPC_FLOW"]).
Return ONLY the JSON array."""

    try:
      from google.genai import types as genai_types
      gen_config = genai_types.GenerateContentConfig(
          response_mime_type="application/json",
          temperature=0.2,
      )
      response = self.client.models.generate_content(
          model=self.config.model,
          contents=prompt,
          config=gen_config,
      )
      data = json.loads(response.text)
      if isinstance(data, list) and data:
        return [str(x) for x in data]
    except Exception:
      pass

    # Heuristic fallback matching keywords
    text_lower = case_text.lower()
    inferred = []
    if any(k in text_lower for k in ("aws", "cloudtrail", "glue", "iam", "sts", "s3")):
      inferred.append("AWS_CLOUDTRAIL")
      if any(k in text_lower for k in ("ip", "network", "connection", "vpc", "flow")):
        inferred.append("AWS_VPC_FLOW")
    elif any(k in text_lower for k in ("gcp", "google", "bigquery")):
      inferred.append("GCP_CLOUDAUDIT")
    elif any(k in text_lower for k in ("azure", "entra")):
      inferred.append("AZURE_ACTIVITY")
    elif "slack" in text_lower:
      inferred.append("SLACK_AUDIT")
    elif "github" in text_lower:
      inferred.append("GITHUB")

    return inferred or ["AWS_CLOUDTRAIL"]

  def generate_from_case(
      self,
      case_text: str,
      log_types: Optional[List[str]] = None,
      surround_before: str = "30m",
      surround_after: str = "30m",
      outcome: str = "benign",
      base_time: Optional[datetime] = None,
      custom_system_prompt: Optional[str] = None,
      enrich_gti: bool = False,
  ) -> GeneratedScenario:
    """Generate a multi-stage surrounding log scenario from an input case report."""
    if not log_types:
      log_types = self.infer_log_types(case_text)

    case_scenario_prompt = f"""### INPUT CASE REPORT / INCIDENT ALERT:
{case_text}

### SCENARIO GENERATION REQUIREMENTS:
1. **Pre-Incident Phase (-{surround_before} before anchor timeline)**:
   Generate initial authentication, network handshakes, STS session creation, API key lookups, or user activity leading up to the case events.
2. **Core Incident Anchor Phase**:
   Re-create the exact sequence of events detailed in the case report timeline.
3. **Post-Incident Phase (+{surround_after} after anchor timeline)**:
   Generate the outcome activity based on the specified verdict/outcome: '{outcome}'.
   If benign: routine data verification, cleanup, session logout, or normal scheduled task completion.
   If malicious: credential dumping, data exfiltration, lateral movement, or backdoor creation.
4. **Entity Consistency**:
   Re-use all exact IPs, usernames, role ARNs, session IDs, hostnames, and account IDs from the case report across all generated log types.
"""
    return self.generate(
        scenario=case_scenario_prompt,
        log_types=log_types,
        base_time=base_time,
        custom_system_prompt=custom_system_prompt,
        enrich_gti=enrich_gti,
    )


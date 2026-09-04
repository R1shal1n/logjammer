"""High-level Python SDK client for Log Jammer OSS."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from .config import LogJammerConfig
from .generator import ScenarioGenerator
from .models import GeneratedScenario, LearnResult
from .playbook import PlaybookService
from .sinks.base import BaseSink
from .sinks.file import FileSink
from .sinks.secops import SecOpsSink
from .sinks.syslog import SyslogSink
from .sinks.webhook import WebhookSink


class LogJammer:
  """Main entry point for Log Jammer Python library.

  Usage:
      client = LogJammer(api_key="...")
      client.learn("MY_APP", "./sample_app.log")
      scenario = client.generate(
          scenario="Ransomware lateral movement via SMB",
          log_types=["MY_APP", "WINEVTLOG"]
      )
      client.export(scenario, destination="./output.jsonl")
  """

  def __init__(
      self,
      api_key: Optional[str] = None,
      gti_api_key: Optional[str] = None,
      model: str = "gemini-3.7-flash",
      guides_dir: Optional[Union[str, Path]] = None,
      temperature: float = 1.0,
      thinking_budget: int = -1,
  ):
    guides_path = Path(guides_dir) if guides_dir else None
    self.config = LogJammerConfig(
        api_key=api_key,
        gti_api_key=gti_api_key,
        model=model,
        temperature=temperature,
        thinking_budget=thinking_budget,
    )
    if guides_path:
      self.config.guides_dir = guides_path
      self.config.guides_dir.mkdir(parents=True, exist_ok=True)

    self.playbook_service = PlaybookService(self.config)
    self.generator = ScenarioGenerator(self.config, self.playbook_service)

  def learn(
      self,
      log_type: str,
      sample: Union[str, Path, List[str]],
      output_dir: Optional[Union[str, Path]] = None,
  ) -> LearnResult:
    """Analyze sample logs and compile a new schema playbook."""
    out_path = Path(output_dir) if output_dir else None
    return self.playbook_service.learn(log_type, sample, output_dir=out_path)

  def enrich_with_gti(self, scenario: str) -> str:
    """Enrich a high-level scenario description using the Google Threat Intelligence Agent."""
    return self.generator.gti_client.enrich_scenario(scenario)

  def generate(
      self,
      scenario: str,
      log_types: List[str],
      base_time: Optional[datetime] = None,
      custom_system_prompt: Optional[str] = None,
      enrich_gti: bool = False,
  ) -> GeneratedScenario:
    """Generate multi-source synthetic logs matching the given scenario."""
    return self.generator.generate(
        scenario=scenario,
        log_types=log_types,
        base_time=base_time,
        custom_system_prompt=custom_system_prompt,
        enrich_gti=enrich_gti,
    )

  def export(
      self,
      scenario: GeneratedScenario,
      destination: Union[str, Path, BaseSink],
      project: Optional[str] = None,
      tag: Optional[str] = None,
      scenario_name: Optional[str] = None,
      labels: Optional[Dict[str, str]] = None,
  ) -> int:
    """Export a generated scenario to a file, network syslog, or webhook."""
    if isinstance(destination, BaseSink):
      return destination.emit(scenario)

    dest_str = str(destination)
    if dest_str.startswith("syslog://"):
      # Parse syslog URL, e.g. syslog://localhost:514?protocol=udp
      host_port = dest_str.replace("syslog://", "").split("?")[0]
      parts = host_port.split(":")
      host = parts[0]
      port = int(parts[1]) if len(parts) > 1 else 514
      sink = SyslogSink(host=host, port=port)
      return sink.emit(scenario)
    elif dest_str.startswith(("secops://", "chronicle://")):
      # Format: secops://[PROJECT:]CUSTOMER_ID[@REGION][?project=...&scenario_name=...]
      import urllib.parse

      parsed_url = urllib.parse.urlparse(dest_str)
      target = parsed_url.netloc or parsed_url.path.lstrip("/")
      query_params = urllib.parse.parse_qs(parsed_url.query)

      region = query_params.get("region", ["us"])[0]
      proj = query_params.get("project", [project])[0]
      tag_val = (
          tag
          or scenario_name
          or query_params.get("tag", [None])[0]
          or query_params.get("scenario_tag", [None])[0]
          or query_params.get("simulation_tag", [None])[0]
          or query_params.get("scenario_name", [None])[0]
      )

      merged_labels = {}
      for k, v in query_params.items():
        if k.startswith("label."):
          label_key = k[6:]
          merged_labels[label_key] = v[0]
      if labels:
        merged_labels.update(labels)

      customer_id = target
      if "@" in target:
        customer_id, reg_part = target.split("@", 1)
        if reg_part:
          region = reg_part
      if ":" in customer_id:
        proj_part, customer_id = customer_id.split(":", 1)
        if proj_part:
          proj = proj_part

      sink = SecOpsSink(
          customer_id=customer_id,
          project_number=proj,
          region=region,
          tag=tag_val,
          labels=merged_labels,
      )
      return sink.emit(scenario)
    elif dest_str.startswith(("http://", "https://")):
      sink = WebhookSink(url=dest_str)
      return sink.emit(scenario)
    else:
      sink = FileSink(output_path=destination)
      return sink.emit(scenario)

  def list_log_types(self) -> List[str]:
    """List all available learned log types."""
    return self.playbook_service.list_available_log_types()

  def get_guide(self, log_type: str) -> Optional[str]:
    """Retrieve schema guide text for a log type."""
    return self.playbook_service.get_guide(log_type)

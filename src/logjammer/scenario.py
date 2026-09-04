"""Scenario persistence and management service for Log Jammer OSS."""

import json
import logging
from pathlib import Path
from typing import List, Optional, Union

from .config import LogJammerConfig
from .models import GeneratedScenario

logger = logging.getLogger(__name__)


class ScenarioService:
  """Manages local caching, listing, loading, and saving of generated scenarios."""

  def __init__(self, config: Optional[LogJammerConfig] = None):
    self.config = config or LogJammerConfig()
    self.scenarios_dir = self.config.scenarios_dir
    self.scenarios_dir.mkdir(parents=True, exist_ok=True)

  def save_scenario(
      self,
      scenario: GeneratedScenario,
      filepath: Optional[Union[str, Path]] = None,
  ) -> Path:
    """Save a scenario object to the local scenario store or specified file path."""
    if filepath:
      target_path = Path(filepath)
    else:
      target_path = self.scenarios_dir / f"{scenario.scenario_id[:8]}.json"

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
      f.write(scenario.to_json())
    return target_path

  def list_scenarios(self) -> List[GeneratedScenario]:
    """List all scenarios saved in the local scenario store, sorted by creation date."""
    scenarios = []
    if not self.scenarios_dir.exists():
      return scenarios

    for p in sorted(
        self.scenarios_dir.glob("*.json"),
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    ):
      try:
        scenarios.append(GeneratedScenario.from_file(p))
      except Exception as e:
        logger.warning("Could not load scenario from %s: %s", p, e)
    return scenarios

  def get_scenario(self, identifier: str) -> Optional[GeneratedScenario]:
    """Find scenario by exact file path, 8-char scenario ID prefix, or filename."""
    # 1. Check if identifier is a direct existing file path
    path_candidate = Path(identifier)
    if path_candidate.exists() and path_candidate.is_file():
      try:
        return GeneratedScenario.from_file(path_candidate)
      except Exception:
        pass

    # 2. Check in scenarios_dir by filename/prefix
    if not self.scenarios_dir.exists():
      return None

    clean_id = identifier.lower().strip()
    for p in sorted(
        self.scenarios_dir.glob("*.json"),
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    ):
      if p.stem.lower().startswith(clean_id):
        try:
          return GeneratedScenario.from_file(p)
        except Exception:
          pass

    # 3. Check scenario_id inside files
    for p in sorted(
        self.scenarios_dir.glob("*.json"),
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    ):
      try:
        sc = GeneratedScenario.from_file(p)
        if sc.scenario_id.lower().startswith(clean_id):
          return sc
      except Exception:
        pass

    return None

  def delete_scenario(self, identifier: str) -> bool:
    """Delete a scenario file by identifier from the store."""
    sc = self.get_scenario(identifier)
    if not sc:
      return False
    file_path = self.scenarios_dir / f"{sc.scenario_id[:8]}.json"
    if file_path.exists():
      file_path.unlink()
      return True
    return False

"""Command-line interface for Log Jammer OSS."""

import argparse
import os
from pathlib import Path
import sys
from typing import List, Optional

try:
  from logjammer.client import LogJammer
  from logjammer.models import LogFormat
  from logjammer.templates import replace_time_templates
except ImportError:
  from .client import LogJammer
  from .models import LogFormat
  from .templates import replace_time_templates


def create_parser() -> argparse.ArgumentParser:
  """Build the top-level argument parser."""
  parser = argparse.ArgumentParser(
      prog="logjammer",
      description="AI-powered synthetic log generator for security testing and SIEM validation.",
  )
  parser.add_argument(
      "--api-key",
      help="Google Gemini API key (defaults to GEMINI_API_KEY environment variable)",
  )
  parser.add_argument(
      "--gti-api-key",
      help="Google Threat Intelligence API key (defaults to GTI_API_KEY environment variable)",
  )
  parser.add_argument(
      "--model",
      default="gemini-3.7-flash",
      help="Gemini model to use (default: gemini-3.7-flash)",
  )
  parser.add_argument(
      "--guides-dir",
      help="Custom directory storing schema guides",
  )

  subparsers = parser.add_subparsers(dest="command", required=True)

  # Command: learn
  learn_p = subparsers.add_parser(
      "learn",
      help="Analyze sample logs to create a reusable schema playbook",
  )
  learn_p.add_argument(
      "--type",
      "-t",
      required=True,
      help="Log type identifier (e.g. OKTA, CS_EDR, MY_CUSTOM_APP)",
  )
  learn_p.add_argument(
      "--sample",
      "-s",
      required=True,
      type=Path,
      help="Path to sample log file or directory of sample files (.json, .log, .raw, .csv)",
  )
  learn_p.add_argument(
      "--output-dir",
      "-o",
      type=Path,
      help="Directory to save the generated playbook",
  )

  # Command: generate
  gen_p = subparsers.add_parser(
      "generate",
      help="Generate synthetic logs for a security scenario",
  )
  gen_p.add_argument(
      "--scenario",
      "-s",
      help="Natural language description of the attack or activity scenario",
  )
  gen_p.add_argument(
      "--types",
      "-t",
      help="Comma-separated log types to generate (e.g. OKTA,CS_EDR,WINEVTLOG). Auto-inferred if omitted with --from-case",
  )
  gen_p.add_argument(
      "--from-case",
      "-c",
      type=Path,
      help="Path to a SOAR/SIEM case report or alert file (e.g. ~/case.txt) to expand with surrounding events",
  )
  gen_p.add_argument(
      "--surround-before",
      default="30m",
      help="Time window before anchor event for pre-incident setup telemetry (default: 30m)",
  )
  gen_p.add_argument(
      "--surround-after",
      default="30m",
      help="Time window after anchor event for post-incident follow-on telemetry (default: 30m)",
  )
  gen_p.add_argument(
      "--outcome",
      choices=["benign", "malicious"],
      default="benign",
      help="Post-incident outcome behavior (default: benign)",
  )
  gen_p.add_argument(
      "--enrich-gti",
      "--gti",
      action="store_true",
      help="Enrich scenario using Google Threat Intelligence (GTI) Agent before generation",
  )
  gen_p.add_argument(
      "--show-gti-enrichment",
      action="store_true",
      help="Display the enriched threat intelligence narrative in the terminal",
  )
  gen_p.add_argument(
      "--output",
      "-o",
      help="Output file path (.jsonl, .log, .json) or destination URI (syslog://host:514, secops://CUSTOMER_ID, https://...)",
  )
  gen_p.add_argument(
      "--project",
      "-p",
      help="Google Cloud Project ID or Project Number (for Google SecOps ingestion)",
  )
  gen_p.add_argument(
      "--scenario-name",
      "--scenario-tag",
      "--tag",
      dest="scenario_name",
      help="Custom tag or scenario name applied to metadata.ingestion_labels (SCENARIO_TAG)",
  )
  gen_p.add_argument(
      "--label",
      "-l",
      action="append",
      help="Custom key=value ingestion label pair (e.g., --label SCENARIO_NAME=office_worker)",
  )
  gen_p.add_argument(
      "--format",
      choices=["auto", "jsonl", "raw", "json"],
      default="auto",
      help="Output formatting style (default: auto based on extension)",
  )

  # Command: list
  subparsers.add_parser(
      "list",
      help="List all available learned log types",
  )

  # Command: show-guide
  show_p = subparsers.add_parser(
      "show-guide",
      help="Display the schema guide for a specific log type",
  )
  show_p.add_argument(
      "--type",
      "-t",
      required=True,
      help="Log type identifier",
  )

  # Command: replay
  replay_p = subparsers.add_parser(
      "replay",
      help="Replay a pre-generated scenario from local storage or JSON file without calling LLM",
  )
  replay_p.add_argument(
      "--scenario",
      "-s",
      required=True,
      help="Scenario ID prefix (e.g. 'a1b2c3d4') or path to scenario .json file",
  )
  replay_p.add_argument(
      "--output",
      "-o",
      required=True,
      help="Output file path (.jsonl, .log, .json) or destination URI (syslog://..., secops://...)",
  )
  replay_p.add_argument(
      "--project",
      "-p",
      help="Google Cloud Project ID or Project Number (for Google SecOps ingestion)",
  )
  replay_p.add_argument(
      "--scenario-name",
      "--scenario-tag",
      "--tag",
      dest="scenario_name",
      help="Custom tag or scenario name applied to metadata.ingestion_labels (SCENARIO_TAG)",
  )
  replay_p.add_argument(
      "--label",
      "-l",
      action="append",
      help="Custom key=value ingestion label pair (e.g. --label SCENARIO_NAME=office_worker)",
  )

  # Command: scenario / scenarios
  for cmd_name in ("scenario", "scenarios"):
    sc_p = subparsers.add_parser(
        cmd_name,
        help="Manage locally saved synthetic scenarios (list, show, save, delete)",
    )
    sc_sub = sc_p.add_subparsers(dest="scenario_action", required=False)

    # scenario list
    sc_sub.add_parser("list", help="List all saved scenarios in ~/.logjammer/scenarios/")

    # scenario show
    show_sc_p = sc_sub.add_parser("show", help="Display details of a saved scenario")
    show_sc_p.add_argument("id", help="Scenario ID or prefix")

    # scenario save
    save_sc_p = sc_sub.add_parser("save", help="Save / export scenario JSON file")
    save_sc_p.add_argument("id", help="Scenario ID or prefix")
    save_sc_p.add_argument("--output", "-o", required=True, help="Destination filepath or directory")

    # scenario delete
    del_sc_p = sc_sub.add_parser("delete", help="Delete a scenario from local store")
    del_sc_p.add_argument("id", help="Scenario ID or prefix")

  return parser


def main(args: Optional[List[str]] = None) -> int:
  """Main CLI execution routine."""
  parser = create_parser()
  parsed = parser.parse_args(args)

  if not parsed.command:
    parser.print_help()
    return 0

  try:
    client = LogJammer(
        api_key=parsed.api_key,
        gti_api_key=getattr(parsed, "gti_api_key", None),
        model=parsed.model,
        guides_dir=parsed.guides_dir,
    )
  except Exception as e:
    print(f"Configuration Error: {e}", file=sys.stderr)
    return 1

  if parsed.command == "learn":
    if not parsed.sample.exists():
      print(f"Error: Sample path '{parsed.sample}' does not exist.", file=sys.stderr)
      return 1

    target_type = "directory" if parsed.sample.is_dir() else "file"
    print(f"Analyzing sample {target_type} '{parsed.sample}' for log type '{parsed.type}' with {parsed.model}...")
    try:
      result = client.learn(parsed.type, parsed.sample, output_dir=parsed.output_dir)
      print("Successfully generated schema playbook!")
      print(f"  - Log Type: {result.log_type}")
      print(f"  - Files Analyzed: {result.files_analyzed}")
      print(f"  - Total Lines Analyzed: {result.sample_count}")
      print(f"  - Saved to: {result.guide_path}")
      return 0
    except Exception as e:
      print(f"\n[Error] Failed to learn log schema:\n{e}", file=sys.stderr)
      return 1

  elif parsed.command == "generate":
    if not parsed.scenario and not getattr(parsed, "from_case", None):
      print("Error: Please provide either --scenario or --from-case.", file=sys.stderr)
      return 1

    enrich_gti = getattr(parsed, "enrich_gti", False)
    if enrich_gti:
      print("[GTI Agent] Querying Google Threat Intelligence Agent for real-world threat model & indicators...")

    try:
      if getattr(parsed, "from_case", None):
        case_file = Path(parsed.from_case).expanduser()
        if not case_file.exists():
          print(f"Error: Case file '{case_file}' does not exist.", file=sys.stderr)
          return 1
        case_text = case_file.read_text(encoding="utf-8")

        if parsed.types:
          log_types = [t.strip() for t in parsed.types.split(",") if t.strip()]
        else:
          print("Analyzing case report to infer required SIEM log types...")
          log_types = client.infer_log_types(case_text)
          print(f"  • Inferred Log Types: {', '.join(log_types)}")

        print(f"Expanding case scenario from '{case_file}'...")
        print(f"  • Pre-Incident Window:  -{parsed.surround_before}")
        print(f"  • Post-Incident Window: +{parsed.surround_after}")
        print(f"  • Post-Incident Outcome: {parsed.outcome}")

        scenario = client.generate_from_case(
            case_text=case_text,
            log_types=log_types,
            surround_before=parsed.surround_before,
            surround_after=parsed.surround_after,
            outcome=parsed.outcome,
            enrich_gti=enrich_gti,
        )
      else:
        if not parsed.types:
          print("Error: Please specify at least one log type via --types.", file=sys.stderr)
          return 1
        log_types = [t.strip() for t in parsed.types.split(",") if t.strip()]
        print(f"Generating scenario with {len(log_types)} log source(s)...")
        print(f"  Scenario: {parsed.scenario}")
        print(f"  Log Types: {', '.join(log_types)}")

        scenario = client.generate(
            scenario=parsed.scenario,
            log_types=log_types,
            enrich_gti=enrich_gti,
        )

      if scenario.enriched_narrative and getattr(parsed, "show_gti_enrichment", False):
        print("\n" + "=" * 60)
        print("GOOGLE THREAT INTELLIGENCE (GTI) ENRICHED SCENARIO")
        print("=" * 60)
        print(scenario.enriched_narrative)
        print("=" * 60)

      sc_path = client.config.scenarios_dir / f"{scenario.scenario_id[:8]}.json"
      print(f"Scenario saved to local store: {sc_path}")
      print(f"Replay anytime without LLM: logjammer replay -s {scenario.scenario_id[:8]} -o <DESTINATION>")

      if parsed.output:
        labels_dict = {}
        if getattr(parsed, "label", None):
          for item in parsed.label:
            if "=" in item:
              k, v = item.split("=", 1)
              labels_dict[k.strip()] = v.strip()

        count = client.export(
            scenario,
            parsed.output,
            project=parsed.project,
            scenario_name=getattr(parsed, "scenario_name", None),
            labels=labels_dict,
        )
        print(f"\nExported {count} logs to {parsed.output}")

        if parsed.output.startswith(("secops://", "chronicle://")):
          scenario_tag = (
              getattr(parsed, "scenario_name", None)
              or os.environ.get("CHRONICLE_TAG")
              or os.environ.get("CHRONICLE_SCENARIO_TAG")
              or os.environ.get("CHRONICLE_SCENARIO_NAME")
              or f"logjammer-{scenario.scenario_id[:8]}"
          )
          print("\n" + "=" * 60)
          print("GOOGLE SECOPS (CHRONICLE) INGESTION DETAILS")
          print("=" * 60)
          print("Ingestion Labels Applied:")
          print("  • SOURCE:        LOGJAMMER")
          print(f"  • SCENARIO_ID:   {scenario.scenario_id[:8]}")
          print(f"  • SCENARIO_TAG:  {scenario_tag}")
          if labels_dict:
            for lk, lv in labels_dict.items():
              print(f"  • {lk}: {lv}")
          print("\nHow to Query in Google SecOps:")
          print("  • UDM Search Filter (by Scenario ID):")
          print(
              '    metadata.ingestion_labels.key = "SCENARIO_ID" AND'
              f' metadata.ingestion_labels.value = "{scenario.scenario_id[:8]}"'
          )
          print("  • UDM Search Filter (by Scenario Tag / Name):")
          print(
              '    metadata.ingestion_labels.key = "SCENARIO_TAG" AND'
              f' metadata.ingestion_labels.value = "{scenario_tag}"'
          )
          if labels_dict:
            for lk, lv in labels_dict.items():
              print(
                  f'  • UDM Search Filter (by {lk}):\n'
                  f'    metadata.ingestion_labels.key = "{lk}" AND'
                  f' metadata.ingestion_labels.value = "{lv}"'
              )
          print("  • Raw Log Search:")
          print(f'    "{scenario.scenario_id[:8]}"')
          print("=" * 60)
      else:
        # Print directly to stdout
        for log_type, entries in scenario.logs.items():
          print(f"\n--- {log_type} ({len(entries)} events) ---")
          for entry in entries:
            print(entry.content)
      return 0
    except Exception as e:
      print(f"\n[Error] Failed to generate logs:\n{e}", file=sys.stderr)
      return 1

  elif parsed.command == "replay":
    labels_dict = {}
    if getattr(parsed, "label", None):
      for item in parsed.label:
        if "=" in item:
          k, v = item.split("=", 1)
          labels_dict[k.strip()] = v.strip()

    try:
      sc = client.get_scenario(parsed.scenario)
      if not sc:
        print(f"[Error] Could not find saved scenario matching '{parsed.scenario}'.", file=sys.stderr)
        print("Run 'logjammer scenario list' to view available saved scenarios.", file=sys.stderr)
        return 1

      print(f"Replaying Scenario [{sc.scenario_id[:8]}]: {sc.description}")
      count = client.replay(
          scenario=sc,
          destination=parsed.output,
          project=parsed.project,
          scenario_name=getattr(parsed, "scenario_name", None),
          labels=labels_dict,
      )
      print(f"Replayed {count} logs to {parsed.output} without LLM execution.")
      return 0
    except Exception as e:
      print(f"\n[Error] Replay failed:\n{e}", file=sys.stderr)
      return 1

  elif parsed.command in ("scenario", "scenarios"):
    action = getattr(parsed, "scenario_action", None) or "list"

    if action == "list":
      scenarios = client.list_scenarios()
      if not scenarios:
        print("No saved scenarios found.")
        print("Generate your first scenario using 'logjammer generate -s ... -t ...'")
      else:
        print(f"Saved Scenarios ({len(scenarios)} in {client.config.scenarios_dir}):\n")
        print(f"{'ID':<10} {'CREATED AT':<20} {'EVENTS':<8} {'DESCRIPTION'}")
        print("-" * 75)
        for s in scenarios:
          created_str = s.created_at.strftime("%Y-%m-%d %H:%M:%S")
          desc_short = (s.description[:35] + "...") if len(s.description) > 38 else s.description
          print(f"{s.scenario_id[:8]:<10} {created_str:<20} {s.total_log_count:<8} {desc_short}")
      return 0

    elif action == "show":
      sc = client.get_scenario(parsed.id)
      if not sc:
        print(f"[Error] Scenario '{parsed.id}' not found.", file=sys.stderr)
        return 1
      print("=" * 60)
      print(f"SCENARIO DETAILS: {sc.scenario_id[:8]}")
      print("=" * 60)
      print(f"ID:          {sc.scenario_id}")
      print(f"Created At:  {sc.created_at.isoformat()}")
      print(f"Total Logs:  {sc.total_log_count}")
      print(f"Description: {sc.description}")
      if sc.enriched_narrative:
        print("\nThreat Intelligence Narrative:")
        print(sc.enriched_narrative)
      print("\nLog Source Breakdown:")
      for lt, entries in sc.logs.items():
        print(f"  • {lt}: {len(entries)} events")
      print("=" * 60)
      return 0

    elif action == "save":
      sc = client.get_scenario(parsed.id)
      if not sc:
        print(f"[Error] Scenario '{parsed.id}' not found.", file=sys.stderr)
        return 1
      out_path = Path(parsed.output)
      if out_path.is_dir():
        out_path = out_path / f"{sc.scenario_id[:8]}.json"
      saved_path = client.save_scenario(sc, filepath=out_path)
      print(f"Saved scenario {sc.scenario_id[:8]} to {saved_path}")
      return 0

    elif action == "delete":
      success = client.delete_scenario(parsed.id)
      if success:
        print(f"Deleted scenario '{parsed.id}'.")
      else:
        print(f"[Error] Could not find scenario '{parsed.id}' to delete.", file=sys.stderr)
        return 1
      return 0

  elif parsed.command == "list":
    types_list = client.list_log_types()
    if not types_list:
      print("No schema playbooks found.")
      print("Use 'logjammer learn --type <NAME> --sample <FILE>' to analyze your first log sample.")
    else:
      print(f"Available Log Types ({len(types_list)}):")
      for t in types_list:
        print(f"  - {t}")
    return 0

  elif parsed.command == "show-guide":
    guide = client.get_guide(parsed.type)
    if not guide:
      print(f"No schema guide found for log type '{parsed.type}'.", file=sys.stderr)
      return 1
    print(f"=== Schema Guide for {parsed.type} ===")
    print(guide)
    return 0

  return 0


if __name__ == "__main__":
  sys.exit(main())

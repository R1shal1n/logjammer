# Log Jammer (Open Source Edition)

AI-Powered Synthetic Log Generator for Security Testing, Detection Engineering, and SIEM Validation.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

---

## ⚡ Overview

**Log Jammer** is an open-source framework that creates realistic, multi-source synthetic log events driven by **Google Gemini 3.7 Flash**. It empowers detection engineers, purple teams, and security researchers to simulate complex attack chains across custom and standard log formats without needing live attack infrastructure.

---

## 🚀 Key Features

- **Learn Any Custom Schema**: Provide raw sample logs (`.json`, `.log`, `.csv`, `.raw`) from internal services, custom firewalls, or niche appliances. Log Jammer analyzes the structure and produces an AI schema playbook.
- **Natural Language Attack Scenarios**: Describe full attack chains in plain English (e.g., *"Spear-phishing email with PDF attachment leading to credential dumping via Mimikatz and S3 exfiltration"*).
- **Dynamic Relative Time Templating**: Automatically resolves chronological offsets (e.g. `##$TimeStamp-0d2h15m0s$##` $\to$ ISO 8601 timestamps) ensuring events tell a coherent chronological story.
- **Pluggable Output Sinks**: Export generated events directly to **JSONL files**, **Syslog (UDP/TCP/TLS)**, **SIEM Webhooks (Splunk HEC, Elastic, Chronicle)**, or **stdout**.
- **Pure Python SDK & CLI**: Zero infrastructure dependencies—run locally with standard `GEMINI_API_KEY`.

## 📦 Installation

### Option 1: Install via PyPI
```bash
pip install logjammer
```

### Option 2: Install from Source (GitHub)
```bash
git clone https://github.com/your-org/logjammer.git
cd logjammer
pip install -r requirements.txt
pip install -e .
```

---

## ⚙️ Configuration & Environment Variables

Log Jammer uses **environment variables** or command-line options for configuration. No dedicated `.conf` or `.ini` file is required.

| Environment Variable | Description | Default / Fallback |
| --- | --- | --- |
| `GEMINI_API_KEY` | **Required**. Google Gemini API Key for log learning and generation. | CLI `--api-key` |
| `GTI_API_KEY` (or `VIRUSTOTAL_API_KEY`) | Google Threat Intelligence / VirusTotal API Key for `--enrich-gti`. | CLI `--gti-api-key` |
| `SECOPS_CUSTOMER_ID` / `CHRONICLE_CUSTOMER_ID` | Google SecOps / Chronicle Instance Customer ID for direct log replay. | URI `secops://CUSTOMER_ID` |
| `GCP_PROJECT_NUMBER` / `GOOGLE_CLOUD_PROJECT` | GCP Project ID or Number for Google SecOps `v1alpha` API ingestion. | CLI `--project` |
| `CHRONICLE_REGION` | Google SecOps API region (`us`, `europe-west1`, `asia-east1`, etc.). | `us` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP Service Account JSON credentials for SecOps authentication. | `gcloud` ADC |
| `LOGJAMMER_MODEL` | Gemini model to use for schema learning and generation. | `gemini-3.7-flash` |
| `LOGJAMMER_GUIDES_DIR` | Path to directory storing learned AI schema guide playbooks. | `~/.logjammer/guides` |

---

## 🛠️ CLI Quickstart

### 1. Learn a Custom Log Schema
Feed a sample file OR an entire directory containing multiple sample event files (e.g., `login.json`, `privilege_change.json`):
```bash
# Learn from a single sample file
logjammer learn --type CUSTOM_AUTH --sample ./samples/auth/login.json

# Or learn from an entire directory of diverse event samples
logjammer learn --type OKTA --sample ./samples/identity/okta/
```

### 2. List & Inspect Learned Guides
```bash
# List all available learned log types
logjammer list

# Display the AI schema guide playbook for a log type
logjammer show-guide --type OKTA
```

### 3. Generate Synthetic Attack Logs
Generate multi-source attack logs and save to a JSONL file:
```bash
logjammer generate \
  --scenario "Brute force attack on admin portal followed by privilege escalation and MFA bypass" \
  --types CUSTOM_AUTH,WINEVTLOG \
  --output ./attack_scenario.jsonl
```

### 4. Enrich Scenario with Google Threat Intelligence (GTI)
Use the GTI Agent to enrich your prompt with real-world IOCs, commands, and MITRE ATT&CK techniques before generation:
```bash
export GTI_API_KEY="your-gti-api-key"

logjammer generate \
  --scenario "BlackSuit ransomware infection and lateral movement" \
  --types WINDOWS_SYSMON,WINDOWS_DNS \
  --enrich-gti \
  --show-gti-enrichment \
  --output ./ransomware_simulation.jsonl
```

### 5. Replay Directly to Google SecOps (Chronicle) or Syslog
```bash
# Stream directly to network Syslog (UDP/TCP)
logjammer generate \
  --scenario "Port scan followed by SQL injection" \
  --types PAN_FIREWALL,APACHE \
  --output syslog://siem.corp.internal:514

# Replay directly into Google SecOps (Chronicle) SIEM
logjammer generate \
  --scenario "Phishing email leading to credential dumping" \
  --types OFFICE_365,WINDOWS_SYSMON \
  --output secops://YOUR_SECOPS_CUSTOMER_ID@us \
  --project YOUR_GCP_PROJECT_ID
```

---

## 🐍 Python SDK Usage

```python
import logjammer

# 1. Initialize client
client = logjammer.LogJammer()

# 2. Learn a custom log format from a file
client.learn(
    log_type="PAYMENT_GATEWAY",
    sample="sample_payment_logs.json"
)

# 3. Generate a scenario (optionally enriched with GTI)
scenario = client.generate(
    scenario="Failed login bursts from TOR exit nodes followed by successful API token creation",
    log_types=["PAYMENT_GATEWAY", "OKTA"],
    enrich_gti=True
)

# 4. Export to file or SIEM (JSONL, Syslog, Webhook, SecOps)
client.export(scenario, destination="secops://YOUR_SECOPS_CUSTOMER_ID@us", project="YOUR_GCP_PROJECT")
print(f"Generated and ingested {scenario.total_log_count} realistic events into Google SecOps!")
```

---

## 🧪 Testing

Run test suite:
```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

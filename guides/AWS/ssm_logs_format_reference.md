# AWS Systems Manager Session Manager Logs Format Reference

## Overview
Shell session logs from SSM Session Manager showing commands executed on EC2 instances.

## Format
**Type**: JSONL (CloudTrail + command logs)  
**File Extension**: `.jsonl`

## Example - Session Start
```json
{
  "eventName": "StartSession",
  "eventSource": "ssm.amazonaws.com",
  "requestParameters": {
    "target": "i-1234567890abcdef0",
    "documentName": "AWS-StartInteractiveCommand"
  },
  "responseElements": {
    "sessionId": "user-abc123def456"
  }
}
```

## Command Log
```json
{
  "timestamp": "2025-11-03T15:30:00Z",
  "sessionId": "user-abc123def456",
  "user": "admin",
  "command": "whoami",
  "exitCode": 0
}
```

## Attack Indicators
- Privilege escalation commands (sudo -l, cat /etc/shadow)
- Credential harvesting (cat ~/.aws/credentials)
- Persistence mechanisms (crontab, authorized_keys)
- Data exfiltration (tar, curl to external IP)
- Reverse shell commands

## MITRE ATT&CK
- T1078: Valid Accounts (SSM access)
- T1552: Unsecured Credentials (credential harvesting)
- T1053: Scheduled Task/Job (cron persistence)
- T1071: Application Layer Protocol (reverse shell)

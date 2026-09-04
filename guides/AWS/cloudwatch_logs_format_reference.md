# AWS CloudWatch Logs Format Reference

## Overview
Application logs from AWS services and custom applications.

## Format
**Type**: JSON  
**File Extension**: `.jsonl`

## Example
```json
{
  "timestamp": 1699027800000,
  "message": "[INFO] 2025-11-03T15:30:00Z API request processed",
  "logGroup": "/aws/application/api-service",
  "logStream": "api-server-1"
}
```

## Use Cases
- Application debugging
- API request tracking
- Error monitoring
- Security event correlation

## Attack Indicators
- SQL injection errors
- XSS attempts in input
- Brute force login patterns
- Large data access patterns
- Privilege escalation errors

## MITRE ATT&CK
- T1190: Exploit Public-Facing Application
- T1110: Brute Force

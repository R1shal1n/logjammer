# AWS DynamoDB CloudTrail Logs Format Reference

## Overview
DynamoDB operations captured via CloudTrail. Detects data access patterns, table deletions, and unauthorized operations.

## Format
**Type**: JSONL (CloudTrail format)  
**File Extension**: `.jsonl`

## Example - Scan Operation (Data Exfiltration)
```json
{
  "eventSource": "dynamodb.amazonaws.com",
  "eventName": "Scan",
  "requestParameters": {
    "tableName": "Users"
  },
  "readOnly": true,
  "resources": [{
    "type": "AWS::DynamoDB::Table",
    "ARN": "arn:aws:dynamodb:us-east-1:123456789012:table/Users"
  }]
}
```

## Attack Indicators
- **Scan without limit**: Full table data exfiltration
- **BatchGetItem**: Bulk data access
- **DeleteTable**: Destructive operation
- **UpdateItem with admin attributes**: Backdoor account creation

## MITRE ATT&CK
- T1530: Data from Cloud Storage (Scan operations)
- T1485: Data Destruction (DeleteTable)

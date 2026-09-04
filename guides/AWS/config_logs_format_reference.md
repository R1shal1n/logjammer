# AWS Config Logs Format Reference

## Overview
Configuration changes and compliance evaluations for AWS resources.

## Format
**Type**: JSONL  
**File Extension**: `.jsonl`

## Example - Compliance Violation
```json
{
  "version": "1.1",
  "configRuleName": "s3-bucket-public-read-prohibited",
  "resourceType": "AWS::S3::Bucket",
  "resourceId": "sensitive-data-bucket",
  "complianceType": "NON_COMPLIANT",
  "annotation": "S3 bucket allows public read access",
  "resultRecordedTime": "2025-11-03T15:30:00Z"
}
```

## Compliance Types
- COMPLIANT
- NON_COMPLIANT
- NOT_APPLICABLE
- INSUFFICIENT_DATA

## Attack Indicators
- S3 bucket made public
- CloudTrail disabled
- Unencrypted volumes
- Overly permissive security groups
- IAM policy granting *:*

## MITRE ATT&CK
- T1562.008: Disable Cloud Logs (CloudTrail disabled)
- T1537: Transfer Data to Cloud Account (Public S3)

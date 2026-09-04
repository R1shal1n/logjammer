# AWS STS (Security Token Service) Logs Format Reference

## Overview

AWS STS logs (captured via CloudTrail) record temporary credential operations including role assumptions, cross-account access, and federated authentication. Critical for detecting privilege escalation and unauthorized access patterns.

## Format

**Type**: JSONL (CloudTrail format)
**File Extension**: `.jsonl`
**Use Case**: Privilege escalation detection, role abuse monitoring, cross-account activity tracking

## Log Structure

```json
{
  "eventVersion": "1.08",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "AIDAEXAMPLEID",
    "arn": "arn:aws:iam::123456789012:user/admin-user",
    "accountId": "123456789012",
    "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
    "userName": "admin-user"
  },
  "eventTime": "2025-11-03T15:30:00Z",
  "eventSource": "sts.amazonaws.com",
  "eventName": "AssumeRole",
  "awsRegion": "us-east-1",
  "sourceIPAddress": "203.0.113.5",
  "userAgent": "aws-cli/2.13.5 Python/3.11.4",
  "requestParameters": {
    "roleArn": "arn:aws:iam::123456789012:role/AdminRole",
    "roleSessionName": "admin-session",
    "durationSeconds": 3600
  },
  "responseElements": {
    "credentials": {
      "accessKeyId": "ASIATEMP123EXAMPLE",
      "expiration": "REDACTED",
      "sessionToken": "REDACTED"
    },
    "assumedRoleUser": {
      "assumedRoleId": "AROAEXAMPLE:admin-session",
      "arn": "arn:aws:sts::123456789012:assumed-role/AdminRole/admin-session"
    }
  },
  "requestID": "abcd1234-5678-90ef-ghij-klmnopqrstuv",
  "eventID": "12345678-abcd-ef12-3456-789012345678",
  "readOnly": false,
  "eventType": "AwsApiCall",
  "managementEvent": true,
  "recipientAccountId": "123456789012"
}
```

## Key Event Types

### AssumeRole
Standard role assumption for privilege elevation.

### AssumeRoleWithSAML
Federated authentication via SAML provider.
```json
{
  "eventName": "AssumeRoleWithSAML",
  "userIdentity": {
    "type": "SAMLUser",
    "identityProvider": "ExampleCorp-SAML"
  },
  "requestParameters": {
    "sAMLAssertionID": "assertion-id",
    "roleArn": "arn:aws:iam::123456789012:role/FederatedRole",
    "principalArn": "arn:aws:iam::123456789012:saml-provider/ExampleCorp"
  }
}
```

### GetSessionToken
Temporary credential generation (often with MFA).
```json
{
  "eventName": "GetSessionToken",
  "requestParameters": {
    "durationSeconds": 43200,
    "serialNumber": "arn:aws:iam::123456789012:mfa/user",
    "tokenCode": "REDACTED"
  }
}
```

### Cross-Account AssumeRole
```json
{
  "requestParameters": {
    "roleArn": "arn:aws:iam::999888777666:role/CrossAccountRole",
    "externalId": "unique-external-id"
  },
  "recipientAccountId": "999888777666",
  "sharedEventID": "shared-event-id"
}
```

## Attack Scenarios

### Role Chaining (Privilege Escalation)
```json
{
  "userIdentity": {
    "type": "AssumedRole",
    "principalId": "AROAEXAMPLE:low-privilege-session",
    "arn": "arn:aws:sts::123456789012:assumed-role/ReadOnlyRole/low-privilege-session",
    "sessionContext": {
      "sessionIssuer": {
        "type": "Role",
        "principalId": "AROAEXAMPLE",
        "arn": "arn:aws:iam::123456789012:role/ReadOnlyRole"
      }
    }
  },
  "eventName": "AssumeRole",
  "requestParameters": {
    "roleArn": "arn:aws:iam::123456789012:role/AdminRole"
  }
}
```

## MITRE ATT&CK Mapping

| Event Type | MITRE Technique | Description |
|------------|-----------------|-------------|
| AssumeRole (elevated) | T1098.001 - Additional Cloud Credentials | Privilege escalation via role |
| AssumeRoleWithSAML | T1078.004 - Valid Accounts: Cloud | Federated authentication abuse |
| Cross-Account AssumeRole | T1550.001 - Use Alternate Authentication Material | Cross-account lateral movement |

## Detection Queries

### Find role chaining
```bash
cat sts_logs.jsonl | jq 'select(.userIdentity.type == "AssumedRole" and .eventName == "AssumeRole")'
```

### Cross-account activity
```bash
cat sts_logs.jsonl | jq 'select(.recipientAccountId != .userIdentity.accountId)'
```

## References

- [AWS STS API Reference](https://docs.aws.amazon.com/STS/latest/APIReference/)
- [CloudTrail STS Events](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-aws-sts.html)

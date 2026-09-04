# AWS Cognito User Pool Logs Format Reference

## Overview

AWS Cognito User Pool logs capture authentication and user management events for applications using Cognito for identity management. These logs are essential for monitoring authentication patterns, detecting account takeover attempts, and investigating security incidents.

## Format

**Type**: JSONL (JSON Lines)
**File Extension**: `.jsonl`
**Use Case**: Authentication monitoring, fraud detection, user behavior analysis

## Log Structure

```json
{
  "version": "1",
  "userPoolId": "us-east-1_abc123def",
  "clientId": "abcdefghijklmnopqrstuvwxyz",
  "eventType": "SignIn",
  "eventId": "12345678-1234-5678-1234-567812345678",
  "timestamp": "2025-11-03T15:30:00Z",
  "request": {
    "userAttributes": {
      "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "email": "user@example.com",
      "email_verified": "true"
    },
    "validationData": {},
    "clientMetadata": {}
  },
  "response": {
    "statusCode": 200,
    "message": "Authentication successful"
  },
  "callerContext": {
    "sourceIp": "203.0.113.5",
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  },
  "mfaUsed": true,
  "authenticationMethod": "USER_PASSWORD_AUTH"
}
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Log format version |
| `userPoolId` | string | Cognito user pool identifier |
| `clientId` | string | Application client ID |
| `eventType` | string | Event type (SignIn, SignUp, ForgotPassword, etc.) |
| `eventId` | string | Unique event identifier (UUID) |
| `timestamp` | string | Event timestamp (ISO 8601) |
| `request.userAttributes.sub` | string | User's unique identifier (UUID) |
| `request.userAttributes.email` | string | User's email address |
| `response.statusCode` | integer | HTTP status code (200, 401, 403, etc.) |
| `response.message` | string | Response message |
| `callerContext.sourceIp` | string | Client IP address |
| `callerContext.userAgent` | string | Client user agent string |
| `mfaUsed` | boolean | Whether MFA was used |
| `authenticationMethod` | string | Authentication method used |

## Event Types

### SignIn
Successful or failed user sign-in attempt.
```json
{
  "eventType": "SignIn",
  "response": {
    "statusCode": 200,
    "message": "Authentication successful"
  }
}
```

### ForgotPassword
Password reset request.
```json
{
  "eventType": "ForgotPassword",
  "response": {
    "statusCode": 200,
    "message": "Password reset code sent"
  }
}
```

### RiskDecision
Advanced security risk assessment (account takeover detection).
```json
{
  "eventType": "RiskDecision",
  "response": {
    "statusCode": 403,
    "message": "Account takeover risk detected",
    "riskLevel": "HIGH",
    "riskDecision": "BLOCK"
  },
  "riskDecisionMetadata": {
    "ipAddressReputation": "LOW",
    "deviceFingerprint": "unknown",
    "locationAnomaly": true,
    "velocityCheck": "FAILED"
  }
}
```

### RespondToAuthChallenge
MFA challenge response.
```json
{
  "eventType": "RespondToAuthChallenge",
  "request": {
    "challengeName": "SMS_MFA"
  },
  "mfaUsed": true,
  "mfaMethod": "SMS_MFA"
}
```

### TokenRefresh
Access token refresh operation.
```json
{
  "eventType": "TokenRefresh",
  "response": {
    "statusCode": 200,
    "message": "Token refreshed successfully"
  }
}
```

## Attack Detection Patterns

### Credential Stuffing
```json
{
  "eventType": "SignIn",
  "response": {
    "statusCode": 429,
    "message": "Too many failed authentication attempts"
  },
  "failureReason": "Rate limit exceeded",
  "riskDecisionMetadata": {
    "attemptCount": 150,
    "timeWindow": "5 minutes"
  }
}
```

### Account Takeover
```json
{
  "eventType": "RiskDecision",
  "response": {
    "riskLevel": "HIGH",
    "riskDecision": "BLOCK"
  },
  "riskDecisionMetadata": {
    "ipAddressReputation": "LOW",
    "locationAnomaly": true
  }
}
```

## MITRE ATT&CK Mapping

| Event Type | MITRE Technique | Description |
|------------|-----------------|-------------|
| Failed SignIn | T1110 - Brute Force | Multiple failed authentication attempts |
| RiskDecision (BLOCK) | T1078 - Valid Accounts | Account takeover attempt detected |
| Rate Limit Exceeded | T1110.003 - Password Spraying | Credential stuffing attack |
| MFA Bypass | T1556 - Modify Authentication Process | MFA challenge failures |

## Example Usage

### Query failed logins
```bash
cat cognito_logs.jsonl | jq 'select(.response.statusCode != 200 and .eventType == "SignIn")'
```

### Count events by type
```bash
cat cognito_logs.jsonl | jq -r '.eventType' | sort | uniq -c
```

### Find high-risk decisions
```bash
cat cognito_logs.jsonl | jq 'select(.eventType == "RiskDecision" and .response.riskLevel == "HIGH")'
```

## References

- [AWS Cognito User Pool Logs](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-logs.html)
- [Cognito Advanced Security](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pool-settings-advanced-security.html)

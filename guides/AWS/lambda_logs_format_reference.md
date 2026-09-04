# AWS Lambda CloudWatch Logs Format Reference

## Overview
Lambda function execution logs including invocations, errors, and application output.

## Format
**Type**: Text (tab-delimited)  
**File Extension**: `.log`

## Example
```
2025-11-03T15:30:00Z    abc123-def456-789    START RequestId: abc123-def456-789 Version: $LATEST
2025-11-03T15:30:00Z    abc123-def456-789    INFO    Processing request
2025-11-03T15:30:01Z    abc123-def456-789    END RequestId: abc123-def456-789
2025-11-03T15:30:01Z    abc123-def456-789    REPORT RequestId: abc123-def456-789 Duration: 1250.00 ms Billed Duration: 1300 ms Memory Size: 512 MB Max Memory Used: 256 MB
```

## Log Types
- **START**: Invocation started
- **END**: Invocation completed
- **REPORT**: Performance metrics
- **ERROR**: Application errors
- **Application logs**: Custom output (INFO, WARN, ERROR)

## Attack Indicators
- Timeout with high CPU: Crypto mining
- External connections to unknown IPs: Data exfiltration
- Command injection errors: Code injection attempts

## MITRE ATT&CK
- T1496: Resource Hijacking (Crypto mining causing timeouts)
- T1204: User Execution (Malicious code injection)

# AWS WAF Logs Format Reference

Complete specification for AWS WAF (Web Application Firewall) logs.

## Overview

AWS WAF logs capture detailed information about web requests that are analyzed by your web access control lists (web ACLs). These logs include information about rules that matched the request and the action taken.

## Format

- **Format**: JSON (one log entry per request)
- **Delivery**: Amazon Kinesis Data Firehose to S3, Redshift, or Elasticsearch
- **Format Version**: Currently 1
- **Encoding**: UTF-8

## Complete Log Entry Structure

### Top-Level Fields

| Field | Type | Description | Always Present |
|-------|------|-------------|----------------|
| **timestamp** | Number | Unix epoch timestamp in milliseconds | Yes |
| **formatVersion** | Number | Format version (currently 1) | Yes |
| **webaclId** | String | ARN of the web ACL | Yes |
| **terminatingRuleId** | String | ID of the rule that terminated the request | Yes |
| **terminatingRuleType** | String | Type of terminating rule | Yes |
| **action** | String | Action taken (ALLOW, BLOCK, COUNT, CAPTCHA, CHALLENGE) | Yes |
| **terminatingRuleMatchDetails** | Array | Details about the terminating rule match | Yes |
| **httpSourceName** | String | Source of HTTP request (ALB, APIGW, CLOUDFRONT) | Yes |
| **httpSourceId** | String | ID of the HTTP source | Yes |
| **ruleGroupList** | Array | List of rule groups that matched | Yes |
| **rateBasedRuleList** | Array | List of rate-based rules that matched | Yes |
| **nonTerminatingMatchingRules** | Array | Non-terminating rules that matched | Yes |
| **requestHeadersInserted** | Array | Headers inserted by WAF | No |
| **responseCodeSent** | Number | HTTP response code sent to client | No |
| **httpRequest** | Object | Details about the HTTP request | Yes |
| **labels** | Array | Labels applied to the request | No |
| **captchaResponse** | Object | CAPTCHA challenge response details | No |
| **challengeResponse** | Object | Challenge response details | No |
| **ja3Fingerprint** | String | JA3 TLS fingerprint | No |

### Action Values

| Action | Description |
|--------|-------------|
| **ALLOW** | Request allowed to proceed to resource |
| **BLOCK** | Request blocked, returns 403 Forbidden |
| **COUNT** | Request counted but allowed (monitoring mode) |
| **CAPTCHA** | CAPTCHA challenge issued |
| **CHALLENGE** | Silent challenge issued |

### Terminating Rule Types

| Type | Description |
|------|-------------|
| **REGULAR** | Standard rule |
| **RATE_BASED** | Rate-limiting rule |
| **MANAGED_RULE_GROUP** | AWS or third-party managed rule |
| **GROUP** | Customer rule group |

### httpRequest Object

```json
{
  "httpRequest": {
    "clientIp": "192.0.2.1",
    "country": "US",
    "headers": [
      {
        "name": "Host",
        "value": "example.com"
      },
      {
        "name": "User-Agent",
        "value": "Mozilla/5.0..."
      },
      {
        "name": "Accept",
        "value": "text/html,application/xhtml+xml"
      }
    ],
    "uri": "/api/login",
    "args": "username=admin&password=test",
    "httpVersion": "HTTP/1.1",
    "httpMethod": "POST",
    "requestId": "FGK3K8E5VJG30QVJ9EXAMPLE"
  }
}
```

**httpRequest Fields:**
| Field | Type | Description |
|-------|------|-------------|
| **clientIp** | String | IP address of the client |
| **country** | String | Two-letter country code (ISO 3166-1 alpha-2) |
| **headers** | Array | HTTP request headers (name/value pairs) |
| **uri** | String | URI of the request |
| **args** | String | Query string parameters |
| **httpVersion** | String | HTTP version (HTTP/1.0, HTTP/1.1, HTTP/2.0) |
| **httpMethod** | String | HTTP method (GET, POST, PUT, DELETE, etc.) |
| **requestId** | String | Unique identifier for the request |

### ruleGroupList Object

```json
{
  "ruleGroupList": [
    {
      "ruleGroupId": "AWS#AWSManagedRulesSQLiRuleSet",
      "terminatingRule": {
        "ruleId": "SQLi_QUERYARGUMENTS",
        "action": "BLOCK",
        "ruleMatchDetails": [
          {
            "conditionType": "SQL_INJECTION",
            "location": "QUERY_STRING",
            "matchedData": [
              "' OR '1'='1"
            ]
          }
        ]
      },
      "nonTerminatingMatchingRules": [],
      "excludedRules": null
    }
  ]
}
```

**ruleGroupList Fields:**
| Field | Type | Description |
|-------|------|-------------|
| **ruleGroupId** | String | ID of the rule group |
| **terminatingRule** | Object | Rule that terminated request processing (if any) |
| **nonTerminatingMatchingRules** | Array | Rules that matched but didn't terminate |
| **excludedRules** | Array | Rules excluded from evaluation |

### Condition Types

Common `conditionType` values in rule match details:

| Condition Type | Description |
|----------------|-------------|
| **SQL_INJECTION** | SQL injection pattern detected |
| **XSS** | Cross-site scripting pattern detected |
| **SIZE_CONSTRAINT** | Request size exceeds limit |
| **GEO_MATCH** | Geographic location match |
| **IP_MATCH** | IP address match |
| **REGEX_MATCH** | Regular expression match |
| **STRING_MATCH** | String pattern match |
| **BYTE_MATCH** | Byte pattern match |

### Location Values

Where the match was found:

| Location | Description |
|----------|-------------|
| **QUERY_STRING** | URL query string |
| **URI** | Request URI |
| **BODY** | Request body |
| **HEADER** | HTTP header |
| **METHOD** | HTTP method |
| **JSON_BODY** | JSON request body |
| **COOKIES** | HTTP cookies |

## AWS Managed Rule Groups

### Core Rule Sets

| Rule Group ID | Description |
|---------------|-------------|
| **AWS#AWSManagedRulesCommonRuleSet** | General web application protection |
| **AWS#AWSManagedRulesAdminProtectionRuleSet** | Admin page protection |
| **AWS#AWSManagedRulesKnownBadInputsRuleSet** | Known malicious inputs |
| **AWS#AWSManagedRulesSQLiRuleSet** | SQL injection protection |
| **AWS#AWSManagedRulesLinuxRuleSet** | Linux-specific vulnerabilities |
| **AWS#AWSManagedRulesUnixRuleSet** | Unix-specific vulnerabilities |
| **AWS#AWSManagedRulesWindowsRuleSet** | Windows-specific vulnerabilities |
| **AWS#AWSManagedRulesPHPRuleSet** | PHP application protection |
| **AWS#AWSManagedRulesWordPressRuleSet** | WordPress protection |
| **AWS#AWSManagedRulesBotControlRuleSet** | Bot detection and mitigation |
| **AWS#AWSManagedRulesATPRuleSet** | Account takeover prevention |
| **AWS#AWSManagedRulesACFPRuleSet** | Account creation fraud prevention |
| **AWS#AWSManagedRulesAnonymousIpList** | Anonymous IP detection |
| **AWS#AWSManagedRulesAmazonIpReputationList** | IP reputation list |

## Example Log Entries

### Example 1: SQL Injection Blocked

```json
{
  "timestamp": 1576280412771,
  "formatVersion": 1,
  "webaclId": "arn:aws:wafv2:us-east-1:123456789012:regional/webacl/test/a1b2c3d4-5678-90ab-cdef-EXAMPLE11111",
  "terminatingRuleId": "SQLi_BODY",
  "terminatingRuleType": "MANAGED_RULE_GROUP",
  "action": "BLOCK",
  "terminatingRuleMatchDetails": [
    {
      "conditionType": "SQL_INJECTION",
      "location": "QUERY_STRING",
      "matchedData": [
        "' OR '1'='1"
      ]
    }
  ],
  "httpSourceName": "ALB",
  "httpSourceId": "123456789012-app/my-alb/1234567890abcdef",
  "ruleGroupList": [
    {
      "ruleGroupId": "AWS#AWSManagedRulesSQLiRuleSet",
      "terminatingRule": {
        "ruleId": "SQLi_QUERYARGUMENTS",
        "action": "BLOCK",
        "ruleMatchDetails": [
          {
            "conditionType": "SQL_INJECTION",
            "location": "QUERY_STRING",
            "matchedData": [
              "' OR '1'='1"
            ]
          }
        ]
      },
      "nonTerminatingMatchingRules": [],
      "excludedRules": null
    }
  ],
  "rateBasedRuleList": [],
  "nonTerminatingMatchingRules": [],
  "requestHeadersInserted": null,
  "responseCodeSent": null,
  "httpRequest": {
    "clientIp": "192.0.2.1",
    "country": "US",
    "headers": [
      {
        "name": "Host",
        "value": "example.com"
      },
      {
        "name": "User-Agent",
        "value": "sqlmap/1.0"
      }
    ],
    "uri": "/api/login",
    "args": "username=admin&password=%27+OR+%271%27%3D%271",
    "httpVersion": "HTTP/1.1",
    "httpMethod": "POST",
    "requestId": "FGK3K8E5VJG30QVJ9EXAMPLE"
  }
}
```

### Example 2: XSS Attack Blocked

```json
{
  "timestamp": 1576280412772,
  "formatVersion": 1,
  "webaclId": "arn:aws:wafv2:us-east-1:123456789012:regional/webacl/test/a1b2c3d4-5678-90ab-cdef-EXAMPLE11111",
  "terminatingRuleId": "XSS_BODY",
  "terminatingRuleType": "MANAGED_RULE_GROUP",
  "action": "BLOCK",
  "terminatingRuleMatchDetails": [
    {
      "conditionType": "XSS",
      "location": "QUERY_STRING",
      "matchedData": [
        "<script>alert('XSS')</script>"
      ]
    }
  ],
  "httpSourceName": "ALB",
  "httpSourceId": "123456789012-app/my-alb/1234567890abcdef",
  "ruleGroupList": [
    {
      "ruleGroupId": "AWS#AWSManagedRulesKnownBadInputsRuleSet",
      "terminatingRule": {
        "ruleId": "CrossSiteScripting_QUERYARGUMENTS",
        "action": "BLOCK",
        "ruleMatchDetails": [
          {
            "conditionType": "XSS",
            "location": "QUERY_STRING",
            "matchedData": [
              "<script>alert('XSS')</script>"
            ]
          }
        ]
      },
      "nonTerminatingMatchingRules": [],
      "excludedRules": null
    }
  ],
  "rateBasedRuleList": [],
  "nonTerminatingMatchingRules": [],
  "requestHeadersInserted": null,
  "responseCodeSent": null,
  "httpRequest": {
    "clientIp": "192.0.2.1",
    "country": "US",
    "headers": [
      {
        "name": "Host",
        "value": "example.com"
      },
      {
        "name": "User-Agent",
        "value": "Mozilla/5.0"
      }
    ],
    "uri": "/search",
    "args": "q=%3Cscript%3Ealert%28%27XSS%27%29%3C%2Fscript%3E",
    "httpVersion": "HTTP/1.1",
    "httpMethod": "GET",
    "requestId": "ABC123DEF456GHI789EXAMPLE"
  }
}
```

### Example 3: Rate Limit Exceeded

```json
{
  "timestamp": 1576280412773,
  "formatVersion": 1,
  "webaclId": "arn:aws:wafv2:us-east-1:123456789012:regional/webacl/test/a1b2c3d4-5678-90ab-cdef-EXAMPLE11111",
  "terminatingRuleId": "RateLimitRule",
  "terminatingRuleType": "RATE_BASED",
  "action": "BLOCK",
  "terminatingRuleMatchDetails": [],
  "httpSourceName": "ALB",
  "httpSourceId": "123456789012-app/my-alb/1234567890abcdef",
  "ruleGroupList": [],
  "rateBasedRuleList": [
    {
      "rateBasedRuleId": "RateLimitRule",
      "limitKey": "IP",
      "maxRateAllowed": 100
    }
  ],
  "nonTerminatingMatchingRules": [],
  "requestHeadersInserted": null,
  "responseCodeSent": null,
  "httpRequest": {
    "clientIp": "192.0.2.1",
    "country": "US",
    "headers": [
      {
        "name": "Host",
        "value": "example.com"
      },
      {
        "name": "User-Agent",
        "value": "python-requests/2.28.0"
      }
    ],
    "uri": "/api/login",
    "args": "",
    "httpVersion": "HTTP/1.1",
    "httpMethod": "POST",
    "requestId": "RATE123LIMIT456EXAMPLE"
  }
}
```

### Example 4: Allowed Request (Baseline)

```json
{
  "timestamp": 1576280412774,
  "formatVersion": 1,
  "webaclId": "arn:aws:wafv2:us-east-1:123456789012:regional/webacl/test/a1b2c3d4-5678-90ab-cdef-EXAMPLE11111",
  "terminatingRuleId": "Default_Action",
  "terminatingRuleType": "REGULAR",
  "action": "ALLOW",
  "terminatingRuleMatchDetails": [],
  "httpSourceName": "ALB",
  "httpSourceId": "123456789012-app/my-alb/1234567890abcdef",
  "ruleGroupList": [],
  "rateBasedRuleList": [],
  "nonTerminatingMatchingRules": [],
  "requestHeadersInserted": null,
  "responseCodeSent": null,
  "httpRequest": {
    "clientIp": "192.0.2.100",
    "country": "US",
    "headers": [
      {
        "name": "Host",
        "value": "example.com"
      },
      {
        "name": "User-Agent",
        "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      },
      {
        "name": "Accept",
        "value": "text/html,application/xhtml+xml,application/xml"
      }
    ],
    "uri": "/",
    "args": "",
    "httpVersion": "HTTP/1.1",
    "httpMethod": "GET",
    "requestId": "NORMAL123REQUEST456EXAMPLE"
  }
}
```

### Example 5: Bot Detection

```json
{
  "timestamp": 1576280412775,
  "formatVersion": 1,
  "webaclId": "arn:aws:wafv2:us-east-1:123456789012:regional/webacl/test/a1b2c3d4-5678-90ab-cdef-EXAMPLE11111",
  "terminatingRuleId": "BadBotUserAgent",
  "terminatingRuleType": "MANAGED_RULE_GROUP",
  "action": "BLOCK",
  "terminatingRuleMatchDetails": [],
  "httpSourceName": "ALB",
  "httpSourceId": "123456789012-app/my-alb/1234567890abcdef",
  "ruleGroupList": [
    {
      "ruleGroupId": "AWS#AWSManagedRulesBotControlRuleSet",
      "terminatingRule": {
        "ruleId": "CategoryScrapingFramework",
        "action": "BLOCK",
        "ruleMatchDetails": []
      },
      "nonTerminatingMatchingRules": [],
      "excludedRules": null
    }
  ],
  "rateBasedRuleList": [],
  "nonTerminatingMatchingRules": [],
  "requestHeadersInserted": null,
  "responseCodeSent": null,
  "httpRequest": {
    "clientIp": "192.0.2.50",
    "country": "US",
    "headers": [
      {
        "name": "Host",
        "value": "example.com"
      },
      {
        "name": "User-Agent",
        "value": "Nikto/2.1.5"
      }
    ],
    "uri": "/",
    "args": "",
    "httpVersion": "HTTP/1.1",
    "httpMethod": "GET",
    "requestId": "BOT123SCANNER456EXAMPLE"
  }
}
```

## HTTP Source Types

| Source | Description |
|--------|-------------|
| **ALB** | Application Load Balancer |
| **APIGW** | API Gateway |
| **CLOUDFRONT** | CloudFront distribution |
| **APPSYNC** | AWS AppSync |
| **COGNITOUSERPOOL** | Cognito User Pool |
| **VERIFIEDACCESS** | Verified Access |

## Logging Delivery

### Kinesis Data Firehose
- Real-time delivery
- Can route to S3, Redshift, Elasticsearch, HTTP endpoint
- Compressed with GZIP
- Buffered (size or time based)

### S3 Bucket Structure
```
s3://bucket-name/prefix/
  └── year=2024/
      └── month=01/
          └── day=15/
              └── hour=10/
                  └── uuid-timestamp.gz
```

### File Format
- Multiple log entries per file (newline-delimited JSON)
- GZIP compressed
- UTF-8 encoding

## Important Notes

1. **Sampled Logs**: WAF logs can be sampled (default 100% but configurable)
2. **Redacted Fields**: Sensitive data in headers/body can be redacted
3. **Log Delay**: Typically delivered within 5 minutes
4. **Size Limits**: Individual log entries can be up to 8KB
5. **Header Limits**: Only first 200 headers logged
6. **Body Inspection**: Limited to first 8KB of body for inspection

## Common Use Cases

1. **Attack Analysis**: Identify attack patterns and sources
2. **Rule Tuning**: Analyze false positives and adjust rules
3. **Compliance**: Meet regulatory logging requirements
4. **Threat Intelligence**: Feed IP reputation systems
5. **Security Automation**: Trigger automated responses to attacks

## Best Practices

1. **Enable Logging**: Always enable for production web ACLs
2. **Retention Policy**: Set appropriate S3 lifecycle rules
3. **Monitor Costs**: WAF logging has per-request charges
4. **SIEM Integration**: Stream to security monitoring tools
5. **Alert on Patterns**: Set up CloudWatch alarms for attack trends
6. **Redact PII**: Use redaction for sensitive fields
7. **Sample Strategically**: Balance cost vs. visibility needs

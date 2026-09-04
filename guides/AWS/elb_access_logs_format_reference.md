# AWS Elastic Load Balancer Access Logs Format Reference

Complete specification for AWS ELB (Application Load Balancer) access logs.

## Overview

ELB access logs capture detailed information about requests sent to your load balancer. Each log entry contains details about the request, including the time the request was received, the client's IP address, latencies, request paths, and server responses.

## Format

- **Format**: Space-delimited text (32+ fields for ALB, 25+ for Classic LB)
- **Delivery**: S3 bucket
- **Compression**: GZIP (optional)
- **Encoding**: UTF-8
- **Version**: ALB logs (most common), Classic LB logs (legacy)

## Load Balancer Types

| Type | Description | Common Use Cases |
|------|-------------|------------------|
| **Application Load Balancer (ALB)** | Layer 7 (HTTP/HTTPS) load balancer | Web applications, microservices, containers |
| **Network Load Balancer (NLB)** | Layer 4 (TCP/UDP) load balancer | High throughput, low latency |
| **Classic Load Balancer (CLB)** | Legacy (Layer 4/7) | EC2-Classic, older applications |

**Note**: This document focuses on **Application Load Balancer (ALB)** logs as they are most commonly used and provide the most detail.

## ALB Access Log Structure

### Complete Field List (32 Fields)

ALB access logs are space-delimited with the following fields:

```
type timestamp elb client:port target:port request_processing_time target_processing_time response_processing_time elb_status_code target_status_code received_bytes sent_bytes "request" "user_agent" ssl_cipher ssl_protocol target_group_arn "trace_id" "domain_name" "chosen_cert_arn" matched_rule_priority request_creation_time "actions_executed" "redirect_url" "error_reason" "target:port_list" "target_status_code_list" "classification" "classification_reason"
```

### Field Definitions

| # | Field | Type | Description | Example |
|---|-------|------|-------------|---------|
| 1 | **type** | String | Protocol type | `http`, `https`, `h2`, `ws`, `wss` |
| 2 | **timestamp** | String | ISO 8601 timestamp | `2024-01-15T10:30:45.123456Z` |
| 3 | **elb** | String | Load balancer resource ID | `app/my-alb/50dc6c495c0c9188` |
| 4 | **client:port** | String | Client IP and port | `192.0.2.1:54321` |
| 5 | **target:port** | String | Target IP and port (or `-` if none) | `10.0.0.1:80` or `-` |
| 6 | **request_processing_time** | Number | Time to receive request (seconds) | `0.001` or `-1` (error) |
| 7 | **target_processing_time** | Number | Time for target to respond (seconds) | `0.050` or `-1` (error) |
| 8 | **response_processing_time** | Number | Time to send response (seconds) | `0.001` or `-1` (error) |
| 9 | **elb_status_code** | Number | HTTP status from ELB | `200`, `403`, `502` |
| 10 | **target_status_code** | Number | HTTP status from target (or `-` if none) | `200` or `-` |
| 11 | **received_bytes** | Number | Bytes received from client | `1234` |
| 12 | **sent_bytes** | Number | Bytes sent to client | `5678` |
| 13 | **request** | String (quoted) | HTTP request line | `"GET / HTTP/1.1"` |
| 14 | **user_agent** | String (quoted) | User-Agent header | `"Mozilla/5.0..."` |
| 15 | **ssl_cipher** | String | SSL cipher (HTTPS only) | `ECDHE-RSA-AES128-GCM-SHA256` or `-` |
| 16 | **ssl_protocol** | String | SSL protocol (HTTPS only) | `TLSv1.2`, `TLSv1.3` or `-` |
| 17 | **target_group_arn** | String (quoted) | Target group ARN | `"arn:aws:elasticloadbalancing:..."` |
| 18 | **trace_id** | String (quoted) | X-Amzn-Trace-Id header | `"Root=1-58337..."` |
| 19 | **domain_name** | String (quoted) | SNI domain (HTTPS) | `"example.com"` or `-` |
| 20 | **chosen_cert_arn** | String (quoted) | Certificate ARN (HTTPS) | `"arn:aws:acm:..."` or `-` |
| 21 | **matched_rule_priority** | Number | Priority of matched listener rule | `0`, `1`, `10` |
| 22 | **request_creation_time** | String | ISO 8601 timestamp | `2024-01-15T10:30:45.123456Z` |
| 23 | **actions_executed** | String (quoted) | Actions taken | `"forward"`, `"redirect"`, `"fixed-response"`, `"authenticate"` |
| 24 | **redirect_url** | String (quoted) | Redirect URL (if action=redirect) | `"https://example.com/new"` or `-` |
| 25 | **error_reason** | String (quoted) | Error reason (if applicable) | `"TargetResponseCodeMismatch"` or `-` |
| 26 | **target:port_list** | String (quoted) | List of targets contacted | `"10.0.0.1:80 10.0.0.2:80"` or `-` |
| 27 | **target_status_code_list** | String (quoted) | Status codes from targets | `"200 200"` or `-` |
| 28 | **classification** | String (quoted) | Traffic classification | `"-"` or specific value |
| 29 | **classification_reason** | String (quoted) | Reason for classification | `"-"` or specific reason |

### Protocol Types

| Type | Description | Port |
|------|-------------|------|
| **http** | HTTP/1.x | 80 |
| **https** | HTTPS/1.x | 443 |
| **h2** | HTTP/2 | 443 |
| **ws** | WebSocket | 80 |
| **wss** | WebSocket Secure | 443 |

### ELB Status Codes

Common HTTP status codes returned by the load balancer:

| Code | Description | Typical Cause |
|------|-------------|---------------|
| **200** | OK | Successful request |
| **301** | Moved Permanently | Redirect rule |
| **302** | Found (Redirect) | Redirect rule |
| **400** | Bad Request | Malformed request |
| **401** | Unauthorized | Authentication required |
| **403** | Forbidden | WAF block, security group deny |
| **404** | Not Found | Path not found |
| **408** | Request Timeout | Client didn't send data in time |
| **413** | Payload Too Large | Request body exceeds limit |
| **500** | Internal Server Error | Target error |
| **502** | Bad Gateway | Target connection failed |
| **503** | Service Unavailable | No healthy targets |
| **504** | Gateway Timeout | Target didn't respond in time |

### Target Status Codes

- `-` means request never reached a target (e.g., WAF block, no healthy targets)
- Otherwise, matches the HTTP status returned by the backend target

### Actions Executed

| Action | Description |
|--------|-------------|
| **forward** | Request forwarded to target group |
| **redirect** | Request redirected to different URL |
| **fixed-response** | ALB returned fixed response (no target) |
| **authenticate** | Authentication via Cognito or OIDC |
| **waf** | Request evaluated by WAF |
| **waf-failed** | WAF blocked the request |

### Error Reasons

| Error Reason | Description |
|--------------|-------------|
| **TargetResponseCodeMismatch** | Target returned unexpected status code |
| **LambdaInvalidResponse** | Lambda target returned malformed response |
| **LambdaResponseTooLarge** | Lambda response exceeded size limit |
| **LambdaUnhandledException** | Lambda threw unhandled exception |
| **TargetNotFound** | Target deregistered or doesn't exist |
| **TargetTimeout** | Target didn't respond within timeout |
| **TargetFailedHealthCheck** | Target failed health check |

## Example Log Entries

### Example 1: Successful HTTP Request

```
http 2024-01-15T10:00:00.123456Z app/my-alb/50dc6c495c0c9188 192.0.2.1:54321 10.0.0.1:80 0.000 0.050 0.000 200 200 512 2048 "GET https://example.com:443/ HTTP/1.1" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/50dc6c495c0c9188 "Root=1-58337262-36d228ad5d99923122bbe354" "example.com" "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012" 0 2024-01-15T10:00:00.073456Z "forward" "-" "-" "10.0.0.1:80" "200" "-" "-"
```

**Analysis**: Normal HTTPS request successfully forwarded to target, 50ms processing time.

### Example 2: WAF Blocked Request (SQL Injection)

```
https 2024-01-15T11:00:00.123456Z app/my-alb/50dc6c495c0c9188 198.51.100.50:12345 - 0.001 -1 -1 403 - 256 0 "GET https://example.com:443/api/login?username=admin&password=%27+OR+%271%27%3D%271 HTTP/1.1" "sqlmap/1.0" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/50dc6c495c0c9188 "Root=1-58337263-36d228ad5d99923122bbe355" "example.com" "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012" 1 2024-01-15T11:00:00.000456Z "waf,waf-failed" "-" "-" "-" "-" "-" "-"
```

**Analysis**: WAF blocked SQL injection attempt, request never reached backend target.

### Example 3: XSS Attack Attempt

```
https 2024-01-15T11:05:00.123456Z app/my-alb/50dc6c495c0c9188 198.51.100.50:12346 - 0.001 -1 -1 403 - 345 0 "GET https://example.com:443/search?q=%3Cscript%3Ealert%28%27XSS%27%29%3C%2Fscript%3E HTTP/1.1" "Mozilla/5.0" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/50dc6c495c0c9188 "Root=1-58337264-36d228ad5d99923122bbe356" "example.com" "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012" 1 2024-01-15T11:05:00.000456Z "waf,waf-failed" "-" "-" "-" "-" "-" "-"
```

**Analysis**: XSS attempt blocked by WAF, 403 Forbidden response.

### Example 4: Path Traversal Attempt

```
https 2024-01-15T11:10:00.123456Z app/my-alb/50dc6c495c0c9188 198.51.100.50:12347 - 0.001 -1 -1 403 - 289 0 "GET https://example.com:443/../../etc/passwd HTTP/1.1" "curl/7.68.0" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/50dc6c495c0c9188 "Root=1-58337265-36d228ad5d99923122bbe357" "example.com" "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012" 1 2024-01-15T11:10:00.000456Z "waf,waf-failed" "-" "-" "-" "-" "-" "-"
```

**Analysis**: Path traversal attempt to access system files, blocked by WAF.

### Example 5: Brute Force Login Attempt

```
https 2024-01-15T11:15:00.123456Z app/my-alb/50dc6c495c0c9188 198.51.100.50:12348 10.0.0.1:80 0.001 0.030 0.000 200 401 456 234 "POST https://example.com:443/api/login HTTP/1.1" "python-requests/2.28.0" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/50dc6c495c0c9188 "Root=1-58337266-36d228ad5d99923122bbe358" "example.com" "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012" 0 2024-01-15T11:15:00.000456Z "forward" "-" "-" "10.0.0.1:80" "401" "-" "-"
```

**Analysis**: Login attempt forwarded to backend but failed (401 Unauthorized), part of brute force pattern.

### Example 6: Scanner Request (Nikto/Nessus)

```
http 2024-01-15T11:20:00.123456Z app/my-alb/50dc6c495c0c9188 198.51.100.50:12349 10.0.0.1:80 0.001 0.020 0.000 404 404 178 89 "GET http://example.com:80/admin/config.php HTTP/1.1" "Nikto/2.1.5" - - arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/50dc6c495c0c9188 "Root=1-58337267-36d228ad5d99923122bbe359" "-" "-" 0 2024-01-15T11:20:00.000456Z "forward" "-" "-" "10.0.0.1:80" "404" "-" "-"
```

**Analysis**: Security scanner probing for common admin paths, page not found.

### Example 7: Backend Timeout (504)

```
https 2024-01-15T12:00:00.123456Z app/my-alb/50dc6c495c0c9188 192.0.2.100:55000 10.0.0.1:80 0.000 60.000 -1 504 - 512 0 "POST https://example.com:443/api/process HTTP/1.1" "Mozilla/5.0" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/50dc6c495c0c9188 "Root=1-58337268-36d228ad5d99923122bbe360" "example.com" "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012" 0 2024-01-15T12:00:00.000456Z "forward" "-" "TargetTimeout" "10.0.0.1:80" "-" "-" "-"
```

**Analysis**: Backend took too long to respond (60 seconds), ELB returned 504 Gateway Timeout.

### Example 8: No Healthy Targets (503)

```
https 2024-01-15T13:00:00.123456Z app/my-alb/50dc6c495c0c9188 192.0.2.150:56000 - 0.000 -1 -1 503 - 456 0 "GET https://example.com:443/ HTTP/1.1" "Mozilla/5.0" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/50dc6c495c0c9188 "Root=1-58337269-36d228ad5d99923122bbe361" "example.com" "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012" 0 2024-01-15T13:00:00.000456Z "forward" "-" "-" "-" "-" "-" "-"
```

**Analysis**: All backend targets unhealthy or deregistered, ELB returned 503 Service Unavailable.

### Example 9: Redirect Action

```
http 2024-01-15T14:00:00.123456Z app/my-alb/50dc6c495c0c9188 192.0.2.200:57000 - 0.000 -1 -1 301 - 234 0 "GET http://example.com:80/old-path HTTP/1.1" "Mozilla/5.0" - - arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/50dc6c495c0c9188 "Root=1-58337270-36d228ad5d99923122bbe362" "-" "-" 5 2024-01-15T14:00:00.000456Z "redirect" "https://example.com/new-path" "-" "-" "-" "-" "-"
```

**Analysis**: ALB listener rule redirected HTTP to HTTPS, no backend involved.

### Example 10: Oversized Request (413)

```
https 2024-01-15T15:00:00.123456Z app/my-alb/50dc6c495c0c9188 192.0.2.250:58000 - 0.001 -1 -1 413 - 10485760 0 "POST https://example.com:443/upload HTTP/1.1" "curl/7.68.0" ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/50dc6c495c0c9188 "Root=1-58337271-36d228ad5d99923122bbe363" "example.com" "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012" 0 2024-01-15T15:00:00.000456Z "forward" "-" "-" "-" "-" "-" "-"
```

**Analysis**: Request body exceeded size limit (10MB), ELB rejected with 413 Payload Too Large.

## Timing Fields

### Request Processing Time
- Time (in seconds) ELB took to receive the request from client
- `-1` indicates error or request never completed

### Target Processing Time
- Time (in seconds) for target to process request and send response
- `-1` indicates no target was contacted (WAF block, no healthy targets, etc.)

### Response Processing Time
- Time (in seconds) for ELB to send response to client
- `-1` indicates error or connection closed

**Total Time** = request_processing_time + target_processing_time + response_processing_time

## Security Patterns

### Web Application Attacks

**Indicators in logs:**
- User-Agent: `sqlmap`, `Nikto`, `Nessus`, `python-requests`, `curl`
- ELB status: `403` (WAF block)
- Actions: `waf,waf-failed`
- URL patterns: SQL syntax (`%27`, `OR`, `1=1`), XSS (`%3Cscript%3E`), path traversal (`..%2F`)

### Brute Force Attacks

**Indicators in logs:**
- High request volume from single IP
- Target status: `401 Unauthorized` repeated
- URI: `/login`, `/api/auth`, `/admin`
- User-Agent: Often scripted tools (`python-requests`, `curl`)

### Scanner Activity

**Indicators in logs:**
- User-Agent: `Nikto`, `Nessus`, `OpenVAS`, `masscan`
- URIs: Common paths (`/admin`, `/config`, `/backup`, `/.git`)
- Multiple 404s from same IP
- Sequential requests to different paths

### DDoS/Flood Attacks

**Indicators in logs:**
- Extremely high request rate
- Many connections from distributed IPs (DDoS)
- Small received_bytes (SYN flood)
- Many 503 errors (resource exhaustion)

## Log Delivery

### S3 Bucket Structure

```
s3://bucket-name/prefix/AWSLogs/account-id/elasticloadbalancing/region/YYYY/MM/DD/
  └── account-id_elasticloadbalancing_region_app.load-balancer-id_end-time_random-string.log.gz
```

Example:
```
123456789012_elasticloadbalancing_us-east-1_app.my-alb.50dc6c495c0c9188_20240115T1100Z_172.16.0.1_8hSqR3o4.log.gz
```

### File Format
- GZIP compressed (optional)
- UTF-8 encoding
- One log entry per line
- Space-delimited fields
- Quoted fields contain spaces or special characters

### Delivery Timing
- Logs published every 5 minutes (if traffic occurred)
- Up to 60 minutes delay in rare cases
- Empty files not created

## Parsing Considerations

### Quoted Fields
Fields 13-29 may contain spaces and are quoted:
- `"request"`
- `"user_agent"`
- `"target_group_arn"`
- `"trace_id"`
- `"domain_name"`
- `"chosen_cert_arn"`
- `"actions_executed"`
- `"redirect_url"`
- `"error_reason"`
- `"target:port_list"`
- `"target_status_code_list"`
- `"classification"`
- `"classification_reason"`

### Special Characters
- Spaces in URLs encoded as `%20`
- Quotes in User-Agent escaped as `\"`
- `-` represents null/empty value

### Numeric Fields
- `-1` in timing fields = error or N/A
- `-` in numeric fields = null/empty

## Integration with Other Services

### WAF Correlation
- `actions_executed` contains `waf` or `waf-failed`
- ELB status `403` often indicates WAF block
- Correlate with WAF logs using `trace_id`

### VPC Flow Logs Correlation
- Match using client IP and timestamp
- VPC Flow shows network-layer (TCP/UDP)
- ELB shows application-layer (HTTP)

### CloudTrail Correlation
- Track ALB configuration changes
- Match using `elb` resource ID
- Investigate rule modifications, target changes

### GuardDuty Correlation
- GuardDuty may detect reconnaissance from ELB logs
- Correlate malicious IPs across services
- GuardDuty finding → review ELB logs for full request details

## Best Practices

1. **Enable Access Logging**: Always enable for production load balancers
2. **Set S3 Lifecycle**: Archive logs after 90 days, delete after 1 year (adjust for compliance)
3. **Monitor 4xx/5xx Rates**: Alert on sudden spikes (attacks or outages)
4. **Analyze User-Agents**: Identify bots, scanners, and malicious tools
5. **Track Top IPs**: Identify high-volume clients and potential attackers
6. **Correlate with WAF**: Review blocked requests to tune rules
7. **Export to SIEM**: Stream logs to security monitoring platform
8. **Baseline Normal Traffic**: Understand typical patterns to detect anomalies
9. **Automated Response**: Lambda functions triggered on attack patterns
10. **Cost Management**: Compress logs, set retention policies

## Common Use Cases

1. **Security Monitoring**: Detect and investigate attacks (SQL injection, XSS, brute force)
2. **Troubleshooting**: Debug 5xx errors, timeouts, connectivity issues
3. **Performance Analysis**: Identify slow backend targets, optimize caching
4. **Compliance**: Meet regulatory logging requirements (PCI-DSS, HIPAA, SOC 2)
5. **Capacity Planning**: Analyze traffic patterns, peak hours, user distribution
6. **DDoS Detection**: Identify flood attacks and abnormal traffic spikes
7. **Bot Detection**: Distinguish legitimate users from scrapers/bots
8. **Incident Response**: Forensic analysis of security incidents

## Limitations

1. **Sampling**: Logs not sampled - all requests logged (can be expensive)
2. **5-Minute Delay**: Logs delivered in batches, not real-time
3. **Request Body**: Body content not logged (only headers and URL)
4. **Response Body**: Response content not logged
5. **Size Limits**: Very large request/response headers may be truncated
6. **Header Count**: Only first 200 headers logged

## Athena Queries

### Create Table (Example)
```sql
CREATE EXTERNAL TABLE alb_logs (
  type string,
  time string,
  elb string,
  client_ip string,
  client_port int,
  target_ip string,
  target_port int,
  request_processing_time double,
  target_processing_time double,
  response_processing_time double,
  elb_status_code int,
  target_status_code string,
  received_bytes bigint,
  sent_bytes bigint,
  request_verb string,
  request_url string,
  request_proto string,
  user_agent string,
  ssl_cipher string,
  ssl_protocol string,
  target_group_arn string,
  trace_id string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1',
  'input.regex' = '([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*):([0-9]*) ([^ ]*)[:-]([0-9]*) ([-.0-9]*) ([-.0-9]*) ([-.0-9]*) (|[-0-9]*) (-|[-0-9]*) ([-0-9]*) ([-0-9]*) \"([^ ]*) ([^ ]*) (- |[^ ]*)\" \"([^\"]*)\" ([A-Z0-9-]+) ([A-Za-z0-9.-]*) ([^ ]*) \"([^\"]*)\".*'
)
LOCATION 's3://bucket-name/prefix/AWSLogs/account-id/elasticloadbalancing/region/';
```

### Top Attack IPs
```sql
SELECT client_ip, COUNT(*) as request_count
FROM alb_logs
WHERE elb_status_code = 403
GROUP BY client_ip
ORDER BY request_count DESC
LIMIT 10;
```

### SQL Injection Attempts
```sql
SELECT time, client_ip, request_url, user_agent
FROM alb_logs
WHERE request_url LIKE '%27%'  -- SQL quote
   OR request_url LIKE '%OR%1%'  -- OR 1=1
   OR request_url LIKE '%UNION%SELECT%'
ORDER BY time DESC;
```

### Error Rate by Status Code
```sql
SELECT elb_status_code, COUNT(*) as count
FROM alb_logs
WHERE elb_status_code >= 400
GROUP BY elb_status_code
ORDER BY count DESC;
```

---

**Status**: ✅ Complete
**Version**: ALB (Application Load Balancer) format
**Last Updated**: 2025-11-03

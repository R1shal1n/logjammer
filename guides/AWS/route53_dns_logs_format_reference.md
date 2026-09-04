# AWS Route53 DNS Query Logs Format Reference

Complete specification for AWS Route53 DNS query logs.

## Overview

Route53 query logging captures information about the DNS queries that Route53 receives for a specified hosted zone. These logs are useful for security monitoring, troubleshooting DNS resolution, and detecting DNS-based attacks.

## Format

- **Format**: Space-delimited text (11 fields)
- **Delivery**: CloudWatch Logs
- **Version**: 1.0 (current)
- **Encoding**: UTF-8

## Field Structure

Route53 query logs have **11 space-delimited fields** in the following order:

```
version query_timestamp hosted_zone_id query_name query_type response_code layer4_protocol location source_ip query_class edns_client_subnet
```

### Field Definitions

| # | Field Name | Description | Example | Can be `-` |
|---|------------|-------------|---------|------------|
| 1 | **version** | Log format version | `1.0` | No |
| 2 | **query_timestamp** | ISO 8601 timestamp (UTC) | `2024-01-15T10:30:45Z` | No |
| 3 | **hosted_zone_id** | Route53 hosted zone ID | `Z1234567890ABC` | No |
| 4 | **query_name** | Domain name queried | `example.com` | No |
| 5 | **query_type** | DNS query type | `A`, `AAAA`, `MX`, etc. | No |
| 6 | **response_code** | DNS response code | `NOERROR`, `NXDOMAIN`, etc. | No |
| 7 | **layer4_protocol** | Transport protocol | `UDP` or `TCP` | No |
| 8 | **location** | Edge location code | `SEA19`, `IAD12`, etc. | No |
| 9 | **source_ip** | IP address of DNS client | `192.0.2.1` | No |
| 10 | **query_class** | DNS query class | `IN` (Internet) | No |
| 11 | **edns_client_subnet** | EDNS client subnet | `192.0.2.0/24` or `-` | Yes |

## DNS Query Types

Common query types seen in Route53 logs:

| Query Type | Description | Typical Usage |
|------------|-------------|---------------|
| **A** | IPv4 address | Standard web browsing |
| **AAAA** | IPv6 address | IPv6-enabled services |
| **CNAME** | Canonical name | Alias records |
| **MX** | Mail exchange | Email routing |
| **TXT** | Text record | SPF, DKIM, verification |
| **NS** | Name server | Zone delegation |
| **SOA** | Start of authority | Zone metadata |
| **PTR** | Pointer (reverse DNS) | IP to name lookup |
| **SRV** | Service locator | Service discovery |
| **CAA** | Certification authority authorization | SSL/TLS certificate validation |
| **ANY** | All available records | Often used in reconnaissance/attacks |
| **AXFR** | Zone transfer | Full zone replication (often blocked) |
| **NULL** | Null record | Sometimes used for covert channels |

## DNS Response Codes

| Response Code | Description | Common Causes |
|---------------|-------------|---------------|
| **NOERROR** | Successful query | Domain exists and has records |
| **NXDOMAIN** | Non-existent domain | Domain doesn't exist (typo or DGA) |
| **SERVFAIL** | Server failure | DNS server error or misconfiguration |
| **REFUSED** | Query refused | Policy block or AXFR denied |
| **FORMERR** | Format error | Malformed query |
| **NOTIMP** | Not implemented | Unsupported query type |
| **NOTAUTH** | Not authoritative | Server not authoritative for zone |

## Transport Protocols

| Protocol | Description | Typical Usage |
|----------|-------------|---------------|
| **UDP** | User Datagram Protocol | Standard DNS queries (most common) |
| **TCP** | Transmission Control Protocol | Large responses, zone transfers (AXFR) |

## Edge Location Codes

Route53 uses three-letter airport codes + number for edge locations:

| Code | Location | Region |
|------|----------|--------|
| **SEA19** | Seattle | US West |
| **IAD12** | Ashburn, VA | US East |
| **SFO5** | San Francisco | US West |
| **DFW3** | Dallas | US Central |
| **LHR62** | London | Europe |
| **NRT12** | Tokyo | Asia Pacific |
| **SYD1** | Sydney | Asia Pacific |

(Note: Specific numbers vary and change as AWS adds capacity)

## Query Class

| Class | Description | Usage |
|-------|-------------|-------|
| **IN** | Internet | Standard internet DNS (99.9% of queries) |
| **CH** | Chaos | Legacy (rarely seen) |
| **HS** | Hesiod | Legacy (rarely seen) |

## EDNS Client Subnet

- **Purpose**: Allows DNS resolvers to provide client subnet information
- **Format**: CIDR notation (e.g., `192.0.2.0/24`)
- **Value `-`**: Client subnet not provided (most common)
- **Security Note**: Can leak network topology information

## Example Log Records

### Example 1: Standard A Record Query
```
1.0 2024-01-15T10:30:45Z Z1234567890ABC example.com A NOERROR UDP SEA19 192.0.2.1 IN -
```
**Analysis**: Normal IPv4 address lookup from Seattle edge location via UDP.

### Example 2: AAAA Query (IPv6)
```
1.0 2024-01-15T10:31:12Z Z1234567890ABC example.com AAAA NOERROR UDP IAD12 2001:db8::1 IN -
```
**Analysis**: IPv6 address lookup from IPv6 client.

### Example 3: Non-Existent Domain (NXDOMAIN)
```
1.0 2024-01-15T10:32:05Z Z1234567890ABC typo-domain.com A NXDOMAIN UDP SFO5 192.0.2.50 IN -
```
**Analysis**: Query for non-existent domain (could be typo or DGA malware).

### Example 4: MX Record Query (Email)
```
1.0 2024-01-15T10:33:22Z Z1234567890ABC example.com MX NOERROR UDP DFW3 192.0.2.100 IN -
```
**Analysis**: Mail server lookup for email routing.

### Example 5: TXT Record Query (SPF/DKIM)
```
1.0 2024-01-15T10:34:18Z Z1234567890ABC _dmarc.example.com TXT NOERROR UDP IAD12 192.0.2.150 IN -
```
**Analysis**: DMARC policy lookup (common for email validation).

### Example 6: Zone Transfer Attempt (AXFR - Usually Refused)
```
1.0 2024-01-15T10:35:45Z Z1234567890ABC example.com AXFR REFUSED TCP SEA19 198.51.100.10 IN -
```
**Analysis**: Zone transfer attempt (reconnaissance), refused and logged.

### Example 7: PTR Query (Reverse DNS)
```
1.0 2024-01-15T10:36:30Z Z1234567890ABC 1.2.0.192.in-addr.arpa PTR NOERROR UDP IAD12 192.0.2.200 IN -
```
**Analysis**: Reverse DNS lookup to map IP to hostname.

### Example 8: ANY Query (Often Malicious)
```
1.0 2024-01-15T10:37:15Z Z1234567890ABC example.com ANY NOERROR UDP SFO5 198.51.100.20 IN -
```
**Analysis**: Request for all record types (sometimes used in DDoS amplification).

### Example 9: TCP DNS Query (Large Response)
```
1.0 2024-01-15T10:38:00Z Z1234567890ABC large-response.example.com TXT NOERROR TCP DFW3 192.0.2.250 IN -
```
**Analysis**: TCP used for response larger than 512 bytes (standard UDP limit).

### Example 10: Query with EDNS Client Subnet
```
1.0 2024-01-15T10:39:12Z Z1234567890ABC cdn.example.com A NOERROR UDP LHR62 192.0.2.75 IN 203.0.113.0/24
```
**Analysis**: Query with client subnet information (used for CDN geo-routing).

## Security-Relevant Patterns

### DNS Tunneling Detection
High-entropy subdomains or very long query names:
```
1.0 2024-01-15T11:00:00Z Z1234567890ABC dGVzdGRhdGE.tunnel.evil.com TXT NOERROR UDP SEA19 192.0.2.10 IN -
1.0 2024-01-15T11:00:05Z Z1234567890ABC YWJjZGVmZ2g.tunnel.evil.com TXT NOERROR UDP SEA19 192.0.2.10 IN -
1.0 2024-01-15T11:00:10Z Z1234567890ABC MTIzNDU2Nzg.tunnel.evil.com TXT NOERROR UDP SEA19 192.0.2.10 IN -
```
**Indicators**:
- Base64-encoded subdomains
- TXT or NULL record types
- Rapid sequential queries from same IP
- Very long domain names (approaching 253-character limit)

### DGA (Domain Generation Algorithm) Queries
Random-looking, non-existent domains:
```
1.0 2024-01-15T11:15:00Z Z1234567890ABC qjkxvmwpzlrn.com A NXDOMAIN UDP IAD12 192.0.2.30 IN -
1.0 2024-01-15T11:15:02Z Z1234567890ABC yhgtrfdsaqwz.com A NXDOMAIN UDP IAD12 192.0.2.30 IN -
1.0 2024-01-15T11:15:04Z Z1234567890ABC plmoknijbuhv.com A NXDOMAIN UDP IAD12 192.0.2.30 IN -
```
**Indicators**:
- High NXDOMAIN rate
- Random character sequences
- Multiple queries from same IP
- Short time intervals between queries

### C2 Beaconing
Regular queries to same suspicious domain:
```
1.0 2024-01-15T12:00:00Z Z1234567890ABC c2.malicious.com A NOERROR UDP SFO5 192.0.2.40 IN -
1.0 2024-01-15T12:05:00Z Z1234567890ABC c2.malicious.com A NOERROR UDP SFO5 192.0.2.40 IN -
1.0 2024-01-15T12:10:00Z Z1234567890ABC c2.malicious.com A NOERROR UDP SFO5 192.0.2.40 IN -
```
**Indicators**:
- Regular time intervals (beaconing)
- Same source IP
- Queries to known malicious domains

### Fast Flux DNS
Multiple A record queries in short time for same domain:
```
1.0 2024-01-15T13:00:00Z Z1234567890ABC fastflux.bad.com A NOERROR UDP SEA19 192.0.2.60 IN -
1.0 2024-01-15T13:00:30Z Z1234567890ABC fastflux.bad.com A NOERROR UDP SEA19 192.0.2.60 IN -
1.0 2024-01-15T13:01:00Z Z1234567890ABC fastflux.bad.com A NOERROR UDP SEA19 192.0.2.60 IN -
```
**Indicators**:
- Frequent re-queries for same domain
- Associated with botnets and malware distribution

### Zone Enumeration
Systematic querying of subdomains:
```
1.0 2024-01-15T14:00:00Z Z1234567890ABC admin.example.com A NOERROR UDP DFW3 198.51.100.50 IN -
1.0 2024-01-15T14:00:02Z Z1234567890ABC api.example.com A NOERROR UDP DFW3 198.51.100.50 IN -
1.0 2024-01-15T14:00:04Z Z1234567890ABC db.example.com A NXDOMAIN UDP DFW3 198.51.100.50 IN -
1.0 2024-01-15T14:00:06Z Z1234567890ABC dev.example.com A NOERROR UDP DFW3 198.51.100.50 IN -
```
**Indicators**:
- Sequential subdomain queries
- Same source IP
- Mix of NOERROR and NXDOMAIN responses
- Dictionary-based subdomain names

## Log Delivery and Storage

### CloudWatch Logs
- **Log Group**: Created automatically when query logging is enabled
- **Log Stream**: One per edge location
- **Retention**: Configurable (default: never expire)
- **Format**: Newline-delimited text

### Log Group Naming
```
/aws/route53/hosted-zone-name
```

### Permissions Required
Route53 needs permission to write to CloudWatch Logs:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "route53.amazonaws.com"
      },
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/route53/*"
    }
  ]
}
```

## Query Volume and Costs

### Cost Factors
1. **CloudWatch Logs ingestion**: Per GB ingested
2. **CloudWatch Logs storage**: Per GB per month
3. **CloudWatch Logs data transfer**: If exporting

### Volume Estimates
- Small website: 1,000-10,000 queries/day
- Medium website: 100,000-1,000,000 queries/day
- Large website: 10,000,000+ queries/day

### Log Size
- Average log entry: ~150 bytes
- 1 million queries ≈ 150 MB logs

## Integration and Analysis

### CloudWatch Insights Queries

**Top queried domains:**
```
fields query_name, query_type
| stats count() by query_name
| sort count desc
| limit 10
```

**NXDOMAIN queries (potential DGA):**
```
fields query_name, source_ip
| filter response_code = "NXDOMAIN"
| stats count() by source_ip
| sort count desc
```

**Large TXT queries (potential tunneling):**
```
fields query_name, source_ip
| filter query_type = "TXT"
| filter strlen(query_name) > 50
```

### SIEM Integration
- Export to S3 for long-term retention
- Stream to Kinesis for real-time analysis
- Lambda subscriptions for alerting

## Best Practices

1. **Enable for All Public Zones**: Monitor all internet-facing DNS
2. **Set Retention Policies**: Balance cost vs. compliance needs
3. **Alert on Anomalies**: NXDOMAIN spikes, unusual query types
4. **Correlate with VPC Flow**: Match DNS queries to network connections
5. **Baseline Normal**: Understand typical query patterns
6. **Monitor Query Types**: Alert on AXFR, ANY, excessive TXT queries
7. **Track Source IPs**: Identify reconnaissance sources
8. **Export for Analysis**: Regular S3 exports for deep analysis

## Limitations

1. **Edge Location Only**: Only queries to Route53 authoritative servers
2. **No Resolver Logs**: Doesn't log recursive resolver activity
3. **Sampling**: Not sampled - all queries logged
4. **Private Zones**: Separate configuration required
5. **Latency**: Small delay between query and log appearance (typically < 1 minute)

## Common Use Cases

1. **Security Monitoring**: Detect DNS tunneling, DGA, C2 beaconing
2. **Troubleshooting**: Debug DNS resolution issues
3. **Capacity Planning**: Understand query patterns and volume
4. **Compliance**: Meet regulatory DNS logging requirements
5. **Threat Intelligence**: Identify malicious domains and sources
6. **Incident Response**: Investigate historical DNS activity

# AWS Network Firewall Logs Format Reference

Complete specification for AWS Network Firewall logs.

## Overview

AWS Network Firewall is a managed service providing network protections for VPCs. It generates two types of logs: **Flow Logs** (NetFlow-style connection records) and **Alert Logs** (IDS/IPS threat detections).

## Log Types

### 1. Flow Logs
- **Purpose**: Record network flow information (similar to VPC Flow Logs but with more detail)
- **Format**: JSON
- **Contains**: Connection metadata, packet/byte counts, application protocol

### 2. Alert Logs
- **Purpose**: Record security events detected by stateful rule engine
- **Format**: JSON
- **Contains**: IDS/IPS alerts, malware detections, protocol anomalies

## Delivery

- **Destination**: CloudWatch Logs, S3, or Kinesis Data Firehose
- **Format**: JSON (one event per line when stored)
- **Delivery Latency**: Typically < 60 seconds

## Common Top-Level Fields

Both log types share these fields:

| Field | Type | Description |
|-------|------|-------------|
| **firewall_name** | String | Name of the firewall |
| **availability_zone** | String | AZ where traffic was processed |
| **event_timestamp** | String | ISO 8601 timestamp of log creation |
| **event** | Object | Event details (structure varies by type) |

## Flow Log Structure

### Complete Flow Log Example
```json
{
  "firewall_name": "my-firewall",
  "availability_zone": "us-east-1a",
  "event_timestamp": "2024-01-15T10:30:45.123Z",
  "event": {
    "timestamp": "2024-01-15T10:30:45Z",
    "flow_id": 123456789,
    "event_type": "netflow",
    "src_ip": "10.0.1.5",
    "src_port": 54321,
    "dest_ip": "203.0.113.10",
    "dest_port": 443,
    "proto": "TCP",
    "app_proto": "https",
    "netflow": {
      "pkts": 15,
      "bytes": 8500,
      "start": "2024-01-15T10:30:30Z",
      "end": "2024-01-15T10:30:45Z",
      "age": 15,
      "min_ttl": 64,
      "max_ttl": 64
    }
  }
}
```

### Flow Event Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **timestamp** | String | Event timestamp | `2024-01-15T10:30:45Z` |
| **flow_id** | Number | Unique flow identifier | `123456789` |
| **event_type** | String | Always `"netflow"` for flow logs | `netflow` |
| **src_ip** | String | Source IP address | `10.0.1.5` |
| **src_port** | Number | Source port | `54321` |
| **dest_ip** | String | Destination IP address | `203.0.113.10` |
| **dest_port** | Number | Destination port | `443` |
| **proto** | String | IP protocol | `TCP`, `UDP`, `ICMP` |
| **app_proto** | String | Application protocol (if identified) | `https`, `dns`, `ssh` |

### NetFlow Sub-Object

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **pkts** | Number | Total packets in flow | `15` |
| **bytes** | Number | Total bytes in flow | `8500` |
| **start** | String | Flow start timestamp | `2024-01-15T10:30:30Z` |
| **end** | String | Flow end timestamp | `2024-01-15T10:30:45Z` |
| **age** | Number | Flow duration in seconds | `15` |
| **min_ttl** | Number | Minimum TTL value seen | `64` |
| **max_ttl** | Number | Maximum TTL value seen | `64` |

### Application Protocols

Common `app_proto` values:

| Protocol | Port(s) | Description |
|----------|---------|-------------|
| **http** | 80 | HTTP web traffic |
| **https** | 443 | HTTPS encrypted web traffic |
| **ssh** | 22 | SSH secure shell |
| **ftp** | 21 | File Transfer Protocol |
| **smtp** | 25 | Email (SMTP) |
| **dns** | 53 | DNS queries |
| **rdp** | 3389 | Remote Desktop Protocol |
| **mysql** | 3306 | MySQL database |
| **postgresql** | 5432 | PostgreSQL database |
| **unknown** | Various | Unidentified protocol |

## Alert Log Structure

### Complete Alert Log Example
```json
{
  "firewall_name": "my-firewall",
  "availability_zone": "us-east-1a",
  "event_timestamp": "2024-01-15T11:00:15.456Z",
  "event": {
    "timestamp": "2024-01-15T11:00:15Z",
    "flow_id": 987654321,
    "event_type": "alert",
    "src_ip": "198.51.100.50",
    "src_port": 54322,
    "dest_ip": "10.0.1.10",
    "dest_port": 22,
    "proto": "TCP",
    "alert": {
      "action": "blocked",
      "signature": "ET EXPLOIT SSH Brute Force Attempt",
      "signature_id": 2001219,
      "rev": 20,
      "category": "Attempted Administrator Privilege Gain",
      "severity": 1
    }
  }
}
```

### Alert Event Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **timestamp** | String | Alert timestamp | `2024-01-15T11:00:15Z` |
| **flow_id** | Number | Flow identifier | `987654321` |
| **event_type** | String | Always `"alert"` for alert logs | `alert` |
| **src_ip** | String | Source IP (attacker) | `198.51.100.50` |
| **src_port** | Number | Source port | `54322` |
| **dest_ip** | String | Destination IP (target) | `10.0.1.10` |
| **dest_port** | Number | Destination port | `22` |
| **proto** | String | Protocol | `TCP`, `UDP`, `ICMP` |

### Alert Sub-Object

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **action** | String | Action taken | `blocked`, `alerted`, `rejected` |
| **signature** | String | Rule signature description | `ET EXPLOIT SSH Brute Force` |
| **signature_id** | Number | Unique signature identifier | `2001219` |
| **rev** | Number | Signature revision number | `20` |
| **category** | String | Alert category | See categories table below |
| **severity** | Number | Severity level (1-4) | `1` (highest) to `4` (lowest) |

### Alert Actions

| Action | Description |
|--------|-------------|
| **blocked** | Traffic was blocked |
| **alerted** | Traffic was allowed but alert generated |
| **rejected** | Connection was rejected (RST sent) |
| **dropped** | Packet silently dropped |

### Alert Severities

| Severity | Level | Description |
|----------|-------|-------------|
| **1** | High | Critical threats (exploits, malware) |
| **2** | Medium | Suspicious activity, policy violations |
| **3** | Low | Informational, potential reconnaissance |
| **4** | Informational | Benign or very low risk |

### Alert Categories

Common alert categories (based on Suricata/Snort taxonomy):

| Category | Description | Example Signatures |
|----------|-------------|-------------------|
| **A Network Trojan was detected** | Backdoor/trojan communication | C2 callbacks, RAT activity |
| **Attempted Administrator Privilege Gain** | Privilege escalation attempts | SSH brute force, exploit attempts |
| **Attempted Information Leak** | Data exfiltration or reconnaissance | Port scans, directory traversal |
| **Attempted User Privilege Gain** | User-level privilege escalation | Local exploits |
| **Denial of Service** | DoS/DDoS attacks | SYN floods, ICMP floods |
| **Executable Code was Detected** | Shellcode, malware download | Buffer overflow exploits |
| **Misc Attack** | Various attack types | Generic attack patterns |
| **Potentially Bad Traffic** | Suspicious but not definitive | Unusual protocols, anomalies |
| **Web Application Attack** | HTTP/HTTPS attacks | SQL injection, XSS, path traversal |
| **Not Suspicious Traffic** | Known benign (should be tuned out) | False positives |

## Example Logs

### Example 1: Allowed HTTPS Flow
```json
{
  "firewall_name": "production-firewall",
  "availability_zone": "us-east-1a",
  "event_timestamp": "2024-01-15T10:00:00.000Z",
  "event": {
    "timestamp": "2024-01-15T10:00:00Z",
    "flow_id": 100000001,
    "event_type": "netflow",
    "src_ip": "10.0.1.5",
    "src_port": 50123,
    "dest_ip": "203.0.113.10",
    "dest_port": 443,
    "proto": "TCP",
    "app_proto": "https",
    "netflow": {
      "pkts": 150,
      "bytes": 125000,
      "start": "2024-01-15T09:59:50Z",
      "end": "2024-01-15T10:00:00Z",
      "age": 10,
      "min_ttl": 64,
      "max_ttl": 64
    }
  }
}
```

### Example 2: Malware C2 Communication (Blocked)
```json
{
  "firewall_name": "production-firewall",
  "availability_zone": "us-east-1a",
  "event_timestamp": "2024-01-15T11:30:22.567Z",
  "event": {
    "timestamp": "2024-01-15T11:30:22Z",
    "flow_id": 200000002,
    "event_type": "alert",
    "src_ip": "10.0.2.15",
    "src_port": 49321,
    "dest_ip": "198.51.100.100",
    "dest_port": 4444,
    "proto": "TCP",
    "alert": {
      "action": "blocked",
      "signature": "ET MALWARE Suspicious Outbound Connection to Known C2",
      "signature_id": 2024001,
      "rev": 1,
      "category": "A Network Trojan was detected",
      "severity": 1
    }
  }
}
```

### Example 3: SQL Injection Attempt (Blocked)
```json
{
  "firewall_name": "production-firewall",
  "availability_zone": "us-east-1b",
  "event_timestamp": "2024-01-15T12:15:10.123Z",
  "event": {
    "timestamp": "2024-01-15T12:15:10Z",
    "flow_id": 300000003,
    "event_type": "alert",
    "src_ip": "198.51.100.200",
    "src_port": 55678,
    "dest_ip": "10.0.3.50",
    "dest_port": 80,
    "proto": "TCP",
    "alert": {
      "action": "blocked",
      "signature": "ET WEB_SPECIFIC_APPS SQL Injection Attempt",
      "signature_id": 2010935,
      "rev": 3,
      "category": "Web Application Attack",
      "severity": 1
    }
  }
}
```

### Example 4: Port Scan Detection
```json
{
  "firewall_name": "production-firewall",
  "availability_zone": "us-east-1a",
  "event_timestamp": "2024-01-15T13:00:05.789Z",
  "event": {
    "timestamp": "2024-01-15T13:00:05Z",
    "flow_id": 400000004,
    "event_type": "alert",
    "src_ip": "198.51.100.250",
    "src_port": 54321,
    "dest_ip": "10.0.1.100",
    "dest_port": 22,
    "proto": "TCP",
    "alert": {
      "action": "blocked",
      "signature": "ET SCAN Potential TCP SYN Scan",
      "signature_id": 2100366,
      "rev": 7,
      "category": "Attempted Information Leak",
      "severity": 3
    }
  }
}
```

### Example 5: DNS Tunneling Detected
```json
{
  "firewall_name": "production-firewall",
  "availability_zone": "us-east-1b",
  "event_timestamp": "2024-01-15T14:20:33.456Z",
  "event": {
    "timestamp": "2024-01-15T14:20:33Z",
    "flow_id": 500000005,
    "event_type": "alert",
    "src_ip": "10.0.4.25",
    "src_port": 52341,
    "dest_ip": "8.8.8.8",
    "dest_port": 53,
    "proto": "UDP",
    "alert": {
      "action": "blocked",
      "signature": "ET POLICY Suspicious Long DNS TXT Query",
      "signature_id": 2019835,
      "rev": 2,
      "category": "Potentially Bad Traffic",
      "severity": 2
    }
  }
}
```

### Example 6: Shellcode Detection
```json
{
  "firewall_name": "production-firewall",
  "availability_zone": "us-east-1a",
  "event_timestamp": "2024-01-15T15:45:18.234Z",
  "event": {
    "timestamp": "2024-01-15T15:45:18Z",
    "flow_id": 600000006,
    "event_type": "alert",
    "src_ip": "198.51.100.75",
    "src_port": 33445,
    "dest_ip": "10.0.5.10",
    "dest_port": 8080,
    "proto": "TCP",
    "alert": {
      "action": "blocked",
      "signature": "ET SHELLCODE x86 inc ebx NOOP",
      "signature_id": 2009582,
      "rev": 2,
      "category": "Executable Code was Detected",
      "severity": 1
    }
  }
}
```

### Example 7: DoS Attack Detection
```json
{
  "firewall_name": "production-firewall",
  "availability_zone": "us-east-1a",
  "event_timestamp": "2024-01-15T16:30:00.000Z",
  "event": {
    "timestamp": "2024-01-15T16:30:00Z",
    "flow_id": 700000007,
    "event_type": "alert",
    "src_ip": "198.51.100.150",
    "src_port": 0,
    "dest_ip": "10.0.1.50",
    "dest_port": 0,
    "proto": "ICMP",
    "alert": {
      "action": "blocked",
      "signature": "ET DOS ICMP Flood Detected",
      "signature_id": 2100649,
      "rev": 4,
      "category": "Denial of Service",
      "severity": 2
    }
  }
}
```

## Rule Sources

AWS Network Firewall can use multiple rule sources:

### 1. Suricata Compatible Rules
- Open-source IDS/IPS signature format
- ET Open rules (Emerging Threats)
- Custom signatures
- Community rules

### 2. AWS Managed Rule Groups
- AWS-curated and maintained
- Updated automatically
- Threat intelligence fed
- Categories:
  - Malware domains
  - Botnet C2
  - Known exploits

### 3. Domain Allow/Deny Lists
- Simple domain filtering
- Wildcard support
- Protocol enforcement

### 4. IP Set Allow/Deny Lists
- CIDR-based filtering
- Geolocation blocking
- Threat feed integration

## Log Configuration

### Log Destination Types

| Type | Use Case | Retention | Query |
|------|----------|-----------|-------|
| **CloudWatch Logs** | Real-time monitoring | Configurable | CloudWatch Insights |
| **S3** | Long-term storage, compliance | Lifecycle policies | Athena, S3 Select |
| **Kinesis Data Firehose** | Real-time streaming | N/A (pass-through) | Downstream analytics |

### Log Type Selection

You can enable:
- **Flow logs only** - Lower cost, traffic visibility
- **Alert logs only** - Security events only
- **Both** - Complete visibility (recommended)

## Log Volume Considerations

### Factors Affecting Volume
1. **Traffic volume** - More connections = more flow logs
2. **Rule sensitivity** - More rules = more alerts
3. **Attack traffic** - Attacks generate many alerts
4. **Connection duration** - Long connections = fewer flow logs
5. **Aggregation** - Flows aggregated over time windows

### Typical Volumes
- **Low traffic**: 1-10 GB/day
- **Medium traffic**: 10-100 GB/day
- **High traffic**: 100+ GB/day

## CloudWatch Insights Queries

### Top Alert Signatures
```
fields @timestamp, event.alert.signature
| filter event.event_type = "alert"
| stats count() by event.alert.signature
| sort count desc
| limit 10
```

### Blocked IPs
```
fields @timestamp, event.src_ip
| filter event.alert.action = "blocked"
| stats count() by event.src_ip
| sort count desc
```

### High Severity Alerts
```
fields @timestamp, event.src_ip, event.dest_ip, event.alert.signature
| filter event.alert.severity = 1
| sort @timestamp desc
```

### Traffic by Application Protocol
```
fields @timestamp, event.app_proto, event.netflow.bytes
| filter event.event_type = "netflow"
| stats sum(event.netflow.bytes) by event.app_proto
| sort sum desc
```

## Integration with Other AWS Services

### VPC Flow Logs Correlation
- Network Firewall sees same traffic as VPC
- Correlate using 5-tuple (src/dst IP/port, protocol)
- Network Firewall provides application-layer visibility

### GuardDuty Integration
- Both detect threats independently
- GuardDuty focuses on AWS API and broader context
- Network Firewall focuses on network traffic content

### Security Hub
- Network Firewall findings sent to Security Hub
- Centralized security dashboard
- Cross-service threat correlation

## Best Practices

1. **Enable Both Log Types**: Flow + Alert for complete visibility
2. **Right-Size Rules**: Balance security vs. false positives
3. **Tune Signatures**: Suppress known false positives
4. **Set Retention**: Match compliance requirements
5. **Monitor Costs**: Logs can be expensive at scale
6. **Alert on Critical**: High-severity alerts to SNS/email
7. **Export to SIEM**: Feed to centralized security platform
8. **Regular Review**: Analyze trends, update rules
9. **Baseline Normal**: Understand typical traffic patterns
10. **Test Rules**: Validate rules don't break legitimate traffic

## Common Use Cases

1. **Malware Detection**: C2 communication blocking
2. **Exploit Prevention**: IDS/IPS for known vulnerabilities
3. **Data Exfiltration**: Large outbound transfers to suspicious IPs
4. **Compliance**: Meet regulatory network monitoring requirements
5. **Threat Hunting**: Investigate suspicious patterns
6. **Incident Response**: Forensic analysis of attacks
7. **DDoS Mitigation**: Detect and block flood attacks
8. **Policy Enforcement**: Block prohibited protocols/destinations

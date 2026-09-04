# VPC Flow Logs Format Reference

Complete specification for AWS VPC Flow Logs based on AWS VPC User Guide.

## Overview

VPC Flow Logs capture information about IP traffic going to and from network interfaces in your VPC. The logs support **8 versions** (v2-v8), with each version introducing new fields.

## Default Format (Version 2)

The default format includes 14 fields in this order:

```
version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status
```

## All Available Fields (Versions 2-8)

| Field | Description | Version | Data Type |
|-------|-------------|---------|-----------|
| **version** | VPC Flow Logs version (default: 2) | 2 | INT_32 |
| **account-id** | AWS account ID of source network interface owner | 2 | STRING |
| **interface-id** | Network interface ID | 2 | STRING |
| **srcaddr** | Source IP address | 2 | STRING |
| **dstaddr** | Destination IP address | 2 | STRING |
| **srcport** | Source port | 2 | INT_32 |
| **dstport** | Destination port | 2 | INT_32 |
| **protocol** | IANA protocol number | 2 | INT_32 |
| **packets** | Number of packets transferred | 2 | INT_64 |
| **bytes** | Number of bytes transferred | 2 | INT_64 |
| **start** | Unix timestamp - first packet received | 2 | INT_64 |
| **end** | Unix timestamp - last packet received | 2 | INT_64 |
| **action** | Traffic action: **ACCEPT** or **REJECT** | 2 | STRING |
| **log-status** | Logging status: **OK**, **NODATA**, **SKIPDATA** | 2 | STRING |
| **vpc-id** | VPC ID | 3 | STRING |
| **subnet-id** | Subnet ID | 3 | STRING |
| **instance-id** | EC2 instance ID (or '-' for managed interfaces) | 3 | STRING |
| **tcp-flags** | TCP flags bitmask (FIN=1, SYN=2, RST=4, SYN-ACK=18) | 3 | INT_32 |
| **type** | Traffic type: **IPv4**, **IPv6**, **EFA** | 3 | STRING |
| **pkt-srcaddr** | Packet-level source IP (original, before NAT) | 3 | STRING |
| **pkt-dstaddr** | Packet-level destination IP (original, before NAT) | 3 | STRING |
| **region** | AWS region | 4 | STRING |
| **az-id** | Availability Zone ID | 4 | STRING |
| **sublocation-type** | Sublocation type: **wavelength**, **outpost**, **localzone** | 4 | STRING |
| **sublocation-id** | Sublocation ID | 4 | STRING |
| **pkt-src-aws-service** | AWS service name for source IP | 5 | STRING |
| **pkt-dst-aws-service** | AWS service name for destination IP | 5 | STRING |
| **flow-direction** | Flow direction: **ingress** or **egress** | 5 | STRING |
| **traffic-path** | Path for egress traffic (1-8, see below) | 5 | INT_32 |
| **ecs-cluster-arn** | ECS cluster ARN | 7 | STRING |
| **ecs-cluster-name** | ECS cluster name | 7 | STRING |
| **ecs-container-instance-arn** | ECS container instance ARN | 7 | STRING |
| **ecs-container-instance-id** | ECS container instance ID | 7 | STRING |
| **ecs-container-id** | First container Docker runtime ID | 7 | STRING |
| **ecs-second-container-id** | Second container Docker runtime ID | 7 | STRING |
| **ecs-service-name** | ECS service name | 7 | STRING |
| **ecs-task-definition-arn** | ECS task definition ARN | 7 | STRING |
| **ecs-task-arn** | ECS task ARN | 7 | STRING |
| **ecs-task-id** | ECS task ID | 7 | STRING |
| **reject-reason** | Rejection reason: **BPA** (Block Public Access) or '-' | 8 | STRING |

## Field Value Definitions

### Action Values
- **ACCEPT**: Traffic was accepted
- **REJECT**: Traffic was rejected (security group/ACL blocked, or packets after connection closed)

### Log-Status Values
- **OK**: Normal logging
- **NODATA**: No network traffic during aggregation interval
- **SKIPDATA**: Some records skipped (capacity constraints/errors)

### TCP Flags (Bitmask)
- FIN = 1
- SYN = 2
- RST = 4
- SYN-ACK = 18
- Values can be OR-ed (e.g., 19 = SYN-ACK + FIN)

### Traffic Path Values
1. Through another resource in same VPC
2. Through internet gateway or gateway VPC endpoint
3. Through virtual private gateway
4. Through intra-region VPC peering
5. Through inter-region VPC peering
6. Through Local Zone or Wavelength Zone
7. Through gateway VPC endpoint (Nitro-based only)
8. Through internet gateway (Nitro-based only)

### AWS Service Codes
AMAZON, AMAZON_APPFLOW, AMAZON_CONNECT, API_GATEWAY, AURORA_DSQL, CHIME_MEETINGS, CHIME_VOICECONNECTOR, CLOUD9, CLOUDFRONT, CLOUDFRONT_ORIGIN_FACING, CODEBUILD, DYNAMODB, EBS, EC2, EC2_INSTANCE_CONNECT, GLOBALACCELERATOR, IVS_LOW_LATENCY, IVS_REALTIME, KINESIS_VIDEO_STREAMS, MEDIA_PACKAGE_V2, ROUTE53, ROUTE53_HEALTHCHECKS, ROUTE53_HEALTHCHECKS_PUBLISHING, ROUTE53_RESOLVER, S3, WORKSPACES_GATEWAYS

## Common Protocol Numbers
- 1 = ICMP
- 6 = TCP
- 17 = UDP

## Example Log Records

### Example 1: Accepted SSH Traffic (Version 2)
```
2 123456789010 eni-1235b8ca123456789 172.31.16.139 172.31.16.21 20641 22 6 20 4249 1418530010 1418530070 ACCEPT OK
```

### Example 2: Rejected RDP Traffic
```
2 123456789010 eni-1235b8ca123456789 172.31.9.69 172.31.9.12 49761 3389 6 20 4249 1418530010 1418530070 REJECT OK
```

### Example 3: No Data
```
2 123456789010 eni-1235b8ca123456789 - - - - - - - 1431280876 1431280934 - NODATA
```

### Example 4: IPv6 SSH Traffic
```
2 123456789010 eni-1235b8ca123456789 2001:db8:1234:a100:8d6e:3477:df66:f105 2001:db8:1234:a102:3304:8879:34cf:4071 34892 22 6 54 8855 1477913708 1477913820 ACCEPT OK
```

### Example 5: Custom Format with TCP Flags (Version 3)

**SYN (Connection initiation):**
```
3 vpc-abcdefab012345678 subnet-aaaaaaaa012345678 i-01234567890123456 eni-1235b8ca123456789 123456789010 IPv4 52.213.180.42 10.0.0.62 43416 5001 52.213.180.42 10.0.0.62 6 568 8 1566848875 1566848933 ACCEPT 2 OK
```

**SYN-ACK (Server response):**
```
3 vpc-abcdefab012345678 subnet-aaaaaaaa012345678 i-01234567890123456 eni-1235b8ca123456789 123456789010 IPv4 10.0.0.62 52.213.180.42 5001 43416 10.0.0.62 52.213.180.42 6 376 7 1566848875 1566848933 ACCEPT 18 OK
```

**FIN (Connection close):**
```
3 vpc-abcdefab012345678 subnet-aaaaaaaa012345678 i-01234567890123456 eni-1235b8ca123456789 123456789010 IPv4 10.0.0.62 52.213.180.42 5001 43418 10.0.0.62 52.213.180.42 6 63388 1219 1566848933 1566849113 ACCEPT 1 OK
```

### Example 6: NAT Gateway Traffic

**Instance to NAT gateway:**
```
- eni-1235b8ca123456789 10.0.1.5 10.0.0.220 10.0.1.5 203.0.113.5
```
Note: `dstaddr` = NAT gateway IP, `pkt-dstaddr` = final destination

**NAT gateway to internet:**
```
- eni-1235b8ca123456789 10.0.0.220 203.0.113.5 10.0.0.220 203.0.113.5
```

### Example 7: EC2 to S3 Traffic (Version 5)

**Ingress (S3 to EC2):**
```
5 52.95.128.179 10.0.0.71 80 34210 6 1616729292 1616729349 IPv4 14 15044 123456789012 vpc-abcdefab012345678 subnet-aaaaaaaa012345678 i-0c50d5961bcb2d47b eni-1235b8ca123456789 ap-southeast-2 apse2-az3 - - ACCEPT 19 52.95.128.179 10.0.0.71 S3 - - ingress OK
```

**Egress (EC2 to S3):**
```
5 10.0.0.71 52.95.128.179 34210 80 6 1616729292 1616729349 IPv4 7 471 123456789012 vpc-abcdefab012345678 subnet-aaaaaaaa012345678 i-0c50d5961bcb2d47b eni-1235b8ca123456789 ap-southeast-2 apse2-az3 - - ACCEPT 3 10.0.0.71 52.95.128.179 - S3 8 egress OK
```

## Important Concepts

### Security Groups vs Network ACLs
- **Security Groups**: Stateful - response traffic automatically allowed
- **Network ACLs**: Stateless - response traffic must be explicitly allowed

Example: Ping from 203.0.113.12 to instance 172.31.16.139
- Security group: allows inbound ICMP, blocks outbound ICMP
- Network ACL: allows inbound ICMP, blocks outbound ICMP
- Result: Incoming ping = **ACCEPT**, response = **REJECT** (due to network ACL)

### Aggregation
- Default: 10-minute maximum aggregation window
- Can be configured to 1 minute
- Nitro-based instances: Always ≤1 minute

### Log Delivery
- CloudWatch Logs: ~5 minutes
- Amazon S3: ~10 minutes
- Best-effort delivery (may be delayed)

### Missing Values
- `-` indicates field is not applicable or not computable
- Metadata fields are best-effort approximations

## Implementation Notes

1. **Space-delimited format** - fields separated by single space
2. **Custom formats** - Can specify any combination of fields
3. **Extensibility** - AWS may add new fields in future versions
4. **Version selection** - Custom format version = highest version among specified fields
5. **Timestamps** - Unix epoch format (seconds since 1970-01-01 00:00:00 UTC)
